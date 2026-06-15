# Architectural Decision Records (ADRs)

An Architectural Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences.

## Why Use ADRs?
- **Knowledge Sharing**: Explains to future developers (and AI agents) why a certain design path was taken (e.g., "Why did we isolate credit card profiles into a 1:1 table?").
- **Audit Trails**: Keeps a history of architectural changes alongside database migrations.
- **Agent Alignment**: When an AI agent needs to modify a core system behavior, it should review past ADRs to avoid repeating mistakes or violating previous architectural constraints.

## Naming Convention
Save new ADR files in this directory (`docs/adr/`) using the format:
`ADR-[Sequence Number]-[kebab-case-title].md`

For example:
- `ADR-0001-use-explicit-junction-tables.md`
- `ADR-0002-isolate-blob-content-performance.md`

## Template
Use the [TEMPLATE.md](file:///C:/Users/lealt/OneDrive/Escritorio/db-forge-agent-rules/docs/adr/TEMPLATE.md) file in this directory to seed your ADRs.
