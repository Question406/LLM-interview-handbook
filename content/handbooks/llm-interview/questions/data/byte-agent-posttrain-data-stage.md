---
id: byte-agent-posttrain-data-stage
section: data
order: 100
level: S
title: 字节 AI 数据技术：Agent 后训练的 SFT / RL 数据怎么设计，何时切 RL？
quick: "监督微调（SFT）先教会合法的工具调用格式、工具和参数选择、状态跟踪、失败恢复和安全边界；强化学习（RL）再去探索模型已经会、但表现不稳定的可验证能力。什么时候切，看留出任务的轨迹成功率、格式合规率、奖励能否区分好坏和探索覆盖，epoch 和 loss 说明不了。"
tags:
  - ByteDance
  - Agent Post-training
  - SFT Data
  - Agent RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 4.28 字节 AI数据技术一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/8e812a2e2b824779bea596a90d7603e0?sourceSSR=enterprise
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 团队 / 岗位：AI 数据技术
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-28
- 来源类型与可信度：牛客候选人原帖，B（岗位、轮次与题单明确；届别、面试日期未披露）
- 原始措辞：**“如果让你做Agent方向的后训练，SFT数据怎么设计？RL数据怎么设计？SFT做到什么程度可以开始做RL？”**

Agent 后训练我会让监督微调（SFT）负责可执行的格式和基本行为，强化学习（RL）负责已经会但不稳的可验证探索。切 RL 的时机看 held-out 轨迹成功率、格式合规率，以及奖励分数（reward）能不能把一组里的好坏分开，跑了多少 epoch、loss 多低都不能当依据。

举个例子：SFT 之后 loss 已经很低了，一跑 held-out，却有大量调用的 JSON 解析失败。这时候开 RL，reward 几乎全打在 parse 失败上，模型学的是「把格式写对」，这本来是 SFT 该做完的事。另一种常见错法是 SFT 只放最终正确答案。

## SFT 数据分层覆盖

SFT 集要覆盖任务意图、可调用工具集合、合法 JSON / 参数、观测结果（observation）grounding、多步 state、拒绝与澄清、timeout / tool error recovery、安全终止。按任务、工具、失败类型、轨迹长度、风险等级分层，免得数量最多的简单工具调用主导损失（loss）。环境返回的 token 排除在损失计算之外（见 `pt-tool-mask`）。

要判断某一类数据有没有带来额外收益，就做消融。比如去掉「失败恢复」这一桶再训，held-out 的超时任务应该会掉。

## RL 数据和开始的门槛

RL 数据来自当前策略在可复现环境里新采样的轨迹，保留成功、近成功和有诊断价值的失败。开始 RL 我一般要求三条同时满足：格式合法率高于阈值，否则 reward 全打在 parse 失败上；held-out 基础任务明显高于随机探索；同一个输入提示的一组回答里有对有错，优势 $\hat A_i$ 不是常数。如果绝大多数组全对或全错，先去调难度、SFT 覆盖或 reward，别加大 RL 步数。

对照实验是只加 SFT 步数，和达到门槛后开 RL，两边都报格式率、任务成功率、钻奖励规则空子的比例。

## 追问

**loss 降了能开 RL 吗？**
不能。简单调用就能把 loss 刷低，要看 holdout 成功率和组内区分度。

**RL 为什么要用当前策略新采样的轨迹？**
离线轨迹对当前策略是 off-policy，优势偏差大；环境版本一变还回放不了。

**一组全对怎么办？**
优势为 0，这一步更新是空的。提高难度或者做动态采样，见 GRPO 零优势那张卡。
