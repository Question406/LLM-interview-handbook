---
id: openai-logprob
section: openai
order: 24
level: A
title: OpenAI：logprobs、calibration 和温度，什么时候不该信模型的 p
quick: >-
  logprob 是给定前缀时下一个 token 的条件概率，整句分数要把各 token 的 logprob
  加起来。它能比较续写，却不能直接证明事实为真；偏好优化、温度与截断 sampling 后，置信度还要在独立验证集重新 calibration。
tags:
  - OpenAI
  - Logprobs
  - Calibration
  - Temperature
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: GPT-4 Technical Report
    url: 'https://arxiv.org/abs/2303.08774'
    type: primary
  - title: On Calibration of Modern Neural Networks
    url: 'https://arxiv.org/abs/1706.04599'
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: OpenAI API logprobs
    url: 'https://platform.openai.com/docs/api-reference/chat/create'
    type: primary
---

## 可以这样回答

API 的 `logprobs` / `top_logprobs` 说明某个 token 在当前前缀后有多像模型会写的内容，不能直接当事实可信度。比如早期已经生成了一个错误前提，后面的续写仍可能很流畅、概率很高，因为概率条件里已经包含那个错误。

GPT-4 报告在选择题上显示预训练模型 calibration 较好，RLHF 后出现过自信；InstructGPT 也讨论偏好优化会改变概率形态。换到开放回答、工具和长对话，需要重新定义对错并验证，不能沿用选择题结论。

## 技术备查

API 的 `logprobs` / `top_logprobs` 说明某个 token 在当前前缀后有多像模型会写的内容，不能直接当事实可信度。比如早期已经生成了一个错误前提，后面的续写仍可能很流畅、概率很高，因为概率条件里已经包含那个错误。

GPT-4 报告在选择题上显示预训练模型 calibration 较好，RLHF 后出现过自信；InstructGPT 也讨论偏好优化会改变概率形态。换到开放回答、工具和长对话，需要重新定义对错并验证，不能沿用选择题结论。

## 先确认读到的概率是什么

模型在位置 $t$ 输出

$$
p_\theta(x_t\mid x_{1:t-1})=\mathrm{softmax}(z_t)_{x_t},\qquad
\log p(x_{1:T})=\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{1:t-1}).
$$

API 给的是这项条件 logprob，外加可选的 top-$k$ 竞争 token。句子 / 答案的分数是和，不是最后一个 token 的 $p$。长度不同时要决定是否除以 $T$；不除会长答案在对数空间更负，乱比。分类用 prompt 末尾选项的 logprob，必须同一套 prompt 模板，否则在比格式不是在比答案。

sampling 温度 $T$ 先把 logits 变成 $z/T$ 再 softmax 抽样，$T\to 0$ 接近 greedy，$T \gt 1$ 更平。API 可能返回原生分布，也可能按实现返回 sampling 分布，先确认读到的 $p$ 是否除过 $T$；尤其 $T\neq 1$ 时，sampling probability definition 会影响解释。

Guo et al. 的 calibration 温度则在验证集估计 $T_{\mathrm{cal}}$，只改置信度、不改 argmax。它是事后 calibration，与控制生成随机性的温度分开调。

nucleus / top-$k$ 会把质量截断再重归一，截断后的 $p$ 更不能当 calibration 概率。实现见 `coding-topk-nucleus`。speculative decoding 用的是草稿和目标的 token 概率比，那是正确性耦合，不是 calibration，见 `openai-speculative-decoding`。

## 再验证它能否表示置信度

RLHF / DPO 优化标注偏好，不能当贝叶斯后验，先在新验证集画可靠性图。高概率的错句和低概率的“我不知道”都可能存在，事实仍需检索或外部评测。工具、RAG 的 token 概率也无法验证 API 结果是否为真，工具选择需要 `openai-function-calling` 的专门评测。

可靠性图怎么画：把预测 $p$ 分组统计，横轴平均 $p$，纵轴经验准确率。ECE 是桶内 $|{\mathrm{acc}}-\mathrm{conf}|$ 的加权和。选择题可以这么做；开放生成要先定义「对」，否则 calibration 数字是空的。

需要排序（哪个续写更像）时 logprob 有用；需要「这事是不是真的」时不够。内部 eval 仍走 `openai-eval-harness`，不要用平均 logprob 当能力榜。

相关：`openai-entropy-l1`、`openai-instructgpt-kl`

## 追问

**序列 logprob 要不要除以长度？**
比「哪句更像模型」时常除；比「整句联合概率」时不除。两种比法不要混在一张表。
**温度调小是不是更 calibration？**
不是。$T\to 0$ 只是更尖，对错都更自信。calibration 要单独的 $T_{\mathrm{cal}}$ 或其它后处理。
**top_logprobs 能当不确定度吗？**
可以看到竞争词。质量若集中在同义改写上，不是事实不确定；集中在互斥答案上，才有一点信号。
**DPO 之后 $p$ 还能当 reward model（RM） 吗？**
隐式奖励是 log 比，尺度和绝对 $p$ 都不是现成 RM，见 `openai-dpo-loss`。

## 相关题

- [[coding-token-logprob]]：动手写从 logits 取 token logprob：错一位对齐、除温度、切块省显存。
