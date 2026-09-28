---
id: code-tool-schema-validator
section: coding
order: 216
level: A
title: 手写 Tool JSON Schema 校验器：type、required、additionalProperties
quick: >-
  服务端递归校验，不要信模型。核对 `type`、`required` 缺键、以及
  `additionalProperties: false` 拒多余字段。Python 里 `bool` 是 `int` 子类，必须先排除。契约题见
  `agent-schema-contract`。
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

错法：「模型会按 schema 生成，不必再验」或只查顶层 type。Agent 工具调用必须服务端拒绝合法 JSON 但缺必填、多字段、类型错的参数，见 `agent-schema-contract`。本题子集：`type`、`properties`、`required`、`additionalProperties`（`true` / `false` / 嵌套 schema）。`$ref` 是加分，现场可以声明不支持。返回 `errors: [(path, msg)]`，path 用 `$.a[0].b`，方便模型改参。

## 实现要点

JSON Schema 的 object 默认允许未声明键；`additionalProperties: false` 才禁止。`required` 与 `properties` 独立：必填键可以没有 property schema（仍须存在）。`type: number` 含整数；`integer` 不含小数。Python 陷阱：`isinstance(True, int)` 为真，校验 `integer`/`number` 要先排除 `bool`。

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

测三例：缺 `required`；多一个未声明键且 `additionalProperties` 为 false；`"count": true` 不得当成 integer。Nested object 递归即可。不要在校验器里做单位换算或权限，那是业务契约，schema 只挡结构。

## 失败怎么回给模型

校验器输出必须是结构化路径，不要一句「参数不合法」。`$.start_date` 缺 required、`$.extra` 撞上 `additionalProperties: false`、`$.n` 是 bool 却声明 integer，三条要能分开改。Agent 循环里这是可恢复错误：模型改字段再调，工具侧不要猜默认值。猜默认会把「漏了幂等键」变成「服务端替它生成」，副作用无法审计。

类型对但业务错（金额单位、越权 id）不属于本题子集，schema 通过后由业务层拒绝，仍回机器可读 `error_code`。机械校验和业务校验拆开，才能和 `agent-schema-contract` 对上。生产建议显式 `additionalProperties: false`。空对象 `{}` 在没有 `required` 时应通过；`type: array` 要递归 `items`；`number` 接受 `3` 和 `3.5`，`integer` 拒绝 `3.5` 也拒绝 `true`。子集不实现 `$ref` / `anyOf` 时当场声明。校验失败不得执行工具。validator 做成纯函数；schema 变更要版本化。

## 追问

- **为什么必须服务端验？** Constrained decoding 只能提高格式命中率；越权 id、多字段探测、缺幂等键仍会发生。校验失败回结构化错误，让模型改参而不是执行。
- **`additionalProperties` 默认？** 默认 true（允许未声明键）。生产工具建议显式 false，缩小注入面。
- **`required` 不在 `properties` 里？** 规范允许。键必须出现，值若无子 schema 则只验存在。
- **array 的 `type` 漏写只写了 `items`？** 子集实现可在有 `items` 时当数组走；面试声明行为，避免静默跳过。
- **和 `agent-schema-contract` 分工？** 本题是机械校验器；那题还要 when-to-call、副作用、幂等与错误码。校验通过不等于可以执行。
- **`integer` 为什么必须先排除 `bool`？** Python 里 `True` 是 `int` 子类，不排除会把 JSON `true` 当成 1 放行。规范里 boolean 与 integer 不相交，这是现场最常见的静默 bug。
---
