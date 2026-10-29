---
id: drustz-33d98b9bdbd52a3919
section: forum-notes
order: 136
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 1: Understanding the Code'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 1: Understanding the Code'
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
## Part 1: Understanding the Code

You are given two functions: `tokenize` and `detokenize`. Your goal is to:

- **Read the code** and understand what it does.
- **Find the bugs** or logic errors in the tokenization process.

```python
def tokenize(text: str, vocab: dict):
    tokens = []
    key = ""
    for i in range(len(text)):
        key += text[i]
        if key in vocab:
            tokens.append(vocab[key])
            key = ""
    return tokens


def detokenize(tokens, vocab: dict):
    text = ""
    reversed_vocab = {value: key for key, value in vocab.items()}
    for token in tokens:
        text += reversed_vocab[token]
    return text
```



**Example:**

```python
vocab = {"a": 1, "b": 2, "cd": 3}

tokens = tokenize("acdebe", vocab)
result = detokenize(tokens, vocab)
```



### Your Task

- **Explain** how this code works to your interviewer.
- **Identify** the problems with this logic.
- **Explain** when this code will fail.

### Questions to Ask Yourself

- How does the code choose which token to pick?
- What happens if the text has a letter that is NOT in the `vocab`?
- What happens to the `key` variable if it never finds a match?
- Does this code pick the best match, or just the first one it sees?

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
