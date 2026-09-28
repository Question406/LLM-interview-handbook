---
id: meta-llama-guard
section: meta
order: 17
level: A
title: Meta：Llama Guard 当独立安全分类器，和基座对齐怎么分工
quick: >-
  Guard 是另训的 Llama 分类器，不是把 chat 模型的拒答头拆出来。它读「策略 + 对话」，生成 safe / unsafe 和类别；分数取首
  token 概率。基座负责有用且尽量不伤人；Guard 做输入输出闸门，策略可换、可独立升级。
tags:
  - Meta
  - Llama
  - Safety
  - Llama Guard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama Guard — LLM-based Input-Output Safeguard for Human-AI Conversations
    url: https://arxiv.org/abs/2312.06674
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: PurpleLlama Llama Guard
    url: https://github.com/meta-llama/PurpleLlama
    type: primary
  - title: Llama Guard 3 8B model card
    url: https://huggingface.co/meta-llama/Llama-Guard-3-8B
    type: primary
---

Llama / 安全 / 推理平台岗会问：为什么不把安全完全做进 chat 模型。公开答案是 **两套模型、两种损失、两种发布节奏**。Llama Guard 论文（2023）是 Llama 2-7B 指令微调；Llama Guard 3 挂在 Llama 3.1-8B 上，Herd 论文建议和 3.1 一起部署。不要把 Prompt Guard、Code Shield 和 Guard 混成一个 checkpoint。

## Guard 实际在算什么

它还是因果 LM，但任务是分类。输入里带：**风险 taxonomy 的明文说明**、要判的是 user prompt 还是 assistant response、对话内容。输出约定：先一个 token `safe` 或 `unsafe`；若 unsafe，下一行列出违反的类别编号。二分类分数读**第一个生成 token** 的概率，再设阈值。不是另接一个 $[D, 2]$ 线性头。好处是换策略、换输出格式时，可以用同一套指令微调或 zero-shot / few-shot 改 prompt。

论文把 **prompt 分类** 和 **response 分类** 拆成两种指令。同一句「怎么做炸弹」：用户侧是求助/攻击，模型侧是教了还是拒了，标签可以不同。一个 chat 模型的 RLHF 拒答，分不清这两层。

taxonomy 可替换：训练时做过丢类别、打乱编号的增强，所以推理时只留你关心的几条策略，模型应只按留下的条判。现场别保证 zero-shot 换政策无损，要在你的政策测试集上画 PR。公开对比过 OpenAI Moderation、ToxicChat；taxonomy 对不齐，数字只能当量级。

Llama Guard 3：对齐 MLCommons 危害类型，另加 Code Interpreter Abuse，覆盖多语言和工具调用。Herd 论文写系统级安全靠它抬，也可能增加对良性请求的误拒。面试主动报 **FPR / 拒答率**，不要只报「更安全」。

## 和基座对齐的分工

我会画三条线：

1. **预训练 / SFT / DPO 里的安全。** 基座要学会拒绝、要有用、要不过度拒答。这是行为对齐，损失是 next-token 或偏好。换产品政策意味着重训或再对齐，贵、慢、还可能伤能力。合成 SFT 也会把拒答风格洗进去，见 `meta-synth-sft`。
2. **Guard。** 独立 7B/8B，专判输入输出。策略在 prompt 里，权重点可以独立发版。主模型一次生成，Guard 再跑一次前向（或只对高风险流量开）。延迟和成本是 $8\mathrm{B}$ 的 prefill，不是「免费的安全层」。
3. **系统策略。** 正则、工具白名单、检索过滤。Guard 是 LLM 闸门，不是唯一闸门。

错法：把 Guard 的生成文本当 chat 回复，或把 chat 模型的「我不能帮你」当成分类分数。前者格式一漂阈值就坏；后者没有稳定的 unsafe 概率。另一个错法：只拦输出、不拦输入：越狱 prompt 已经进了上下文，主模型可能在内部推理里被带偏，再靠输出分类补就晚了。

分数怎么用：首 token $\log p(\texttt{unsafe})$ 设阈值。要按类别拦，用 1-vs-all：每次 prompt 只放一个类别，看该次 unsafe 概率。吞吐会乘上类别数，生产上常先二分类再对 unsafe 做多标签解码。

## 部署时我会主动说的坑

Guard 的 chat 模板必须和训练一致，多一个 `begin_of_text` 或角色头，首 token 分布就偏。分类要覆盖整段 user/assistant，不是只看最后一句。和 RAG / 工具：要把检索片段、代码执行结果一并送进 response 分类，否则模型「引用了有害段落」会漏。

和评测：安全数字很容易自污染：把公开 jailbreak 写进 SFT 再在同一套上报表。Guard 的测试集要和训练 taxonomy 对齐，并留一块政策外 holdout。能力评测见 `meta-llama-eval`，别用 MMLU 证明安全。Guard 和基座可以不同步发版：基座一周升一次，政策变了只换 Guard prompt 或只微调 8B，这才叫独立分类器：政策变了不必重训基座。

## 追问

- **为什么不在基座上加一个分类头？** 能。失去的是「策略当文本、可 zero-shot 改 taxonomy」。独立模型还能对多个基座复用同一闸门。
- **和 RLHF 拒答重复吗？** 互补。RLHF 改生成分布；Guard 是事前/事后二分类，阈值可调，不必每次改政策都重训 405B。
- **延迟怎么办？** 短 prompt 上 8B prefill 往往可接受；长上下文要量化、截断分类窗口，或只对触发词打满窗。不要默认为零成本。
- **误拒怎么收？** 调阈值、few-shot 加硬负例、对产品政策微调。Herd 已经警告 Guard 3 可能抬 FPR。
- **和 Prompt Guard / Code Shield 是一个模型吗？** 不是。Prompt Guard 拦注入，Code Shield 拦不安全代码；Llama Guard 是对话危害分类。不要绑成一个 checkpoint。
