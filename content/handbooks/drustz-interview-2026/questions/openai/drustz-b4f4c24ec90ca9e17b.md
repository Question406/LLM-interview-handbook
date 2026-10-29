---
id: drustz-b4f4c24ec90ca9e17b
section: openai
order: 6
level: A
title: Toy Language Type Inference
quick: locally-saved-topic-editorial · Toy Language Type Inference
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
      https://www.1point3acres.com/interview/problems/company/openai/toy-language-type-inference
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Toy Language Type System

## Problem Description

You need to build a type system for a simple programming language. This language has four main features:

- **Primitives**: Basic types like `int`, `float`, and `str`.
- **Generics**: Placeholders usually written as uppercase letters (e.g., `T`, `T1`, `S`).
- **Tuples**: Lists of types inside brackets. These can hold primitives, generics, or other tuples.

*Examples:* `[int, T1, str]` or `[int, [str, T1]]`.
- **Functions**: These have a list of input parameters and one return type.

*Syntax:* `[input1, input2] -> output`
- *Example:* `[int, T1] -> [str, T1]`
Your goal is to write two classes: `Node` and `Function`.

## Class Requirements

### Node Class

The `Node` class defines a specific type. It can be a single value (like `int`) or a list (a tuple).

**Constructor:**

```text
def __init__(self, node_type: Union[str, List['Node']])
```



- If `node_type` is a string: It is a primitive or generic type.
- If `node_type` is a list: It is a tuple holding other `Node` objects.
**Required Methods:**

- `__str__()`: Returns the text version of the node (explained in Task 1).

### Function Class

The `Function` class defines a function's structure.

**Constructor:**

```text
def __init__(self, parameters: List[Node], output_type: Node)
```



- `parameters`: A list of `Node` objects acting as inputs.
- `output_type`: A single `Node` object acting as the result.
**Required Methods:**

- `__str__()`: Returns the text version of the function (explained in Task 1).

## Task 1: Converting to String

You must write the `__str__()` method for both classes.

### Node Format

- **Primitives/Generics**: Return the name exactly as it is.

*Example:* `int` becomes `"int"`.
- **Tuples**: Return the types separated by commas, inside brackets.

*Example:* `[int, float]` becomes `"[int,float]"`.
- *Nested Example:* `[int, [str, T1]]` becomes `"[int,[str,T1]]"`.

### Function Format

- Format: `(param1,param2) -> returnType`
- *Example:* If inputs are `[int, T1]` and return type is `[T1, str]`, the string is `"(int,T1) -> [T1,str]"`.

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

## Tips for Solution

### Helper Functions

It helps to break the code into smaller pieces:

- **`is_generic_type(node)`**: Returns true if the node is a generic (like `T1`) or contains one.
- **`clone(node)`**: Creates a copy of a node.
- **`bind_generics(func_param, actual_param, binding_map)`**:

Matches the function definition to the real input.
- Saves matches (like `T1` = `int`) into the `binding_map` (a Dictionary/HashMap).
- Raises an error if there is a conflict.
- **`substitute_generics(node, binding_map)`**:

Takes the return type node.
- Replaces every generic placeholder with the real value from the map.

### Step-by-Step Logic

```text
1. Check if the number of inputs matches the function definition.
2. Create an empty dictionary called binding_map.
3. Loop through every pair of (function_param, actual_param):
   a. If function_param is Generic:
      - If it's already in the map, check if it matches the current input.
      - If not in the map, add it.
   b. If function_param is Concrete (e.g., int):
      - Ensure it exactly matches the actual_param.
   c. If function_param is a Tuple:
      - Recursively check every item inside the tuple.
4. Take the return type node and swap all generics using the binding_map.
5. Return the new result node.
```



## Code Solution

Here is a working solution in Python.

```python
from typing import Union, List


class Node:
    def __init__(self, node_type: Union[str, List['Node']]):
        # List of known primitive types
        self.type_list = ['str', 'float', 'int']

        if isinstance(node_type, str):
            self.base = node_type
            self.children = []
        else:
            self.base = None
            self.children = node_type

    def get_content(self) -> Union[str, List['Node']]:
        if self.base:
            return self.base
        return self.children

    # Check if this specific node is a generic (e.g., "T1")
    def is_base_generic_type(self):
        return self.base and self.base not in self.type_list

    # Check if this node OR any children contain generics
    def is_generic_type(self):
        if self.is_base_generic_type():
            return True
        return any([child.is_generic_type() for child in self.children])

    # Deep copy the node
    def clone(self):
        if self.base:
            return Node(self.base)
        return Node([child.clone() for child in self.children])

    # Task 1: String representation
    def __str__(self) -> str:
        if self.base:
            return self.base

        node_types = []
        for child in self.children:
            node_types.append(str(child))

        return f"[{','.join(node_types)}]"

    # Helper for equality checks
    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            return False
        return str(other) == str(self)


class Function:
    def __init__(self, param: List[Node], output: Node):
        self.parameters = param
        self.output_type = output

    # Task 1: String representation for Function
    def __str__(self) -> str:
        param_str = ','.join([str(param) for param in self.parameters])
        output_str = str(self.output_type)
        return f'({param_str}) -> {output_str}'


def binding(func_param: Node, param: Node, binding_map: dict):
    # Case 1: The function parameter is a generic placeholder (e.g., T1)
    if func_param.is_generic_type() and func_param.base:
        # If we already saw this generic, make sure it matches the new input
        if func_param.base in binding_map and binding_map[func_param.base] != param:
            raise Exception(
                f'invocation argument type mismatched on {func_param} and {param}'
            )
        # If it's new, save the mapping
        if func_param.base not in binding_map:
            binding_map[func_param.base] = param

    # Case 2: Both are concrete types (e.g., int == int)
    elif func_param == param:
        return

    # Case 3: Both are tuples, we need to check inside them
    elif not func_param.base and not param.base:
        # First, ensure tuple lengths are the same
        if len(func_param.children) != len(param.children):
            raise Exception(f'tuple length mismatch: {func_param} vs {param}')

        # Recursively bind each item in the tuple
        for sub_func_node, sub_param_node in zip(func_param.children, param.children):
            binding(sub_func_node, sub_param_node, binding_map)
    else:
        raise Exception(f'mismatch parameter on {func_param} and {param}')


def replace_invocation_arguments(node: Node, binding_map: dict) -> Node:
    # If there are no generics here, just return a copy
    if not node.is_generic_type():
        return node.clone()

    # If this is a base node (not a tuple), swap it with the mapped value
    if not node.children:
        cloned = binding_map[node.base].clone()
        return Node(cloned.get_content())

    # If it is a tuple, recursively replace children
    return Node(
        [replace_invocation_arguments(child, binding_map) for child in node.children]
    )


def get_return_type(parameters: List[Node], function: Function) -> Node:
    # Step 1: Validate argument count
    if len(parameters) != len(function.parameters):
        raise Exception("Illegal Arguments")

    binding_map = {}

    # Step 2: Build the binding map
    for func_node, param_node in zip(function.parameters, parameters):
        binding(func_node, param_node, binding_map)

    # Step 3: If return type has no generics, return it as is
    if not function.output_type.is_generic_type():
        return function.output_type

    # Step 4: Substitute generics in the return type
    return replace_invocation_arguments(function.output_type, binding_map)


# Example usage to verify logic
if __name__ == "__main__":
    # Test string representation
    node1 = Node('T')
    node2 = Node('float')
    node3 = Node('T')
    node4 = Node([node1, node2])
    node5 = Node([node4, node3])

    print(node5)  # Output: [[T,float],T]

    func = Function([node5, Node('S')], Node([Node('S'), Node('T')]))

    print(func)  # Output: ([[T,float],T],S) -> [S,T]

    # Test type inference logic
    node11 = Node('str')
    node22 = Node('float')
    node33 = Node('str')
    node44 = Node([node11, node22])
    node55 = Node([node44, node33])

    node = get_return_type([node55, Node([Node('float'), Node('int')])], func)
    print(node)  # Output: [[float,int],str]
```



*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100065*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/toy-language-type-inference)
- [相关来源](https://www.1point3acres.com/bbs/thread-1172199-1-1.html)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
