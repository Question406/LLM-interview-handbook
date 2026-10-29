---
id: drustz-872d1c6b52c6b3a72c
section: openai
order: 20
level: A
title: In Memory Database SQL
quick: locally-saved-topic-editorial · In Memory Database SQL
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/in-memory-database-sql
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## In-Memory Database with SQL Operations

## Problem Statement

You need to build a simple in-memory database. Think of it as a simplified version of SQL. You will build this system step-by-step. It needs to handle creating tables, adding data, and finding data. You also need to support filtering (WHERE) and sorting (ORDER BY).

**Key Rules:**

- **Ask questions:** There are several parts to this problem. Ask your interviewer how many parts there are so you can manage your time.
- **Design your own inputs:** Do not write code to parse SQL strings (like "SELECT * FROM..."). That takes too long. Instead, pass arguments directly to your functions.
- **Keep it simple:** Use standard dictionaries or maps. You do not need complex algorithms.
- **Test your code:** Write your own test cases to prove it works.
- **Write clean code:** Make sure your code is easy to read.

## Part 1: Basic Setup

First, create a `Database` class. It needs to do three things:

- **Create a table:** Define the table name and its column names.
- **Insert data:** Add a row of data to a table.
- **Query data:** Get data back from a table. You should be able to pick which columns you want to see (this is called "projection").

### Required Code Structure

```python
class Database:
    def __init__(self):
        """Initialize the database"""
        pass

    def create_table(self, table_name: str, columns: List[str]):
        """Create a new table with specified columns"""
        pass

    def insert(self, table_name: str, row: Dict[str, Any]):
        """Insert a row into the specified table"""
        pass

    def query(self, table_name: str, columns: List[str]) -> List[Dict[str, Any]]:
        """
        Query specific columns from a table (projection).
        Returns all rows but only with the specified columns.
        """
        pass
```



### Example Usage

```python
db = Database()
db.create_table("users", ["id", "name", "birthday"])

db.insert("users", {"id": "1", "name": "Alice", "birthday": "1990-05-15"})
db.insert("users", {"id": "2", "name": "Bob", "birthday": "1985-08-20"})
db.insert("users", {"id": "3", "name": "Charlie", "birthday": "1992-03-10"})

# Get all users, but only show 'id' and 'name'
result = db.query("users", ["id", "name"])
# Result should be:
# [
#   {"id": "1", "name": "Alice"},
#   {"id": "2", "name": "Bob"},
#   {"id": "3", "name": "Charlie"}
# ]
```



### Testing Ideas

- Make two different tables.
- Add many rows to one table.
- Ask for only one column.
- Ask for a column that does not exist (handle the error).

## Part 2: Filtering Data

Now, update the `query` method. You need to filter the results. This is like using a `WHERE` clause in SQL. Start by supporting just one condition.

### Updated Code Structure

```python
def query(
    self,
    table_name: str,
    columns: List[str],
    where: Optional[Callable[[Dict], bool]] = None,
) -> List[Dict[str, Any]]:
    """
    Query with optional WHERE condition.

    Args:
        table_name: Name of the table to query
        columns: List of column names to return
        where: Optional filter function that takes a row dict and returns bool
    """
    pass
```



### Example Usage

```python
# Get users born after 1990-01-01
result = db.query(
    "users", ["name", "birthday"], where=lambda row: row["birthday"] > "1990-01-01"
)
```



### Testing Ideas

- Run a query without a filter (it should still work like Part 1).
- Filter by numbers (e.g., id > 1).
- Filter by strings (e.g., name == "Alice").
- Filter so that no rows match (return empty list).

## Part 3: Advanced Filtering

Now, update the filter to handle more than one rule. For example, finding a user with a specific ID *AND* a specific name.

### Option 1: Using Logic in the Function

You can simply use `and` inside your lambda function.

```python
# Find users with id > 1 AND name starting with 'C'
result = db.query(
    "users",
    ["id", "name"],
    where=lambda row: int(row["id"]) > 1 and row["name"].startswith("C"),
)
```



### Option 2: List of Rules

You can change your design to accept a list of rules.

```python
def query(
    self,
    table_name: str,
    columns: List[str],
    where: Optional[List[Tuple[str, str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Args:
        where: List of conditions [(column, operator, value), ...]
               All conditions are combined with AND
               Operators: "=", ">", "<", ">=", "<=", "!="
    """
    pass


# Query users with id > 1 AND name = "Charlie"
result = db.query(
    "users", ["id", "name"], where=[("id", ">", "1"), ("name", "=", "Charlie")]
)
```



## Part 4: Sorting Data

Add the ability to sort the results. This is like using `ORDER BY`.

### Updated Code Structure

The method signature needs to change to accept sorting instructions.

```python
def query(
    self,
    table_name: str,
    columns: List[str],
    where: Optional[Callable[[Dict], bool]] = None,
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query with optional WHERE and ORDER BY.

    Args:
        order_by: Column name to sort by (ascending order)
    """
    pass
```



### Example Usage

```python
# Sort users by name
result = db.query("users", ["name", "age"], order_by="name")

# Sort users by name AND filter by age
result = db.query(
    "users", ["name", "age"], where=lambda row: int(row["age"]) > 28, order_by="name"
)
```



### Testing Ideas

- Sort by a text column.
- Sort by a number column.
- Sort with and without a filter.

## Part 5: Advanced Sorting

Extend the sorting feature. You need to support sorting by **multiple columns**. You also need to choose the direction (ascending or descending).

### Updated Code Structure

```python
def query(
    self,
    table_name: str,
    columns: List[str],
    where: Optional[Callable[[Dict], bool]] = None,
    order_by: Optional[Tuple[List[str], bool]] = None,
) -> List[Dict[str, Any]]:
    """
    Query with optional WHERE and ORDER BY.

    Args:
        order_by: Tuple of (column_list, is_ascending)
                  Example: (["age", "name"], True) sorts by age then name, both ascending
                  Example: (["age", "name"], False) sorts by age then name, both descending
    """
    pass
```



### Example Usage

```python
# Sort by name descending, then birthday descending
result = db.query(
    "users", ["id", "name", "birthday"], order_by=(["name", "birthday"], False)
)
```



## Part 6: Optimization Discussion

**Note:** You usually discuss this part without writing code.

The interviewer might ask: "How can we make these queries faster?" You should discuss **Indexing**.

### Key Concepts

- **Inverted Index (For exact matches):**

This is like the index at the back of a book.
- Structure: `{column_name: {value: [list_of_row_indices]}}`.
- Example: If you look for "Alice", the index tells you exactly which row she is in.
- Benefit: Improves speed from O(n) to O(1).
- **B-Tree Index (For ranges):**

This keeps data sorted.
- It is great for queries using `>`, `<`, `>=`, or `<=`.
- **Composite Index:**

This is an index that combines two columns (like `age` and `name`) to speed up queries that check both.
- **Trade-offs:**

Indexes make **reading** (querying) faster.
- Indexes make **writing** (inserting) slower because you must update the index every time you add data.

## Helpful Tips

- **Avoid SQL Parsing:** Do not try to read a string like `SELECT * FROM`. Use function arguments instead.
- **Copy Data:** When inserting data, use `.copy()`. If you don't, changing the original dictionary later might mess up your database.
- **Check for None:** Your `where` and `order_by` arguments are optional. Make sure your code handles `None` without crashing.
- **Empty Results:** If no data matches the filter, return an empty list `[]`, not `None`.

## Complete Solution Code

Here is a full working solution. It puts all the parts together.

```python
from typing import List, Dict, Any, Optional, Callable, Tuple


class Database:
    def __init__(self):
        self.tables = {}  # {table_name: [rows]}
        self.schemas = {}  # {table_name: [column_names]}

    def create_table(self, table_name: str, columns: List[str]):
        """Create a new table with specified columns"""
        self.schemas[table_name] = columns
        self.tables[table_name] = []

    def insert(self, table_name: str, row: Dict[str, Any]):
        """Insert a row into the specified table"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")

        # Deep copy to avoid reference issues
        self.tables[table_name].append(row.copy())

    def query(
        self,
        table_name: str,
        columns: List[str],
        where: Optional[Callable[[Dict], bool]] = None,
        order_by: Optional[Tuple[List[str], bool]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query table with optional WHERE and ORDER BY.

        Args:
            table_name: Name of the table to query
            columns: List of column names to return (projection)
            where: Optional filter function that takes a row and returns bool
            order_by: Optional tuple of (column_list, is_ascending)
                      If None, no sorting is applied

        Returns:
            List of row dictionaries containing only the specified columns
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")

        # Start with all rows
        rows = self.tables[table_name]

        # Apply WHERE filter
        if where:
            rows = [row for row in rows if where(row)]

        # Apply ORDER BY
        if order_by:
            sort_columns, is_ascending = order_by
            # Sort by multiple columns using tuple comparison
            rows = sorted(
                rows,
                key=lambda row: tuple(row[col] for col in sort_columns),
                reverse=not is_ascending,
            )

        # Apply column projection
        result = []
        for row in rows:
            projected_row = {col: row[col] for col in columns if col in row}
            result.append(projected_row)

        return result


# Example usage and test cases
if __name__ == "__main__":
    db = Database()

    # Part 1: Basic operations
    db.create_table("users", ["id", "name", "age", "birthday"])

    db.insert(
        "users", {"id": "1", "name": "Alice", "age": "30", "birthday": "1990-05-15"}
    )
    db.insert(
        "users", {"id": "2", "name": "Bob", "age": "25", "birthday": "1985-08-20"}
    )
    db.insert(
        "users", {"id": "3", "name": "Charlie", "age": "35", "birthday": "1992-03-10"}
    )
    db.insert(
        "users", {"id": "4", "name": "Diana", "age": "28", "birthday": "1995-12-25"}
    )

    # Test Part 1: Basic query
    print("Part 1: Query all users (id, name)")
    result = db.query("users", ["id", "name"])
    for row in result:
        print(row)
    print()

    # Test Part 2: WHERE clause - single condition
    print("Part 2: Query users with age > 28")
    result = db.query("users", ["name", "age"], where=lambda row: int(row["age"]) > 28)
    for row in result:
        print(row)
    print()

    # Test Part 3: WHERE clause - multiple conditions (AND)
    print("Part 3: Query users with age > 28 AND name starting with 'A' or 'C'")
    result = db.query(
        "users",
        ["name", "age"],
        where=lambda row: int(row["age"]) > 28 and row["name"][0] in ['A', 'C'],
    )
    for row in result:
        print(row)
    print()

    # Test Part 4: ORDER BY - single column
    print("Part 4: Query all users ordered by name")
    result = db.query("users", ["name", "age"], order_by=(["name"], True))
    for row in result:
        print(row)
    print()

    # Test Part 5: ORDER BY - multiple columns with DESC
    print("Part 5: Query all users ordered by age DESC, then name ASC")
    db.insert(
        "users", {"id": "5", "name": "Alice", "age": "30", "birthday": "1993-01-01"}
    )

    # For mixed ASC/DESC, you might need two separate queries or enhanced logic
    # This example shows all DESC
    result = db.query("users", ["name", "age"], order_by=(["age", "name"], False))
    for row in result:
        print(row)
    print()

    # Test comprehensive example
    print("Comprehensive: WHERE + ORDER BY")
    result = db.query(
        "users",
        ["id", "name"],
        where=lambda row: int(row["age"]) >= 28,
        order_by=(["name"], True),
    )
    for row in result:
        print(row)
```



*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100052*)

---


## 未能解锁的外链帖（请自行打开查看）

- [LLM Inference Timeout and Restart Strategy](https://www.1point3acres.com/interview/thread/7100488)
- [Multi-Tenant CI/CD Workflow System](https://www.1point3acres.com/interview/thread/7100483)
- [Payment Processing System (Stripe-like)](https://www.1point3acres.com/interview/thread/7100485)
- [Implement a CD Command](https://www.1point3acres.com/interview/thread/7100341)

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/in-memory-database-sql)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
