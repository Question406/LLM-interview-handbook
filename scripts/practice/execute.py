"""Child process: execute editor buffers and return diagnostics and plot artifacts."""
import ast
import io
import json
import linecache
from pathlib import Path
import sys
import traceback
import importlib.util

spec = importlib.util.spec_from_file_location("official_cases", Path(__file__).with_name("official_cases.py"))
official_cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(official_cases)


def diagnostic(error):
    frames = traceback.extract_tb(error.__traceback__)
    frame = next((f for f in reversed(frames) if f.filename in ("user_code.py", "test_code.py")), None)
    return {
        "type": type(error).__name__, "message": str(error),
        "file": getattr(error, "filename", None) or (frame.filename if frame else None),
        "line": getattr(error, "lineno", None) or (frame.lineno if frame else None),
        "traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
    }


def run(request):
    namespace = {"__name__": "__main__", "__file__": "user_code.py"}
    checks = []
    result = {"status": "passed", "checks": checks, "error": None, "plots": []}
    sys.stdin = io.StringIO(request.get("stdin", ""))
    for name, source in (("user_code.py", request["code"]), ("test_code.py", request.get("tests", ""))):
        linecache.cache[name] = (len(source), None, source.splitlines(True), name)

    def assert_equal(actual, expected):
        if not actual == expected:
            raise AssertionError(f"Expected: {expected!r}\nActual:   {actual!r}")

    namespace["__practice_assert_equal__"] = assert_equal
    namespace["check_example"] = lambda slug, entrypoint, index: official_cases.check_example(namespace, slug, entrypoint, index)
    try:
        exec(compile(request["code"], "user_code.py", "exec"), namespace)
        if request.get("tests", "").strip():
            tree = ast.parse(request["tests"], filename="test_code.py")
            # Run top-level statements in the same namespace, preserving setup
            # and future-import compiler flags. Nested assertions keep normal
            # Python semantics; top-level checks get individual result rows.
            flags = 0
            for statement in tree.body:
                executable = statement
                if (isinstance(statement, ast.Assert) and statement.msg is None
                        and isinstance(statement.test, ast.Compare) and len(statement.test.ops) == 1
                        and isinstance(statement.test.ops[0], ast.Eq)):
                    executable = ast.copy_location(ast.Expr(value=ast.Call(
                        func=ast.Name(id="__practice_assert_equal__", ctx=ast.Load()),
                        args=[statement.test.left, statement.test.comparators[0]], keywords=[])), statement)
                    ast.fix_missing_locations(executable)
                module = ast.Module(body=[executable], type_ignores=[])
                compiled = compile(module, "test_code.py", "exec", flags=flags)
                flags |= compiled.co_flags & sum(
                    getattr(__import__("__future__"), feature).compiler_flag
                    for feature in __import__("__future__").all_feature_names
                )
                is_check = isinstance(statement, ast.Assert) or (
                    isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)
                    and "assert" in ast.unparse(statement.value.func)
                )
                try:
                    exec(compiled, namespace)
                    if is_check:
                        checks.append({"line": statement.lineno, "label": ast.get_source_segment(request["tests"], statement), "passed": True})
                except BaseException as error:
                    result["status"] = "failed"
                    result["error"] = diagnostic(error)
                    checks.append({"line": statement.lineno, "label": ast.get_source_segment(request["tests"], statement), "passed": False})
                    # A failed state-changing check can invalidate later checks.
                    # Stop at the first error instead of reporting misleading passes.
                    break
    except BaseException as error:
        result["status"] = "failed"
        result["error"] = diagnostic(error)
    finally:
        if "matplotlib.pyplot" in sys.modules:
            pyplot = sys.modules["matplotlib.pyplot"]
            try:
                import base64
                for number in pyplot.get_fignums()[:4]:
                    buffer = io.BytesIO()
                    pyplot.figure(number).savefig(buffer, format="png", dpi=100)
                    if buffer.tell() <= 2_000_000:
                        result["plots"].append(base64.b64encode(buffer.getvalue()).decode())
            except Exception as error:
                print("Plot export:", error, file=sys.stderr)
            finally:
                pyplot.close("all")
    return result


if __name__ == "__main__":
    request = json.loads(Path(sys.argv[1]).read_text())
    # stdout/stderr remain ordinary streams, collected by the parent. The result
    # file is independent of printed output and remains valid when tests fail.
    result = run(request)
    Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False))
