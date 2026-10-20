---
id: dt-bench-vs-user
section: labs
order: 53
level: A
title: Cognition：榜涨了，用户说更差，数据侧先查哪几层？
quick: "先排查四类问题：训练集是否泄漏了评测题，评分器是否偏爱某种文风，基准题和测试本身是否有错，以及榜单任务是否代表用户实际工作。找到原因后再改数据，否则加数据可能只会继续提高榜单分数。"
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

先按顺序排查四类原因。

1. 训练数据是否泄漏了评测题？既要查 n-gram 重合，也要查教师模型是否间接泄漏答案，见 `dt-contamination`。
2. 评分器是否偏爱长回答或同一模型家族的文风？这可能让 Arena 得分上升，却让事实忠实度下降，见 `dt-judge-bias`、`dt-length-hack-data`。
3. 基准本身是否有错？OpenAI 停报 SWE-bench Verified 时，涉及测试质量与标准答案泄漏这两类问题。
4. 榜单和产品任务是否差得太远？榜单可能测函数级 Python 题，用户却要在整个仓库里修改测试、处理工具失败。训练数据可能只改善了前一种任务。

公开题库将这类问题记在 Cognition 等 agent 岗位中。回答时要先诊断再调整训练配比；直接说「再加数据」，可能沿着错误方向继续优化。

用于苹果的场景时，要评估通知、摘要、工具调用和各语言地区的实际任务，不能只看 MMLU。发布检查要包含这些产品任务的子集。用户反馈效果变差时，用研究数据复现问题，不要把用户原文直接用于训练基座模型。SWE 那种公开榜过期，见 `dt-agent-verified-stale`。加数据掉目标切片，走 `dt-worse-after-data`。

公开资料包括 LiveBench 对 Arena 表现强、客观题表现弱的讨论，其中涉及文风影响；还有 OpenAI 在 2026-02 停报 Verified 的博文。题面来自公开公司题库，不是逐字稿。

## 追问

- **内部人评也涨、用户还是差？** 人评员不是用户。协议可能在标「完整」，用户在标「别啰嗦」。把产品任务录成研究集，按真实权重加权。
- **只掉某一个 locale？** 检查训练配比和过滤分类器是否让这个语言或地区的数据大量减少，见 `dt-locale-data`、`dt-neg-transfer`。
- **agent 步数少了但任务失败？** 模型可能学会跳过只读检查。最终状态正确，也不代表中间步骤符合要求，见 `dt-agent-state-path`。
