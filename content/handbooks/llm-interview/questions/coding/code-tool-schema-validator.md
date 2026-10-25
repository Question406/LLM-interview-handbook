---
id: code-tool-schema-validator
section: coding
order: 216
level: A
title: 手写 Tool JSON Schema 校验器：type、required、additionalProperties
quick: >-
  在服务端递归校验，模型生成的参数一律当不可信输入。检查 `type` 是否匹配、`required` 里的键有没有缺，`additionalProperties: false` 时拒掉多余字段。Python 里 `bool` 是 `int` 的子类，校验数字前要先排除。契约题见 `agent-schema-contract`。
tags:
  - JSON Schema
  - Tools
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: JSON Schema — object
    url: https://json-schema.org/understanding-json-schema/reference/object
    type: primary
---

## 题目描述

实现一个受限JSON Schema参数检查器，返回所有发现的字段错误，便于工具调用修复参数。候选参数是否符合schema正是本题要判断的业务结果。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `validate(inst,schema,path="$")`。schema保证合法，仅使用type、required、properties、additionalProperties、items；type可为object/array/string/boolean/null/number/integer。inst为JSON数据；additionalProperties可为布尔值或一个子schema。

### 输出与约束

返回由 `(路径,错误字符串)` 组成的列表，无错误返回[]。对象字段路径为`$.name`，数组为`$[i]`。错误用"want 类型"、"required"、"additional"；类型不匹配后不再深入该值，其他字段错误累积返回。Python bool不能当integer/number。只要求这个子集，不需支持完整JSON Schema规范。

### 示例

```text
schema={"type":"object","required":["n"],"properties":{"n":{"type":"integer"}},"additionalProperties":false}
inst={"n":2} -> []
inst={} -> [("$.n","required")]
inst={"n":true} -> [("$.n","want integer")]
```

## 解题思路与参考答案

校验器在服务端递归走一遍 schema：先看 `type` 对不对，再查 `required` 有没有缺键，`additionalProperties: false` 时拒掉多余字段，遇到嵌套对象和数组就往下递归。模型就算按 schema 生成，也会产出合法 JSON 但缺必填、多字段、类型错的参数，这些都要服务端挡住，见 `agent-schema-contract`。只查顶层 type 会漏掉嵌套字段里的错。

比如模型调一个建日程的工具，传了 `{"title": "周会", "count": true, "extra": 1}`：`start_date` 没给，`count` 是布尔却声明成 integer，`extra` 是没声明的键。校验器要把这三条分开报出来，模型才知道改哪里。本题的子集是 `type`、`properties`、`required`、`additionalProperties`（`true` / `false` / 嵌套的字段和类型规范（schema））。`$ref` 算加分项，现场可以声明不支持。返回 `errors: [(path, msg)]`，path 用 `$.a[0].b` 这种写法，方便模型改参数。

## 实现要点

动手前先把几条规范细节想清楚。JSON Schema 的 object 默认允许未声明的键，`additionalProperties: false` 才禁止。`required` 和 `properties` 互相独立，必填键可以没有 property schema，但仍然必须出现。`type: number` 包含整数，`integer` 不含小数。Python 里还有个坑，`isinstance(True, int)` 为真，不排除的话 JSON `true` 会被当成 1 放行；规范里 boolean 和 integer 不相交，这是现场最常见的静默 bug，所以校验 `integer`/`number` 要先排除 `bool`。

```python
def validate(inst, schema, path="$"):
    errors = []
    t = schema.get("type")
    py = {
        "object": dict, "array": list, "string": str,
        "boolean": bool, "null": type(None),
    }
    if t == "number":
        if isinstance(inst, bool) or not isinstance(inst, (int, float)):
            return [(path, "want number")]
    elif t == "integer":
        if isinstance(inst, bool) or not isinstance(inst, int):
            return [(path, "want integer")]
    elif t is not None and not isinstance(inst, py[t]):
        return [(path, f"want {t}")]
    if t == "object" or "properties" in schema or "required" in schema:
        if not isinstance(inst, dict):
            return errors
        for k in schema.get("required", []):
            if k not in inst:
                errors.append((f"{path}.{k}", "required"))
        props = schema.get("properties", {})
        add = schema.get("additionalProperties", True)
        for k, v in inst.items():
            if k in props:
                errors.extend(validate(v, props[k], f"{path}.{k}"))
            elif add is False:
                errors.append((f"{path}.{k}", "additional"))
            elif isinstance(add, dict):
                errors.extend(validate(v, add, f"{path}.{k}"))
    if t == "array" and isinstance(inst, list) and "items" in schema:
        for i, x in enumerate(inst):
            errors.extend(validate(x, schema["items"], f"{path}[{i}]"))
    return errors
```

测三个例子就够：缺 `required`；多一个未声明的键且 `additionalProperties` 为 false；`"count": true` 不能当成 integer 放过。嵌套对象递归就行。单位换算和权限别放进校验器，那是业务契约，Schema 只检查数据结构。

## 失败怎么回给模型

校验器的输出要带结构化路径，一句「参数不合法」模型没法改。`$.start_date` 缺 required、`$.extra` 撞上 `additionalProperties: false`、`$.n` 是 bool 却声明 integer，这三条要能分开改。在 Agent 循环里这是可恢复的错误，模型改了字段再调一次，工具侧别猜默认值。一猜默认，「漏了幂等键」就变成了「服务端替它生成」，副作用没法审计。

类型对但业务错的情况，比如金额单位、越权 id，不在本题子集里，schema 通过之后由业务层拒绝，同样回机器可读的 `error_code`。机械校验和业务校验拆开，才能和 `agent-schema-contract` 对上。还有几个边界顺手说一下：空对象 `{}` 在没有 `required` 时应该通过；`type: array` 要递归 `items`；`number` 接受 `3` 和 `3.5`，`integer` 拒绝 `3.5` 也拒绝 `true`。子集不实现 `$ref` / `anyOf` 的话当场声明。校验失败就不执行工具。validator 写成纯函数，schema 变更要版本化。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

schema 同时约束必填整数和禁止额外字段。True 在 Python 里属于 int 的子类，因此专门测试布尔值不能冒充整数，并检查错误路径。

```python
schema = {"type": "object", "required": ["n"],
          "properties": {"n": {"type": "integer"}}, "additionalProperties": False}
assert validate({"n": 2}, schema) == []
assert validate({}, schema) == [("$.n", "required")]
assert validate({"n": True}, schema) == [("$.n", "want integer")]
assert validate({"n": 2, "x": 1}, schema) == [("$.x", "additional")]
print("simple tests passed")
```

## 追问

**为什么必须在服务端验？**
Constrained decoding 只能提高格式命中率，越权 id、多字段探测、缺幂等键照样会发生。校验失败就回结构化错误，让模型改参数，工具不执行。

**`additionalProperties` 默认是什么？**
默认 true，允许未声明的键。生产工具建议显式写 false，缩小注入面。

**`required` 里的键不在 `properties` 里行吗？**
行，规范允许。键必须出现，值没有子 schema 就只验存在。

**只写了 `items`、漏写了 array 的 `type` 怎么办？**
子集实现可以在有 `items` 时当数组走。面试时把这个行为说出来，避免静默跳过。

**和 `agent-schema-contract` 怎么分工？**
本题是机械校验器；那题还要管 when-to-call、副作用、幂等和错误码。校验通过也不代表可以执行。
---
