---
id: drustz-42b1d0d0fe286f47f7
section: forum-notes
order: 357
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 5: Advanced Sorting'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 5: Advanced Sorting'
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
