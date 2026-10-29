---
id: drustz-aebe591e792659e6ef
section: forum-notes
order: 317
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Code Solution
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Code Solution
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
