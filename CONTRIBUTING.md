# Contributing / Development notes

This repository is primarily a portfolio MVP, but changes should remain small, testable and explainable.

## Development principles

- Never commit API keys or customer data.
- Keep retrieval and orchestration concerns separated.
- Prefer explicit graph nodes over hidden side effects.
- Add tests when behaviour changes.
- Document architectural trade-offs in the README.
- Use synthetic support documentation for demonstrations.

## Suggested next contribution

Add an evidence-grading node after retrieval. If the retrieved context is not relevant enough, route to a human-escalation node instead of invoking the answer generator.
