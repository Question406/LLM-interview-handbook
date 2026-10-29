---
id: drustz-a23abb5a4cdab45697
section: collections
order: 13
level: A
title: Anthropic 题库（爬取全量） · ML Coding 题
quick: 作者文档章节 · Anthropic 题库（爬取全量） · ML Coding 题
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md
    type: primary
---
## ML Coding 题

### Agent Coding 轮：用 Claude API 搭 agent loop（tool use 答股票价格问题）
*medium · 频率: high (4+ reports, 2026 Q2 上升) · 2026-05*

SWE/RE 技术店面 track 之一：'写代码把 LLM 当 building block'，实现 Claude agent loop——定义 tools、解析模型 tool call、执行并回传结果、循环到回答完成。Telegram 镜像具体版本：'Claude agent loop，用 tools 回答关于股票价格的问题'。相关帖：interview thread 1178346 'Technical Phone Screen: LLM Agent Coding Interview'（2026-05）、bbs thread 1172086 '人类学Anthropic求助 Agent Interview题目'（Agents Interview 测试 writing code with LLMs as a building block + prompting to create an agent）、interview thread 1141199 'RE Interview: Agent Coding and Coding Design Topics'。

**解法**: 熟练手写 Anthropic messages API 的 tool use 协议：tools schema、stop_reason=='tool_use' 分支、tool_result 回传、while 循环+最大步数保护、错误处理（tool 抛异常回传 error 让模型重试）；准备讨论 prompt 设计、防hallucination（强制引用 tool 结果）、并行 tool call。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/thread/1178346&gt;)

### RL Fundamentals 轮：debug GRPO training loop + 解释 ratio ≠ 1（RE 高频新题）
*hard · 频率: medium (3+ reports, 2026 Q2 新增) · 2026-05*

给一份简化的 GRPO（on-policy RLHF）训练 step 实现，含 3 个埋好的 bug，常见 bug 类型：log-prob 计算错误（未对齐 autoregressive shift）、loss/KL 里 token masking 错误、advantage normalization 错误（组内奖励全相同时除零/无信号）、新旧 policy 混用（rollout 与 update 的 policy 不一致）。每个 bug 要求给出检测方法+具体修复，不能只点名。核心追问：明明设计上严格 on-policy，为什么 importance ratio = exp(log πθ − log  $π_{old}$ ) 不等于 1？要求设计判别实验区分'设计内偏差'（推理引擎与训练器 forward 路径不同、bf16/fp32 数值精度、每个 rollout batch 走多次 optimizer step）与真 bug。Follow-up：clipped surrogate 如何防崩、组内奖励全相同怎么办、engine-to-trainer log-prob 修正、process vs outcome supervision、KL penalty 放 reward 里还是 loss 里的 trade-off。应主动澄清：reward 类型、每 batch optimizer 步数、生成与打分是否同一 forward 路径、sampling温度/top-p、KL 实现、数值精度。1p3a 对应帖：interview thread 1167043 'RL Fundamental Interview: Code, Design, and Configuration'、1166898、bbs thread 1167940。

**解法**: prachub 页面给了完整评分维度（见 detail）。ratio≠1 三大合法原因：多次 minibatch update 后 πθ 已漂移、vLLM sampling与 HF 训练 forward 的 kernel/精度差异、bf16 舍入；判别实验：同一 checkpoint 用训练器重算生成 log-prob 对比、fp32 复算、第一次 optimizer step 前检查 ratio 是否恰为 1。

来源: &lt;[来源链接](https://prachub.com/interview-questions/debug-a-grpo-training-loop-and-explain-ratios&gt;)

### Coding & Design：Weighted Data Batcher with Checkpointing（research track，MLE/RE 向）
*hard · 频率: medium (2026-05 last asked) · 2026-05*

55 min，research-track 1-of-N coding-and-design 题，难度标 hard。构建 DataBatcher：从 DataRegistry 按权resampling生成 batch，要求确定性的 save/resume——用 offset 参数实现 checkpoint 后精确恢复sampling流。标签：sampling/checkpointing/iterator/Python/MLE。Last asked 2026-05，frequency: Medium。与候选人 mid-training 数据管线背景高度相关。相关：interview thread 1162037 'Onsite Coding and Design Interview for Machine Learning Role'。

**解法**: 我的推断：seeded RNG + 可序列化状态（rng state + per-source offset/epoch 计数）；确定性恢复的关键是把随机流做成 offset 可重放（如 counter-based RNG 或 rng.getstate/setstate）；讨论加权sampling（别名法 vs 前缀和二分）、数据源动态增删对确定性的影响、多 worker 分片。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/company/anthropic/coding-design-data-batcher&gt;)

### Prompting & Engineering with LLMs 轮（55 min Colab）
*medium · 频率: medium (3+ reports) · 2026-02*

55 分钟 Google Meet，在 Colab 里做 prompting and engineering with LLMs：用 prompt 工程解决任务（评估/迭代 prompt、处理模型输出）。是 RE/RS 和 MLE 店面四选一 track 之一。一位 MLE 候选人路径：OA（Recipe 题）→ 55-min 'Prompting and Engineering with LLMs' 店面。interview thread 1147266 'Anthropic Interview Experience: 55-Minute Google Meet Coding Challenge on LLM Prompting'。

**解法**: 我的推断：典型形态是给一个分类/抽取任务和小数据集，要求写 prompt+评估 loop，迭代提升准确率；准备结构化输出解析、few-shot 选择、失败案例分析话术。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/thread/1147266&gt;)

### Take-home 汇总：RS 4 小时作业；Accelerator 团队 4 小时多核模拟器（performance 向）
*hard · 频率: medium (3 reports) · 2026-01*

(1) RS（Research Scientist）take-home assignment：4 小时，非 OA 形式（bbs thread 1103094 '请问Anthropic的take home assignment'）。(2) Accelerator/performance 团队 take-home：4 小时，Python multi-core simulator（多核处理器模拟器），发帖人建议提前复习 VLIW 和 pointer 概念（bbs thread 1135727 'Anthropic 挂经'）。(3) 题库'Other'类还有 interpretability / ML experiments / GPU performance analysis 类 take-home（题库页可见分类，正文需登录）。

**解法**: 多核模拟器（我的推断）：实现指令级模拟（VLIW bundle 并行发射、内存/指针语义、核间同步），先写单核正确版本再扩展；时间盒 4 小时，优先正确性+清晰 README。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1135727-1-1.html&gt;)

### RE/MLE 轨道 ML 轮主题（聚合来源，置信度中等）
*hard · 频率: 聚合站信息（部分与 Glassdoor 碎片交叉） · 2026*

多个聚合指南（finalroundai/jobright/linkjob 等，非第一人称，作交叉参考）：RE 轨道 = SWE 流程 + ML 深挖轮，coding OA 与 SWE 相同（题目领域会提前邮件告知）。ML 轮内容：从零实现 Transformer 组件（multi-head attention）、BPE、sampling（sampling）；调试损坏的训练代码；手推梯度；MoE/Mamba/attention 变体的数学推导；scaling laws 与小规模实验外推大模型性能的讨论。ML 理论样题："Explain the architecture of a Transformer model"、"How would you optimize a model for inference latency?"（量化/distillation/硬件加速）、"Design a distributed training pipeline for a LLM. How would you handle fault tolerance?"。Research Scientist 轨道额外：research presentation（30-45min 报告 + 30min Q&A，深挖假设/方法/局限）、48 小时 take-home（问题集或小数据集，评审重 reasoning 过程——写清试了什么、为何失败、有更多时间会做什么，胜过干净但缺推理的报告）。Glassdoor 碎片：有候选人收到 QKV attention 预习材料但面试官问的是 attention-free transformers。

**解法**: 对 post-training 背景：把 attention/BPE/sampling三件套练到 20 分钟内裸写无 bug；准备一个 45 分钟版本的自己代表作 research talk，预演'假设-证据-局限-下一步'追问。

来源: &lt;[来源链接](https://www.finalroundai.com/blog/anthropic-interview-process&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
