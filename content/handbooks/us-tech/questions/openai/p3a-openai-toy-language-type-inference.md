---
id: p3a-openai-toy-language-type-inference
section: openai
order: 610
level: A
title: "OpenAI：玩具语言：泛型、嵌套元组与类型推断"
quick: "把类型看成树，同时递归比较形参和实参的结构，类型变量第一次出现时绑定、之后必须一致，冲突就报错；最后按树结构把返回类型里的变量替换成绑定结果。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · toy-language-type-inference"
    url: https://www.1point3acres.com/interview/problems/company/openai/toy-language-type-inference
    type: secondary
---

## 题目

给一门玩具语言实现类型推断。类型有基本类型、泛型（类型变量）和可以嵌套的元组；给出函数签名（形参类型和返回类型）和调用时的实参类型，检查实参能否匹配形参，并把返回类型里的泛型替换成具体类型。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先把类型看成一棵树：基本类型和类型变量是叶子，元组是内部节点。匹配就是同时递归走形参树和实参树：

- 形参是类型变量：第一次遇到就记下它绑定的具体类型（可以是整棵子树）；之后再遇到，必须和已绑定的类型完全相同，冲突时报错，不能静默覆盖；
- 形参是元组：实参也必须是长度相同的元组，再逐个子节点匹配；
- 形参是基本类型：实参必须是同一个基本类型。

所有参数匹配完，再递归地把返回类型树里的类型变量替换成绑定结果。返回类型里出现了没被任何参数绑定的变量，就报错。

写代码前先把「类型变量」和「类型构造器」（这里只有元组）分清楚，错误信息要说明是哪一处、期望什么、实际是什么。还要确认有没有隐式转换（这份练习没有，`int` 不能匹配 `float`）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- 类型的表示：基本类型是字符串 `"int"`、`"float"`、`"str"`、`"bool"`；类型变量是以 `$` 开头的字符串，如 `"$T"`；元组类型是 Python `tuple`，可以嵌套。
- `infer(params, return_type, actual)`：`params` 是形参类型列表，`actual` 是实参类型列表。检查参数个数和结构，把同名类型变量绑定到同一个具体类型，返回代换后的 `return_type`。
- `actual` 里不能含类型变量。个数不对、结构不匹配、同一变量绑定冲突、返回类型含未绑定变量或未知类型，都抛 `ValueError`。没有隐式的 `int` → `float` 转换。
- 嵌套深度不超过 50，类型树节点总数不超过 1000。

### 输入输出示例

```text
infer(["$T", ("$T", "str")], ("$T", "$T"), ["int", ("int", "str")])     -> ("int", "int")
infer(["$T"], "$T", [("int", "float")])                                 -> ("int", "float")
infer(["$T", ("$T", "str")], "$T", ["int", ("float", "str")])           -> ValueError（$T 先绑 int，再遇到 float）
```

### 解题思路与正确性

`unify` 同时递归两棵树，每个形参节点只按上面三种情况之一处理，所以只要返回没报错，形参树代换后就和实参树完全相同。类型变量第一次出现时记录绑定，之后每次出现都严格比较，所以同名变量一定绑定到同一个类型。

因为实参全是具体类型，绑定的右边不会含类型变量，也就不会出现 `$T` 绑定到包含 `$T` 自身的类型这种无限展开。如果扩展成两边都能有类型变量的统一（比如推断高阶函数），就要加 occurs check。

返回类型按树结构递归替换，不对字符串做文本 replace，所以 `$T` 不会误改 `$TT` 这类前缀相同的变量。

### 完整参考实现（Python 3）

```python
PRIMITIVES = {"int", "float", "str", "bool"}


def is_type_var(type_expr):
    """以 $ 开头的字符串是类型变量，如 "$T"。"""
    return isinstance(type_expr, str) and type_expr.startswith("$")


def is_concrete(type_expr):
    """只由基本类型和 tuple 组成、不含类型变量的类型。"""
    if isinstance(type_expr, tuple):
        return all(is_concrete(item) for item in type_expr)
    return type_expr in PRIMITIVES


def infer(params, return_type, actual):
    """用实参类型 actual 匹配形参 params，绑定类型变量，返回代换后的 return_type。

    类型是基本类型字符串、类型变量字符串或嵌套 tuple。不匹配、泛型冲突、返回类型含未绑定变量都抛 ValueError。
    """
    if len(params) != len(actual):
        raise ValueError(f"expected {len(params)} arguments, got {len(actual)}")
    if not all(is_concrete(item) for item in actual):
        raise ValueError("actual argument types must be concrete")

    bindings = {}

    def unify(pattern, value):
        if is_type_var(pattern):
            if pattern in bindings and bindings[pattern] != value:
                raise ValueError(f"{pattern} bound to {bindings[pattern]!r}, conflicts with {value!r}")
            bindings[pattern] = value
            return
        if isinstance(pattern, tuple):
            if not isinstance(value, tuple) or len(pattern) != len(value):
                raise ValueError(f"type mismatch: expected {pattern!r}, got {value!r}")
            for sub_pattern, sub_value in zip(pattern, value):
                unify(sub_pattern, sub_value)
            return
        if pattern not in PRIMITIVES or pattern != value:
            raise ValueError(f"type mismatch: expected {pattern!r}, got {value!r}")

    def substitute(type_expr):
        if isinstance(type_expr, tuple):
            return tuple(substitute(item) for item in type_expr)
        if is_type_var(type_expr):
            if type_expr not in bindings:
                raise ValueError(f"unbound type variable in return type: {type_expr}")
            return bindings[type_expr]
        if type_expr not in PRIMITIVES:
            raise ValueError(f"unknown type: {type_expr!r}")
        return type_expr

    for param, argument in zip(params, actual):
        unify(param, argument)
    return substitute(return_type)
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 同一个 $T 在两处出现，绑定一致，返回类型里两处都替换
params = ["$T", ("$T", "str")]
assert infer(params, ("$T", "$T"), ["int", ("int", "str")]) == ("int", "int")

# 类型变量可以绑定到整个 tuple
assert infer(["$T"], "$T", [("int", "float")]) == ("int", "float")

# $T 先绑 int 再遇到 float：冲突；没有隐式 int -> float 转换
expect_value_error(infer, ["$T", "$T"], "$T", ["int", "float"])
expect_value_error(infer, params, "$T", ["int", ("float", "str")])

# 返回类型里的 $X 没有被任何参数绑定
expect_value_error(infer, [], "$X", [])

# 结构不匹配、参数个数不对、实参含类型变量
expect_value_error(infer, [("int", "str")], "int", [("int",)])
expect_value_error(infer, ["int"], "int", [])
expect_value_error(infer, ["$T"], "$T", ["$U"])
```

### 复杂度与追问

设形参、实参和返回类型的树节点总数为 n，绑定的类型最大为 s 个节点。每个节点访问一次，类型变量重复出现时要比较整棵绑定子树，所以时间是 O(n·s)，最坏情况是同一个大泛型结构反复出现；空间是 O(绑定类型总大小 + 递归深度)。

- 绑定比较太慢：把类型做 hash-consing（结构相同的子树共享同一个对象），比较就变成 O(1) 的身份比较。
- 支持函数类型和多态：函数类型也是一种构造器，按参数和返回值递归统一；两边都可能有变量时改用 union-find 维护等价类，并加 occurs check。
- 子类型和重载：匹配不再是相等，而是「实参是形参的子类型」，重载还要定义多个候选都能匹配时选哪一个。这些都超出了这份练习的范围。
