---
id: stepfun-rlvr-benchmark-iteration
section: posttrain
order: 106
level: S
title: 阶跃星辰：RLVR 用什么策略，如何根据 benchmark 定位问题并迭代？
quick: "RLVR 先要有可靠的验证器，再用当前策略生成轨迹、打分、更新，基准评测的分数不能拿来当训练奖励。迭代时按能力、难度和错误类型分组看评测，判断问题出在数据覆盖、探索、奖励还是训练与推理预算，一次只改一项，最后用没参与调参的 holdout 确认。"
tags:
  - StepFun
  - RLVR
  - Benchmark
  - Iteration
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
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

RLVR 的策略是先有一个可靠的验证器，再用当前策略生成轨迹、打分、更新；用 benchmark 迭代时，先分组定位问题出在哪，一次只改一个因素，最后用没参与调参的 holdout 确认。原帖这两问我会串成一条讲：先讲训练闭环（verifier → 采样 → 可审计的奖励 → 更新），再讲怎么用分组评测定位。benchmark 分数不能直接当训练奖励，把评测题和答案反复喂进训练换分，那叫污染。说「哪个 benchmark 低就加哪类数据」却不谈归因，会失分。

## 训练闭环怎么搭

第一步是定义一个能执行、抗投机的 verifier，比如规则、单测、字段校验，输出要可审计。然后挑当前策略能探索到的 prompts，全对或全错的组没有梯度。对同一道题生成一组轨迹、算奖励，控制好 KL 和 policy freshness 再更新。正确路径太少时，先用 SFT 冷启动、调任务难度或做拒绝采样，光加大 group 只会空转。

reward 必须和业务上的成功一致。解析器太松，模型会靠格式刷分；太严，又会把对的判成错。训练分布和评测包的隔离也是策略的一部分，要在训练开始前就落实。

## 用分组统计定位问题

benchmark 要按任务类型、难度、答案长度、tool / verifier 类型和错误模式分组统计。低分的原因可能是模型能力不够、数据覆盖有空洞、reward 失真、rollout 预算不足、评测解析器有问题，或者污染。先用 trace 和 ablation 证明是哪一个，再只改那一项。比如「难的算术题全错」，可能是探索不足，该降难度或冷启动，改 KL 没用；「会做但解析失败」，就该修 verifier，加数据没用。切片也比总分有用，总分涨了、某个 failure-type 却在掉，说明总体提升掩盖了某类错误变多。

## 单变量迭代，用 holdout 复验

每次只改 reward、数据、预算里的一项，几项一起改就定位不了。seed、输入提示（prompt）、模型、verifier 和 decoding 的版本都要留着，不然「涨了」没法复现。所有调参结果最后都要在不参与选择的 holdout 和真实任务上复验，过门禁的应该是 holdout，不是你拿来选超参的那张表。

## 追问

**能不能直接拿 benchmark 当 reward？**
不能。这会污染评测，评测本身的波动也会被优化成刷分。

**正确路径很少怎么办？**
用冷启动、课程、拒绝采样，先让组内出现有对有错的情况。

**怎么证明是 reward 的问题？**
人工抽 trace 看：模型对了 verifier 判错，或者反过来。修解析器优先于改算法。

**什么时候停止迭代？**
holdout 和线上任务都过了门禁，目标桶也不再掉，就可以停。别去追调参集上的分数。
