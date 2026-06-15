# ADR-XXXX: [Short Title of the Decision]

* **Status**: [Proposed | Accepted | Rejected | Superceded by ADR-YYYY]
* **Date**: [YYYY-MM-DD]
* **Author**: [Your Name/Agent ID]

## Context
Provide brief background context regarding the technical challenge, design trade-offs, or requirements. 
*Why are we looking at this decision now? What are the limitations of the current design?*

## Decision
Describe the chosen design path, architectural change, or schema update. Be specific and include:
* Concrete SQL, schema definitions, or routing rules if applicable.
* The exact components or files modified.
* Rejection of alternative approaches and why.

## Consequences
List the outcomes, benefits, and negative implications of this decision.
* **Positive (Pros)**: E.g., improved read efficiency, strict relational integrity, clear data isolation.
* **Negative (Cons)**: E.g., added table-joining overhead, complex write transaction limits.
* **Follow-up work**: Do we need to run a migration script? Update existing application tests?
