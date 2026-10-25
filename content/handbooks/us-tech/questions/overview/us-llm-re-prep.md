---
id: us-llm-re-prep
section: overview
order: 7
level: S
title: 美国 Tech / frontier lab：LLM Research Engineer 六周怎么准备？
quick: "六周按产出安排：前两周练 debug 与张量计算，第三周补训练 / 推理系统，第四周推对齐目标，第五周练设计评测，第六周计时模拟。再按公司调整重点：OpenAI 多练改错，Anthropic 多练分层实现，NVIDIA 多练 kernel 和并行；地图见 `us-prep-map`。"
tags:
  - US Tech
  - Research Engineer
  - 备考
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Guide (Exponent)
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

这份六周计划按 RE 面试要展示的能力安排：先改对训练代码，再补 KV cache、并行和对齐，最后用设计与模拟面串起来。每天写代码或推导，周末用一篇论文解释本周实现，避免读完仍不会改 mask。Scientist / Applied 的准备差异见 `us-research-vs-applied`；轮次形态见 `us-loop-types`；精读清单见 `us-llm-paper-stack`。

## 六周骨架

**第 1-2 周：debug 与 ML coding。** 闭卷写 attention、causal mask、softmax 轴、$\sqrt{d_k}$、RoPE 偏移。再专门练「给一份能跑但错的 Transformer」：四个区间各一个 bug，改完加 KV cache。这是 OpenAI 电面的公开形态，见 `us-debug-vs-leetcode`、`openai-transformer-debug`。白板手撕 softmax / layernorm / 采样，见 `coding-softmax-stable`、`coding-layernorm`。Apple 会要你手写 MHA，见 `apple-mha-code`。不要一周只看论文不写 shape。

**第 3 周：系统。** 三维并行切哪一维、ZeRO 省什么、激活重计算换什么、paged attention 为什么能连续批。NVIDIA 岗把这周权重大于对齐。见 `sys-3d-parallel`、`sys-paged-attn`、`openai-continuous-batching`、`sys-prefix-cache`。自己画一张：输入预填充（prefill，即处理输入并建立缓存）影响首 token 延迟，decode 决定生成槽位的占用，KV 使用量决定能否接收新请求。能讲清「为什么请求级 batch 会队头阻塞」，这周过关。

**第 4 周：对齐。** 推一遍：反向 KL 为什么在 $\pi_\theta$ 这边、直接偏好优化（DPO） 隐式奖励、$Z(x)$ 为什么消掉、GRPO 少了哪张网。不要背损失名字。见 `align-rlhf-kl`、`align-dpo`、`align-grpo`、`align-reward-model`。顺手：钻奖励规则的空子、过度拒绝、LLM-as-judge 位置偏差，见 `align-reward-hack`、`align-over-refuse`、`align-llm-judge`。Anthropic 会把 CAI / 偏好 BT 问深，见 `align-cai`、`anthropic-pref-bt`。

**第 5 周：设计与评测。** 一道生产 检索增强生成（RAG） 或对话 serving：权限、引用、p95、前缀缓存、限流。见 `design-prod-rag`、`design-chat-serving`、`design-offline-eval`。代码助手 / 工具调用若目标是 Copilot 岗，加 `design-code-assistant`、`design-tool-prod`。评测讲污染和门禁，不要只报公开榜。

**第 6 周：串起来。** 两套模拟：45 分钟改 Transformer + 加 cache；45 分钟设计题限时画完约束。行为面用真实权衡，不要背原则。级别预期见 `us-leveling`。有 Meta onsite 再模拟 AI coding，见 `us-onsite-ai-coding`。论文栈过一遍，每篇只留「面试会问的那一页」。

## 按目标岗位调整节奏

阅读要和代码、shape 及推导一起推进。对齐章先掌握 GRPO / IPO / KTO，暂时不扩展到二十个算法缩写。Meta / Amazon / Microsoft 仍可能考中等 LeetCode，见 `us-debug-vs-leetcode`，需要保留这部分练习。项目叙述以论文或业务里真实的失败和取舍为材料，没做过的万卡训练经验不要补写。

公司倾斜：OpenAI 加一周 debug + 信息论；Anthropic 加分层实现和宪法；NVIDIA 加并行和 用 Nsight 分析性能；Apple / Amazon 加端侧或企业 RAG 约束。地图表见 `us-prep-map`。

节奏：工作日 60-90 分钟写代码或推式，周末 3 小时把本周主题连到一篇论文（第 2 周 Attention，第 3 周 vLLM，第 4 周 InstructGPT + DPO，第 5 周按目标岗选 RAG 或 serving）。模拟面要计时、出声、写 shape，不要只在心里过。

产出检查：能闭卷写带 cache 的一步 decode；能画 paged KV 准入；能从 基于人类反馈的强化学习（RLHF） 目标推到 DPO；能在白板上拒绝「再加一个大模型」并给出闸门。这四项可以用作六周结束时的验收。简历上的项目准备 8 分钟：问题、你改的假设、哪张表能证伪、上线约束。RE 岗会从论文追问到训练实现，见 `us-research-vs-applied`。

工作日清单（可打印）：今天写了哪一个 shape；今天推了哪一条目标；今天画了哪一张系统图。三天没有新代码就停阅读。电面头 10 分钟用来明确接口和测试，不要先重构。Anthropic 分层题先让 CRUD 过测再加 TTL，见 `us-loop-types`。统计轮补 Chernoff / 重复码，见 `us-prep-map` 里 OpenAI 那一行。

## 追问

**只有三周？**
砍设计广度，保 debug + KV + DPO 推导。系统只留 paged attention 和连续批。
**没有 GPU 经验？**
用小模型把 shape 和显存公式写对，NVIDIA 岗另补 kernel 阅读，不要装做过万卡。
**Scientist 岗也走这张表？**
前两周可缩短，把时间给消融和「结果反了信哪条假设」，见 `us-research-vs-applied`。
**要不要刷 Arena 分数故事？**
不要。要能讲偏差，见 `align-arena`。面试不看你有没有上过榜。
**每天读一篇 arXiv 行不行？**
不行。没有推导和代码的阅读，电面推不动 DPO 也不会改 mask。
**LeetCode 还要刷吗？**
Meta / Amazon / Microsoft 通用轮要中等题。lab RE 可以少刷 hard，但不能零，见 `us-debug-vs-leetcode`。
**模拟面找谁？**
同伴计时即可。没有官方内部平台时不要去找账号，见 `us-onsite-ai-coding`。

材料包就四样：一份带 bug 的 nanoGPT、一张并行/KV 草稿纸、DPO 推导半页、一道 RAG 或 serving 设计。每天只推进其中一样。论文精读按 `us-llm-paper-stack`，不要另开二十篇。

按目标级别验收时：初级把模块改对；中级主动提 SLO 和门禁；更高级定义评测和失败模式，见 `us-leveling`。跨级投也先保证 attention 写对。

六周结束时用 `us-prep-map` 过一遍公司列，缺的只补那一列，别重开新计划。
