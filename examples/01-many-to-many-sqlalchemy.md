# Example: Explicit Many-to-Many Relationships (SQLAlchemy)

This example demonstrates the required architectural standard for Many-to-Many relationships.

## ❌ BAD (REJECT THIS)

Do NOT use implicit junction tables using the `secondary` parameter without a defined model. It lacks auditability and cannot hold extra metadata.

```python
# Anti-pattern: Implicit N:M relation
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# ❌ BAD: Implicit table, no created_at, no ID
user_workspace_table = Table(
    "user_workspaces", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("workspace_id", Integer, ForeignKey("workspaces.id"))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    workspaces = relationship("Workspace", secondary=user_workspace_table)
```

## ✅ GOOD (ACCEPT THIS)

Always create an explicit, standalone Model for the junction table. This allows for audit columns and extra metadata (e.g., `role`, `joined_at`).

```python
# Correct pattern: Explicit junction table with audit columns
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class UserWorkspaceRole(Base):
    __tablename__ = "user_workspace_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)

    # Metadata fields (Cannot exist in the BAD example)
    role = Column(Enum("admin", "member", "viewer"), nullable=False, default="member")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="workspaces")
    workspace = relationship("Workspace", back_populates="users")

    __table_args__ = (
        # Enforce unique combinations
        UniqueConstraint('user_id', 'workspace_id', name='uq_user_workspace_id'),
    )

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # Updated relationship to point to the JOIN MODEL, not the target table
    workspaces = relationship("UserWorkspaceRole", back_populates="user")

class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True)
    # Updated relationship to point to the JOIN MODEL
    users = relationship("UserWorkspaceRole", back_populates="workspace")
```
