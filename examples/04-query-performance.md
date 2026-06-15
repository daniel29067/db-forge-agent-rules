# Example: Query Performance (N+1 Problem & Keyset Pagination)

This example demonstrates how to avoid the N+1 query problem, optimize query sargability, and implement scalable Keyset (Cursor) pagination.

---

## 1. The N+1 Query Problem

The N+1 query problem occurs when an application executes 1 query to fetch parent records plus N queries to fetch child records for each parent. This destroys database performance as the dataset grows.

### Prisma / TypeScript

#### ❌ BAD (REJECT THIS)
Do NOT loop through parent records to query their child relationships individually.
```typescript
// Anti-pattern: N+1 query execution
const users = await prisma.user.findMany();

const usersWithWorkspaces = await Promise.all(
  users.map(async (user) => {
    // ❌ BAD: Executes a database query for EVERY single user row
    const workspaces = await prisma.userWorkspaceRole.findMany({
      where: { userId: user.id },
    });
    return { ...user, workspaces };
  })
);
```

#### ✅ GOOD (ENFORCE THIS)
Always use explicit eager loading (`include` or `select` in Prisma) to fetch all required relations in a single database query.
```typescript
// Correct pattern: Eager loading in one single query
const usersWithWorkspaces = await prisma.user.findMany({
  include: {
    workspaces: true, // Performs a JOIN or batch fetch under the hood
  },
});
```

### SQLAlchemy / Python

#### ❌ BAD (REJECT THIS)
Accessing relationships inside a loop without pre-fetching.
```python
# Anti-pattern: Implicit lazy loading in a loop
from sqlalchemy import select
from models import Post

result = await db.execute(select(Post))
posts = result.scalars().all()

for post in posts:
    # ❌ BAD: Accessing .author triggers a lazy-load SELECT query for each post
    print(post.author.username)
```

#### ✅ GOOD (ENFORCE THIS)
Pre-fetch relations using eager loading strategies like `joinedload` or `selectinload`.
```python
# Correct pattern: Joined eager loading
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models import Post

result = await db.execute(
    select(Post).options(joinedload(Post.author))
)
posts = result.scalars().all()

for post in posts:
    # ✅ GOOD: Relation is already loaded in-memory; no extra query is triggered
    print(post.author.username)
```

---

## 2. Sargability (Avoid Functions in WHERE Clauses)

Do NOT apply database functions or computations directly to indexed columns in `WHERE` clauses. This prevents the query optimizer from executing an index seek, forcing a costly full table scan instead.

#### ❌ BAD (REJECT THIS)
```sql
-- ❌ BAD: EXTRACT function forces the planner to scan the entire table to compute values
SELECT * FROM transactions
WHERE EXTRACT(YEAR FROM transaction_date) = 2026;
```

#### ✅ GOOD (ENFORCE THIS)
```sql
-- ✅ GOOD: Range query aligns perfectly with index boundaries (Sargable query)
SELECT * FROM transactions
WHERE transaction_date >= '2026-01-01' AND transaction_date < '2027-01-01';
```

---

## 3. Keyset Pagination (Cursor-based)

Offset pagination (`OFFSET 100000 LIMIT 20`) performs poorly on large datasets because the database engine must scan and discard all preceding records (100,000 rows) before returning the requested page.

Keyset pagination retrieves pages relative to a sequential index (the cursor), allowing the query planner to seek directly to the next set of rows.

### SQL Comparison

#### ❌ BAD (REJECT THIS)
```sql
-- ❌ BAD: Sequentially scans 100,000 records
SELECT * FROM posts
ORDER BY id ASC
LIMIT 20 OFFSET 100000;
```

#### ✅ GOOD (ENFORCE THIS)
```sql
-- ✅ GOOD: Performs an index lookup directly for id > last_seen_id
SELECT * FROM posts
WHERE id > 100000
ORDER BY id ASC
LIMIT 20;
```

### Prisma / TypeScript Implementation

#### ✅ GOOD (ENFORCE THIS)
```typescript
// Correct pattern: Idiomatic keyset pagination in Prisma
interface KeysetParams {
  limit: number;
  cursorId?: number; // The primary key ID of the last record seen by the client
}

async function getPosts({ limit = 20, cursorId }: KeysetParams) {
  const query: Prisma.PostFindManyArgs = {
    take: limit,
    // 1. Must order by the sequential indexed column (the keyset)
    orderBy: { id: "asc" },
  };

  // 2. Start seeking directly from the last ID
  if (cursorId) {
    query.cursor = { id: cursorId };
    query.skip = 1; // Skip the cursor record itself so it is not duplicated in results
  }

  const posts = await prisma.post.findMany(query);

  // 3. Determine the next cursor to return to the client
  const nextCursorId = posts.length === limit ? posts[posts.length - 1].id : null;

  return {
    posts,
    nextCursorId,
  };
}
```
