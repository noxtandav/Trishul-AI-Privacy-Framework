# Trishul CLI: Multi-Step Agent for Coding & Complex Tasks

A chat interface works well for single-turn conversations. But many real-world tasks require multi-step reasoning: building a feature across multiple files, debugging iteratively, running code, checking output, and looping until it works. The Trishul CLI handles these workflows while respecting privacy tiers.

## Why a Separate CLI?

When you're coding, you need the AI to:

- Read files from your local filesystem
- Execute shell commands and inspect output
- Apply code changes across multiple files
- Run tests and iterate based on failures
- Manage git commits and branches

A web UI can't do this safely. The CLI runs locally on your dev machine with filesystem access and command execution, while routing all LLM reasoning through Trishul's privacy tiers.

## Installation

```bash
# From the project root
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Set up your API key (for Tier 2 via OpenRouter)
export OPENROUTER_API_KEY="your-key-here"
```

Optionally, create a config file at `~/.trishul/config.json`:

```json
{
    "openrouter_api_key": "your-key-here",
    "openrouter_model": "anthropic/claude-sonnet-4-20250514",
    "custom_redaction_terms": {
        "company": ["Acme Corp"],
        "project": ["Project Atlas"]
    },
    "use_ner": true
}
```

## CLI Commands

```bash
# Start a task at Tier 2 (anonymous, default)
python -m src.cli.main task "Add rate limiting to the API endpoints"

# Start a task at Tier 1 (full isolation via Bedrock)
python -m src.cli.main task --tier 1 "Analyze this financial CSV"

# Start a task at Tier 3 (open, no privacy precautions)
python -m src.cli.main task --tier 3 "Help me write unit tests"

# Interactive chat mode
python -m src.cli.main chat --tier 2

# List past conversations (requires backend)
python -m src.cli.main history

# Resume a previous conversation (requires backend)
python -m src.cli.main resume <conversation_id>

# Switch tier mid-session (inside interactive mode):
> /tier 1
```

## The Agent Loop

The core of the CLI is a task loop that separates local operations (private by nature) from LLM reasoning (routed through tiers):

```
1. USER TASK ──> "Refactor auth module to support OAuth2"
       |
2. CONTEXT GATHERING (local, private)
       |  - Read relevant source files
       |  - Analyze project structure
       |
3. SELECTIVE CONTEXT BUILDING
       |  - Pick only the code snippets the LLM needs
       |  - Strip file paths, project names (Tier 2)
       |  - Never send full codebase
       |
4. PII REDACTION (Tier 2 only)
       |  - Run PIIRedactor on outgoing context
       |  - Replace identifiers with placeholders
       |
5. LLM CALL ──> OpenRouter / Bedrock / Local
       |         (based on conversation tier)
       |
6. RESPONSE PROCESSING
       |  - Rehydrate placeholders (Tier 2)
       |  - Parse code changes, commands, plan
       |
7. LOCAL EXECUTION (private)
       |  - Apply file edits
       |  - Run commands
       |  - Capture output
       |
8. EVALUATION
       |  - Did it work? ──> Yes ──> Done / Next step
       |  - Did it fail? ──> Loop back to step 3
```

## Key Design: Minimal Context Exposure

The CLI never sends your entire codebase to the LLM. The `ContextBuilder` builds a focused context window for each step:

- Only files relevant to the current task are included
- In Tier 2, file paths are anonymized and PII is redacted
- Conversation history is managed locally; only the necessary context goes to the LLM

## Unified Architecture: Web + CLI

The CLI and Web UI share a single FastAPI backend. Both connect to the same API and encrypted database.

| Capability | Web UI | CLI Agent |
|-----------|--------|-----------|
| Conversational chat | Primary use | Interactive mode |
| File analysis (upload) | Upload & analyze | Direct filesystem access |
| Multi-step coding tasks | -- | Primary use |
| Command execution | -- | Local shell access |
| Git operations | -- | Commit, branch, diff |
| Tier switching | Per-conversation | Per-task or mid-session |
| Mobile / remote access | Browser-based | Terminal only |
| Shared history | Full history view | Resume any conversation |

### Running the Backend

```bash
# Development
uvicorn src.backend.app:app --reload --port 8000

# Production (Docker)
docker compose up -d
```

### Cross-interface Workflow

1. Start a Tier 2 conversation in the **Web UI** to brainstorm architecture
2. The conversation is saved in the shared database
3. Switch to the **CLI** and run `python -m src.cli.main resume <conversation_id>`
4. The CLI agent implements the feature, running tests and iterating
5. Back in the **Web UI**, see the full task log

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations` | List all conversations |
| `GET` | `/api/conversations/{id}` | Get conversation with messages |
| `POST` | `/api/conversations/{id}/messages` | Send a message |
| `POST` | `/api/tasks` | Create a multi-step task |
| `GET` | `/api/tasks/{id}` | Get task status and steps |
| `POST` | `/api/tasks/{id}/steps` | Log a task step |

## Environment Variables

| Variable | Description | Required For |
|----------|-------------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Tier 2 |
| `DIRECT_API_KEY` | Direct provider API key | Tier 3 |
| `AWS_ACCESS_KEY_ID` | AWS credentials | Tier 1 (Bedrock) |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials | Tier 1 (Bedrock) |
| `AWS_REGION` | AWS region (default: us-east-1) | Tier 1 (Bedrock) |
| `OLLAMA_BASE_URL` | Ollama URL (default: localhost:11434) | Tier 1 (local) |
| `OLLAMA_MODEL` | Ollama model (default: llama3.1:8b) | Tier 1 (local) |
| `TRISHUL_DB_PATH` | Database path | Backend |
| `TRISHUL_CUSTOM_TERMS` | JSON dict of custom redaction terms | Tier 2 |
| `TRISHUL_USE_NER` | Enable spaCy NER (default: true) | Tier 2 |
