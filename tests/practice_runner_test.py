"""Integration tests for the real local Python child process."""
import os
import ast
from pathlib import Path
import sys
import threading
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/practice"))
import server
from exercises import load_exercise, description
from official_cases import check_example, official_questions
from interview_tests import interview_tests


def run(code, tests="", **kwargs):
    return server.execute({"id": str(uuid.uuid4()), "code": code, "tests": tests, **kwargs})


class RunnerTests(unittest.TestCase):
    def test_transformer_starter_preserves_frozen_weight_fixture(self):
        exercise = load_exercise("us-tech-interview", "kv-prefix-transformer")
        namespace = {}
        exec(exercise["starter"], namespace)
        model = namespace["TinyTransformer"](seed=7, layers=3)
        self.assertFalse(model.embed.flags.writeable)
        self.assertEqual(len(model.weights), 3)
        with self.assertRaises(NotImplementedError):
            model.forward([1, 2])
        with self.assertRaises(NotImplementedError):
            namespace["slice_cache"]((), 0)

    def test_leetcode_followup_cannot_replace_main_problem_entrypoint(self):
        for question in ("lc-392-is-subsequence", "lc-105-construct-binary-tree-from-preorder-and-inorder-traversal", "lc-148-sort-list"):
            with self.subTest(question=question):
                exercise = load_exercise("leetcode-150", question)
                result = run(exercise["reference"], exercise["tests"])
                self.assertEqual(result["status"], "passed", result)

    def test_statement_cannot_fall_back_to_a_solution_or_placeholder(self):
        with self.assertRaises(ValueError):
            description("先计算距离，再排序。\n```python\ndef solve(): pass\n```", "KNN", None, "test-task")
        task = "给定数据并返回题目约定的结果。输入参数、输出类型与示例都属于题面，不能读取后面的解法。" * 5
        for ending in ("\n## 解题思路\nDO_NOT_LEAK_SOLUTION", "\n<!-- problem-statement:end -->\n<div>DO_NOT_LEAK_SOLUTION</div>"):
            result = description("## 题目描述\n" + task + ending, "task", None, "test-task")
            self.assertEqual(result, task)
            self.assertNotIn("DO_NOT_LEAK", result)

    def test_scoped_dfs_only_requires_the_function_in_its_statement(self):
        exercise = load_exercise("us-tech-interview", "p3a-google-deepmind-graph-dfs")
        names = {node.name for node in ast.parse(exercise["starter"]).body if isinstance(node, ast.FunctionDef)}
        self.assertEqual(names, {"dfs"})
        self.assertNotIn("suffix_counts", exercise["tests"])
        self.assertNotIn("topk", exercise["tests"])
        result = run(exercise["reference"], exercise["tests"])
        self.assertEqual(result["status"], "passed", result)

    def test_bank_account_provided_scaffolding_can_be_used_without_reimplementing_it(self):
        exercise = load_exercise("us-tech-interview", "p3a-xai-multithreaded-bank-account-bug-hunt")
        reference = ast.parse(exercise["reference"])
        account = next(node for node in reference.body if isinstance(node, ast.ClassDef) and node.name == "Account")
        # Simulate completing only the Account class described by the task.
        result = run(exercise["starter"] + "\n" + ast.unparse(account), exercise["tests"])
        self.assertEqual(result["status"], "passed", result)

    def test_assertions_and_stdin(self):
        result = run("x = int(input())\nprint(x * 2)", "assert x == 4\nassert x * 2 == 8", stdin="4\n")
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["stdout"], "8\n")
        self.assertEqual(len(result["checks"]), 2)

    def test_failure_reports_actual_expected_and_correct_file_line(self):
        result = run("x = 3", "# test\nassert x == 4\nassert True")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["file"], "test_code.py")
        self.assertEqual(result["error"]["line"], 2)
        self.assertIn("Expected: 4", result["error"]["message"])
        self.assertIn("Actual:   3", result["error"]["message"])
        self.assertEqual(len(result["checks"]), 1)

    def test_syntax_error_and_runtime_error(self):
        result = run("def broken(:\n    pass")
        self.assertEqual(result["error"]["type"], "SyntaxError")
        self.assertEqual(result["error"]["line"], 1)
        result = run("x = 1\nraise ValueError('bad input')")
        self.assertEqual(result["error"]["file"], "user_code.py")
        self.assertEqual(result["error"]["line"], 2)

    def test_fresh_namespace_and_no_server_secret(self):
        self.assertEqual(run("secret = 42")["status"], "passed")
        self.assertEqual(run("print(secret)")["error"]["type"], "NameError")
        result = run("import os\nassert 'PRACTICE_RUNNER_TOKEN' not in os.environ")
        self.assertEqual(result["status"], "passed")

    def test_timeout_output_limit_and_recovery(self):
        self.assertEqual(run("while True: pass", timeout=1)["status"], "timeout")
        self.assertEqual(run("while True: print('x' * 10000)")["status"], "output_limit")
        self.assertEqual(run("print('recovered')")["stdout"], "recovered\n")

    def test_cancel(self):
        job_id, result = str(uuid.uuid4()), []
        worker = threading.Thread(target=lambda: result.append(server.execute({"id": job_id, "code": "while True: pass", "timeout": 10})))
        worker.start()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            with server.LOCK:
                ready = bool(server.JOBS.get(job_id, {}).get("process"))
            if ready:
                break
            time.sleep(.01)
        self.assertTrue(server.cancel(job_id))
        worker.join(5)
        self.assertFalse(worker.is_alive())
        self.assertEqual(result[0]["status"], "cancelled")

    def test_native_packages_and_plot(self):
        result = run("""import torch, numpy as np, pandas as pd, scipy.linalg
import sympy, sortedcontainers, PIL, pytest
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
x = torch.tensor([1., 2., 3.], requires_grad=True)
(x ** 2).sum().backward()
torch.testing.assert_close(x.grad, torch.tensor([2., 4., 6.]))
model = LinearRegression().fit([[1], [2], [3]], [3, 5, 7])
np.testing.assert_allclose(model.predict([[4]]), [9])
assert scipy.linalg.det([[1, 0], [0, 2]]) == 2
assert list(sortedcontainers.SortedList([3, 1])) == [1, 3]
assert sympy.diff(sympy.Symbol('x') ** 2) == 2 * sympy.Symbol('x')
plt.plot([1, 2], [3, 4])
""", timeout=30)
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(len(result["plots"]), 1)
        self.assertTrue(result["plots"][0].startswith("iVBOR"))

    def test_pytorch_attention_backward_and_optimizer(self):
        result = run("""import torch
import torch.nn.functional as F
q = torch.randn(1, 2, 3, 4, requires_grad=True)
F.scaled_dot_product_attention(q, q, q, is_causal=True).sum().backward()
assert torch.isfinite(q.grad).all()
layer = torch.nn.Linear(4, 2)
opt = torch.optim.AdamW(layer.parameters(), lr=0.01)
layer(torch.ones(1, 4)).sum().backward()
before = layer.weight.detach().clone()
opt.step()
assert not torch.equal(before, layer.weight)
""")
        self.assertEqual(result["status"], "passed", result)

    def test_question_extraction_uses_helpers_and_hides_primary_solution(self):
        for book, question in [("leetcode-150", "lc-1-two-sum"),
                               ("leetcode-150", "lc-2-add-two-numbers"),
                               ("llm-interview-v2", "code-softmax-stable"),
                               ("ml-101", "ml101-knn-implementation"),
                               ("us-tech-interview", "xai-kv-txn")]:
            with self.subTest(question=question):
                exercise = load_exercise(book, question)
                self.assertIn("NotImplementedError", exercise["starter"])
                result = run(exercise["reference"], exercise["tests"])
                self.assertEqual(result["status"], "passed", result)

    def test_question_paths_reject_traversal(self):
        with self.assertRaises(ValueError):
            load_exercise("../..", "secret")

    def test_official_examples_allow_valid_variants_and_reject_bad_answers(self):
        self.assertTrue(check_example({"twoSum": lambda nums, target: [1, 0]}, "two-sum", "twoSum", 1))
        with self.assertRaises(AssertionError):
            check_example({"twoSum": lambda nums, target: [0, 0]}, "two-sum", "twoSum", 1)
        # Returning the right length while leaving the wrong prefix must fail.
        with self.assertRaises(AssertionError):
            check_example({"removeElement": lambda nums, val: 2}, "remove-element", "removeElement", 1)

    def test_descriptions_default_cases_and_official_provenance(self):
        for book, question in [("leetcode-150", "lc-2-add-two-numbers"),
                               ("ml-101", "ml101-knn-implementation"),
                               ("data-team-interview", "dt-countmin-code")]:
            exercise = load_exercise(book, question)
            self.assertTrue(exercise["description"])
            self.assertTrue(exercise["examples"])
            self.assertTrue(exercise["reference"])
            self.assertIn("assert", exercise["tests"])
        record = load_exercise("leetcode-150", "lc-2-add-two-numbers")
        self.assertEqual(record["source"]["kind"], "leetcode")
        self.assertEqual(record["examples"][0]["output"], "[7,0,8]")
        self.assertTrue(record["constraints"])
        snapshot = official_questions()
        self.assertEqual(len(snapshot), 209)
        self.assertEqual(sum(len(row["examples"]) for row in snapshot.values()), 512)
        self.assertTrue(all("content" not in row for row in snapshot.values()))

    def test_starter_hides_all_solution_functions(self):
        exercise = load_exercise("llm-interview-v2", "code-ppo-grpo-gspo")
        functions = [node for node in ast.parse(exercise["starter"]).body if isinstance(node, ast.FunctionDef)]
        self.assertGreater(len(functions), 3)
        self.assertTrue(all(len(node.body) == 1 and isinstance(node.body[0], ast.Raise) for node in functions))

    def test_interview_softmax_does_not_require_defensive_input_validation(self):
        exercise = load_exercise("us-tech-interview", "coding-softmax-stable")
        self.assertNotIn("expect_value_error", exercise["tests"])
        # This implementation intentionally has no NaN/shape/all-masked guards.
        code = """import numpy as np
def softmax(x, axis=-1):
    z = np.asarray(x, dtype=np.float64)
    z = z - np.max(z, axis=axis, keepdims=True)
    exps = np.exp(z)
    return exps / exps.sum(axis=axis, keepdims=True)
def log_softmax(x, axis=-1):
    z = np.asarray(x, dtype=np.float64)
    z = z - np.max(z, axis=axis, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=axis, keepdims=True))
"""
        result = run(code, exercise["tests"])
        self.assertEqual(result["status"], "passed", result)
        self.assertGreater(len(result["checks"]), 5)

    def test_validation_filter_preserves_legal_edges_and_state_errors(self):
        source = """def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError('accepted invalid input')
for bad in (None, float('nan')):
    expect_value_error(fn, bad)
assert fn([]) == []
assert fn([1]) == [1]
with pytest.raises(ValueError):
    fn(None)
with pytest.raises(RuntimeError):
    closed_transaction.commit()
"""
        filtered = interview_tests(source)
        self.assertNotIn("expect_value_error", filtered)
        self.assertNotIn("for bad", filtered)
        self.assertNotIn("raises(ValueError)", filtered)
        self.assertIn("fn([])", filtered)
        self.assertIn("fn([1])", filtered)
        self.assertIn("raises(RuntimeError)", filtered)

    def test_javascript_default_tests_and_error_location(self):
        exercise = load_exercise("us-tech-interview", "p3a-xai-input-field-review")
        result = server.execute({"id": str(uuid.uuid4()), "code": exercise["reference"],
                                 "tests": exercise["tests"], "language": "javascript"})
        self.assertEqual(result["status"], "passed", result)
        self.assertTrue(result["checks"])
        result = server.execute({"id": str(uuid.uuid4()), "code": "const value = 3;",
                                 "tests": "import assert from 'node:assert/strict';\nassert.equal(value, 4);", "language": "javascript"})
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["line"], 2)
        self.assertEqual(result["error"]["file"], "test_code.py")


if __name__ == "__main__":
    unittest.main(verbosity=2)
