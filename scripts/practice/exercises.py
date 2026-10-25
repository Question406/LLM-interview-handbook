"""Prepare editable exercises from source Markdown, never from rendered HTML."""
import ast
from html import unescape
import json
from pathlib import Path
import re
from official_cases import official_questions
from interview_tests import interview_tests

ROOT = Path(__file__).resolve().parents[2]


def python_blocks(text):
    # Consume every fenced block so literal <pre> examples inside ```text
    # never get mistaken for executable legacy HTML.
    matches = re.finditer(r"^```([^\n]*)\n(.*?)^```|<pre[^>]*>(.*?)</pre>", text, re.M | re.S)
    return [match[2] if match[1] is not None else unescape(re.sub(r"<[^>]+>", "", match[3]))
            for match in matches if match[1] is None or match[1].strip() == "python"]


def starter_code(reference, entrypoints=None, preserve_methods=None):
    """Keep node conversion scaffolding; hide all solution callables."""
    tree = ast.parse(reference)
    preserve_methods = preserve_methods or {}
    scaffolding = {"ListNode", "TreeNode", "Node", "from_list", "to_list", "from_pairs", "to_pairs",
                   "build_tree", "tree_from_list", "list_to_tree", "to_level", "to_levels", "from_level",
                   "build", "to_adj", "list_values", "tree_values", "linked_to_list", "list_to_linked"}
    candidates = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                  and node.name not in scaffolding and node.name != "main"
                  and (entrypoints is None or node.name in entrypoints)]
    if not candidates:
        return "# 在这里编写你的解法\n"
    for primary in candidates:
        if isinstance(primary, ast.ClassDef):
            for node in primary.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name not in preserve_methods.get(primary.name, []):
                    node.body = [ast.Raise(exc=ast.Call(func=ast.Name(id="NotImplementedError", ctx=ast.Load()), args=[], keywords=[]))]
        else:
            primary.body = [ast.Raise(exc=ast.Call(func=ast.Name(id="NotImplementedError", ctx=ast.Load()), args=[], keywords=[]))]
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + "\n"


def description(text, title, practice, question):
    match = re.match(r"\s*## 题目描述[^\n]*\n(.*?)(?=^## |^<!-- problem-statement:end -->|\Z)", text, re.M | re.S)
    if not match or len(match[1].strip()) < 180:
        raise ValueError(f"{question}: 缺少完整独立题面，不能用题解或代码自动代替")
    return match[1].strip()


def default_examples(tests):
    examples = []
    tree = ast.parse(tests)
    for statement in ast.walk(tree):
        if isinstance(statement, ast.Assert):
            test = statement.test
            if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                inputs, output = ast.unparse(test.left), ast.unparse(test.comparators[0])
            else:
                inputs, output = ast.unparse(test), "断言为 True"
        elif isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call) and "assert" in ast.unparse(statement.value.func):
            args = statement.value.args
            inputs = ast.unparse(args[0]) if args else ast.unparse(statement.value)
            output = ast.unparse(args[1]) if len(args) > 1 else "断言通过"
        else:
            continue
        examples.append({"name": f"默认测例 {len(examples)+1}", "input": inputs, "output": output, "origin": "handbook"})
        if len(examples) == 5:
            break
    if not examples:
        examples.append({"name": "默认测试场景", "input": "按测试编辑器中的操作序列执行", "output": "全部断言通过，无异常", "origin": "handbook"})
    return examples


def load_exercise(book, question):
    if not re.fullmatch(r"[a-z0-9-]+", book) or not re.fullmatch(r"[a-z0-9-]+", question):
        raise ValueError("Invalid question identifier")
    catalog = json.loads((ROOT / "public/content/catalog.json").read_text())
    handbook = next((entry for entry in catalog if book in (entry["id"], entry["slug"])), None)
    if not handbook:
        raise ValueError("Unknown handbook")
    files = list((ROOT / "content/handbooks" / handbook["slug"] / "questions").glob(f"**/{question}.md"))
    if len(files) != 1:
        raise ValueError("Question source not found")
    source = files[0].read_text()
    frontmatter, text = source.split("---", 2)[1:]
    title_match = re.search(r"^title: (.*)$", frontmatter, re.M)
    title = title_match[1].strip().strip('"') if title_match else question
    practice = re.search(r"^## 完整编程练习[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    implementation_text = practice[1] if practice else text
    if handbook["slug"].startswith("leetcode-"):
        # Follow-up variants often reuse the same function name with a different
        # signature. They must not replace the reference for the main problem.
        implementation_text = re.split(r"^## 追问[^\n]*\n", implementation_text, maxsplit=1, flags=re.M)[0]
    blocks = python_blocks(implementation_text)
    if not blocks:
        javascript = re.findall(r"^```javascript\n(.*?)^```", practice[1] if practice else text, re.M | re.S)
        if len(javascript) >= 2:
            reference, tests = javascript[:2]
            names = re.findall(r"^export (?:class|function) (\w+)", reference, re.M)
            starter = "import React from 'react';\n\n" + "\n\n".join(
                f"export class {name} {{ constructor() {{ throw new Error('请实现 {name}'); }} }}" if f"export class {name}" in reference else f"export function {name}() {{ throw new Error('请实现 {name}'); }}"
                for name in names
            ) + "\n"
            return {"id": question, "book": handbook["id"], "title": title, "language": "javascript",
                    "description": description(text, title, practice, question), "constraints": [],
                    "starter": starter, "reference": reference, "tests": tests,
                    "examples": [{"name": "默认测试场景", "input": "测试编辑器中的异步事件与操作序列", "output": "全部 Node.js 断言通过；服务端渲染输出符合约定", "origin": "handbook"}],
                    "source": {"label": "手册自定义练习", "url": None, "kind": "handbook"},
                    "note": "JavaScript / React 默认测试由本地 Node.js 执行。"}
        raise ValueError("This question has no executable implementation")
    # Framework fragments / intentionally partial examples are left editable,
    # with an explicit note rather than guessed executable tests.
    additional = []
    # Multi-part cards can define auxiliary interfaces in later blocks.
    for block in blocks[1:]:
        try:
            parsed = ast.parse(block)
        except SyntaxError:
            continue
        if all(isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in parsed.body):
            additional.append(block)
    module = ast.parse("\n\n".join([blocks[0], *additional]))
    if question in ("code-fw-miles", "code-fw-verl"):
        simple = re.search(r"^## 简单测试怎么写(.*?)(?=^## |\Z)", text, re.M | re.S)
        module = ast.parse(python_blocks(simple[1])[0])
    if question == "code-ppo-grpo-gspo":
        module = ast.parse("\n\n".join(block for block in blocks if "from trl import" not in block))
    guards = [node for node in module.body if isinstance(node, ast.If) and "__main__" in ast.unparse(node.test)]
    tests = ""
    if practice and len(blocks) >= 2:
        tests = blocks[1]
    elif guards:
        tests = "\n\n".join(ast.unparse(node) for guard in guards for node in guard.body
                              if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == "main"))
    if not tests:
        simple = re.search(r"^(?:## 简单测试怎么写|<h2>简单测试怎么写</h2>)(.*?)(?=^## |<h2>|\Z)", text, re.M | re.S)
        simple_blocks = python_blocks(simple[1]) if simple else []
        if simple_blocks:
            tests = simple_blocks[0]
        elif len(blocks) > 1 and not practice:
            # Separate test block, common in data-team cards.
            candidate = blocks[1]
            if re.search(r"\bassert\b|assert_", candidate) and not re.search(r"^class |^def ", candidate, re.M):
                tests = candidate
    module.body = [node for node in module.body if node not in guards]
    # Existing self-tests in the first block belong in the test editor.
    definitions, inline_tests = [], []
    for node in module.body:
        # Mark a boundary at the first check, then retain the complete scenario
        # (including setup) in the tests editor. Previously assignments before
        # an assert could swallow the only default test in data-team cards.
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign)) and not inline_tests:
            definitions.append(node)
        else:
            inline_tests.append(node)
    if not tests or tests.lstrip().startswith("#") and not any(isinstance(node, (ast.Assert, ast.Expr)) for node in ast.walk(ast.parse(tests))):
        if inline_tests:
            tests = ast.unparse(ast.Module(body=inline_tests, type_ignores=[]))
    if not tests and len(blocks) > 1:
        for candidate in blocks[1:]:
            if re.search(r"\bassert\b|assert_", candidate):
                tests = candidate
                break
    if not tests and inline_tests:
        tests = ast.unparse(ast.Module(body=inline_tests, type_ignores=[]))
    scope = json.loads((ROOT / "content/practice/runtime-scopes.json").read_text()).get(question, {})
    removed_definitions = set(scope.get("removeDefinitions", []))
    definitions = [node for node in definitions if getattr(node, "name", None) not in removed_definitions]
    reference = ast.unparse(ast.Module(body=definitions, type_ignores=[])) + "\n"
    if question in ("code-rmsnorm", "code-gae", "code-rope"):
        reference = "import torch\nimport torch.nn as nn\n\n" + reference
    legacy_tests = tests
    if "tests" in scope:
        tests = scope["tests"]
    tests = interview_tests(tests)
    prompt = description(text, title, practice, question)
    constraints = []
    source_info = {"label": "手册自定义练习", "url": None, "kind": "handbook"}
    examples = default_examples(tests) if tests else []
    if handbook["slug"].startswith("leetcode-"):
        slug = re.search(r"https://leetcode(?:\.com|\.cn)/problems/([^/\s]+)", frontmatter)[1]
        official = official_questions()[slug]
        constraints = official["constraints"]
        source_info = {"label": "LeetCode 官方公开示例", "url": official["url"], "kind": "leetcode", "retrievedAt": official["retrievedAt"]}
        examples = [{**example, "name": f"官方示例 {index}", "origin": "leetcode"} for index, example in enumerate(official["examples"], 1)]
        signature = official["signature"]
        entrypoint = signature.get("classname") or signature["name"]
        if entrypoint not in {getattr(node, "name", None) for node in definitions}:
            candidates = [node.name for node in definitions if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name not in ("ListNode", "TreeNode", "Node") and not node.name.startswith("_")]
            entrypoint = candidates[-1]
        tests = "# LeetCode 官方公开示例；check_example 负责构造节点、检查原地修改及合法的多解。\n" + "\n".join(
            f"assert check_example({slug!r}, {entrypoint!r}, {index})  # 官方示例 {index}"
            for index in range(1, len(examples)+1)
        ) + "\n"
    starter = starter_code(reference, scope.get("entrypoints"), scope.get("preserveMethods"))
    if question == "code-fw-miles":
        starter = "import torch\n\nratio = torch.tensor([1.5, 0.5])\nadvantages = torch.tensor([1., -1.])\neps_clip, eps_clip_high = 0.2, 0.28\n\n# 计算逐项损失\nclip_pg_losses1 = None\n"
    elif question == "code-fw-verl":
        starter = "import torch\nimport math\n\nresponse_mask = torch.tensor([[1., 0.], [1., 1.]])\nnegative_approx_kl = torch.tensor([[math.log(2), 99.], [math.log(2), math.log(2)]])\nlog_prob = torch.zeros(2, 2, requires_grad=True)\n\n# 计算保留 log_prob 梯度的序列重要性权重\nseq_importance_ratio = None\n"
    return {
        "id": question, "book": handbook["id"], "title": title, "language": "python", "starter": starter,
        "description": prompt, "constraints": constraints, "examples": examples, "source": source_info,
        "reference": reference, "tests": tests or "# 添加自己的测试，例如 assert ...\n",
        "legacyTests": legacy_tests,
        "note": "默认测试覆盖合法输入与有效边界，不要求额外的非法输入校验。" if tests else "原题含多个片段或没有独立测试，请自行补充接口与断言。",
    }
