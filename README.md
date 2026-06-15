# Agentic DB Architect Skills

A repository of specialized agent skills, prompts, and context rules designed for AI coding assistants (Cursor, Claude, Codex, etc.) to autonomously design, audit, and refactor database architectures via code. 

## 🎯 Vision
The goal of these skills is to enforce strict database engineering best practices. The agents utilizing these skills will not execute commands directly against a live database. Instead, they will act as **Database Architects**, generating, reviewing, and improving DDL scripts, ORM models, and migration files.

## 🧠 Core Engineering Principles (Agent Directives)

When operating under these skills, the AI must strictly adhere to the following principles:

1.  **Set-Based Operations Over Procedural Loops:** * **Rule:** Absolutely avoid `WHILE` loops, cursors, or procedural row-by-row processing in SQL.
    * **Action:** Always refactor logic to use set-based operations (JOINs, Window Functions, CTEs) for data manipulation.

2.  **Strict Relationship Management:**
    * **Rule:** Default to `1-to-N` relationships.
    * **Action:** * Reject `1-to-1` relationships unless explicitly justified (e.g., strict security partitioning or isolating massive BLOB columns).
        * Never implement direct `N-to-N` relationships. Always construct an explicit associative (junction/mapping) table with its own primary key and audit timestamps.

3.  **Code-First Architecture:**
    * **Rule:** All architectural changes must be represented as version-controlled code.
    * **Action:** Produce standardized DDL schemas, constraints (Foreign Keys, UNIQUE, CHECK), and precise rollback scripts.

4.  **Auditing & Consistency:**
    * **Rule:** Every table must be traceable.
    * **Action:** Automatically append standard audit columns (e.g., `created_at`, `updated_at`, `is_active`/`deleted_at` for soft deletes) to all new table definitions.

## 🚀 How to Use

* **Cursor:** Copy the contents of `.cursorrules` into your project root.
* **CLI Agents:** Mount or sync the markdown files located in the `/skills` directory into your agent's global or workspace skill configuration.
