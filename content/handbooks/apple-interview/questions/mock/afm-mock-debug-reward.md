---
id: afm-mock-debug-reward
section: mock
order: 40
level: A
title: 附件诊断 2：RM 分和自动胜率上涨，真实工具成功却下降
quick: 将候选生成、奖励排序、judge 测量和任务真值拆开检查。扫描 best-of-N、交换位置、核对高分错例，再决定修 RM 数据、评测协议还是生成策略。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - 全流程模拟
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: 'https://arxiv.org/abs/2210.10760'
    type: primary
  - title: Large Language Models are not Fair Evaluators
    url: 'https://arxiv.org/abs/2305.17926'
    type: primary
  - title: Length-Controlled AlpacaEval
    url: 'https://arxiv.org/abs/2404.04475'
    type: primary
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: 'https://arxiv.org/abs/2306.05685'
    type: primary
---

## 候选人材料
原创45分钟题，数值为教学构造。[N 扫描 CSV](/apple-prep/reward_sweep.csv)、[交换评审 CSV](/apple-prep/judge_swaps.csv)、[高分候选 JSONL](/apple-prep/reward_candidates.jsonl)。可用 [分析脚本](/apple-prep/analyze_cases.py) 核对描述统计。先自行分析，避免直接读答案。

N=1/4/16/64 时代理 RM 均值为0.4/0.8/1.2/1.7，隐藏执行成功率65/74/70/58%，每档100任务。另有6个刻意挑选的交换评审例子，不是随机总体样本。

请给至少四个假设，按成本排查，并提出下周1000对标注的分配原则。第25分钟面试官追加：新回答平均长度翻倍，teacher 和 judge 是同一模型家族。不能只回答“换个 judge”。

## 参考分析
先确认 N 扫描是否同源嵌套候选、任务是否相同、executor 与超时是否一致；汇总数据不包含这些信息，需索取。若受控条件成立，N 大时代理升而任务降提示过度优化。候选样本包含伪造成功、错误字段但礼貌总结、短而正确、长且必要的例子，可支持构造审计方向，不能估自然比例。

交换评审先映射身份：总选 first 的样本是不一致而非内容 tie。单独报告稳定胜负、不一致率和交换平均分。对长度做内容等价干预；对家族做交叉评审与独立人审；对工具结果直接核验状态。统一实验只改一个因素，避免同时换策略、judge 和数据后无法 attribution。

1000对预算按风险、覆盖、代表性与新策略分歧划分，保留随机审计，不给未经试验的固定万能 data mix。标注需将事实、执行、帮助性和风格分维度。补高 RM 分但执行失败的困难负例，也保留长且必要的正例。独立任务选择 N 和停止规则，最终 blind set 不参与调参。

## 评分与追问
五项各0–4：控制变量、代理与真值区分、顺序/长度/家族审计、数据干预、验收成本。14分为自练通过线。
**N=4一定可上线？** 这张表不够，缺独立重复、关键错误和成本。
**同家族就一定有偏？** 是假设，需要质量控制后的交叉实验；不能仅看模型名 attribution。
