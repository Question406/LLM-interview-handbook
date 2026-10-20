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


def test():
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


if __name__ == "__main__":
    test()
