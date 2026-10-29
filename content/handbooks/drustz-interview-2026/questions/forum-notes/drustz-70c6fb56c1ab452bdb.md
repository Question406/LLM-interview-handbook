---
id: drustz-70c6fb56c1ab452bdb
section: forum-notes
order: 273
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 3: 2D List Iterator (Matrix)'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 3: 2D List Iterator (Matrix)'
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
## Part 3: 2D List Iterator (Matrix)

Now, build an iterator for a "list of lists" (2D). You will need to track your position across two levels.

### What You Need to Do

- Take a 2D list (a list that contains other lists) as input.
- Go through every item, row by row.
- Track the "outer index" (which row) and "inner index" (position in that row).
- Handle edge cases:

Empty outer list.
- Empty inner lists (skip these).
- Rows that are different lengths.

### Common Problems

The hardest parts are usually:

- Skipping empty inner lists.
- Moving correctly from the end of one list to the start of the next.
- Knowing when the whole thing is done.
- Restoring state correctly when you are between lists.

### Example Implementation

```python
class Resumable2DIterator(ResumableIterator):
    def __init__(self, items: list[list]):
        self.items = items
        self.outer_index = 0
        self.inner_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        # We might need to skip empty lists
        while self.outer_index < len(self.items):
            current_list = self.items[self.outer_index]

            # If this list is empty, go to the next one
            if len(current_list) == 0:
                self.outer_index += 1
                self.inner_index = 0
                continue

            # If we finished this list, go to the next one
            if self.inner_index >= len(current_list):
                self.outer_index += 1
                self.inner_index = 0
                continue

            # Return the item and move forward
            result = current_list[self.inner_index]
            self.inner_index += 1
            return result

        # Everything is finished
        raise StopIteration

    def get_state(self) -> Dict[str, Any]:
        return {'outer_index': self.outer_index, 'inner_index': self.inner_index}

    def set_state(self, state: Dict[str, Any]) -> None:
        self.outer_index = state['outer_index']
        self.inner_index = state['inner_index']
```



### Alternative Way (Recursive)

```python
def __next__(self):
    """Using recursion to find the next item"""
    if self.outer_index >= len(self.items):
        raise StopIteration

    current_list = self.items[self.outer_index]

    # If list is done or empty, move to next
    if self.inner_index >= len(current_list):
        self.outer_index += 1
        self.inner_index = 0
        return self.__next__()  # Try the next list

    # Return item
    result = current_list[self.inner_index]
    self.inner_index += 1
    return result
```



### How to Use It

```python
data = [
    [1, 2, 3],
    [],  # Empty list
    [4, 5],
    [6],
]

iterator = Resumable2DIterator(data)

# Loop a little
print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3

# Save state (we finished the first list)
state = iterator.get_state()

# Continue
print(next(iterator))  # 4 (it skips the empty list)
print(next(iterator))  # 5

# Restore state
iterator.set_state(state)
print(next(iterator))  # 4 (resumes correctly)
print(next(iterator))  # 5
print(next(iterator))  # 6
# next(iterator) stops here
```



### Critical Corner Cases

```python
# Test 1: All inner lists are empty
data = [[], [], []]
iterator = Resumable2DIterator(data)
# Should stop immediately

# Test 2: Empty at start and end
data = [[], [1, 2], []]
iterator = Resumable2DIterator(data)
assert list(iterator) == [1, 2]

# Test 3: Saving state exactly between lists
data = [[1], [2], [3]]
iterator = Resumable2DIterator(data)
next(iterator)  # 1
state = iterator.get_state()  # outer=0, inner=1 (finished first list)
next(iterator)  # 2
iterator.set_state(state)
assert next(iterator) == 2  # Should work

# Test 4: Weird lengths
data = [[1], [2, 3, 4, 5], [6, 7]]
iterator = Resumable2DIterator(data)
state_after_3 = None
for i, val in enumerate(iterator):
    if i == 2:  # We just got '3'
        state_after_3 = iterator.get_state()

iterator.set_state(state_after_3)
assert next(iterator) == 4
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
