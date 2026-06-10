# Project-agnostic library

This is a general-purpose library. It must carry **no knowledge of any
consuming application or deployment** — not in code, comments, docstrings,
tests, READMEs, or any other file in this repository.

- Never reference a consumer's services, repositories, or infrastructure by
  name (service names, message buses, databases, orchestrators, parent/umbrella
  repositories).
- Describe consumers generically: "a consuming service", "a message bus",
  "a durable backend (SQLite, Postgres, an object store, …)".
- State design rationale in terms of this library's own contracts and
  invariants, never in terms of how a particular deployment uses it.
- Tests likewise: name scenarios by the contract they pin ("a forwarding
  process", "the receiver"), not by the consumer that hit the bug.
