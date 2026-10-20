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


def test():
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


if __name__ == "__main__":
    test()
