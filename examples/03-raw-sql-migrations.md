# Example: Raw SQL DDL and Migrations (PostgreSQL / Standard SQL)

This example demonstrates the required standard for generating raw SQL scripts for database creation and migrations.

## ❌ BAD (REJECT THIS)

Do NOT generate tables without explicit constraints, missing indexes on foreign keys, or lacking audit columns.

```sql
-- Anti-pattern: Missing constraints, no indexes, implicit naming
CREATE TABLE user_workspaces (
    user_id INT,
    workspace_id INT
);

-- Missing explicit Primary Key
-- Missing Foreign Key constraints
-- Missing indexes for JOIN performance
-- Missing created_at / updated_at
```

## ✅ GOOD (ACCEPT THIS)

Always generate tables with explicit primary keys, foreign key constraints, indexes on all foreign keys, audit columns, and proper SQL standards.

```sql
-- Correct pattern: Complete SQL DDL with all constraints and indexes

-- Primary table: Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Primary table: Workspaces
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Junction table: UserWorkspaceRoles (Explicit Many-to-Many)
CREATE TABLE user_workspace_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    workspace_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key constraints with ON DELETE CASCADE
    CONSTRAINT fk_user_workspace_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_workspace_workspace FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id)
        ON DELETE CASCADE,

    -- Unique constraint for user-workspace combinations
    CONSTRAINT uq_user_workspace_id UNIQUE (user_id, workspace_id)
);

-- Indexes for performance
CREATE INDEX idx_user_workspace_user ON user_workspace_roles(user_id);
CREATE INDEX idx_user_workspace_workspace ON user_workspace_roles(workspace_id);
CREATE INDEX idx_user_workspace_role ON user_workspace_roles(role);

-- Trigger for updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at
    BEFORE UPDATE ON workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_workspace_roles_updated_at
    BEFORE UPDATE ON user_workspace_roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```
