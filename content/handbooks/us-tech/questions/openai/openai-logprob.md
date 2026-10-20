---
id: openai-logprob
section: openai
order: 24
level: A
title: OpenAI：logprobs、校准和温度，什么时候不该信模型的 p
quick: "API 给的是条件 token 对数概率，句级要沿 token 加和。预训练 GPT-4 报告里校准不错，基于人类反馈的强化学习（RLHF） 之后会过自信。采样温度和校准温度是两颗旋钮。事实、工具、长序列、截断采样时，不要把 $p$ 当成信念。"
tags:
  - OpenAI
  - Logprobs
  - Calibration
  - Temperature
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: GPT-4 Technical Report
    url: https://arxiv.org/abs/2303.08774
    type: primary
  - title: On Calibration of Modern Neural Networks
    url: https://arxiv.org/abs/1706.04599
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: OpenAI API logprobs
    url: https://platform.openai.com/docs/api-reference/chat/create
    type: primary
---

## 题怎么来的

Chat Completions 可以回 `logprobs` / `top_logprobs`。研究岗问的不是字段名，是：这个 $p$ 是什么分布上的数、校准过没有、什么时候能当置信度。GPT-4 报告有一张很有名的图：预训练模型在选择题上接近对角线，基于人类反馈的强化学习（RLHF） 之后点跑到对角线上方，过自信。InstructGPT 也写过偏好优化会改概率形态。熵正则见 `openai-entropy-l1`，KL 锚见 `openai-instructgpt-kl`。

## $p$ 是条件 token 概率，不是事实信念

模型在位置 $t$ 输出

$$
p_\theta(x_t\mid x_{1:t-1})=\mathrm{softmax}(z_t)_{x_t},\qquad
\log p(x_{1:T})=\sum_{t=1}^{T}\log p_\theta(x_t\mid x_{1:t-1}).
$$

API 给的是这项条件 logprob，外加可选的 top-$k$ 竞争 token。句子 / 答案的分数是和，不是最后一个 token 的 $p$。长度不同时要决定是否除以 $T$；不除会长答案在对数空间更负，乱比。分类用 输入提示（prompt） 末尾选项的 logprob，必须同一套 prompt 模板，否则在比格式不是在比答案。

温度出现两次，不要并成一个旋钮：

- **采样温度 $T$。** 画 $z/T$ 再 softmax 再抽样。$T\to 0$ 近 greedy；$T \gt 1$ 更平。API 的 logprobs 通常仍来自模型的原生分布（或按实现返回抽样用的那份），面试要问清楚「你读的 $p$ 有没有除过 $T$」。用 $T\neq 1$ 抽出来的 token，去解释「模型有多确信」，口径已经歪了。
- **校准温度。** Guo et al. 的 temperature scaling：在验证集上估一个 $T_{\mathrm{cal}}$，只改置信度、不改 argmax。这是事后校准，不是解码超参。

nucleus / top-$k$ 会把质量截断再重归一，截断后的 $p$ 更不能当校准概率。实现见 `coding-topk-nucleus`。投机解码用的是草稿和目标的 token 概率比，那是正确性耦合，不是校准，见 `openai-speculative-decoding`。

## 什么时候不该信

GPT-4 报告的校准图是选择题、有明确对错。换成开放生成、工具、长对话，这张图不能直接搬。我会主动列不该把 $p$ 当信念的场景：

1. **偏好优化之后。** RLHF / 直接偏好优化（DPO） 改的是「标注员更喜欢哪句」，不是贝叶斯后验。过自信是默认假设，除非你在新验证集上重画可靠性图。
2. **用最大 token $p$ 当事实置信度。** 流畅的错句可以 token 级 $p$ 很高。「我不知道」可能被训成低 $p$ 的拒答。事实要用检索或外部评测，不要用生成 logprob。
3. **长序列累加。** 逐步条件概率相乘，早期一个错 token 后面的 $p$ 仍可以看起来「合理」，因为它条件在错误前缀上。
4. **工具 / 检索增强生成（RAG）。** 模型给的是「在当前上下文里下一个 token 像什么」，不是「这个 API 返回值在世界上为真」。工具该不该调，见 `openai-function-calling`。
5. **$T\neq 1$ 或 top-$p$ 截断后再读 $p$。** 你改了抽样，没改世界。

可靠性图怎么画：把预测 $p$ 分组统计，横轴平均 $p$，纵轴经验准确率。ECE 是桶内 $|{\mathrm{acc}}-\mathrm{conf}|$ 的加权和。选择题可以这么做；开放生成要先定义「对」，否则校准数字是空的。

需要排序（哪个续写更像）时 logprob 有用；需要「这事是不是真的」时不够。内部 eval 仍走 `openai-eval-harness`，不要用平均 logprob 当能力榜。

## 追问

- **序列 logprob 要不要除以长度？** 比「哪句更像模型」时常除；比「整句联合概率」时不除。两种比法不要混在一张表。
- **温度调小是不是更校准？** 不是。$T\to 0$ 只是更尖，对错都更自信。校准要单独的 $T_{\mathrm{cal}}$ 或其它后处理。
- **top_logprobs 能当不确定度吗？** 可以看到竞争词。质量若集中在同义改写上，不是事实不确定；集中在互斥答案上，才有一点信号。
- **DPO 之后 $p$ 还能当 奖励模型（RM） 吗？** 隐式奖励是 log 比，尺度和绝对 $p$ 都不是现成 RM，见 `openai-dpo-loss`。

## 相关题

- [[coding-token-logprob]]：动手写从 logits 取 token logprob：错一位对齐、除温度、切块省显存。
