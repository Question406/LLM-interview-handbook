---
id: drustz-869b30ad812f0e80cd
section: forum-notes
order: 293
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Faster Solution (Update Immediately)'
quick: >-
  作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Faster Solution (Update
  Immediately)
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
