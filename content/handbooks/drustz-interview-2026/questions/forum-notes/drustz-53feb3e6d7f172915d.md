---
id: drustz-53feb3e6d7f172915d
section: forum-notes
order: 315
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Task 2: Determining Return Types'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Task 2: Determining Return Types'
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
## Task 2: Determining Return Types

Write a function called `get_return_type(parameters: List[Node], function: Function) -> Node`. This function should:

- Take a list of **actual** inputs and a defined **function**.
- Match the actual inputs to the function's generics (like `T1`).
- Figure out what the return type looks like after filling in the generics.
- Raise an error if the types do not match.

### Input Rules

- The actual input parameters are always **concrete**. They will not contain generics.
- You do not need to do a deep DFS traversal on the input list.

### Error Handling

You must raise an error if:

- **Wrong number of arguments**: The input list length is different from the function definition.
- **Type Mismatch**: A concrete type does not match.

*Example:* The function wants `int` but you gave `str`.
- **Generic Conflict**: A generic placeholder matches two different types.

*Example:* `T1` matches `int` in the first argument, but matches `str` in the second argument.

### Usage Examples

#### Example 1: Basic Logic

**Function Definition:**
Expects inputs `[T1, T2, int, T1]` and returns `[T1, T2]`.

```python
func = Function(
    [Node('T1'), Node('T2'), Node('int'), Node('T1')], Node([Node('T1'), Node('T2')])
)
```



**Actual Inputs:**
`[int, str, int, int]`

**Result:**
`[int, str]`

**Logic:**

- `T1` matches `int` (seen in the 1st and 4th spot).
- `T2` matches `str` (seen in the 2nd spot).
- The return type `[T1, T2]` becomes `[int, str]`.

#### Example 2: Type Mismatch

**Function Definition:** Same as above.
**Actual Inputs:** `[int, str, float, int]`

**Result:** Error.

**Logic:**

- The 3rd argument expects `int` (concrete), but received `float`. This is invalid.

#### Example 3: Generic Conflict

**Function Definition:** Same as above.
**Actual Inputs:** `[int, str, int, str]`

**Result:** Error.

**Logic:**

- Argument 1 says `T1` is `int`.
- Argument 4 says `T1` is `str`.
- `T1` cannot be both. This is a conflict.

#### Example 4: Nested Tuples

**Function Definition:**
Expects `[[T1, float], T1]` and returns `[T1, [T1, float]]`.

**Actual Inputs:**
`[[str, float], str]`

**Result:**
`[str, [str, float]]`

**Logic:**

- `T1` matches `str` in both arguments.
- The return type replaces all `T1`s with `str`.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
