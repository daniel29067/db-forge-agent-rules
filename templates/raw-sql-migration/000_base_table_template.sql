-- ==============================================================================
-- FUNCTION: Helper para actualizar timestamp automáticamente
-- Motor: PostgreSQL (Standard)
-- ==============================================================================
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ==============================================================================
-- TEMPLATE: Standard Table Creation with Audit & Performance Enforcement
-- ENGINE: PostgreSQL (Standard)
-- ==============================================================================

-- 1. Table Definition
CREATE TABLE IF NOT EXISTS {{table_name}} (
    -- Primary Key
    id SERIAL PRIMARY KEY, -- Or UUID depending on project architecture

    -- Business Columns
    -- {{inject_columns_here}}

    -- Foreign Keys
    -- {{foreign_key_column}} INT NOT NULL,

    -- Mandatory Audit Columns
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Explicit Constraints
    CONSTRAINT fk_{{table_name}}_{{parent_table}} 
        FOREIGN KEY ({{foreign_key_column}}) 
        REFERENCES {{parent_table}}(id) ON DELETE CASCADE
);

-- 2. Mandatory Indexes for Foreign Keys
CREATE INDEX IF NOT EXISTS idx_{{table_name}}_{{foreign_key_column}} 
ON {{table_name}}({{foreign_key_column}});

-- 3. Trigger for Auto-Updating 'updated_at'
CREATE TRIGGER set_timestamp_{{table_name}}
BEFORE UPDATE ON {{table_name}}
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
