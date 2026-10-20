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


def test():
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


if __name__ == "__main__":
    test()
