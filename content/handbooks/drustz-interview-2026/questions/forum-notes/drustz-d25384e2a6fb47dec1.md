---
id: drustz-d25384e2a6fb47dec1
section: forum-notes
order: 271
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Defining the Rules'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Defining the Rules'
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
