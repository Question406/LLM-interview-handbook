from collections import deque


def _validate(requests, slots):
    if slots < 1:
        raise ValueError("slots must be at least 1")
    ids = [request_id for request_id, _, _ in requests]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate request id")
    if any(max_new < 0 for _, _, max_new in requests):
        raise ValueError("max_new must be non-negative")


def generate(requests, model, slots, eos):
    """动态批处理解码：每轮把所有活跃请求的完整序列送进 model，各取一个 next token。

    requests 是 (request_id, prompt_tokens, max_new) 列表；返回 request_id -> 新生成的 token 列表。
    请求遇到 eos（不计入输出）或生成满 max_new 个 token 后立即腾出槽位，下一轮从队列补上。
    """
    _validate(requests, slots)
    waiting = deque((request_id, list(prompt), max_new) for request_id, prompt, max_new in requests)
    generated = {request_id: [] for request_id, _, _ in requests}
    active = []  # 每项是 (request_id, prompt, max_new)，和本轮 model 输出按下标一一对应

    while waiting or active:
        # 先用等待中的请求填满空槽；max_new 为 0 的请求直接完成，不占槽
        while waiting and len(active) < slots:
            request = waiting.popleft()
            if request[2] > 0:
                active.append(request)
        if not active:
            continue

        batch = [prompt + generated[request_id] for request_id, prompt, _ in active]
        next_tokens = model(batch)
        if len(next_tokens) != len(active):
            raise ValueError(f"model returned {len(next_tokens)} tokens for batch of {len(active)}")

        # 本轮结果全部按旧的 active 归属处理完，才进入下一轮补位
        still_running = []
        for (request_id, prompt, max_new), token in zip(active, next_tokens):
            if token == eos:
                continue
            generated[request_id].append(token)
            if len(generated[request_id]) < max_new:
                still_running.append((request_id, prompt, max_new))
        active = still_running

    return generated


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    def always_nine(batch):
        return [9] * len(batch)

    # 单槽：a 生成满 2 个后 b 才进来
    result = generate([("a", [], 2), ("b", [], 1)], always_nine, 1, -1)
    assert result == {"a": [9, 9], "b": [9]}

    # 以 1 开头的序列立刻遇到 EOS；max_new=0 的 c 不进入任何批次
    calls = []

    def eos_for_prompt_one(batch):
        calls.append(batch)
        return [-1 if sequence[0] == 1 else 7 for sequence in batch]

    result = generate([("a", [1], 5), ("b", [2], 2), ("c", [3], 0)], eos_for_prompt_one, 2, -1)
    assert result == {"a": [], "b": [7, 7], "c": []}
    assert len(calls) == 2
    assert calls[1] == [[2, 7]]  # 第二轮只剩 b，且带着它上一轮的输出

    # 非法输入
    expect_value_error(generate, [("a", [], 1)], always_nine, 0, -1)
    expect_value_error(generate, [("a", [], 1), ("a", [], 1)], always_nine, 1, -1)
    expect_value_error(generate, [("a", [], -1)], always_nine, 1, -1)
    expect_value_error(generate, [("a", [], 1)], lambda batch: [], 1, -1)


if __name__ == "__main__":
    test()
