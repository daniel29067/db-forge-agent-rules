---
name: query-optimization
description: Enforcing set-based operations, avoiding loops/cursors, resolving N+1 ORM issues, and optimizing relational database query patterns.
version: 1.0.0
---

# ⚡ Skill: Query Optimization & Performance

This skill ensures CLI agents and coding assistants draft performant SQL and ORM queries by prioritizing set-based logic, avoiding procedural overhead, and eliminating common ORM bottlenecks.

## 1. Directives for Set-Based Operations

### Reject Loops and Cursors

- **No Cursor Processing**: Cursors force the database engine to process data row-by-row, destroying query planner optimizations and locking performance.
- **No Procedural Loop Constructs**: Never use `WHILE` loops in SQL scripts or application-level loops that execute queries on each iteration.
- **Action**: Always refactor row-by-row iterations into a single declarative SQL statement (using `JOIN`s, `UPDATE... FROM...`, `INSERT... SELECT...`, or bulk upserts).

### Leverage Set-Based SQL Features

- **Window Functions**: Use functions like `ROW_NUMBER()`, `RANK()`, `LEAD()`, or `LAG()` inside an `OVER()` clause to perform running totals, rankings, or look-up operations without self-joins.
- **Common Table Expressions (CTEs)**: Break complex queries into readable steps using `WITH cte_name AS (...)` instead of creating temporary tables or looping.

## 2. ORM & Application Data Access

### Prevent The N+1 Query Problem

- **Rule**: Never generate application code that loops over a collection to fetch related records individually.
- **Enforcement**:
  - **Prisma**: Always use `include` or nested `select` to fetch related data in a single query.
  - **SQLAlchemy**: Always use explicit eager loading strategies (`joinedload`, `selectinload`) when accessing related collections.

### Pagination Strategies

- **Rule**: Avoid standard `OFFSET` pagination for large datasets as performance degrades exponentially.
- **Enforcement**: Implement **Keyset Pagination (Cursor-based Pagination)** using an indexed sequential column. (e.g., `WHERE id > :last_seen_id ORDER BY id ASC LIMIT 50`).

## 3. Bulk & Batch Operations

- **Bulk Inserts**: Group multiple `INSERT` records into a single multi-row insert statement (`INSERT INTO table (col) VALUES (val1), (val2), ...`) or use `COPY` commands for large datasets.
- **Bulk Updates**: If updating records based on mappings, use `MERGE` statements or joins to apply the updates in a single query transaction.

## 4. Query Performance Auditing

- **Analyze Execution Plans**: Always request execution plans using `EXPLAIN ANALYZE` (or database equivalent) when analyzing slow queries.
- **Avoid SELECT \***: Request only the columns necessary for the application payload to minimize network transit, reduce memory usage, and allow index-only scans.
- **Index Alignment (Sargability)**: Ensure joins are supported by indexing. Avoid executing functions directly on indexed columns in the `WHERE` clause.
  - ❌ **BAD**: `YEAR(date_column) = 2026` (Causes a full table scan).
  - ✅ **GOOD**: `date_column >= '2026-01-01' AND date_column < '2027-01-01'` (Allows index seek).
