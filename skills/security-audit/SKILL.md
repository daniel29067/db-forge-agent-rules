---
name: security-audit
description: Enforcing audit columns, soft delete support, and protection against SQL injection.
---

# Security & Audit Skill

This skill outlines guidelines to ensure data traceability, structural security, and protection against injection vulnerabilities at the schema and query levels.

## Audit and Traceability Directives

### 1. Mandatory Audit Columns
To ensure historical tracking and audit compliance, every user-defined table (and associative table) must contain:
- `created_at`: The exact time a row was created. Set at insertion via database defaults (`CURRENT_TIMESTAMP`, `NOW()`).
- `updated_at`: The exact time a row was last modified. Configured to update automatically via database triggers or ORM session hooks.
- `is_active` / `deleted_at`: System indicators for soft-deleting records. Avoid physical deletion (`DELETE`) by default to protect historical relations.

### 2. Traceability in Multi-Tenant / Enterprise Environments
For environments requiring individual user accountability, append:
- `created_by`: Foreign key (or simple string identifier) referencing the system user or service ID that created the record.
- `updated_by`: Foreign key (or simple string identifier) referencing the user or service ID that last modified the record.

### 3. Preventing SQL Injection
- **Parameterized Queries**: Never concatenate inputs directly into raw SQL queries (`f"SELECT * FROM users WHERE name = '{input}'"`).
- **ORM Escaping**: Rely on the default escaping behaviors of ORMs (SQLAlchemy parameters, Prisma binding) to pass variables as parameters.
- **Dynamic Identifiers**: If table names or column names must be dynamically injected (e.g., custom filters), validate them against a strict whitelist of schema identifiers before execution.

### 4. Soft Delete Constraints
- **Uniqueness under Soft Deletes**: When creating unique indexes on tables supporting soft deletes, include the deleted flag or timestamp in the index to prevent collisions on deactivated records:
  - *Example (PostgreSQL)*: `CREATE UNIQUE INDEX idx_user_email_active ON users (email) WHERE deleted_at IS NULL;`
- **Global Query Filters**: When fetching records, always filter out soft-deleted rows by default (e.g., append `WHERE is_active = TRUE` or `WHERE deleted_at IS NULL`) unless building an admin-specific interface.
