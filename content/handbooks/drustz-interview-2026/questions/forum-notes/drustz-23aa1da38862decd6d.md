---
id: drustz-23aa1da38862decd6d
section: forum-notes
order: 138
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 3: Writing a Better Solution'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 3: Writing a Better Solution'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Part 3: Writing a Better Solution

Now, write your own version of the `tokenize` function. It needs to handle characters correctly even if they are not in the vocabulary.

### Requirements

- **Handle unknown characters:** Do not crash if a character is missing from the `vocab`.
- **Stay correct:** Ensure `tokenize` and `detokenize` logic holds up.
- **Use the UNK token:** Replace missing characters with `UNK: -1`.
- **Know the limits:** If the original text actually says "UNK", you won't be able to tell the difference between that and a real unknown character later. This is a known limitation.

### Key Challenges

- When should you stop adding letters to the `key`?
- How do you know if the current string you are building will **never** match a real token?
- Should you check if any word in the `vocab` starts with your current `key`?

### Helpful Context

- **Tokenization:** Breaking text into small chunks (tokens) and giving them numbers (IDs).
- **UNK:** Short for "UNKNOWN". It is a placeholder for data the model hasn't seen before.
- **Greedy Matching:** Taking the first match you find immediately. The original code does this.
- **Prefix Check:** You might need to check if your current string is the start (prefix) of any valid key. If it isn't, you know you won't find a match.

### Example Solution Approach

One way to solve this is to "look ahead." Check if the current `key` could possibly become a match later. If not, treat it as unknown.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""
        else:
            # Check: Does any key in vocab start with this string?
            if not any(k.startswith(key) for k in vocab.keys()):
                # No match is possible. Mark as UNK.
                tokens.append(vocab.get("UNK", -1))
                key = ""

    # Handle any leftover text
    if key:
        tokens.append(vocab.get("UNK", -1))

    return tokens
```



This is just one way to do it. Be ready to discuss why this works or if there is a better way.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
