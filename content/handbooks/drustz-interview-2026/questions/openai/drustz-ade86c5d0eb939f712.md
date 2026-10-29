---
id: drustz-ade86c5d0eb939f712
section: openai
order: 29
level: A
title: Opensheet Spreadsheet
quick: locally-saved-topic-editorial · Opensheet Spreadsheet
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
      https://www.1point3acres.com/interview/problems/company/openai/opensheet-spreadsheet
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## OpenSheet: Spreadsheet with Cell Dependencies

## The Challenge

You need to build a simple spreadsheet system called `OpenSheet`. This is like a mini version of Excel. It must handle cell names (like `A1`, `B2`), numbers, and math formulas.

The main goals are:

- Store values in cells.
- Calculate formulas that use other cells (like `=A1 + A2`).
- Stop the program if cells depend on each other in a circle (an infinite loop).
This interview question tests if you can work with **graphs**, **recursion**, and performance **optimization**.

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



## Part 2: Faster Solution (Update Immediately)

The interviewer might ask: **"How can we make `getCell()` extremely fast (O(1))?"**

### The Plan

In the previous solution, we did the math every time we asked for a value.
In this solution, we will save the answer immediately when we set the value. This is called **Eager Updates**.

- When a user sets `A1`, we calculate `A1` and save the result.
- We look for any other cells that use `A1` and update them too.
- When the user asks for `getCell('A1')`, we just return the saved number.

### Data Structures We Need

- **cell_values**: Stores the raw input (like `=A1+B2`).
- **computed_values**: Stores the final number (like `10.5`). This is our cache.
- **dependencies**: A map of who I need. (Example: "A3 needs A1 and A2").
- **dependents**: A map of who needs me. (Example: "A1 is needed by A3").

### Optimized Code Solution

```python
import re
from typing import Dict, Set
from collections import defaultdict, deque


class OptimizedSpreadsheet:
    def __init__(self):
        # Raw values/formulas
        self.cell_values: Dict[str, str] = {}

        # Computed numeric values (cache)
        self.computed_values: Dict[str, float] = {}

        # Dependency graph
        self.dependencies: Dict[str, Set[str]] = defaultdict(
            set
        )  # cell -> cells it depends on
        self.dependents: Dict[str, Set[str]] = defaultdict(
            set
        )  # cell -> cells that depend on it

    def setCell(self, key: str, value: str) -> None:
        """
        Set cell and eagerly update all dependent cells.
        Time: O(D) where D = number of cells affected (topological order)
        Space: O(D)
        """
        # Store raw value
        self.cell_values[key] = value

        # Clear old dependencies
        for dep in self.dependencies[key]:
            self.dependents[dep].discard(key)
        self.dependencies[key].clear()

        # Parse new dependencies
        if value.startswith('='):
            formula = value[1:]
            cell_refs = set(re.findall(r'[A-Z]+\d+', formula))

            for ref in cell_refs:
                self.dependencies[key].add(ref)
                self.dependents[ref].add(key)

        # Check for circular dependencies
        if self._has_cycle(key):
            # Rollback if cycle detected
            # Note: This deletes the cell entirely. Alternative: restore previous value
            for dep in self.dependencies[key]:
                self.dependents[dep].discard(key)
            self.dependencies[key].clear()
            if key in self.cell_values:
                del self.cell_values[key]
            if key in self.computed_values:
                del self.computed_values[key]
            raise ValueError(f"Circular dependency detected involving cell {key}")

        # Recompute this cell and all dependents
        self._recompute_affected(key)

    def getCell(self, key: str) -> float:
        """
        Get cached computed value.
        Time: O(1)
        Space: O(1)
        """
        if key in self.computed_values:
            return self.computed_values[key]
        return 0

    def _has_cycle(self, start: str) -> bool:
        """
        Detect if there's a cycle reachable from start cell.
        Uses DFS with recursion stack.
        """
        visited = set()
        rec_stack = set()

        def dfs(cell: str) -> bool:
            if cell in rec_stack:
                return True  # Cycle found
            if cell in visited:
                return False

            visited.add(cell)
            rec_stack.add(cell)

            for dep in self.dependencies.get(cell, []):
                if dfs(dep):
                    return True

            rec_stack.remove(cell)
            return False

        return dfs(start)

    def _recompute_affected(self, start: str) -> None:
        """
        Recompute start cell and all cells that depend on it.
        Uses topological sort (BFS) to ensure dependencies are computed first.
        """
        # Find all affected cells (start + all transitive dependents)
        affected = set()
        queue = deque([start])

        while queue:
            cell = queue.popleft()
            if cell in affected:
                continue
            affected.add(cell)

            for dependent in self.dependents.get(cell, []):
                queue.append(dependent)

        # Topological sort of affected cells
        in_degree = defaultdict(int)
        for cell in affected:
            for dep in self.dependencies[cell]:
                if dep in affected:
                    in_degree[cell] += 1

        # BFS topological order
        queue = deque([cell for cell in affected if in_degree[cell] == 0])

        while queue:
            cell = queue.popleft()

            # Compute this cell's value
            self._compute_single_cell(cell)

            # Decrease in-degree for dependents
            for dependent in self.dependents.get(cell, []):
                if dependent in affected:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

    def _compute_single_cell(self, key: str) -> None:
        """Compute and cache a single cell's value"""
        if key not in self.cell_values:
            self.computed_values[key] = 0
            return

        value = self.cell_values[key]

        # Simple number
        if not value.startswith('='):
            self.computed_values[key] = float(value)
            return

        # Formula - evaluate using cached dependency values
        formula = value[1:]
        cell_refs = re.findall(r'[A-Z]+\d+', formula)

        evaluated_formula = formula
        for ref in cell_refs:
            ref_value = self.computed_values.get(ref, 0)
            # Use word boundaries to avoid A1 matching in A10
            evaluated_formula = re.sub(
                r'\b' + ref + r'\b', str(ref_value), evaluated_formula
            )

        try:
            result = eval(evaluated_formula)
            self.computed_values[key] = float(result)
        except Exception as e:
            self.computed_values[key] = 0
```



### Example Usage

```python
spreadsheet = OptimizedSpreadsheet()

# Set operations trigger cascade recomputation of dependents
spreadsheet.setCell('A1', '1')
spreadsheet.setCell('A2', '2')
spreadsheet.setCell('A3', '=A1 + A2')
spreadsheet.setCell('A4', '=A3 + A2')
spreadsheet.setCell('A5', '=A3 + A4')

# O(1) get operations (just cache lookup)
print(spreadsheet.getCell('A5'))  # 8.0 - instant

# Update triggers cascade recomputation
spreadsheet.setCell('A1', '10')

# Get is still O(1)
print(spreadsheet.getCell('A5'))  # 26.0 - instant
```



## Part 3: Testing and Special Cases

We must check that our code works correctly in different situations.

```python
import pytest


def test_basic_operations():
    """Test basic set and get"""
    s = OptimizedSpreadsheet()

    s.setCell('A1', '5')
    assert s.getCell('A1') == 5.0

    s.setCell('A2', '=A1 + 3')
    assert s.getCell('A2') == 8.0

    s.setCell('A1', '10')
    assert s.getCell('A2') == 13.0


def test_complex_dependencies():
    """Test multi-level dependencies"""
    s = OptimizedSpreadsheet()

    s.setCell('A1', '1')
    s.setCell('A2', '2')
    s.setCell('B1', '=A1 + A2')
    s.setCell('B2', '=B1 * 2')
    s.setCell('C1', '=B1 + B2')

    assert s.getCell('C1') == 9.0  # (1+2) + (1+2)*2 = 3 + 6 = 9

    s.setCell('A1', '5')
    assert s.getCell('C1') == 21.0  # (5+2) + (5+2)*2 = 7 + 14 = 21


def test_circular_dependency_detection():
    """Test various circular dependency patterns"""
    s = OptimizedSpreadsheet()

    # Direct self-reference
    with pytest.raises(ValueError, match="Circular dependency"):
        s.setCell('A1', '=A1 + 1')

    # Two-cell cycle
    s.setCell('A1', '=A2')
    with pytest.raises(ValueError, match="Circular dependency"):
        s.setCell('A2', '=A1')

    # Three-cell cycle
    s.setCell('B1', '=B2')
    s.setCell('B2', '=B3')
    with pytest.raises(ValueError, match="Circular dependency"):
        s.setCell('B3', '=B1')


def test_formula_operations():
    """Test various arithmetic operations"""
    s = OptimizedSpreadsheet()

    s.setCell('A1', '10')
    s.setCell('A2', '3')
    s.setCell('B1', '=A1 + A2')
    s.setCell('B2', '=A1 - A2')
    s.setCell('B3', '=A1 * A2')
    s.setCell('B4', '=A1 / A2')

    assert s.getCell('B1') == 13.0
    assert s.getCell('B2') == 7.0
    assert s.getCell('B3') == 30.0
    assert abs(s.getCell('B4') - 3.333) < 0.01


def test_nonexistent_cells():
    """Test references to undefined cells"""
    s = OptimizedSpreadsheet()

    # Get nonexistent cell
    assert s.getCell('Z99') == 0

    # Formula with nonexistent reference
    s.setCell('A1', '=Z99 + 5')
    assert s.getCell('A1') == 5.0


def test_cell_reference_matching():
    """Test that A1 doesn't incorrectly match in A10"""
    s = OptimizedSpreadsheet()

    s.setCell('A1', '5')
    s.setCell('A10', '100')
    s.setCell('A2', '=A1 + A10')

    # Should be 5 + 100 = 105, not some corrupted value
    assert s.getCell('A2') == 105.0

    # Update A1 and verify A10 is unaffected
    s.setCell('A1', '10')
    assert s.getCell('A2') == 110.0  # 10 + 100
```



## Speed and Memory Usage

### Basic Implementation (Part 1)

- **setCell()**: **O(1)**. It is very fast because we just save the text.
- **getCell()**: **O(N)**. It is slow. We might have to check every cell in the chain.
- **Memory**: **O(K)**, where K is the number of cells.

### Optimized Implementation (Part 2)

- **setCell()**: **O(D)**. Slower than before. We have to update D cells that depend on the changed cell.
- **getCell()**: **O(1)**. Extremely fast. We just read the saved answer.
- **Memory**: **O(K + E)**. We use more memory to store the connections (edges) between cells.

## Follow-Up Questions

If you solve this quickly, the interviewer might ask:

- **Complex Formulas**: How would you support brackets `( )` or functions like `SUM()`?
- **Ranges**: How would you handle `=SUM(A1:A10)`?
- **Errors**: What if you divide by zero?
- **Saving**: How do you save the spreadsheet to a file?
- **Undo/Redo**: How can users go back to a previous state?
- **Multiple Users**: How do you handle two people editing at the same time?

## Common Mistakes

- **Infinite Loops**: Forgetting to check if cells depend on each other in a circle.
- **Regex Errors**: Using simple string replacement is bad. `A1` might accidentally replace part of `A10`. Use word boundaries (`\b`).
- **Forgetting Updates**: In the optimized version, you must remember to update *every* cell that depends on the change, not just the immediate neighbors.
- **Security**: Using python's `eval()` is dangerous in a real app. Users could type malicious code. You should write a proper parser instead.
- **Cleanup**: When a formula changes, remember to remove the old dependency links.

## Similar Interview Questions

- Topological sort (Project dependencies)
- Expression evaluation (Calculator)
- Reactive programming (Event handling)
- Build systems (Makefiles)

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100054*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/opensheet-spreadsheet)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
