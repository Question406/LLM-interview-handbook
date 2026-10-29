---
id: drustz-58b7f022b13bf2d87c
section: forum-notes
order: 274
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 4: 3D List Iterator (Harder)'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 4: 3D List Iterator (Harder)'
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
## Part 4: 3D List Iterator (Harder)

Now, extend this to three dimensions. You are iterating through a list of lists of lists.

### What You Need to Do

- Take a 3D list structure.
- Track three numbers: outer, middle, and inner indices.
- Skip empty lists at any level.
- Handle the complex logic of nested empty lists.

### Example Implementation

```python
class Resumable3DIterator(ResumableIterator):
    def __init__(self, items: list[list[list]]):
        self.items = items
        self.outer_index = 0
        self.middle_index = 0
        self.inner_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.outer_index < len(self.items):
            if self.middle_index >= len(self.items[self.outer_index]):
                # Finished middle list, move to next outer
                self.outer_index += 1
                self.middle_index = 0
                self.inner_index = 0
                continue

            current_middle = self.items[self.outer_index][self.middle_index]

            if len(current_middle) == 0:
                # Empty inner list, skip it
                self.middle_index += 1
                self.inner_index = 0
                continue

            if self.inner_index >= len(current_middle):
                # Finished inner list, move to next middle
                self.middle_index += 1
                self.inner_index = 0
                continue

            # Return the item
            result = current_middle[self.inner_index]
            self.inner_index += 1
            return result

        raise StopIteration

    def get_state(self) -> Dict[str, Any]:
        return {
            'outer_index': self.outer_index,
            'middle_index': self.middle_index,
            'inner_index': self.inner_index,
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        self.outer_index = state['outer_index']
        self.middle_index = state['middle_index']
        self.inner_index = state['inner_index']
```



### How to Use It

```python
data = [[[1, 2], [3]], [[], [4, 5, 6]], [[7]]]

iterator = Resumable3DIterator(data)

# Loop and pause
print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3

state = iterator.get_state()

print(next(iterator))  # 4 (skips empty list)

# Restore
iterator.set_state(state)
print(next(iterator))  # 4
print(next(iterator))  # 5
```



### Quick Explanation Tips

If you only have 5 minutes in the interview, explain this:

- We need three indices instead of two.
- We need a nested loop logic to handle the extra level.
- We still need to skip empty lists at every level.
- The state dictionary just adds one more field.

```text
# Pseudocode to explain the idea:
def __next__(self):
    # Loop outer
    while not at_end_of_outer:
        # Loop middle
        while not at_end_of_middle:
            # Check inner
            if inner_list_has_elements:
                return element and move inner_index forward
            else:
                move middle_index forward
        move outer_index forward
    raise StopIteration
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
