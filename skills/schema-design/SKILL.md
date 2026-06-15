---
name: schema-design
description: Guidelines for designing relational database schemas, defining constraints, mapping database relations, and enforcing set-based logic.
---

# Schema Design Skill

This skill guides CLI agents and coding assistants in the design of robust, standard-compliant relational database architectures.

## Core Architectural Directives

### 1. Default to 1-to-N Relationships

- Most business domains map naturally to 1-to-N.
- Always use standard foreign key reference definitions in child tables (e.g. `customer_id` on the `orders` table).
- **Mandatory:** Provide indexes on all foreign key columns to avoid slow joins and lock escalations during updates/deletes.

### 2. Forbidden Implicit Many-to-Many Relationships

- **Rule**: Never declare a direct Many-to-Many relationship. Do not rely on implicit junction tables created under the hood by ORMs (like Prisma or SQLAlchemy).
- **Rationale**: Direct M:N schemas cannot store metadata about the relation (e.g., _who_ linked the records, _when_ were they linked, _is active_) and are difficult to refactor.
- **Enforcement**: Create an explicit associative/junction table containing:
  - An explicit compound primary key or a surrogate `id` with a unique index: `PRIMARY KEY (left_id, right_id)`.
  - Foreign Keys referencing both tables with proper referential integrity rules (e.g., `ON DELETE CASCADE` or `RESTRICT` depending on business logic).

### 3. Restrict 1-to-1 Relationships

- **Rule**: Avoid `1-to-1` relationships. Merge columns into a single table by default.
- **Allowed Exceptions**:
  - **Security**: Sensitive data isolated to a restricted access table (e.g. `users` and `user_credentials`).
  - **Performance**: Isolating massive BLOB / CLOB columns to prevent buffer pool pollution during regular queries.
  - **Polymorphism**: Base/derived type modeling.

### 4. Set-Based Operations Over Procedural Loops

- **Rule:** Never generate SQL or procedural logic that relies on `WHILE` loops, cursors, or row-by-row processing.
- **Enforcement:** Always refactor logic to use set-based operations (`JOIN`s, Common Table Expressions (CTEs), Window Functions) for data manipulation and aggregations.

### 5. Mandatory Audit Trail & Constraints

- **Audit Columns:** Every table MUST include tracking columns: `created_at` (Timestamp) and `updated_at` (Timestamp). Consider `is_active` (Boolean) or `deleted_at` for soft deletes where historical data retention is critical.
- **Nullable vs Non-Nullable**: Explicitly define every column as `NULL` or `NOT NULL`. Do not rely on database defaults.
- **Foreign Keys**: Declare all referential constraints at the database level. Do not manage references solely in application logic.

### 6. Naming Standards

- **Tables**: Plural nouns in `snake_case` (e.g., `payments`, `invoices`).
- **Columns**: Singular nouns in `snake_case` (e.g., `amount`, `invoice_id`).
- **Junction tables**: Alphabetical combinations of the tables they connect, joined by an underscore (e.g., `articles_tags`, `users_workspaces`).
- **ORM Mapping:** When generating application code (Python, TypeScript), map these `snake_case` database names to the language's standard conventions (e.g., `camelCase` for properties in TS, `PascalCase` for Model Classes) explicitly.
