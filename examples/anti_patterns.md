# Database Code Anti-Patterns

This reference contains common code-level database anti-patterns that AI agents must detect, reject, and rewrite.

---

## 1. Anti-Pattern: N+1 Queries in APIs

Executing a query inside a loop to retrieve related entities.

### ❌ The BAD Code
This Python code fetches posts and subsequently queries the database in a loop to get the author of each post.
```python
# FastAPI Route causing N+1 database hits
@app.get("/posts")
async def read_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    
    response = []
    for post in posts:
        # Triggering another query on every iteration
        author_result = await db.execute(select(User).where(User.id == post.author_id))
        author = author_result.scalar_one()
        
        response.append({
            "id": post.id,
            "title": post.title,
            "author": author.username
        })
    return response
```

###  The GOOD Code
Use eager loading via `joinedload` to retrieve both posts and their authors in a single optimized `JOIN` query.
```python
from sqlalchemy.orm import joinedload

@app.get("/posts")
async def read_posts(db: AsyncSession = Depends(get_db)):
    # Eagerly load the 'author' relation in a single database query
    result = await db.execute(
        select(Post).options(joinedload(Post.author))
    )
    posts = result.scalars().all()
    
    return [
        {
            "id": post.id,
            "title": post.title,
            "author": post.author.username
        }
        for post in posts
    ]
```

---

## 2. Anti-Pattern: Procedural SQL Loops (Cursors / WHILE)

Performing row-by-row updates in SQL instead of using set-based operations.

### ❌ The BAD Code
Updating user tiers row-by-row using an SQL Cursor.
```sql
-- Procedural row-by-row update loop
DECLARE user_cursor CURSOR FOR 
SELECT id, points FROM users;

OPEN user_cursor;
FETCH NEXT FROM user_cursor INTO @user_id, @points;

WHILE @@FETCH_STATUS = 0
BEGIN
    IF @points > 1000
        UPDATE users SET tier = 'Gold' WHERE id = @user_id;
    ELSE
        UPDATE users SET tier = 'Silver' WHERE id = @user_id;
        
    FETCH NEXT FROM user_cursor INTO @user_id, @points;
END;

CLOSE user_cursor;
DEALLOCATE user_cursor;
```

###  The GOOD Code
Apply a single declarative set-based `UPDATE` statement with a `CASE` expression.
```sql
-- Executed as a single set-based transaction
UPDATE users 
SET tier = CASE 
    WHEN points > 1000 THEN 'Gold'
    ELSE 'Silver'
END
WHERE tier IS DISTINCT FROM (
    CASE WHEN points > 1000 THEN 'Gold' ELSE 'Silver' END
);
```

---

## 3. Anti-Pattern: Missing Audit Fields and Indexes on Foreign Keys

Tables declared without timestamps or indexes on reference columns.

### ❌ The BAD Code
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    total_amount DECIMAL(10,2) NOT NULL
);
-- Anti-Pattern:
-- 1. No created_at or updated_at tracking fields.
-- 2. No index on customer_id, resulting in slow ORDER BY / JOIN operations on customers.
```

###  The GOOD Code
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    total_amount DECIMAL(10,2) NOT NULL,
    
    -- Mandatory audit columns
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Indexing foreign keys is mandatory for relation joins
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```
