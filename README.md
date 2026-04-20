# Aditya Personal MCP Server

Aditya Personal MCP Server is a local, practical context infrastructure project that makes an AI assistant actually useful for your real work. Most assistants become generic because they do not know anything about your active repos, deployed contracts, portfolio updates, or current positioning as a developer. This server solves that by exposing your own data sources as stable MCP tools. Instead of repeating context in every conversation, you run one service and let the assistant query it directly.

This project is designed for developer reality, not demo reality. It includes source connectors that you actually care about as a blockchain-focused engineer: your portfolio website, your GitHub profile, your deployed contract interfaces through Sepolia RPC, optional social context from LinkedIn and X, and a prompt utility that builds cold outreach context from your own profile data. The value is not only automation. The bigger value is consistency and grounded responses. When the assistant can query your live sources, it stops guessing and starts referencing what is true now.

## What You Are Building

At a high level, you are building a personal context API for AI clients. The API is delivered as MCP tools, and those tools are served by a FastMCP Python app. Every tool has a focused job:

- Portfolio tool for website summary and project extraction
- GitHub tools for repository listing and detailed repository context
- Contract tools for state reads and view-function calls on deployed contracts
- LinkedIn tools for profile and recent post summaries (optional)
- X tools for profile and tweet-level engagement snapshots
- Health tool for integration readiness checks
- Prompt tool for personalized cold email generation

The assistant can now answer questions like:

- Which of my projects should I pitch for a specific role?
- What is the current chain ID and readable state of this contract?
- Which repositories best represent my DeFi work?
- Is my environment fully configured or still missing secrets?
- Can you draft a short outreach email based on my real project profile?

This is the shift from prompt engineering to context engineering.

## Core Design Principles

The server follows five practical design principles:

1. Local-first execution
The service runs on your machine, with your env file, under your control. You are not forced to host data in an external service for basic usage.

2. Modular integration boundaries
Each integration lives in its own file, so failures are isolated and extension is easy.

3. Predictable output structures
Tools return consistent dictionaries and lists with explicit error objects when calls fail.

4. Graceful degradation
Optional integrations should not crash the server. If LinkedIn or X is unavailable, the rest should still work.

5. Fast diagnostics
A dedicated integration health tool gives immediate visibility into configuration and connectivity.

These principles keep the project stable while you iterate rapidly.

## System Components

The project is intentionally simple in layout but strong in capability.

The entrypoint is server.py. It loads environment variables, initializes FastMCP, and registers all tools and prompt handlers.

The tools directory contains integration modules:

- portfolio.py: fetches and parses your portfolio site
- github.py: calls GitHub APIs for repo list and detailed repo context
- contracts.py: handles ABI loading and Web3 read calls
- linkedin.py: optional LinkedIn integration with safe error behavior
- twitter.py: X profile and recent tweet analytics
- email_draft.py: creates reusable context for outbound messaging
- health.py: checks env readiness and provider-level status

The abis directory contains contract interface files such as LendingPool, MarginEngine, and TokenizedRepo.

requirements.txt defines runtime dependencies, and .env.example documents expected environment keys.

## Why This Matters for Personal Brand and Career

Most developers underuse AI because they treat it like a standalone chatbot. In reality, AI becomes far more valuable when it can query your work system directly.

When an assistant can read your portfolio and repositories, it can generate better role-targeted summaries. When it can read contract state, it can discuss protocol behavior with accuracy. When it has health checks, it can quickly tell you what is misconfigured before a demo or interview.

This has compounding value:

- Better outbound messages because context is factual
- Faster technical writing because project details are available on demand
- Better interview prep because assistants can reference your own repo history
- Better debugging support because environment and data source health are visible

In short, this server is not only a tooling project. It is a leverage project.

## Setup Strategy

The recommended setup flow is straightforward and reliable:

1. Create virtual environment in project root
2. Install dependencies from requirements.txt
3. Copy .env.example to .env
4. Fill only the integrations you want now
5. Start server.py from the virtual environment
6. Connect through an MCP-compatible client
7. Run integration health first

A practical point: optional providers can stay disabled without blocking core functionality. This matters because social platform APIs often have changing policies and keys. Portfolio, GitHub, contracts, and prompt tooling already provide strong baseline value.

## Environment Variables and Secret Model

The environment model is explicit and easy to reason about.

Portfolio:

- PORTFOLIO_URL

GitHub:

- GITHUB_USERNAME
- GITHUB_PAT (optional for public repos, recommended for stability)

Blockchain:

- RPC_URL

LinkedIn (optional):

- LINKEDIN_EMAIL
- LINKEDIN_PASSWORD

X:

- X_BEARER_TOKEN
- X_CONSUMER_KEY and X_SECRET_KEY preferred
- X_API_KEY and X_API_SECRET supported for backward compatibility
- X_ACCESS_TOKEN and X_ACCESS_SECRET optional depending on endpoint usage

Secret hygiene recommendations:

- Never commit .env
- Rotate leaked tokens immediately
- Use least-privilege scopes
- Prefer fine-grained GitHub tokens
- Keep local-only credentials local

## Tool Behavior Summary

Portfolio tool:
Attempts to fetch your website and extract useful fields like title, about text, and probable project cards. If the site is unreachable, it returns explicit error output without crashing the app.

GitHub repo list:
Returns repo metadata such as stars, language, and descriptions. This is valuable for assistant-side ranking and concise profile generation.

GitHub repo details:
Returns deeper repo context including README extraction when available. Useful for project-level Q and A.

Contract state:
Reads chain info, address balance, and attempts common zero-arg views where present in ABI.

Contract call:
Calls specified zero-arg view or pure function by name. Useful for specific protocol checks.

LinkedIn tools:
Optional and dependency-sensitive by design. If unavailable, they fail gracefully.

X tools:
Support profile-level metrics and recent posts with engagement fields. Some fields depend on account permissions.

Health tool:
Summarizes configured integrations, missing requirements, and provider alias status.

Prompt tool:
Generates a context-driven cold email draft seed using your own data.

## Integration Health as Operational Control Plane

The health tool is a major practical feature, not a cosmetic one. It gives immediate operational clarity before you start using higher-level prompts.

What it tells you:

- Which required env keys are missing
- Whether core setup is ready
- Whether RPC is reachable
- Whether optional dependencies exist
- Whether X key aliases are recognized

This makes debugging fast:

- Run health
- Fix missing keys
- Run health again
- Move to functional prompts

That loop reduces setup friction dramatically.

## Reliability and Error Handling Philosophy

A personal MCP server should fail in a controlled way. This project avoids hard crashes by returning structured error payloads from tool functions wherever possible.

Examples:

- Missing env key returns clear message
- Provider outage returns source-specific error detail
- Optional integration dependency absent returns guidance instead of stack trace
- Unsupported contract call pattern returns actionable explanation

This approach improves both developer experience and assistant behavior. The assistant can report meaningful remediation steps instead of generic failure text.

## Security and Compliance Notes

Even though this is a personal project, security discipline matters.

Do not store secrets in source files. Do not embed tokens in prompts. Do not commit environment files. If credentials have ever been shared in logs or chats, rotate them. For GitHub, use fine-grained tokens with minimal repository scope. For RPC keys, monitor provider dashboard usage and rotate periodically.

For public repositories, remember that anything committed may be indexed quickly. Treat accidental exposure as a rotation event, not a minor mistake.

## Practical Testing Plan

Use this simple test progression after each major change:

1. Import smoke test
Run a one-liner import check against server module.

2. Health tool test
Verify core_ready and missing_required_env fields.

3. Portfolio test
Confirm site fetch and extraction.

4. GitHub list and detail tests
Confirm both broad and deep repository responses.

5. Contract read tests
Check chain connectivity and at least one safe function call.

6. Prompt generation test
Confirm cold_email_draft returns context-aware text.

7. Optional platform tests
Only after keys are valid and required scopes are confirmed.

This structured approach prevents confusion and speeds debugging.

## Deployment and Client Integration Notes

The project is currently optimized for local client connections, especially desktop clients that support MCP server definitions.

For Windows-based Claude Desktop usage, ensure:

- Config JSON is valid and saved without UTF-8 BOM
- Command points to your virtual environment Python executable
- Args points to server.py absolute path
- App is fully restarted after config edits
- New chat is opened after restart

When config is wrong, symptoms can look like unrelated connector behavior. Health prompt in a fresh chat is the quickest truth check.

## Current Constraints and Honest Tradeoffs

No system is perfect, and this one has clear boundaries:

- LinkedIn data extraction can be brittle due upstream platform changes
- X analytics depth depends on account access tier and endpoint permissions
- Contract helper is intentionally conservative for safety and simplicity
- Python ecosystem compatibility can vary by version for native packages

These tradeoffs are acceptable because core value remains high even with partial integrations.

## Expansion Roadmap

Strong next steps for this project:

- Add persistent caching with TTL per integration
- Add request tracing and latency metrics
- Add typed response schemas for every tool
- Add argument-support for contract function calls with ABI-aware conversion
- Add project ranking heuristic for role-targeted summaries
- Add prompt pack for recruiter outreach, grant applications, and investor updates
- Add test suite with mocked provider responses

This roadmap turns the project from useful personal utility into a robust personal AI platform.

## Final Perspective

Aditya Personal MCP Server is a strong foundation for developer-specific AI context. It turns scattered profile data and technical signals into a single local interface that assistants can query in real time. Instead of explaining yourself repeatedly, you expose your data once and let the tools do the work.

The long-term value is compounding. As your repositories grow, contracts evolve, and portfolio changes, the assistant stays aligned because it reads live sources through stable tools. That means better technical conversations, better writing support, better outreach, and better decision support.

This project is already practical today, and it is structured in a way that makes future upgrades straightforward. It is not just another integration script. It is the beginning of a personal context operating layer for AI-native workflows.
