"""
Trishul CLI Agent — core task execution loop.

Handles multi-step reasoning with privacy-aware LLM routing.
Local operations (file I/O, command execution) never leave the machine.
Only LLM reasoning calls go through the tier routing pipeline.
"""

import json
import os
import subprocess
from dataclasses import dataclass
from enum import IntEnum

from ..pii_redactor import PIIRedactor
from .clients import (
    BaseLLMClient,
    BedrockClient,
    DirectAPIClient,
    OllamaClient,
    OpenRouterClient,
)
from .context import ContextBuilder


class Tier(IntEnum):
    FULL_ISOLATION = 1
    ANONYMOUS = 2
    OPEN = 3


@dataclass
class TaskStep:
    """A single step in a multi-step task."""

    description: str
    action: str  # "edit_file", "run_command", "create_file", "done"
    target: str | None  # file path or command
    content: str | None  # new content or expected output


class TrishulAgent:
    """
    Multi-step coding agent with privacy-tier routing.

    Local operations (file I/O, command execution) never leave the machine.
    Only LLM reasoning calls go through the tier routing pipeline.
    """

    SKIP_DIRS = {
        ".git", "node_modules", "__pycache__", ".venv",
        "venv", ".trishul", "dist", "build", ".eggs",
    }

    def __init__(self, config: dict):
        self.tier = Tier(config.get("tier", 2))
        self.project_root = config.get("project_root", os.getcwd())
        self.max_iterations = config.get("max_iterations", 3)
        self.api_client = self._init_client(config)
        self.redactor = PIIRedactor(
            custom_terms=config.get("custom_redaction_terms", {}),
            use_ner=config.get("use_ner", True),
        )
        self.context_builder = ContextBuilder(
            self.project_root, self.redactor, self.tier
        )
        self.conversation_history: list[dict] = []

    def _init_client(self, config: dict) -> BaseLLMClient:
        """Initialize the appropriate LLM client based on tier."""
        if self.tier == Tier.FULL_ISOLATION:
            if config.get("use_bedrock"):
                return BedrockClient(config)
            return OllamaClient(config)
        elif self.tier == Tier.ANONYMOUS:
            return OpenRouterClient(config)
        else:
            return DirectAPIClient(config)

    def execute_task(self, task_description: str) -> None:
        """
        Execute a multi-step task with the agent loop.

        The agent plans, executes, and iterates until the task
        is complete or the user intervenes.
        """
        print(f"[trishul] Tier {self.tier} | {self.tier.name}")
        print(f"[trishul] Task: {task_description}\n")

        # Step 1: Gather project context (local, private)
        project_structure = self._scan_project()
        relevant_files = self._identify_relevant_files(
            task_description, project_structure
        )

        # Step 2: Ask LLM to create a plan
        context = self.context_builder.build_context(
            task_description, relevant_files
        )

        plan_prompt = (
            "You are a coding agent. Given the following task "
            "and code context, create a step-by-step plan. For each step, "
            "specify the action (edit_file, run_command, create_file) "
            "and the target.\n\n"
            f"Task: {task_description}\n\n"
            f"Project context:\n{context}\n\n"
            "Respond with a JSON array of steps. Each step must have keys: "
            '"description", "action", "target", "content".'
        )

        plan_response = self._call_llm(plan_prompt)
        steps = self._parse_plan(plan_response)

        # Step 3: Execute each step
        for i, step in enumerate(steps):
            print(f"\n[trishul] Step {i + 1}/{len(steps)}: {step.description}")

            result = self._execute_step(step)

            if not result["success"]:
                print(f"  FAILED: {result['error']}")
                # Attempt to fix with LLM guidance
                fix_prompt = (
                    f"Step failed with error:\n{result['error']}\n\n"
                    f"Original step: {step.description}\n"
                    f"Output: {result.get('output', '')}\n\n"
                    "Please provide a corrected approach as a single JSON "
                    'object with keys: "description", "action", "target", '
                    '"content".'
                )

                for attempt in range(self.max_iterations):
                    fix_response = self._call_llm(fix_prompt)
                    fixed_step = self._parse_single_step(fix_response)
                    if fixed_step is None:
                        print(f"  Could not parse fix (attempt {attempt + 1})")
                        continue
                    result = self._execute_step(fixed_step)
                    if result["success"]:
                        break

            if result["success"]:
                print("  OK")
            else:
                print(f"  SKIPPED (could not resolve): {result['error']}")

        print("\n[trishul] Task complete.")

    def _call_llm(self, prompt: str) -> str:
        """
        Send a prompt to the LLM through the appropriate tier.
        Handles redaction (Tier 2) and routing transparently.
        """
        if self.tier == Tier.ANONYMOUS:
            prompt = self.redactor.redact(
                prompt, self.context_builder.mapping
            )

        self.conversation_history.append({"role": "user", "content": prompt})

        response = self.api_client.chat(self.conversation_history)

        if self.tier == Tier.ANONYMOUS:
            response = self.context_builder.rehydrate(response)

        self.conversation_history.append(
            {"role": "assistant", "content": response}
        )

        return response

    def _execute_step(self, step: TaskStep) -> dict:
        """
        Execute a task step LOCALLY.
        File I/O and commands never leave the machine.
        """
        try:
            if step.action == "edit_file":
                filepath = os.path.join(self.project_root, step.target)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(step.content or "")
                return {"success": True, "output": f"Wrote {step.target}"}

            elif step.action == "run_command":
                result = subprocess.run(
                    step.target,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=60,
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                }

            elif step.action == "create_file":
                filepath = os.path.join(self.project_root, step.target)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(step.content or "")
                return {"success": True, "output": f"Created {step.target}"}

            elif step.action == "done":
                return {"success": True, "output": "Task marked as done."}

            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {step.action}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _scan_project(self) -> list[str]:
        """Scan project structure locally. Nothing sent externally."""
        files = []
        for root, dirs, filenames in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for fname in filenames:
                filepath = os.path.relpath(
                    os.path.join(root, fname), self.project_root
                )
                files.append(filepath)
        return files

    def _identify_relevant_files(
        self, task: str, all_files: list[str]
    ) -> list[str]:
        """
        Use a lightweight LLM call to identify which files
        are relevant to the task. Only file NAMES are sent,
        not contents.
        """
        file_list = "\n".join(all_files[:200])
        prompt = (
            f'Given this task: "{task}"\n\n'
            f"And these project files:\n{file_list}\n\n"
            "Which files are most likely relevant? Return a JSON array "
            "of file paths. Select at most 10 files."
        )

        response = self._call_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: return files with common code extensions
            return [
                f for f in all_files
                if any(ext in f for ext in [".py", ".js", ".ts", ".jsx"])
            ][:10]

    def _parse_plan(self, response: str) -> list[TaskStep]:
        """Parse the LLM's plan response into TaskStep objects."""
        try:
            # Try to extract JSON from the response
            text = response
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            steps_data = json.loads(text)
            return [
                TaskStep(
                    description=s.get("description", ""),
                    action=s.get("action", ""),
                    target=s.get("target"),
                    content=s.get("content"),
                )
                for s in steps_data
            ]
        except (json.JSONDecodeError, KeyError, IndexError):
            return [
                TaskStep(
                    description="Could not parse plan — manual review needed",
                    action="done",
                    target=None,
                    content=None,
                )
            ]

    def _parse_single_step(self, response: str) -> TaskStep | None:
        """Parse a single step from an LLM fix response."""
        try:
            text = response
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            data = json.loads(text)
            return TaskStep(
                description=data.get("description", ""),
                action=data.get("action", ""),
                target=data.get("target"),
                content=data.get("content"),
            )
        except (json.JSONDecodeError, KeyError):
            return None
