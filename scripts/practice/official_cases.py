"""Adapt LeetCode's public example data to the handbook's Python interfaces.

Expected outputs come from the official example snapshot. Comparisons account
for contracts that permit multiple valid answers and for in-place APIs.
"""
import ast
from collections import Counter, deque
from copy import deepcopy
from functools import lru_cache
import inspect
import json
import math
from pathlib import Path
import re
from types import SimpleNamespace

DATA = Path(__file__).resolve().parents[2] / "content/practice/leetcode-public-examples.json"


@lru_cache(maxsize=1)
def official_questions():
    return json.loads(DATA.read_text())["questions"]


def literal(text):
    text = text.replace("\u200b", "").strip()
    try:
        return json.loads(text)
    except ValueError:
        text = re.sub(r"\bnull\b", "None", text)
        text = re.sub(r"\btrue\b", "True", text)
        text = re.sub(r"\bfalse\b", "False", text)
        text = re.sub(r"(?<=[\[,])\s*#\s*(?=[,\]])", '"#"', text)
        return ast.literal_eval(text)


def named_inputs(text):
    # Parse a call's keyword AST, never eval arbitrary source from the snapshot.
    text = text.replace("\u200b", "").replace("\n", " ")
    expression = ast.parse("dict(" + text + ")", mode="eval").body
    return {keyword.arg: literal(ast.get_source_segment("dict(" + text + ")", keyword.value))
            for keyword in expression.keywords}


def node(namespace, name, value):
    cls = namespace.get(name)
    if cls:
        return cls(value)
    return SimpleNamespace(val=value, next=None, left=None, right=None, random=None, neighbors=[])


def linked(values, namespace):
    nodes = [node(namespace, "ListNode", value) for value in values]
    for first, second in zip(nodes, nodes[1:]):
        first.next = second
    return (nodes[0] if nodes else None), nodes


def tree(values, namespace, name="TreeNode"):
    if not values or values[0] is None:
        return None
    root = node(namespace, name, values[0])
    pending, index = deque([root]), 1
    while pending and index < len(values):
        parent = pending.popleft()
        for side in ("left", "right"):
            if index >= len(values):
                break
            child = node(namespace, name, values[index]) if values[index] is not None else None
            setattr(parent, side, child)
            if child:
                pending.append(child)
            index += 1
    return root


def tree_values(root):
    out, pending = [], deque([root])
    seen = set()
    while pending:
        current = pending.popleft()
        if current is None:
            out.append(None)
            continue
        if id(current) in seen:
            raise AssertionError("Returned tree contains a cycle or shared node")
        seen.add(id(current))
        out.append(current.val)
        pending.extend((current.left, current.right))
    while out and out[-1] is None:
        out.pop()
    return out


def list_values(head):
    out, seen = [], set()
    while head is not None:
        if id(head) in seen:
            raise AssertionError("Returned list contains a cycle")
        seen.add(id(head))
        out.append(head.val)
        head = head.next
    return out


def find_node(root, value):
    if root is None or root.val == value:
        return root
    return find_node(root.left, value) or find_node(root.right, value)


def convert(value, parameter, namespace, inputs, converted):
    kind = parameter["type"]
    if parameter["name"] in ("p", "q") and "root" in converted:
        return find_node(converted["root"], value)
    if kind == "ListNode":
        head, nodes = linked(value, namespace)
        if "pos" in inputs and nodes and inputs["pos"] >= 0:
            nodes[-1].next = nodes[inputs["pos"]]
        return head
    if kind in ("ListNode[]", "list<ListNode>"):
        return [linked(values, namespace)[0] for values in value]
    if kind == "TreeNode":
        if parameter["name"] in ("p", "q") and "root" in converted:
            return find_node(converted["root"], value)
        return tree(value, namespace)
    return deepcopy(value)


def equal(actual, expected):
    if isinstance(actual, (int, float)) and not isinstance(actual, bool) and isinstance(expected, (int, float)):
        return math.isclose(actual, expected, rel_tol=1e-5, abs_tol=1e-5)
    if isinstance(expected, list):
        return isinstance(actual, (list, tuple)) and len(actual) == len(expected) and all(equal(a, b) for a, b in zip(actual, expected))
    return actual == expected


def validate_special(slug, actual, expected, inputs, args, namespace):
    if slug == "lowest-common-ancestor-of-a-binary-tree":
        return actual is find_node(args[0], expected)
    if slug in ("remove-element", "remove-duplicates-from-sorted-array", "remove-duplicates-from-sorted-array-ii"):
        expected_count, expected_prefix = expected
        prefix = args[0][:expected_count]
        return actual == expected_count and (sorted(prefix) == sorted(expected_prefix) if slug == "remove-element" else prefix == expected_prefix)
    if slug == "string-compression":
        from itertools import groupby
        chars = []
        for char, values in groupby(inputs["chars"]):
            count = sum(1 for _ in values)
            chars.extend([char] + (list(str(count)) if count > 1 else []))
        return actual == expected and args[0][:actual] == chars
    if slug == "construct-quad-tree":
        grid = inputs["grid"]
        def covers(current, x, y, width):
            if current is None:
                return False
            if current.isLeaf:
                return all(value == current.val for row in grid[x:x+width] for value in row[y:y+width])
            half = width // 2
            return half > 0 and all(covers(child, a, b, half) for child, a, b in (
                (current.topLeft, x, y), (current.topRight, x, y+half),
                (current.bottomLeft, x+half, y), (current.bottomRight, x+half, y+half)))
        return covers(actual, 0, 0, len(grid))
    if slug == "populating-next-right-pointers-in-each-node-ii":
        values, pending = [], deque([actual] if actual else [])
        while pending:
            level = [pending.popleft() for _ in range(len(pending))]
            current = level[0]
            for target in level:
                if current is not target:
                    return False
                values.append(current.val)
                current = current.next
                pending.extend(child for child in (target.left, target.right) if child is not None)
            if current is not None:
                return False
            values.append("#")
        return actual is args[0] and values == expected
    if slug in ("two-sum", "two-sum-ii-input-array-is-sorted"):
        return sorted(actual) == sorted(expected)
    if slug == "longest-palindromic-substring":
        return actual in inputs["s"] and actual == actual[::-1] and len(actual) == len(expected)
    if slug == "find-peak-element":
        nums = inputs["nums"]
        return isinstance(actual, int) and 0 <= actual < len(nums) and (actual == 0 or nums[actual] > nums[actual-1]) and (actual == len(nums)-1 or nums[actual] > nums[actual+1])
    if slug == "course-schedule-ii":
        if not expected:
            return actual == []
        return sorted(actual) == list(range(inputs["numCourses"])) and all(actual.index(before) < actual.index(after) for after, before in inputs["prerequisites"])
    if slug == "convert-sorted-array-to-binary-search-tree":
        def visit(root):
            if root is None:
                return [], 0
            left, lh = visit(root.left)
            right, rh = visit(root.right)
            if abs(lh-rh) > 1:
                raise AssertionError("BST is not height-balanced")
            return left + [root.val] + right, max(lh, rh) + 1
        return visit(actual)[0] == inputs["nums"]
    if slug == "group-anagrams":
        return sorted(sorted(group) for group in actual) == sorted(sorted(group) for group in expected)
    if slug == "find-the-difference-of-two-arrays":
        return len(actual) == 2 and all(sorted(a) == sorted(b) for a, b in zip(actual, expected))
    if slug in ("3sum", "letter-combinations-of-a-phone-number", "generate-parentheses", "combination-sum", "combinations", "permutations", "combination-sum-iii", "word-search-ii"):
        key = lambda value: json.dumps(value, sort_keys=True)
        return sorted(map(key, actual)) == sorted(map(key, expected))
    if slug == "find-k-pairs-with-smallest-sums":
        # Ties may pick different valid pairs, but multiplicities still matter.
        available = Counter((a, b) for a in inputs["nums1"] for b in inputs["nums2"])
        used = Counter(map(tuple, actual))
        return not (used - available) and sorted(map(sum, actual)) == sorted(map(sum, expected))
    return None


def check_example(namespace, slug, entrypoint, example_index):
    record = official_questions()[slug]
    sample = record["examples"][example_index - 1]
    signature = record["signature"]
    if slug in ("remove-element", "remove-duplicates-from-sorted-array", "remove-duplicates-from-sorted-array-ii"):
        count, rest = sample["output"].split(",", 1)
        expected_count = int(count)
        values = literal(rest.split("=", 1)[1].replace("_", '"_"'))
        expected = (expected_count, values[:expected_count])
    else:
        expected = literal(sample["output"])
    if signature.get("systemdesign"):
        decoder = json.JSONDecoder()
        operations, end = decoder.raw_decode(sample["input"])
        arguments = json.loads(sample["input"][end:].strip())
        constructor_args = [convert(value, parameter, namespace, {}, {}) for value, parameter in zip(arguments[0], signature["constructor"]["params"])]
        instance = namespace[entrypoint](*constructor_args)
        actual = [None]
        for operation, values, wanted in zip(operations[1:], arguments[1:], expected[1:]):
            result = getattr(instance, operation)(*values)
            if slug == "insert-delete-getrandom-o1" and operation == "getRandom":
                # Check against the current set by replaying prior operations.
                present = set()
                for prior, prior_values in zip(operations[1:len(actual)], arguments[1:len(actual)]):
                    if prior == "insert": present.add(prior_values[0])
                    elif prior == "remove": present.discard(prior_values[0])
                if result not in present:
                    raise AssertionError(f"getRandom returned {result!r}, outside {present!r}")
                result = wanted
            actual.append(result)
        valid = equal(actual, expected)
    else:
        inputs = named_inputs(sample["input"])
        if slug == "clone-graph":
            adjacency = inputs["adjList"]
            nodes = [node(namespace, "Node", index+1) for index in range(len(adjacency))]
            for current, neighbors in zip(nodes, adjacency):
                current.neighbors = [nodes[index-1] for index in neighbors]
            cloned = namespace[entrypoint](nodes[0] if nodes else None)
            seen, pending = {}, deque([cloned] if cloned else [])
            original_ids = {id(current) for current in nodes}
            while pending:
                current = pending.popleft()
                if current.val in seen:
                    continue
                if id(current) in original_ids:
                    raise AssertionError("Clone reused an original graph node")
                seen[current.val] = sorted(neighbor.val for neighbor in current.neighbors)
                pending.extend(current.neighbors)
            actual = [seen[value] for value in sorted(seen)]
            if actual != [sorted(neighbors) for neighbors in expected]:
                raise AssertionError(f"Expected {expected!r}, actual {actual!r}")
            return True
        if slug == "copy-list-with-random-pointer":
            pairs = inputs["head"]
            originals = [node(namespace, "Node", pair[0]) for pair in pairs]
            for index, (current, pair) in enumerate(zip(originals, pairs)):
                current.next = originals[index+1] if index+1 < len(originals) else None
                current.random = originals[pair[1]] if pair[1] is not None else None
            cloned = namespace[entrypoint](originals[0] if originals else None)
            clones, seen = [], set()
            while cloned:
                if id(cloned) in seen or any(cloned is original for original in originals):
                    raise AssertionError("Copy reused an original node or introduced a cycle")
                seen.add(id(cloned)); clones.append(cloned); cloned = cloned.next
            indices = {id(current): index for index, current in enumerate(clones)}
            actual = [[current.val, indices[id(current.random)] if current.random is not None else None] for current in clones]
            if actual != expected:
                raise AssertionError(f"Expected {expected!r}, actual {actual!r}")
            return True
        converted = {}
        for parameter in signature["params"]:
            converted[parameter["name"]] = convert(inputs[parameter["name"]], parameter, namespace, inputs, converted)
        function = namespace[entrypoint]
        if slug == "guess-number-higher-or-lower":
            namespace["PICK"] = inputs["pick"]
            namespace["guess"] = lambda value: (inputs["pick"] > value) - (inputs["pick"] < value)
        args = list(converted.values())[:len(inspect.signature(function).parameters)]
        actual = function(*args)
        valid = validate_special(slug, actual, expected, inputs, args, namespace)
        if valid is None:
            output = signature.get("output", {})
            if signature["return"]["type"] == "void" and output:
                actual = args[output["paramindex"]]
            if signature["return"]["type"] == "ListNode": actual = list_values(actual)
            elif signature["return"]["type"] == "TreeNode" or (slug == "flatten-binary-tree-to-linked-list"):
                actual = tree_values(actual)
            elif slug == "lowest-common-ancestor-of-a-binary-tree": actual = actual.val
            valid = equal(actual, expected)
    if not valid:
        raise AssertionError(f"Official example {example_index}\nInput: {sample['input']}\nExpected: {expected!r}\nActual:   {actual!r}")
    return True
