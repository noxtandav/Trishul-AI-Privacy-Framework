"""
Trishul CLI — entry point for the multi-step coding agent.

Usage:
    # Start a task at Tier 2 (anonymous, default)
    trishul task "Add rate limiting to the API endpoints"

    # Start a task at Tier 1 (full isolation via Bedrock)
    trishul task --tier 1 "Analyze this financial CSV and generate a report"

    # Start a task at Tier 3 (open, no privacy precautions)
    trishul task --tier 3 "Help me write unit tests for the utils module"

    # Interactive chat mode
    trishul chat --tier 2

    # List past conversations
    trishul history

    # Resume a previous conversation
    trishul resume <conversation_id>
"""

import argparse
import json
import os
import sys
import uuid

from .agent import Tier, TrishulAgent


def load_config(config_path: str | None = None) -> dict:
    """Load configuration from file or environment variables."""
    config = {}

    # Try loading from config file
    if config_path and os.path.isfile(config_path):
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

    # Default config file location
    default_path = os.path.expanduser("~/.trishul/config.json")
    if not config and os.path.isfile(default_path):
        with open(default_path, encoding="utf-8") as f:
            config = json.load(f)

    # Override with environment variables
    env_map = {
        "OPENROUTER_API_KEY": "openrouter_api_key",
        "AWS_ACCESS_KEY_ID": "aws_access_key_id",
        "AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
        "AWS_REGION": "aws_region",
        "OLLAMA_BASE_URL": "ollama_base_url",
        "OLLAMA_MODEL": "ollama_model",
        "TRISHUL_TIER": "tier",
        "TRISHUL_PROJECT_ROOT": "project_root",
        "DIRECT_API_KEY": "direct_api_key",
    }
    for env_var, config_key in env_map.items():
        value = os.environ.get(env_var)
        if value is not None:
            config[config_key] = value

    # Coerce tier to int if present
    if "tier" in config:
        config["tier"] = int(config["tier"])

    return config


def cmd_task(args: argparse.Namespace, config: dict) -> None:
    """Execute a multi-step task."""
    config["tier"] = args.tier
    config["project_root"] = args.project_root or config.get(
        "project_root", os.getcwd()
    )

    agent = TrishulAgent(config)
    agent.execute_task(args.description)


def cmd_chat(args: argparse.Namespace, config: dict) -> None:
    """Interactive chat mode."""
    config["tier"] = args.tier
    config["project_root"] = args.project_root or config.get(
        "project_root", os.getcwd()
    )

    agent = TrishulAgent(config)
    tier = Tier(args.tier)
    conv_id = uuid.uuid4().hex[:8]

    print(f"[trishul] Chat mode | Tier {tier} | {tier.name}")
    print(f"[trishul] Conversation: {conv_id}")
    print("[trishul] Type /quit to exit, /tier <n> to switch tier.\n")

    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[trishul] Goodbye.")
            break

        if not user_input:
            continue

        if user_input == "/quit":
            print("[trishul] Goodbye.")
            break

        if user_input.startswith("/tier "):
            try:
                new_tier = int(user_input.split()[1])
                if new_tier not in (1, 2, 3):
                    raise ValueError
                agent.tier = Tier(new_tier)
                config["tier"] = new_tier
                agent.context_builder.tier = new_tier
                print(
                    f"[trishul] Switched to Tier {new_tier} "
                    f"| {Tier(new_tier).name}"
                )
            except (ValueError, IndexError):
                print("[trishul] Usage: /tier 1|2|3")
            continue

        response = agent._call_llm(user_input)
        print(f"\nassistant> {response}\n")


def cmd_history(_args: argparse.Namespace, _config: dict) -> None:
    """List past conversations (placeholder — requires backend)."""
    print("[trishul] History requires the Trishul backend to be running.")
    print("[trishul] See docs/cli-agent.md for setup instructions.")


def cmd_resume(args: argparse.Namespace, _config: dict) -> None:
    """Resume a previous conversation (placeholder — requires backend)."""
    print(
        f"[trishul] Resume conversation {args.conversation_id} "
        "requires the Trishul backend."
    )
    print("[trishul] See docs/cli-agent.md for setup instructions.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trishul",
        description="Trishul CLI — privacy-aware AI coding agent",
    )
    parser.add_argument(
        "--config", type=str, default=None, help="Path to config JSON file"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # trishul task
    task_parser = subparsers.add_parser(
        "task", help="Execute a multi-step coding task"
    )
    task_parser.add_argument("description", type=str, help="Task description")
    task_parser.add_argument(
        "--tier", type=int, default=2, choices=[1, 2, 3],
        help="Privacy tier (default: 2)",
    )
    task_parser.add_argument(
        "--project-root", type=str, default=None,
        help="Project root directory (default: cwd)",
    )

    # trishul chat
    chat_parser = subparsers.add_parser(
        "chat", help="Interactive chat mode"
    )
    chat_parser.add_argument(
        "--tier", type=int, default=2, choices=[1, 2, 3],
        help="Privacy tier (default: 2)",
    )
    chat_parser.add_argument(
        "--project-root", type=str, default=None,
        help="Project root directory (default: cwd)",
    )

    # trishul history
    subparsers.add_parser("history", help="List past conversations")

    # trishul resume
    resume_parser = subparsers.add_parser(
        "resume", help="Resume a previous conversation"
    )
    resume_parser.add_argument(
        "conversation_id", type=str, help="Conversation ID to resume"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    config = load_config(args.config)

    commands = {
        "task": cmd_task,
        "chat": cmd_chat,
        "history": cmd_history,
        "resume": cmd_resume,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
