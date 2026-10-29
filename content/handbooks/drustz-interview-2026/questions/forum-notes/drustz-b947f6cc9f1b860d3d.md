---
id: drustz-b947f6cc9f1b860d3d
section: forum-notes
order: 354
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Filtering Data'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Filtering Data'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
