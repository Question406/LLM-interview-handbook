---
id: sys-tokenizer-same
section: systems
order: 71
level: B
title: 系统：rollout 和训练的 tokenizer 不一致，会坏在哪？
quick: "同一段文本可以变成两串不同的 id。生成用的边界、EOS 和奖励看到的字符串，必须和训练 gather logprob 用的 id 是同一套。 特殊 token 多一个或少一个，mask 会整段错位。"
tags:
  - Post-train
  - Tokenizer
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: verl 配置说明
    url: https://verl.readthedocs.io/en/latest/examples/config.html
    type: primary
---

## 题怎么来的

权重切分不对见 `sys-weight-remap`。这道是词表。推理引擎和训练框架各加载一次 tokenizer 时很容易不是同一个文件。按这个故障拟的。

## 会坏的对齐

logprob 是按 id 取的。生成侧的第 t 个 id 若和训练侧重编码之后的第 t 个 id 不同，gather 到的是别的 token 的概率，重要性采样比没有意义。字符串看起来一样，BPE 的边界可以不同，尤其是开头有没有空格、数字怎么切。

EOS、pad、bos 的 id 不同，mask 会把回答的头或尾切错。见 `sys-left-pad` 和 `sys-eos-mask`。

奖励若在解码后的字符串上做，解码也必须用生成时的那份 tokenizer。训练侧用另一份解码再送进沙箱，测试失败可能只是多了一个空格。

## 怎么固定

作业启动时打印词表大小和这几个特殊 id 的校验和，生成进程和训练进程都打。不一致就拒绝开始。不要在中途热更新 tokenizer 而不更新另一边。

chat 模板也算在里面。一边套了模板、一边用裸文本，id 从第一个 token 就不同。

## 代码

```python
def tokenizer_fingerprint(tok):
    names = ["eos_token", "pad_token", "bos_token"]
    return (tok.vocab_size, tuple(tok.convert_tokens_to_ids(getattr(tok, n)) for n in names))

def assert_same(train_tok, rollout_tok):
    if tokenizer_fingerprint(train_tok) != tokenizer_fingerprint(rollout_tok):
        raise RuntimeError("tokenizer mismatch")
```

## 追问

**词表一样、但添加了额外特殊 token？** 大小可以相同而 id 不同，也可以大小不同。校验和要覆盖特殊 token 的名字和 id，不只比 `vocab_size`。

## 相关题

- [[openai-tiktoken]]：特殊 token 单独查表、不进 merge，扩词表是加行，这些正是这里要校验的东西。
- [[meta-llama3-tokenizer]]：Llama 2 和 Llama 3 的 id 空间不同，是 tokenizer 不一致的典型来源。
- [[anthropic-bpe-tokenizer]]：手写 BPE 的往返不变量，从实现层面看 encode 的结果取决于哪些东西。
