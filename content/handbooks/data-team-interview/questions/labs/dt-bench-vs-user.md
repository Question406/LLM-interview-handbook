---
id: dt-bench-vs-user
section: labs
order: 53
level: A
title: Cognition：榜涨了，用户说更差，数据侧先查哪几层？
quick: "先诊断，再改数据。按顺序查四层：训练集是否泄漏了评测题，评分器是否偏爱某种文风，基准题和测试本身是否有错，榜单任务是否代表用户的实际工作。不先找到原因就加数据，很可能只是继续推高榜单分数。"
companies:
  - apple
tags:
  - Cognition
  - Evaluation
  - Product
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: LiveBench
    url: https://arxiv.org/abs/2406.19314
    type: primary
  - title: Why we no longer evaluate SWE-bench Verified
    url: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

榜涨而用户说更差，说明榜单分数和用户体验之间有一层断开了。我会先诊断断在哪，再调整训练配比；直接「再加数据」，可能沿着错误的方向继续优化榜单。公开题库把这类问题记在 Cognition 等 agent 岗位中，这里按题型整理，题面并非逐字稿。

## 按顺序查四层

顺序从「分数是假的」排到「分数是真的但测错了东西」：

1. **训练数据是否泄漏了评测题？** n-gram 重合要查，教师模型间接泄漏答案也要查，见 `dt-contamination`。
2. **评分器是否偏爱长回答或同一模型家族的文风？** 这可能让 Arena 得分上升，事实忠实度却下降。LiveBench 就讨论过模型在 Arena 上表现强、在客观题上表现弱的情况，其中涉及文风影响。见 `dt-judge-bias`、`dt-length-hack-data`。
3. **基准本身是否有错？** OpenAI 在 2026-02 停报 SWE-bench Verified，涉及的正是测试质量和标准答案泄漏这两类问题。公开榜过期的处理见 `dt-agent-verified-stale`。
4. **榜单和用户任务是否差得太远？** 榜单可能测函数级 Python 题，用户却要在整个仓库里修改测试、处理工具失败。训练数据可能只改善了前一种任务。

## 查完之后

发布检查里要放进用户实际做的任务：摘要、工具调用、各语言的真实请求，光看 MMLU 发现不了这一层断裂。用户反馈效果变差时，先用研究数据复现问题。如果是加了数据之后目标切片掉分，按 `dt-worse-after-data` 的流程排查。

## 追问

- **内部人评也涨了，用户还是觉得差？** 人评员和用户的偏好可能不一样。评分协议可能在奖励「完整」，用户想要的是「别啰嗦」。把用户任务录成研究集，按真实使用权重加权。
- **只掉某一个 locale？** 检查训练配比和过滤分类器是否让这个语言或地区的数据大量减少，见 `dt-locale-data`、`dt-neg-transfer`。
- **agent 步数少了，任务却失败？** 模型可能学会了跳过只读检查。最终状态正确，也不代表中间步骤符合要求，见 `dt-agent-state-path`。
