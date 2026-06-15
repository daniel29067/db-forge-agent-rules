```markdown
# 🏛️ db-forge-agent-rules

**Specialized AI agent skills, prompts, and context rules to autonomously design, audit, and refactor database architectures via code.**

## 🎯 The Vision

Modern AI coding assistants (Cursor, Antigravity, Claude Code, Codex) are powerful, but left to their own devices, they often generate poor database architectures (implicit many-to-many tables, procedural loops, N+1 query problems).

This repository acts as a **Senior Database Architect's Brain**. It forces AI models to prioritize set-based operations, strict indexing, explicit relationships, and robust auditability.

## 📂 Repository Structure

- **`.cursor/rules/`**: Context-aware `.mdc` files that Cursor IDE reads automatically when you touch database models or API routes.
- **`skills/`**: Standalone `SKILL.md` directories designed to be mounted as global or workspace skills for CLI agents (like Antigravity).
- **`examples/`**: "Show, Don't Tell" code snippets demonstrating strict anti-patterns vs. enforced standards for SQL, Prisma, and SQLAlchemy.

## 🚀 How to Use

### 1. In Cursor IDE

Clone this repository or copy the `.cursor/rules` folder directly into your project's root. Cursor will automatically read the `globs` and inject these architectural guidelines anytime you open a file matching `schema.prisma`, `models.py`, or `migrations/*.sql`.

### 2. With CLI Agents (Antigravity)

Map the `/skills` directory to your agent's global skills path.
When prompting the agent to design a database, it will adhere to the constraints defined in `skills/schema-design/SKILL.md` and `skills/query-optimization/SKILL.md`.

### 3. With Claude / ChatGPT

Simply copy/paste the content of the relevant `examples/` file alongside your prompt.
_Example:_ "Generate a new Prisma schema for a Blogging platform. Follow the exact relationship constraints shown in `examples/02-many-to-many-prisma.md`."

## 🧠 Core Directives Enforced

1. **Set-Based Over Procedural**: Absolute ban on SQL `WHILE` loops and cursors.
2. **Explicit Relationships**: Absolute ban on implicit Many-to-Many relationships. Associative tables with audit columns are mandatory.
3. **N+1 Prevention**: Forced eager loading patterns in application code.
4. **Scalable Pagination**: Banning `OFFSET` in favor of Keyset (Cursor) pagination.
```
