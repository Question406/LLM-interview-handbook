---
id: dt-bench-vs-user
section: labs
order: 53
level: A
title: Cognition：榜涨了，用户说更差，数据侧先查哪几层？
quick: >-
  先诊断断在哪，再动数据。我会按顺序查四层：training set 有没有 leakage 评测题，scorer
  是不是偏爱某种文风，基准题和测试本身有没有错，榜单任务和用户的实际工作差多远。没找到原因就加数据，很可能只是把榜单继续往上推。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: LiveBench
    url: 'https://arxiv.org/abs/2406.19314'
    type: primary
  - title: Why we no longer evaluate SWE-bench Verified
    url: 'https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

榜涨而用户说更差，说明榜单分数和用户体验之间有一层断开了。我会先找出断在哪一层，再调训练 data mix；没找到原因就「再加数据」，很可能沿着错的方向接着刷榜。

举个例子。榜单测的是函数级的 Python 题，用户却是在整个仓库里改代码、补测试、处理 tool calls 失败。训练数据如果只改善了前一种任务，榜单会涨，用户照样觉得变差。

排查的顺序是从「分数是假的」排到「分数是真的但测错了东西」。先看训练数据有没有 leakage 评测题，n-gram 重合要查，teacher model 间接把答案带进来也要查，方法见 `dt-contamination`。再看 scorer，它可能偏爱长回答或同一模型家族的文风，Arena 分涨了，事实忠实度却在掉，见 `dt-judge-bias`、`dt-length-hack-data`。然后看基准本身有没有错，OpenAI 在 2026-02 停报 SWE-bench Verified，涉及的正是测试质量和标准答案 leakage 这两类问题，公开榜过期怎么处理见 `dt-agent-verified-stale`。前三层都没问题，才轮到上面那个例子：榜单任务和用户任务差得太远。

查完之后，发布检查里要放进用户实际在做的任务，比如摘要、tool calls、各语言的真实请求，光看 MMLU 发现不了这种断裂。用户反馈效果变差时，先用研究数据把问题复现出来；如果是加了某批数据之后 target evaluation slices 掉分，就按 `dt-worse-after-data` 的流程排查。

这道题公开题库记在 Cognition 等 agent 岗位下，这里按题型整理。

## 追问

**Arena 分涨了，能说明模型更好吗？**
只能说明评分者更喜欢它。LiveBench 讨论过模型在 Arena 上表现强、在客观题上表现弱的情况，其中就有文风的影响。

**内部 human evaluation 也涨了，用户还是觉得差，怎么解释？**
human evaluation 员和用户的偏好可能不一样。评分协议可能在奖励「完整」，用户想要的是「别啰嗦」。把用户任务录成研究集，按真实使用权重加权再评。

**只有某一个 locale 掉了呢？**
先查训练 data mix 和过滤分类器，看是不是让这个语言或地区的数据大量减少了，见 `dt-locale-data`、`dt-neg-transfer`。

**agent 步数变少了，任务却更容易失败？**
模型可能学会了跳过只读检查。最终状态正确，也不代表中间步骤符合要求，见 `dt-agent-state-path`。
