"""Keep interview defaults focused on legal inputs, not defensive validation.

Only explicit checks for argument-validation exceptions are removed. Ordinary
assertions, legal empty inputs, masks, numerical stability and state-machine
errors (e.g. RuntimeError / KeyError) keep their original semantics.
"""
import ast

VALIDATION_ERRORS = {"ValueError", "TypeError", "IndexError", "OverflowError"}


def names(node):
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def interview_tests(source):
    if not source.strip():
        return source
    tree = ast.parse(source)
    validation_helpers = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
            node.name.lstrip("_").startswith(("expect_", "assert_", "must_raise", "raises_"))
        ):
            caught = set()
            for handler in ast.walk(node):
                if isinstance(handler, ast.ExceptHandler) and handler.type:
                    caught.update(names(handler.type))
            if caught and caught <= VALIDATION_ERRORS:
                validation_helpers.add(node.name)

    class Filter(ast.NodeTransformer):
        removed = 0

        def reject(self):
            self.removed += 1
            return None

        def validation_call(self, call):
            if not isinstance(call, ast.Call):
                return False
            name = ast.unparse(call.func).split(".")[-1]
            if name in validation_helpers or name in ("expect_value_error", "expect_type_error"):
                return True
            return ((name.lstrip("_").startswith(("expect_", "assert_", "must_raise", "raises")) or name in ("assertRaises", "assertRaisesRegex"))
                    and any(names(arg) & VALIDATION_ERRORS for arg in call.args))

        def visit_FunctionDef(self, node):
            if node.name in validation_helpers:
                return self.reject()
            return self.prune(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Expr(self, node):
            return self.reject() if self.validation_call(node.value) else self.generic_visit(node)

        def visit_Assert(self, node):
            return self.reject() if self.validation_call(node.test) else self.generic_visit(node)

        def visit_Try(self, node):
            caught = set().union(*(names(handler.type) for handler in node.handlers if handler.type))
            if caught and caught <= VALIDATION_ERRORS:
                return self.reject()
            return self.prune(node)

        def visit_With(self, node):
            if any(self.validation_call(item.context_expr) for item in node.items):
                return self.reject()
            return self.prune(node)

        visit_AsyncWith = visit_With

        def prune(self, node):
            self.generic_visit(node)
            if not node.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or getattr(node, "orelse", None):
                    node.body = [ast.Pass()]
                else:
                    return self.reject()
            return node

        visit_For = prune
        visit_AsyncFor = prune
        visit_While = prune
        visit_If = prune
        visit_ClassDef = prune

    transform = Filter()
    filtered = transform.visit(tree)
    if not transform.removed:
        return source
    ast.fix_missing_locations(filtered)
    return "# 面试默认测试：仅检查合法输入与题目要求的有效边界。\n" + ast.unparse(filtered) + "\n"
