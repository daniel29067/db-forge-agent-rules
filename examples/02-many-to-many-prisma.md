# Example: Explicit Many-to-Many Relationships (Prisma / TypeScript)

This example demonstrates the required architectural standard for Many-to-Many relationships using Prisma schema.

## ❌ BAD (REJECT THIS)

Do NOT use Prisma's implicit many-to-many relations. They hide the junction table, prevent adding metadata (like roles or timestamps), and complicate database migrations.

```prisma
// Anti-pattern: Implicit N:M relation
model User {
  id         Int         @id @default(autoincrement())
  email      String      @unique
  // ❌ BAD: Implicit relation
  workspaces Workspace[]
}

model Workspace {
  id    Int    @id @default(autoincrement())
  name  String
  // ❌ BAD: Implicit relation
  users User[]
}

```

## ✅ GOOD (ACCEPT THIS)

Always create an explicit, standalone Model for the junction table. This allows for audit columns and extra metadata (e.g., `role`, `joinedAt`).

```prisma
// Correct pattern: Explicit junction table with audit columns
model UserWorkspaceRole {
  id         Int            @id @default(autoincrement())
  userId     Int
  workspaceId  Int

  // Metadata fields (Cannot exist in the BAD example)
  role       UserWorkspaceRoleEnum @default(MEMBER)
  joinedAt   DateTime       @default(now())
  isActive   Boolean        @default(true)

  // Relationships
  user       User           @relation(fields: [userId], references: [id], onDelete: Cascade)
  workspace  Workspace      @relation(fields: [workspaceId], references: [id], onDelete: Cascade)

  @@unique([userId, workspaceId]) // Enforces unique combinations
}

model User {
  id         Int         @id @default(autoincrement())
  email      String      @unique
  // Updated relationship to point to the JOIN MODEL, not the target table
  workspaces UserWorkspaceRole[]
}

model Workspace {
  id    Int    @id @default(autoincrement())
  name  String
  // Updated relationship to point to the JOIN MODEL
  users UserWorkspaceRole[]
}

enum UserWorkspaceRoleEnum {
  ADMIN
  MEMBER
  VIEWER
}

```
