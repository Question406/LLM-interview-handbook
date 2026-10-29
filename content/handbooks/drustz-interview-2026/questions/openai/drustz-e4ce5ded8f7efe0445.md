---
id: drustz-e4ce5ded8f7efe0445
section: openai
order: 24
level: A
title: Resumable Iterator
quick: locally-saved-topic-editorial · Resumable Iterator
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
      https://www.1point3acres.com/interview/problems/company/openai/resumable-iterator
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Resumable Iterator with Multi-Dimensional Support

## Problem Overview

You need to build a system that can pause and restart a loop (iteration). You must be able to save your current spot and come back to it later. The problem starts easy and gets harder in four steps: defining the rules, making a simple list iterator, making a 2D iterator (matrix), and finally a 3D iterator. The main goal is to save the "state" (your position) so you can resume exactly where you left off.

## Part 1: Defining the Rules

First, define a base class. This sets the rules for how your iterator works.

### What You Need to Do

- Create an abstract class called `ResumableIterator`.
- It must have these standard Python methods:

`__iter__()` and `__next__()` to make it work like a loop.
- `get_state()` to save where you are right now.
- `set_state(state)` to go back to a saved spot.
- The "state" must be simple (like a dictionary or JSON) so it is easy to save.
- Write tests to make sure the rules work.

### Sample Code

```python
from abc import ABC, abstractmethod
from typing import Any, Dict


class ResumableIterator(ABC):
    """Base class for iterators that can pause and resume"""

    @abstractmethod
    def __iter__(self):
        """Return the iterator object"""
        return self

    @abstractmethod
    def __next__(self):
        """Return the next item or stop if finished"""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Save the current spot.
        Returns a dictionary representing the current position.
        """
        pass

    @abstractmethod
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        Go back to a saved spot.
        Args:
            state: The dictionary you got from get_state()
        """
        pass
```



### Example Test Code

```python
import unittest


class TestResumableIterator(unittest.TestCase):
    def test_basic_iteration(self):
        """Test that it can loop through all items"""
        # Specific implementation details go here
        pass

    def test_get_state_returns_serializable(self):
        """Test that get_state returns a standard dictionary"""
        iterator = SomeResumableIterator([1, 2, 3])
        state = iterator.get_state()
        self.assertIsInstance(state, dict)
        # Check if it can be turned into JSON
        import json

        json.dumps(state)  # Should work fine

    def test_set_state_restores_position(self):
        """Test that set_state goes back to the right spot"""
        iterator = SomeResumableIterator([1, 2, 3])
        next(iterator)  # Move to 1
        state = iterator.get_state()
        next(iterator)  # Move to 2
        iterator.set_state(state)  # Go back to 1
        self.assertEqual(next(iterator), 2)  # Should get item at index 1

    def test_pause_and_resume(self):
        """Test a full pause and resume cycle"""
        iterator = SomeResumableIterator([10, 20, 30, 40])
        self.assertEqual(next(iterator), 10)
        self.assertEqual(next(iterator), 20)

        # Pause here
        state = iterator.get_state()

        # Start a new iterator and resume
        new_iterator = SomeResumableIterator([10, 20, 30, 40])
        new_iterator.set_state(state)

        # It should continue from 30
        self.assertEqual(next(new_iterator), 30)
        self.assertEqual(next(new_iterator), 40)
```



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



## Common Mistakes

- **Not skipping empty lists**: If you don't handle `[]`, your code will break.
- **Off-by-one errors**: Adding +1 to the index at the wrong time.
- **Complex State**: Saving whole objects instead of simple numbers/indexes.
- **Bad Data**: Not checking if the saved state matches the current data.
- **Boundaries**: Messing up the logic when moving from one list to another.
- **Infinite Recursion**: If you use recursion and all remaining lists are empty, make sure it stops.
- **Resetting**: Forgetting to set the inner index back to 0 when you move to a new row.

## Tips for the Interview

- **Part 1**: Design a clean class. This makes everything else easier.
- **Part 2**: Make sure the simple list works perfectly. It is the base for the hard parts.
- **Part 3**: This is where people get stuck.

Draw the state changes on paper.
- Test with empty lists explicitly.
- Walk through your logic step by step.
- **Part 4**: If you run out of time, explain the logic clearly:

"I need three indices."
- "The while loop needs to handle one more level."
- "The state dictionary gets one extra number."

## How to Test

```python
def test_comprehensive_2d():
    """Test all edge cases for 2D iterator"""
    test_cases = [
        # (input, expected_output)
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([[], [1], []], [1]),
        ([[], [], []], []),
        ([[1]], [1]),
        ([[1, 2, 3]], [1, 2, 3]),
        ([[1], [2], [3]], [1, 2, 3]),
    ]

    for input_data, expected in test_cases:
        iterator = Resumable2DIterator(input_data)
        result = list(iterator)
        assert result == expected, f"Failed for {input_data}"

    # Test pause/resume
    iterator = Resumable2DIterator([[1, 2], [3, 4]])
    next(iterator)
    next(iterator)
    state = iterator.get_state()
    next(iterator)
    iterator.set_state(state)
    assert next(iterator) == 3
```



## Speed and Memory Use

**Time Complexity**:

- `__next__()`: O(1) on average. Sometimes it has to skip empty lists, but it only checks each list once.
- Total time for N items: O(N).
- `get_state()`: O(1).
- `set_state()`: O(1).
**Space Complexity**:

- O(1) - We only store index numbers. We do not copy the data.
- State dictionary: O(1) - Just a few numbers, no matter how big the data is.

## Where This is Used

This pattern is very useful for:

- **ETL Pipelines**: Processing huge amounts of data. If it stops, you don't want to start over.
- **Distributed Processing**: One computer can pause, and another can pick up the work.
- **Long Jobs**: If a program crashes, it can restart from the save point.
- **Rate-Limited APIs**: If you hit a limit, pause and resume later.
- **Streaming Data**: Buffering and resuming streams if the internet cuts out.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100058*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/resumable-iterator)
- [相关来源](https://www.1point3acres.com/bbs/thread-1180787-1-1.html)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
