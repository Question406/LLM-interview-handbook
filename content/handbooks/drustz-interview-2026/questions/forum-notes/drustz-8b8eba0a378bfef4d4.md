---
id: drustz-8b8eba0a378bfef4d4
section: forum-notes
order: 272
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Simple List Iterator'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Simple List Iterator'
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
## Part 2: Simple List Iterator

Now, make a real class that works with a simple list of items.

### What You Need to Do

- Use the base class you made in Part 1.
- Start with a list of items.
- Keep track of the current index (your position in the list).
- Allow pausing and resuming at that exact index.
- Handle edge cases, like empty lists or trying to go past the end.

### Example Implementation

```python
class ResumableListIterator(ResumableIterator):
    def __init__(self, items: list):
        self.items = items
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.items):
            raise StopIteration

        result = self.items[self.index]
        self.index += 1
        return result

    def get_state(self) -> Dict[str, Any]:
        """Return where we are"""
        return {'index': self.index, 'total_items': len(self.items)}

    def set_state(self, state: Dict[str, Any]) -> None:
        """Go back to the saved position"""
        self.index = state['index']
        # Optional: check if the list size matches
        if state.get('total_items') != len(self.items):
            raise ValueError("State was saved for different data")
```



### How to Use It

```python
# Create iterator
iterator = ResumableListIterator(['a', 'b', 'c', 'd', 'e'])

# Loop a little bit
print(next(iterator))  # 'a'
print(next(iterator))  # 'b'

# Save the spot
state = iterator.get_state()
print(state)  # {'index': 2, 'total_items': 5}

# Loop more
print(next(iterator))  # 'c'

# Go back to the saved spot
iterator.set_state(state)
print(next(iterator))  # 'c' again

# Finish the loop
print(next(iterator))  # 'd'
print(next(iterator))  # 'e'
# next(iterator) would now stop
```



### Tricky Situations

- The list is empty when you start.
- Trying to set a state that is bigger than the list size.
- Using a state from a different list.
- Calling `get_state` many times without moving.
- Trying to go back to a state after the list is finished.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
