---
id: drustz-f5985bd8e68d965aa1
section: forum-notes
order: 275
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Bonus Question: Async Iteration'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Bonus Question: Async Iteration'
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
## Bonus Question: Async Iteration

Interviewers might ask about using this with files or network streams (Async).

### Main Ideas

- Use `async def __anext__()` instead of `__next__()`.
- Use `async for` loops.
- For state, save the progress (like file byte offset), not the file object itself.

### Example Interface

```python
class AsyncResumableIterator(ABC):
    @abstractmethod
    async def __anext__(self):
        """Async version of __next__"""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """State handles positions, not open files"""
        pass

    @abstractmethod
    async def set_state(self, state: Dict[str, Any]) -> None:
        """Async needed if you have to re-open files"""
        pass


# Usage
async for item in async_iterator:
    if some_condition:
        state = async_iterator.get_state()
        # Save state to database or file
        break

# Later, restore
await async_iterator.set_state(saved_state)
async for item in async_iterator:
    # Continues from saved position
    process(item)
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
