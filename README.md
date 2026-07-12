# AI Chatbot Test Harness (V2.0)

A lightweight, dataset-driven testing harness for evaluating the behavioral reliability of large language model (LLM) chatbots across multiple providers and models. It focuses on validating response invariants rather than exact outputs, reflecting the non-deterministic nature of generative AI systems.

The goal of this project is to explore practical testing strategies for AI systems using a traditional QA mindset: constraint validation, edge-case detection, repeatable evaluation, and cross-model behavioral comparison.

## Key Features

- **Multi-provider support** — run evaluations against OpenAI and Anthropic (Claude) from a single harness
- **CLI-driven execution** — filter test runs by provider (`--bots`), model (`--models`), and suite (`--suites`) without editing code
- **Suite-based test organization** — group related test cases into named suites via `suites.json` for targeted or full evaluation runs
- **Dataset-driven test cases** — define test cases in JSON; no code changes required to add new scenarios
- **Invariant-based evaluation** — assert behavioral constraints (e.g. max word count, refusing dangerous prompts) rather than exact outputs
- **Configurable repeated execution** — run each test case multiple times to measure consistency across probabilistic outputs
- **Pass/fail aggregation with pass-rate metrics** — understand reliability at a glance
- **Persistent, timestamped result artifacts** — every run generates a JSON result file for trend analysis
- **Clean separation of concerns** — chatbot routing, model interaction, and response evaluation are fully decoupled

## Why This Exists

Unlike traditional software, AI chatbot responses are probabilistic and may vary between runs and across providers. This project demonstrates how to test such systems by asserting behavioral constraints instead of exact outputs — and how to compare model behavior across providers using the same evaluation framework.

Examples of tested behaviors include:
- Response length limits
- Format compliance
- Behavioral consistency across repeated runs
- Cross-model comparison (OpenAI vs. Claude)

## Setup

1. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
```bash
cp .env.example .env
# Add your API keys:
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
```

## Running the Tests

**Run all test cases:**
```bash
python runner.py
```

**Filter by provider:**
```bash
python runner.py --bots openai
python runner.py --bots claude
```

**Filter by model:**
```bash
python runner.py --models gpt-4o-mini
python runner.py --models claude-sonnet-4-6
```

**Run a specific suite:**
```bash
python runner.py --suites max_word_count
python runner.py --suites safety_checks
```

**Combine filters:**
```bash
python runner.py --bots claude --suites max_word_count
```

**Example Output:**
Running suite: max_word_count
[openai / gpt-4o-mini] max words: 100 | word count: 83 | PASS
[claude / claude-sonnet-4-6] max words: 100 | word count: 91 | PASS
Summary: 2/2 tests passed

## Project Structure 
├── chatbots/          # Provider integrations (OpenAI, Claude) \
├── evals/             # Invariant evaluation logic \
├── test_cases/        # Individual JSON test case definitions \
├── suites.json        # Named groupings of test cases \
├── results/           # Timestamped JSON result artifacts \
├── analysis/          # Result trend analysis \
├── runner.py          # Main entry point with CLI args \
└── requirements.txt

## Test Case Format

Each test case specifies the provider, model, prompt, and behavioral invariant to evaluate:

```json
{
  "id": "openai_max100words_test1",
  "bot": "openai",
  "model": "gpt-4o-mini",
  "prompt": "Summarize the plot of Hamlet in under 100 words.",
  "invariant_type": "max_words",
  "max_words": 100
}
```

## Suite Configuration

Group related test cases into named suites in `suites.json`:

```json
{
  "max_word_count": ["openai_max100words_test1", "claude_max100words_test1"],
  "safety_checks": ["openai_safety_test1", "claude_safety_test1"]
}
```

## 📊 Result Persistence

Each run generates a timestamped JSON artifact:

```json
{
  "run_timestamp": "2026-07-10T14-32-00",
  "results": {
    "openai_max100words_test1": {
      "bot": "openai",
      "model": "gpt-4o-mini",
      "passes": 3,
      "fails": 0,
      "pass_rate": 100.0
    },
    "claude_max100words_test1": {
      "bot": "claude",
      "model": "claude-sonnet-4-6",
      "passes": 3,
      "fails": 0,
      "pass_rate": 100.0
    }
  }
}
```

## Current Limitations

- No statistical significance testing across runs
- No automated cross-model comparison reporting

## Planned Enhancements

- Additional invariants: format compliance, factual consistency
- Automated cross-model behavioral comparison reports
- Bias and edge-case test suites
- Safety and content policy evaluation suite
