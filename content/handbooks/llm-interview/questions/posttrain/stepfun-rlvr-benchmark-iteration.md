---
id: stepfun-rlvr-benchmark-iteration
section: posttrain
order: 106
level: S
title: 阶跃星辰：RLVR 用什么策略，如何根据 benchmark 定位问题并迭代？
quick: >-
  RLVR 的起点是可信 verifier 与 fresh rollout，不是把 benchmark 分数直接当 reward。用 capability / difficulty / failure-type 分桶的
  evaluation 定位 coverage、探索、reward、训练或推理预算问题，再做单变量迭代，并以未参与调参集确认改进。
tags:
  - StepFun
  - RLVR
  - Benchmark
  - Iteration
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 阶跃星辰大模型算法实习一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“讲解一下rlvr使用的策略。”**；追问：**“Benchmark测评情况，如何根据benchmark进行模型效果优化。”**

RLVR 的起点是可信 verifier 与 fresh rollout，不是把 benchmark 分数直接当 reward。把评测题和答案反复喂进训练换分，是污染，不是策略。原帖两问应串成一条：先讲训练闭环（verifier → 采样 → 可审计奖励 → 更新），再讲用分桶评测定位，一次只改一个因素，用未参与调参的 holdout 确认。说「看哪个 benchmark 低就加这类数据」而不谈归因，会失分。

## RLVR 策略：可执行、抗投机的闭环

先定义能执行且抗投机的 verifier：规则、单测、字段校验，输出可审计。再选处于当前策略可探索区域的 prompts——全对全错组没有梯度。采样 group rollout，算 reward，控制 KL / policy freshness 后更新。正确路径稀少时，先做 cold-start SFT、curriculum 或 rejection sampling，而不是加大 group 空转。Reward 必须和业务成功一致：解析器松会让格式刷分；解析器严会把对的判错。

不能以 benchmark 的题目和答案反复喂给训练来换分。训练分布与评测包隔离，是策略的一部分，不是事后良心。

## 用分桶定位，不要一个总分

benchmark 按任务类型、难度、答案长度、tool / verifier 类型与错误模式分桶。低分可能来自：模型能力不够、数据覆盖空洞、reward 失真、rollout 预算不足、评测解析器、或污染。先跑 trace / ablation 证明归因，再只改一项。例如「难算数全错」可能是探索不足，应降难度或冷启动，而不是改 KL；「会做但解析失败」应修 verifier，而不是加数据。

切片比总分有用：总分涨、某一 failure-type 掉，说明在洗另一种错误。

## 单变量迭代，holdout 复验

所有调参以不参与选择的 holdout 与真实任务复验。保留 seed、prompt、模型、verifier 和 decoding 版本，否则「涨了」不可复现。一次改 reward、数据、预算里的一项；多项一起改无法定位。过门禁的是 holdout，不是你用来选超参的那张表。

## 追问

- **能不能直接用 benchmark 当 reward？** 不能。会污染，且评测波动会被优化成刷分。
- **正确路径很少怎么办？** 冷启动、课程、拒绝采样，先让组内出现对错混合。
- **如何证明是 reward 问题？** 人工抽 trace：模型对、verifier 错或相反。修解析器比改算法优先。
- **迭代停手条件？** holdout 与线上任务过门禁，且目标桶不再掉；不要追调参集。
