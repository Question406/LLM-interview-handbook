---
id: p3a-anthropic-oa-recipe-manager
section: anthropic
order: 609
level: A
title: "Anthropic：菜谱管理：大小写、权限、版本与回滚"
quick: "用 casefold 后的名字查找、单独保留显示名；所有写操作走同一个权限检查；版本历史只追加不修改，回滚是把旧内容复制成新版本。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · oa-recipe-manager"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/oa-recipe-manager
    type: secondary
---

## 题目

OA 题，分四级逐步实现一个菜谱管理系统：菜谱的增删改查、按配料数量排序列出、用户权限，以及版本历史和回滚。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

这类分级 OA 主要考的是每加一级需求时，前面的逻辑不被改乱。几个设计点：

- 名字查找不区分大小写，但显示时要保留用户原来写的名字。做法是用 `casefold()` 后的名字当字典键，显示名单独存一份。
- 权限检查只写一处。所有修改入口（更新、回滚）都先经过同一个函数确认用户是 owner 或被授权的 editor，加新的写操作时就不会漏掉检查。
- 版本历史只追加、不修改。每个版本存成 tuple，回滚就是把旧版本的内容再追加成一个新版本，原来的历史都还在。

需要先和面试官确认的边界：回滚是「恢复成旧内容并产生新版本」还是「把历史截断回旧版本」；配料数相同时怎么排序；删除后再用同名创建，旧的权限和历史还算不算数。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Recipes.create(user, name, ingredients)`：创建菜谱，`user` 成为 owner，内容是版本 0。名字按 `casefold()` 判重，保留首次创建时的显示名。
- `Recipes.grant(user, name, editor)`：只有 owner 能授权 editor，否则抛 `PermissionError`。
- `Recipes.update(user, name, ingredients) -> int`：owner 或 editor 可写，追加一个新版本，返回新版本号。
- `Recipes.rollback(user, name, version) -> int`：把第 `version` 版的内容复制成一个新版本，不删除任何历史，返回新版本号。
- `Recipes.list_recipes()`：返回 `(显示名, 当前配料数, 当前版本号)` 列表，按配料数升序，相同时按规范化名字升序。
- 配料是互不重复的字符串列表。菜谱不存在抛 `KeyError`，其余非法输入抛 `ValueError`。最多 1000 个菜谱。

### 输入输出示例

```text
create("a", "Soup", ["water"])                 # 版本 0
grant("a", "SOUP", "b")                        # 名字不区分大小写
update("b", "soup", ["water", "salt"])  -> 1
rollback("a", "soup", 0)                -> 2   # 内容回到 ["water"]
list_recipes()                          -> [("Soup", 1, 2)]
```

回滚后版本 1 的 `("water", "salt")` 仍然可以读到。

### 解题思路与正确性

规范化名字只负责查找和判重，显示名独立保存，所以 `SOUP`、`soup` 都能找到同一个菜谱，列出时仍显示 `Soup`。

`update` 和 `rollback` 都通过 `_get_writable` 取菜谱，权限规则只有一份。历史是一个只追加的列表，元素是 tuple，所以旧版本不会被后续修改影响；回滚直接追加旧版本的 tuple 引用也是安全的。版本号就是列表下标，每次成功修改加一。

### 完整参考实现（Python 3）

```python
class Recipes:
    """菜谱管理：名字不区分大小写、owner/editor 权限、不可变版本历史。"""

    def __init__(self):
        self.recipes = {}  # casefold 后的名字 -> 菜谱记录

    def create(self, user, name, ingredients):
        key = name.casefold()
        if not key:
            raise ValueError("recipe name must not be empty")
        if key in self.recipes:
            raise ValueError(f"recipe already exists: {name!r}")
        self.recipes[key] = {
            "name": name,  # 保留首次创建时的显示名
            "owner": user,
            "editors": set(),
            "history": [normalize_ingredients(ingredients)],  # 版本号就是下标
        }

    def _get(self, name):
        key = name.casefold()
        if key not in self.recipes:
            raise KeyError(f"no such recipe: {name!r}")
        return self.recipes[key]

    def _get_writable(self, user, name):
        """所有写入口都走这里，权限检查只有一份。"""
        recipe = self._get(name)
        if user != recipe["owner"] and user not in recipe["editors"]:
            raise PermissionError(f"{user!r} cannot edit {recipe['name']!r}")
        return recipe

    def grant(self, user, name, editor):
        recipe = self._get(name)
        if recipe["owner"] != user:
            raise PermissionError("only the owner can grant edit access")
        recipe["editors"].add(editor)

    def update(self, user, name, ingredients):
        """追加一个新版本，返回新版本号。"""
        recipe = self._get_writable(user, name)
        recipe["history"].append(normalize_ingredients(ingredients))
        return len(recipe["history"]) - 1

    def rollback(self, user, name, version):
        """把旧版本的内容复制成一个新版本，历史不删除，返回新版本号。"""
        recipe = self._get_writable(user, name)
        history = recipe["history"]
        if not 0 <= version < len(history):
            raise ValueError(f"no such version: {version}")
        history.append(history[version])  # tuple 不可变，共享引用是安全的
        return len(history) - 1

    def list_recipes(self):
        """返回 (显示名, 当前配料数, 当前版本号)，按配料数、再按规范名字排序。"""
        def sort_key(item):
            key, recipe = item
            return len(recipe["history"][-1]), key

        return [
            (recipe["name"], len(recipe["history"][-1]), len(recipe["history"]) - 1)
            for _, recipe in sorted(self.recipes.items(), key=sort_key)
        ]


def normalize_ingredients(ingredients):
    """配料必须是互不重复的字符串，存成 tuple 防止之后被改。"""
    if any(not isinstance(item, str) for item in ingredients):
        raise ValueError("ingredients must be strings")
    if len(set(ingredients)) != len(ingredients):
        raise ValueError("ingredients must not repeat")
    return tuple(ingredients)
```

### 可执行测试

```python
def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise {error_type.__name__}")

# 名字不区分大小写，授权后 editor 可以更新
recipes = Recipes()
recipes.create("a", "Soup", ["water"])
recipes.grant("a", "SOUP", "b")
assert recipes.update("b", "soup", ["water", "salt"]) == 1

# 回滚生成新版本，旧版本仍然保留
assert recipes.rollback("a", "soup", 0) == 2
assert recipes.list_recipes() == [("Soup", 1, 2)]
assert recipes.recipes["soup"]["history"][1] == ("water", "salt")

# 排序：配料数相同时按规范名字
recipes.create("a", "apple pie", ["apple"])
recipes.create("a", "Bread", ["flour", "water"])
assert recipes.list_recipes() == [("apple pie", 1, 0), ("Soup", 1, 2), ("Bread", 2, 0)]

# 权限和输入校验
expect_error(PermissionError, recipes.update, "c", "soup", [])
expect_error(PermissionError, recipes.grant, "b", "soup", "c")   # editor 不能再授权
expect_error(ValueError, recipes.create, "a", "SOUP", [])        # 大小写不同也算重名
expect_error(ValueError, recipes.update, "a", "soup", ["x", "x"])
expect_error(ValueError, recipes.rollback, "a", "soup", 5)
expect_error(KeyError, recipes.update, "a", "missing", [])
```

### 复杂度与追问

设菜谱数为 R、单个菜谱的配料数为 m。`create` 和 `update` 是 O(m)（检查重复），`rollback` 是 O(1)，`list_recipes` 是 O(R log R)。历史的总空间是所有版本配料数之和。

- 要支持删除后用同名重建呢？给每个菜谱实例一个独立的 id，名字只是指向当前实例的索引。删除后重建得到新 id，旧实例的权限和历史默认不继承，具体规则要和面试官确认。
- 历史太长占空间怎么办？可以只存相邻版本的差异，每隔若干版本存一次完整快照，读取某版本时从最近的快照开始应用差异。
