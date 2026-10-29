---
id: us-llm-paper-stack
section: overview
order: 8
level: A
title: 面试前该精读的公开论文栈（Attention、GQA、InstructGPT、DPO、vLLM、Llama）
quick: "先精读 Attention、GQA、InstructGPT、DPO、vLLM 和 Llama 这六篇，分别掌握张量计算、省 KV、RLHF 目标、隐式奖励、分页缓存和工程取舍。每篇要能写出关键式并解释实现会在哪里失败，再按岗位补论文。"
tags:
  - Papers
  - 备考
  - OpenAI
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Direct Preference Optimization — Your Language Model is Secretly a Reward Model
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

这张卡把六篇基础论文串成一条准备路线：从 attention 和 KV，到 RLHF / DPO 的目标函数，再到分页推理和 Llama 工程取舍。每篇都准备关键式、实现约束和失败模式，下面列的是面试时要能讲清的内容。它与六周计划 `us-llm-re-prep` 配套，公司问法见 `us-prep-map`，细节可以沿对应 id 继续读。

## Attention 与 GQA

Vaswani 那篇先掌握 QKV 和缩放点积：因果 mask 要在 softmax 前打 $-\infty$，多头在 $d_k$ 上分。面试事故几乎全是 shape：softmax 沿错轴、没除 $\sqrt{d_k}$、逐 token 生成（decode） 位置用成 0。把这篇读成「张量契约」，然后去改带 bug 的实现，见 `openai-transformer-debug`、`coding-softmax-stable`。

GQA（Ainslie）：KV 头数 $H_{\mathrm{kv}} < H_q$，query 分组共享 KV。省的是 **KV cache 带宽和显存**，不是 FLOPs 故事的全部。MQA 是 $H_{\mathrm{kv}}=1$ 的极端。要能写 $KV \propto H_{\mathrm{kv}}\cdot T\cdot d$。Google / Meta 电面常问「为什么 GQA 不是免费」，见 `google-gqa-mqa`、`meta-llama-gqa`。和 RoPE、GQA 一起出现时，先钉 cache 再钉旋转，见 `meta-llama-rope`。

## InstructGPT 与 DPO

InstructGPT 先用 SFT 学指令格式，再让 RM 从回答对比中学习奖励，PPO 最大化奖励并减去相对 SFT 参考的 reverse KL。要能写清 KL 哪边是 $\pi_\theta$，以及 clip 对 old、KL 对 ref 不是同一项，见 `align-rlhf-kl`。论文自己写了 RM 会被 overoptimize、长度会涨。Hacking 见 `align-reward-hack`。RM 怎么训见 `align-reward-model`。

DPO：把「RM + reverse KL」解析成隐式奖励 $r=\beta\log(\pi/\pi_{\mathrm{ref}})+\beta\log Z(x)$，$Z$ 在 BT 差里消掉。要能从最优策略反解，而不是背 $-\log\sigma(\beta\Delta)$。$\beta$ 太大贴参考，太小 rejected 被打穿，见 `align-dpo`。IPO 把间隔钉在有限靶，见 `align-ipo`。有 pair 用 DPO；只有赞踩看 `align-kto`；在线 sampling 看 `align-grpo`、`align-online-dpo`。

读这两篇时盯 **目标函数和监控曲线**，不要盯「人类更喜欢」的表格数字。面试追的是你换 KL 方向或把 prompt 算进 损失（loss） 会怎样。

## vLLM 与 Llama

vLLM / PagedAttention：KV 按页分配，序列不必连续预留最大长度，才能做 iteration 级调度和前缀共享。Orca 解决请求级 batch 的队头阻塞；分页让变长 append 不把显存预留打满。面试要能说：块多大、前缀命中键含什么、水位怎么做准入，见 `sys-paged-attn`、`sys-prefix-cache`、`openai-continuous-batching`、`nvidia-paged-kv`。产品化排队见 `design-chat-serving`。

Llama 2 报告：预训练数据与 GQA、SFT / RLHF 聊天、上下文长度、安全。面试不当考古：把它当开源栈的默认假设（tokenizer、GQA、RoPE、对话模板）。细节见 `meta-llama-gqa`、`meta-llama3-tokenizer`。Llama 1 可以当预训练配方补充，聊天对齐仍以 2 的 RLHF 章和 InstructGPT 对照。

六篇之外按岗加一篇：NVIDIA 加 Megatron / FlashAttention；Anthropic 加 CAI；代码岗加 SWE-bench。加了也只精读失败模式，不要冲数量。

每篇一张纸：问题、关键式、shape 或复杂度、作者承认的失败、你若实现会踩的坑。合上论文能推 DPO 换元、能画 paged KV、能说明 GQA 省的是哪项显存，才算过。读了二十篇摘要、推导写不出，电面仍会暴露理解不足。

现场可以说「InstructGPT 的 KL 在当前策略上取」；不能说「我读过」然后方向写反。

## 追问

**只要 Llama 3 博客行不行？**
工程细节可以，推导仍要回到 Attention / DPO 原文。
**GRPO 要不要加进栈？**
推理岗要。先有 PPO/DPO 再读 DeepSeekMath 的 group baseline，见 `align-grpo`。
**vLLM 和 FlashAttention 哪篇优先？**
Serving / NVIDIA 先 vLLM 与分页；训练 kernel 岗先 FlashAttention，见 `google-flash-attention`、`nvidia-flash-attn`。
**和国内主题手册重复？**
那本按主题切；这里只收「美国轮次默认你会的那六篇」，问法更偏 debug 和系统。

## 相关题

- [[openai-dpo-loss]]：DPO 相对 PPO（InstructGPT 那套）砍掉了什么，把栈里这两篇连起来问。
- [[meta-llama-gqa]]：把栈里 GQA 和 Llama 两篇连起来问：70B 为什么用 8 个 KV head、decode 省在哪。
