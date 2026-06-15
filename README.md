# 🏛️ db-forge-agent-rules

**Specialized AI agent skills, prompts, and context rules to autonomously design, audit, and refactor database architectures via code.**

## 🎯 The Vision

Modern AI coding assistants (Cursor, Antigravity, Claude Code, Codex) are powerful, but left to their own devices, they often generate poor database architectures (implicit many-to-many tables, procedural loops, N+1 query problems).

This repository acts as a **Senior Database Architect's Brain**. It forces AI models to prioritize set-based operations, strict indexing, explicit relationships, and robust auditability.

## 📂 Repository Structure

- **`.cursor/rules/`**: Context-aware `.mdc` files that Cursor IDE reads automatically when you touch database models or API routes.
- **`skills/`**: Standalone `SKILL.md` directories designed to be mounted as global or workspace skills for CLI agents.
- **`examples/`**: "Show, Don't Tell" code snippets demonstrating strict anti-patterns vs. enforced standards for SQL, Prisma, and SQLAlchemy.
- **`templates/`**: Boilerplate configurations that enforce strict audit columns (`created_at`, `updated_at`) and relationships from line one.

---

## 🚀 How to Use (Tool-Specific Setup)

### 1. 🖱️ Cursor IDE
Cursor natively supports `.mdc` (Markdown with context) rules based on file globs.
* **Per Project:** Copy the `.cursor/rules/` folder from this repository directly into the root of your target project. Cursor will silently enforce these rules in the background when you edit database files.
* **Global Rules:** You can copy the contents of the `.mdc` files directly into your global settings via `Cursor Settings > General > Rules for AI`.

### 2. 🌌 Antigravity & CLI Agents
CLI agents look for `SKILL.md` files structured in directories to understand their capabilities.
* **Workspace Setup:** Copy the `skills/` folder into your current project workspace.
* **Global Setup (Windows):** You can create a directory junction to link this repo directly to your agent's global skills folder so you only have to update it in one place. Open your terminal as Administrator and run:
  `mklink /J "C:\Path\To\Antigravity\global_skills\db-forge" "C:\Users\YOUR_USER\Documents\db-forge-agent-rules\skills"`

### 3. 🧠 Claude (Projects & Claude Code)
Claude excels at reading documentation when explicitly provided.
* **Claude Web (Projects):** Create a new Project. Upload the `SKILL.md` files and the relevant files from the `examples/` directory into the Project's Knowledge Base. Claude will now default to this architecture for all chats in that project.
* **Claude Code (CLI):** When executing the agent in your terminal, explicitly point it to the rules. Example: 
  `claude "Generate a new Prisma schema for a blog. Strictly follow the rules defined in path/to/db-forge-agent-rules/skills/schema-design/SKILL.md"`

### 4. 💬 ChatGPT (Custom GPTs)
* **Create a DB Architect GPT:** Go to "Explore GPTs" -> "Create". In the instructions, define its role as a Strict Database Architect.
* **Upload Knowledge:** Upload the entire `skills/` and `examples/` folders to its Knowledge Base. 
* **Quick Prompting:** Alternatively, just copy the contents of an `example/` file and paste it into a normal chat alongside your prompt: 
  *"Write a SQLAlchemy models file for a store. Follow EXACTLY the architectural constraints shown here: [Paste Example Code]"*

---

## 🧠 Core Directives Enforced

1. **Set-Based Over Procedural**: Absolute ban on SQL `WHILE` loops and cursors.
2. **Explicit Relationships**: Absolute ban on implicit Many-to-Many relationships. Associative tables with audit columns are mandatory.
3. **N+1 Prevention**: Forced eager loading patterns in application code.
4. **Scalable Pagination**: Banning `OFFSET` in favor of Keyset (Cursor) pagination.
