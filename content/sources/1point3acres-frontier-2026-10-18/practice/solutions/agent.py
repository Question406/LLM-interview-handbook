import json


def validate_action(action):
    """检查模型输出的动作格式，不合法时抛 ValueError。"""
    if not isinstance(action, dict):
        raise ValueError("action must be a JSON object")
    if action.get("type") == "final":
        if not isinstance(action.get("answer"), str):
            raise ValueError("final answer must be a string")
        return
    if action.get("type") != "tool":
        raise ValueError("action type must be 'tool' or 'final'")
    if not isinstance(action.get("args"), dict):
        raise ValueError("tool args must be an object")
    call_id = action.get("id")
    if not isinstance(call_id, str) or not call_id:
        raise ValueError("tool call id must be a non-empty string")


def call_tool(tools, name, args):
    """执行白名单里的工具；工具自己抛出的异常转成失败结果，不中断循环。"""
    try:
        return {"ok": True, "value": tools[name](**args)}
    except Exception as error:
        return {"ok": False, "error": f"{type(error).__name__}: {error}"}


def run_agent(model, tools, goal, budget=8):
    """让 model 逐步提议动作，最多 budget 步；返回 (answer, messages)。

    同一个 call id 只执行一次工具：重复请求直接复用缓存结果，
    同一个 id 换了工具名或参数则拒绝。
    """
    if budget < 1:
        raise ValueError("budget must be at least 1")
    messages = [{"role": "user", "content": goal}]
    results_by_id = {}  # call id -> (调用签名, 结果)

    for _ in range(budget):
        action = model(list(messages))  # 传副本，模型改不了真实历史
        messages.append({"role": "assistant", "content": action})
        try:
            validate_action(action)
            if action["type"] == "final":
                return action["answer"], messages

            name, args, call_id = action.get("name"), action["args"], action["id"]
            if name not in tools:
                raise ValueError(f"unknown tool: {name!r}")
            # sort_keys 让参数顺序不同的同一调用得到同一个签名
            signature = json.dumps([name, args], sort_keys=True, allow_nan=False)
            if call_id in results_by_id:
                cached_signature, result = results_by_id[call_id]
                if cached_signature != signature:
                    raise ValueError(f"conflicting reuse of call id {call_id!r}")
            else:
                result = call_tool(tools, name, args)
                results_by_id[call_id] = (signature, result)
        except (ValueError, TypeError) as error:
            # 格式错误也作为 observation 回填，让模型下一步有机会改正
            result = {"ok": False, "error": str(error)}
        messages.append({"role": "tool", "content": result})

    raise RuntimeError("step budget exhausted")


def evaluate(cases, predict):
    """对固定案例严格比较 predict(question) == expected，返回准确率和失败列表。"""
    failures = []
    for index, (question, expected) in enumerate(cases):
        try:
            actual = predict(question)
        except Exception as error:
            actual = {"error": type(error).__name__}
        if actual != expected:
            failures.append((index, expected, actual))
    accuracy = 1 - len(failures) / len(cases) if cases else 0.0
    return {"accuracy": accuracy, "failures": failures}


def test():
    def scripted_model(actions):
        remaining = iter(actions)
        return lambda messages: next(remaining)

    # 同一个 id 请求两次，工具只执行一次
    calls = []

    def add(a, b):
        calls.append((a, b))
        return a + b

    add_call = {"type": "tool", "name": "add", "args": {"a": 2, "b": 3}, "id": "x"}
    model = scripted_model([add_call, add_call, {"type": "final", "answer": "5"}])
    answer, trace = run_agent(model, {"add": add}, "2+3")
    assert answer == "5"
    assert calls == [(2, 3)]
    assert trace[2] == {"role": "tool", "content": {"ok": True, "value": 5}}
    assert trace[4] == trace[2]

    # 同一个 id 换了参数：拒绝，并作为 observation 回填
    changed_call = dict(add_call, args={"a": 1, "b": 1})
    model = scripted_model([add_call, changed_call, {"type": "final", "answer": "done"}])
    answer, trace = run_agent(model, {"add": add}, "2+3")
    assert trace[4]["content"]["ok"] is False
    assert "conflicting" in trace[4]["content"]["error"]

    # 工具抛异常也变成失败结果，循环继续
    def broken():
        raise KeyError("missing")

    broken_call = {"type": "tool", "name": "broken", "args": {}, "id": "b"}
    model = scripted_model([broken_call, {"type": "final", "answer": "gave up"}])
    answer, trace = run_agent(model, {"broken": broken}, "x")
    assert answer == "gave up"
    assert trace[2]["content"]["error"].startswith("KeyError")

    # 未知工具一直重复，步数用完抛 RuntimeError
    unknown_call = {"type": "tool", "name": "nope", "args": {}, "id": "x"}
    try:
        run_agent(lambda messages: unknown_call, {}, "x", 2)
    except RuntimeError:
        pass
    else:
        raise AssertionError("budget should be exhausted")

    # 固定评测集
    assert evaluate([("a", "A"), ("b", "B")], str.upper)["accuracy"] == 1
    report = evaluate([("a", "A"), ("b", "x")], str.upper)
    assert report["accuracy"] == 0.5
    assert report["failures"] == [(1, "x", "B")]


if __name__ == "__main__":
    test()
