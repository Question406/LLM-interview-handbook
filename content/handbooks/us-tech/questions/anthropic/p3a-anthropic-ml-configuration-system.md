---
id: p3a-anthropic-ml-configuration-system
section: anthropic
order: 627
level: A
title: "Anthropic：ML 配置系统：schema、继承与可复现性"
quick: "把继承合并、命令行覆盖、schema 校验和最终冻结拆成独立步骤，合并语义写清楚，并保存解析后的完整配置和 hash 以便复现。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · ml-configuration-system"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/ml-configuration-system
    type: secondary
---

## 题目

为 ML 训练设计并部分实现一个配置系统。网站没有给出完整的具体要求；常见的需求是：配置可以分层继承（默认值、项目配置、实验配置），可以在命令行覆盖，要有类型校验，并保证实验可以复现。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；题卡没有给出精确的合并规则。下面的分层需求、接口、约束和测试是手册补的练习约定，不是原题。

## 思路

把系统拆成几个互相独立的步骤：

1. 解析继承关系：按父配置列表从左到右合并，再合并自身的值，同时检测继承环；
2. 应用命令行覆盖；
3. 按 schema 校验类型和字段；
4. 把最终结果冻结成只读对象，生成规范 JSON 和 hash。

训练代码只读冻结后的结果，不能在训练过程中重新读配置文件或偷偷改值。

动手前先把合并语义说清楚，不能拿一次 `dict.update` 冒充整个系统：

- 嵌套 dict 递归合并，list 整体替换，不隐式拼接；
- 要删除某个继承来的字段时，用显式的删除操作，不要靠写 `null`；
- schema 外的未知字段直接拒绝，拼错的字段名才不会被悄悄忽略；
- 环境变量缺失时报错，不要回退到某台机器上的默认值，否则不同机器跑出来的配置会不一样。

为了复现，每次运行保存解析后的完整 JSON 和它的 hash，以及代码 commit、数据版本和命令行覆盖。最好还记录每个最终字段来自哪一层配置，被问到「`batch_size` 为什么是这个值」时可以直接回答。

密钥不能写进配置快照。配置里只存密钥的引用和版本，真正的凭证由受控的运行环境在运行时读取。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `resolve_config(configs, name, schema, overrides=None) -> dict`：返回 `{"config": 只读配置, "json": 规范 JSON, "sha256": JSON 的哈希}`，不修改任何输入。
- `configs[name]` 可以有 `parents`（有序的父配置名列表）和 `values`（嵌套 dict）。按 `parents` 从左到右深度合并，再合并自身 `values`；dict 递归合并，list 整体替换。继承环或引用不存在的配置抛 `ValueError`。
- `schema` 是嵌套 dict，叶子是 `int`、`float`、`str`、`bool`、`list` 之一。所有字段必填，拒绝未知字段，类型严格匹配（`bool` 不算 `int`）。不满足时抛 `ValueError`。
- `overrides` 的键是点分路径（如 `"train.batch"`），必须指向 schema 里已有的叶子字段。
- 配置不超过 100 个，嵌套深度不超过 30。

### 输入输出示例

```text
base:  train = {batch: 8, lr: 0.01}, tags = ["a"]
child: parents = [base], train = {lr: 0.02}, tags = ["b"]

resolve_config(configs, "child", schema, {"train.batch": 16})["config"]
  -> train = {batch: 16, lr: 0.02}, tags = ("b",)
```

用同样的输入再解析一次，`sha256` 完全相同；`{"a": {"parents": ["a"]}}` 这样的自继承会被拒绝。

### 解题思路与正确性

继承解析用 `visiting` 集合记录当前递归链上的配置，只有在同一条链上再次遇到才算环。菱形继承里两个父配置共享同一个祖先，这个祖先会被访问两次，但不在同一条链上，不会被误判；`cache` 让它只解析一次。

合并函数每次返回新的 dict，并对取来的值做深拷贝，所以输入的 `configs` 和缓存都不会被改动。最终结果先校验，再用 `sort_keys` 生成规范 JSON，hash 只取决于最终的值，与 dict 的插入顺序无关。返回的 `config` 是只读视图，训练代码改它会直接报 `TypeError`。

### 完整参考实现（Python 3）

```python
import hashlib
import json
from copy import deepcopy
from types import MappingProxyType

LEAF_TYPES = (int, float, str, bool, list)


def _deep_merge(base, update):
    """返回新 dict：两边都是 dict 的键递归合并，其余（包括 list）整体替换。"""
    merged = deepcopy(base)
    for key, value in update.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _resolve_inheritance(configs, name):
    """按 parents 从左到右合并，再合并自身 values；检测继承环。"""
    visiting = set()  # 当前递归链上的配置，只有它们重复出现才算环
    cache = {}  # 共享祖先只解析一次

    def load(key):
        if key in visiting:
            raise ValueError(f"inheritance cycle through {key!r}")
        if key in cache:
            return cache[key]
        if key not in configs:
            raise ValueError(f"unknown config {key!r}")
        visiting.add(key)
        resolved = {}
        for parent in configs[key].get("parents", []):
            resolved = _deep_merge(resolved, load(parent))
        resolved = _deep_merge(resolved, configs[key].get("values", {}))
        visiting.remove(key)
        cache[key] = resolved
        return resolved

    return deepcopy(load(name))


def _apply_overrides(resolved, schema, overrides):
    """CLI 覆盖：点分路径必须指向 schema 里的叶子字段。"""
    for path, value in overrides.items():
        *parents, leaf = path.split(".")
        target, rule = resolved, schema
        for key in parents:
            if key not in rule or not isinstance(rule[key], dict):
                raise ValueError(f"override {path!r}: {key!r} is not a section in schema")
            rule = rule[key]
            target = target.setdefault(key, {})
            if not isinstance(target, dict):
                raise ValueError(f"override {path!r}: {key!r} is not a dict in config")
        if leaf not in rule or isinstance(rule[leaf], dict):
            raise ValueError(f"override {path!r} is not a leaf field in schema")
        target[leaf] = deepcopy(value)


def _validate(value, rule, path="<root>"):
    """字段必须和 schema 完全一致，叶子类型严格匹配（bool 不算 int，int 不算 float）。"""
    if isinstance(rule, dict):
        if not isinstance(value, dict):
            raise ValueError(f"{path}: expected a section")
        if set(value) != set(rule):
            missing = sorted(set(rule) - set(value))
            unknown = sorted(set(value) - set(rule))
            raise ValueError(f"{path}: missing {missing}, unknown {unknown}")
        for key, child_rule in rule.items():
            _validate(value[key], child_rule, f"{path}.{key}")
    elif rule not in LEAF_TYPES:
        raise ValueError(f"{path}: unsupported schema type {rule!r}")
    elif type(value) is not rule:
        raise ValueError(f"{path}: expected {rule.__name__}, got {type(value).__name__}")


def _freeze(value):
    """返回只读视图：dict 变 MappingProxyType，list 变 tuple。"""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value


def resolve_config(configs, name, schema, overrides=None):
    """继承合并 -> CLI 覆盖 -> schema 校验 -> 冻结，返回 config、规范 JSON 和它的 SHA-256。"""
    resolved = _resolve_inheritance(configs, name)
    _apply_overrides(resolved, schema, overrides or {})
    _validate(resolved, schema)
    # sort_keys 让 hash 只取决于最终值，与 dict 插入顺序无关
    canonical = json.dumps(resolved, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {
        "config": _freeze(resolved),
        "json": canonical,
        "sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }
```

### 可执行测试

```python
def expect_value_error(*args):
    try:
        resolve_config(*args)
    except ValueError:
        return
    raise AssertionError("resolve_config should raise ValueError")

configs = {
    "base": {"values": {"train": {"batch": 8, "lr": 0.01}, "tags": ["a"]}},
    "child": {"parents": ["base"], "values": {"train": {"lr": 0.02}, "tags": ["b"]}},
}
schema = {"train": {"batch": int, "lr": float}, "tags": list}

# 继承 + 覆盖：dict 递归合并，list 整体替换，CLI 覆盖优先级最高
result = resolve_config(configs, "child", schema, {"train.batch": 16})
assert result["config"]["train"]["batch"] == 16
assert result["config"]["train"]["lr"] == 0.02
assert result["config"]["tags"] == ("b",)

# 同样输入得到同样的 hash；输入配置没有被修改
again = resolve_config(configs, "child", schema, {"train.batch": 16})
assert result["sha256"] == again["sha256"]
assert configs["base"]["values"]["train"]["batch"] == 8

# 结果只读
try:
    result["config"]["train"]["batch"] = 2
except TypeError:
    pass
else:
    raise AssertionError("resolved config should be read-only")

# 类型不符（bool 不算 int）、schema 外的字段
expect_value_error(configs, "child", schema, {"train.batch": True})
expect_value_error(configs, "child", schema, {"train.unknown": 1})

# 继承环
expect_value_error({"a": {"parents": ["a"], "values": {}}}, "a", {})

# 菱形继承：共享祖先不是环，右边的父配置覆盖左边
diamond = {
    "root": {"values": {"x": 1}},
    "left": {"parents": ["root"], "values": {"x": 2}},
    "right": {"parents": ["root"], "values": {"x": 3}},
    "leaf": {"parents": ["left", "right"]},
}
assert resolve_config(diamond, "leaf", {"x": int})["config"]["x"] == 3
```

### 复杂度与追问

设配置数为 C、最终配置大小为 S。每个配置只解析一次，但每次合并都要深拷贝，最坏 O(C × S) 时间和空间。

- schema 里的 `list` 只检查容器类型，不检查元素类型；需要的话可以把 schema 扩展成 `list[int]` 这样的写法。
- 怎么证明方案不只在正常路径上成立？针对具体的失败情形写测试：循环继承、拼错的覆盖字段、类型不符、缺失的环境变量，检查它们都在训练开始前就被拒绝，而且不会留下半合并的配置。
