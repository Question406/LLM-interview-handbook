def plan_reuse(prompt_length, matched_tokens, page_size=1, chunk_budget=4,
               need_last_logits=True):
    values = (prompt_length, matched_tokens, page_size, chunk_budget)
    if any(type(v) is not int for v in values):
        raise ValueError('integer parameters required')
    if prompt_length < 1 or not 0 <= matched_tokens <= prompt_length or min(page_size, chunk_budget) < 1:
        raise ValueError('length or budget')
    reusable = matched_tokens//page_size*page_size
    if need_last_logits and reusable == prompt_length:
        # KV alone is not the final hidden state/logits. Replay at least the last token.
        reusable = (prompt_length-1)//page_size*page_size
    chunks = []
    for start in range(reusable, prompt_length, chunk_budget):
        chunks.append((start, min(prompt_length, start+chunk_budget)))
    return reusable, tuple(chunks)

# === TESTS ===
def test():
    assert plan_reuse(8, 8, 4, 3) == (4, ((4, 7), (7, 8)))
    assert plan_reuse(8, 8, 4, 3, False) == (8, ())
    assert plan_reuse(9, 7, 4, 2) == (4, ((4, 6), (6, 8), (8, 9)))
    assert plan_reuse(1, 1) == (0, ((0, 1),))
    for n in range(1, 31):
        for hit in range(n+1):
            for page in (1, 2, 4, 8):
                reused, chunks = plan_reuse(n, hit, page, 3)
                assert reused <= hit and reused % page == 0 and reused < n
                covered = [i for start, end in chunks for i in range(start, end)]
                assert covered == list(range(reused, n))
                assert all(0 < end-start <= 3 for start, end in chunks)
    # Execute the chunk plan through the real model in an integration test in engine.py.

if __name__ == '__main__':
    test()
