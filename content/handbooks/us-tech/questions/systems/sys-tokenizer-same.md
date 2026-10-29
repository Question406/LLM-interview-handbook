---
id: sys-tokenizer-same
section: systems
order: 71
level: B
title: 系统：rollout 和训练的 tokenizer 不一致，会坏在哪？
quick: >-
  rollout 和训练必须使用一致的 tokenizer 与 chat 模板，否则同一文本可能被编码成不同 id，训练 gather 到的就不是
  sampling 动作的概率。EOS、pad、bos 不一致还会让 mask 错位，作业启动时应核对 vocabulary 与特殊 token。
tags:
  - Post-train
  - Tokenizer
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: verl 配置说明
    url: 'https://verl.readthedocs.io/en/latest/examples/config.html'
    type: primary
---

rollout 和训练的 tokenizer 不一致，会让训练算错 sampling 动作的概率，即使两边看到的字符串一样。比如开头空格不同、数字切分方式不同，都可能让同一段文本对应不同的 token id。

logprob 按 id 取值。如果生成侧第 t 个 id 与训练侧重编码后的第 t 个 id 不同，gather 就取到了另一个 token 的概率，importance sampling 比也失去意义。EOS、pad、bos 的 id 不一致，则会把回答头尾的 mask 切错，见 `sys-left-pad`、`sys-eos-mask`。

奖励也要保持一致。若在 decoding 字符串上跑沙箱，就用生成时同一份 tokenizer decoding；另一份 tokenizer 多解出一个空格，也可能让测试失败。chat 模板同样属于这套约定，一边套模板、一边用裸文本，可能从第一个 token 起就错开。

我会在作业启动时让生成与训练进程都打印 vocabulary 大小、特殊 id 及校验和，不一致就拒绝启动；中途更新 tokenizer，也要同时更新两边。这道题按推理和训练分别加载 tokenizer 时的常见故障拟成，权重切分错误另见 `sys-weight-remap`。

下面做一个简化的 vocabulary 和特殊 token 检查：

```python
def tokenizer_fingerprint(tok):
    names = ["eos_token", "pad_token", "bos_token"]
    return (
        tok.vocab_size,
        tuple(tok.convert_tokens_to_ids(getattr(tok, n)) for n in names),
    )


def assert_same(train_tok, rollout_tok):
    if tokenizer_fingerprint(train_tok) != tokenizer_fingerprint(rollout_tok):
        raise RuntimeError("tokenizer mismatch")
```

## 追问

**vocabulary 一样，只添加了特殊 token 呢？**
仍要核对名字和 id。大小相同也可能 id 不同，添加 token 也可能改变大小，只比较 `vocab_size` 不够。

## 相关题

- [[openai-tiktoken]]：特殊 token 单独查表、不进 merge，扩 vocabulary 是增加行，解释了为什么这些项也要校验。
- [[meta-llama3-tokenizer]]：Llama 2 与 Llama 3 的 id 空间不同，是一个具体例子。
- [[anthropic-bpe-tokenizer]]：手写 BPE 的往返不变量，帮助理解 encode 的结果依赖什么。
