---
id: drustz-ff66c5fe2474d37b1f
section: forum-notes
order: 292
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Simple Solution (Calculate on Demand)'
quick: >-
  作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Simple Solution (Calculate on
  Demand)
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
## Part 1: Simple Solution (Calculate on Demand)

First, we will build a `Spreadsheet` class. In this version, we save the data when the user types it. We only do the math to calculate the result when the user asks for it.

### What We Need to Build

- **Start the System:** A method to create a new spreadsheet.
- **Save Data (`setCell`):**

Inputs: A name (like "A1") and a value.
- The value can be a number ("42") or a formula ("=A1+A2").
- Formulas use basic math: `+`, `-`, `*`, `/`.
- **Get Result (`getCell`):**

Input: A name (like "A3").
- Output: The final number as a float.
- If it is a formula, find the answer by looking up the other cells.
- If there is a loop (A needs B, B needs A), show an error.

### How It Should Work

```python
spreadsheet = Spreadsheet()

# Set simple values
spreadsheet.setCell('A1', '1')
spreadsheet.setCell('A2', '2')

# Set formulas with dependencies
spreadsheet.setCell('A3', '=A1 + A2')  # A3 = 1 + 2 = 3
spreadsheet.setCell('A4', '=A3 + A2')  # A4 = 3 + 2 = 5
spreadsheet.setCell('A5', '=A3 + A4')  # A5 = 3 + 5 = 8

# Get values (triggers recursive evaluation)
print(spreadsheet.getCell('A3'))  # Output: 3.0
print(spreadsheet.getCell('A4'))  # Output: 5.0
print(spreadsheet.getCell('A5'))  # Output: 8.0

# Update a value - dependent cells recompute on next access
spreadsheet.setCell('A1', '10')
print(spreadsheet.getCell('A3'))  # Output: 12.0 (10 + 2)
print(spreadsheet.getCell('A5'))  # Output: 26.0 (12 + 14)

# Non-existent cell
print(spreadsheet.getCell('Z99'))  # Output: 0 or None
```



### First Code Solution

This approach calculates the answer every time you ask for it. This means `getCell()` takes **O(N)** time, where N is the number of connected cells.

```python
import re
from typing import Dict, Set


class Spreadsheet:
    def __init__(self):
        # Store raw cell values/formulas
        self.cell_values: Dict[str, str] = {}

    def setCell(self, key: str, value: str) -> None:
        """
        Store cell value or formula.
        Time: O(1)
        Space: O(1)
        """
        self.cell_values[key] = value

    def getCell(self, key: str) -> float:
        """
        Get computed value, recursively evaluating dependencies.
        Time: O(N) where N = number of dependencies
        Space: O(D) where D = max dependency depth (recursion stack)
        """
        if key not in self.cell_values:
            return 0  # or None

        value = self.cell_values[key]

        # If it's a simple number, return it
        if not value.startswith('='):
            return float(value)

        # It's a formula - evaluate it
        formula = value[1:]  # Remove '=' prefix

        # Find all cell references (e.g., A1, B2, AA10)
        cell_refs = re.findall(r'[A-Z]+\d+', formula)

        # Replace each cell reference with its computed value
        # Use word boundaries to avoid A1 matching in A10
        evaluated_formula = formula
        for ref in cell_refs:
            ref_value = self.getCell(ref)  # Recursive call
            # Replace whole word only using regex
            evaluated_formula = re.sub(
                r'\b' + ref + r'\b', str(ref_value), evaluated_formula
            )

        # Evaluate the arithmetic expression
        try:
            result = eval(evaluated_formula)
            return float(result)
        except Exception as e:
            raise ValueError(f"Error evaluating formula '{value}': {e}")
```



### Problem: Infinite Loops (Cycles)

The code above has a bug. If A1 refers to A2, and A2 refers to A1, the program will crash because it keeps calling itself forever. We need to add "Cycle Detection."

We solve this by keeping a list of cells we are currently visiting. If we see a cell that is already in our list, we know there is a loop.

```python
class Spreadsheet:
    def __init__(self):
        self.cell_values: Dict[str, str] = {}

    def setCell(self, key: str, value: str) -> None:
        self.cell_values[key] = value

    def getCell(self, key: str) -> float:
        """Get cell value with circular dependency detection"""
        visited = set()
        return self._evaluate(key, visited)

    def _evaluate(self, key: str, visited: Set[str]) -> float:
        """
        Recursive evaluation with cycle detection.
        visited: Set of cells currently being evaluated (call stack)
        """
        # Check for circular dependency
        if key in visited:
            raise ValueError(f"Circular dependency detected involving cell {key}")

        if key not in self.cell_values:
            return 0

        value = self.cell_values[key]

        # Simple number
        if not value.startswith('='):
            return float(value)

        # Add to visited set (entering this cell's evaluation)
        visited.add(key)

        try:
            formula = value[1:]
            cell_refs = re.findall(r'[A-Z]+\d+', formula)

            # Recursively evaluate dependencies
            evaluated_formula = formula
            for ref in cell_refs:
                ref_value = self._evaluate(ref, visited)  # Pass visited set
                # Use word boundaries to avoid A1 matching in A10
                evaluated_formula = re.sub(
                    r'\b' + ref + r'\b', str(ref_value), evaluated_formula
                )

            result = eval(evaluated_formula)
            return float(result)
        finally:
            # Remove from visited set (exiting this cell's evaluation)
            visited.remove(key)
```



### Testing for Loops

```python
def test_circular_dependency():
    """Test detection of circular references"""
    spreadsheet = Spreadsheet()

    # A1 -> A2 -> A3 -> A1 (cycle)
    spreadsheet.setCell('A1', '=A2 + 1')
    spreadsheet.setCell('A2', '=A3 + 1')
    spreadsheet.setCell('A3', '=A1 + 1')

    try:
        spreadsheet.getCell('A1')
        assert False, "Should have raised circular dependency error"
    except ValueError as e:
        assert "Circular dependency" in str(e)

    # Self-reference
    spreadsheet.setCell('B1', '=B1 + 1')
    try:
        spreadsheet.getCell('B1')
        assert False, "Should have raised circular dependency error"
    except ValueError as e:
        assert "Circular dependency" in str(e)
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
