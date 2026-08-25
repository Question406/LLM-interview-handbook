---
id: us-agent-prep
section: overview
order: 10
level: S
title: 美国 Tech：Agent / RL 面准备轨迹、工具与评测，不要只背 ReAct
quick: >-
  ReAct 四个字母不够撑一轮。评委要听轨迹怎么记、奖励落在终局还是工具事件、评测环境怎么冻、预算谁来停。
  编码是带超时的工具循环；对齐是稀疏信用和 grader 会被刷。总表见 `us-llm-re-prep`。
tags:
  - US Tech
  - Agent
  - RL
  - 备考
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: WebArena — A Realistic Web Environment for Building Autonomous Agents
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
  - title: Reinforcement fine-tuning (OpenAI)
    url: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning
    type: primary
---

投 OpenAI / Anthropic / Microsoft Copilot / Amazon Bedrock Agents，agent 轮经常混在系统设计或对齐里，很少是「请默写 Thought-Action-Observation」。ReAct 只是日志格式。评委要看你能不能把循环放在宿主：schema、权限、预算、确认、trace。岗位分界见 `us-research-vs-applied`；轮次形态见 `us-loop-types`。

## 不要只背名词，要能画一条轨迹

准备时自己写 30 行伪代码：模型出结构化调用 → 宿主校验 schema 与权限 → 执行 → 截断结果当 data → 再进模型。超时、幂等、不可逆确认，见 `design-tool-prod`、`design-agent-harness`。浏览器再加选择器脆弱和沙箱，见 `design-browser-agent`。语音再加打断和 ASR 传播，见 `design-voice-agent`。预算见底降级到无工具，见 `design-agent-budget`。

轨迹字段要能列出来：时间戳、工具名、参数、返回哈希、剩余步数 / 美元、用户是否确认。没有这些，RL 也做不了，事故也复盘不了。面试被问「多 agent 好不好」时，先说单循环没稳之前不要乘故障，见 `align-agent-rl`。

编码练习：解析 tool JSON、写 budget.charge、对 tool 结果做截断和角色标记。OpenAI 电面仍可能是 Transformer debug，agent 岗只是 onsite 多一道设计；不要用 agent 名词替代 `us-debug-vs-leetcode`。

## RL：奖什么比叫什么算法重要

稀疏终局 0/1、组相对 baseline、过程奖会刷调用次数，这三句要比「我们用 PPO」先说，见 `align-grpo`、`align-tool-rl`、`align-process-reward`。OpenAI RFT / RLVR：grader 可验证、eval 先于训练、验收 grader 分开，见 `align-rft`。RM 当工具好坏的打分器，会走 Gao 的过优化曲线，见 `align-overopt-rm`。隐藏思考不要当标签，见 `align-cot-leak`。

可扩展监督如果被问到：weak-to-strong 是弱老师强学生；debate 是弱裁判看质询；CAI 是原则替代逐条 harmless 标注。能用三句话分开，见 `align-weak-strong`、`align-debate`、`align-cai`。不要宣称生产已靠辩论对齐。

## 评测：功能成功，环境要冻

WebArena 的教训是：真实网页、功能谓词、一次 rollout 不可比。准备一张表：任务图节点、冻结模拟器 sha、温度与采样次数、成本 USD、政策违规。平台共性见 `design-eval-platform`；agent 专用见 `design-eval-agent`。公开榜当参考，污染纪律见 `align-eval-contam`。红队把恶意页面文案和图上指令单列，见 `align-red-team`、`align-mm-harm`。

公司倾斜：Anthropic 爱 harness 和 computer use 确认；OpenAI 爱 function calling + 可验证 RL；Microsoft 爱多工具办公与 Autogen 叙事，但仍要预算；Amazon 爱企业权限和 p95；Google 可能把 agent 塞进 ML design 的数据/评测一体。级别预期见 `us-leveling`：初级把循环写对；中级加 SLO 和降级；更高级定义任务图和失败模式。

两周压缩：一周实现带预算的工具环 + 一条可重放 fixture；一周推稀疏奖励和一张 WebArena 式评测表。论文加 Anthropic「Building effective agents」和 WebArena，不必堆二十个 agent 框架名。模拟面计时画约束，禁止空画「再加一个 planner agent」。

工作日清单：今天写了 charge / 确认 / 截断里的哪一段；今天把哪条轨迹字段补进 trace；今天用冻结夹具重放了一次失败。错法：把 ReAct 当算法；把多 agent 当架构；把温度 0 当可复现；把训练 RM 当工具是否成功的金标。材料包四样：一段工具循环、一张预算状态机、一页稀疏奖励、一份任务图评测。每天只推进一样。

Onsite 45 分钟设计：先钉不可逆动作和预算数字，再画循环，最后才谈「要不要多 agent」。评测问法是「环境 sha 钉在哪」。对齐问法是「$r$ 来自终局还是调用次数」。三句都能答，这一轮不容易空。简历项目准备 8 分钟：哪次工具环死循环、你怎么加熔断、哪张表证明没把模拟器过拟合进分数。

和六周计划的关系：第 4 周对齐加上 RFT / 稀疏信用，第 5 周设计改成工具环而不是只做 RAG。NVIDIA 岗可以少花时间在 agent，把预算留给并行；Anthropic / OpenAI applied 岗反过来。不要用 agent 周替代 Transformer debug，见 `us-debug-vs-leetcode`。

## 追问

- **ReAct 到底还要不要提？** 当日志格式提一句即可。追问应落到权限、预算、评测。
- **没有训过 RL 能面 agent 岗吗？** 能。把 harness 和评测讲透，RL 用稀疏奖励和 grader 纪律补概念。
- **多 agent 简历怎么讲？** 讲你如何拆子目标与 trace，不要讲角色名清单。
- **和多模态准备重叠吗？** 看屏 agent 两边都要：token 走 `us-mm-prep`，沙箱走本题。
- **Computer use 和 function calling 准备同一套吗？** 契约同一套（权限、预算、确认、trace）。定位方式不同：schema vs 截屏坐标，见 `design-browser-agent`、`anthropic-computer-use`。
- **要不要实现一个开源 agent 框架？** 不要为面试重写框架。把循环、夹具、grader 写对比熟记 LangGraph 名词有用。
- **SWE-bench 分数能当故事讲吗？** 可以当任务定义，不能当你的能力证明。要讲冻结环境、成本、失败分类，见 `design-eval-agent`。
