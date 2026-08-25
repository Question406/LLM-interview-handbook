---
id: kuaishou-agent-intent-recovery
section: agent
order: 103
level: S
title: 快手大模型算法：Agent 用户意图识别不准确，工程上如何优化？
quick: >-
  先确认错在输入理解、intent taxonomy、retrieval / tool routing、上下文状态还是执行反馈；再用置信度阈值 + clarification、结构化
  schema、candidate rerank、memory 边界和错误回放修复。必须按 intent slice 测端到端 task success，不能只看分类准确率。
tags:
  - Kuaishou
  - Agent
  - Intent Recognition
  - Production Debugging
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手实习 大模型算法面经 攒人品（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/93a72d1bd0a2418281414f288dcb3629
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法
- 届别 / 流程：实习；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-18
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“如果我们这边的agent对于用户意图识别不准确，在工程上有哪些方法进行优化。”**

这块容易直接答成换更大的分类模型，或只报 intent accuracy。快手算法面要的是工程分桶：错可能在用户表达、taxonomy、路由、上下文污染，或执行对了但回复没 grounding。只升离线分类准确率，线上完成率可能下降，模型更敢路由，高风险意图假阳性变多。京东侧测法见 `jd-intent-accuracy`：按意图切片，并报澄清率和错误路由的业务后果。

## 先从 trace 建 taxonomy，再决定改哪一层

从线上误路由、abstain、用户改写、人工转接抽 case，按高流量和高风险分桶：

- 表达歧义：「那个不行了」没指对象；
- taxonomy 本身糊：创作辅助 vs 数据查询边界不清；
- router / 小模型标错；
- 上下文或长期 memory 把上一任务意图带过来；
- 检索把相邻业务文档混入，模型跟着走偏；
- tool catalog 描述雷同，选错工具；
- 下游执行对，但回答编了未返回的字段。

没有这张表，任何「优化」都无法回归。高风险意图（删除、发布、消耗额度）假阳性要单独阈值，不能和闲聊共用一个 softmax。

## 工程手段与验收指标

手段按桶选，不要一次全上：结构化意图 schema 加 slot 校验；small router + 候选 rerank；置信度 / margin 不足时澄清，别猜，见 `agent-ask-clarify`；会话状态与长期 memory 分层，防止旧任务污染，见 `byte-short-long-memory`；限制当前可见工具，catalog 描述写互斥条件；把 execution outcome 回流成训练和 eval 样本。

验收不能只看分类 accuracy。要看：澄清后解决率、端到端任务成功、错误工具调用、用户二次改写、时延、人工兜底率。按 intent slice 报，微平均会被简单意图拉高。规划阶段还要问「这步还是原任务吗」，防止计划漂到别的产品，见 `kuaishou-modular-planning`。评测集含歧义句和隐藏目标，乱路由必须能被抓住。工程优化的顺序通常是：先修 taxonomy 和工具描述（便宜、立刻减混肴），再加置信度门槛与澄清，最后才考虑换模型或加训练数据。回流样本要带最终执行结果，不能只标「用户说的 intent」，用户改写前后可能都合理，错在路由策略。快手侧内容 / 创作者工具多、名称接近，catalog 互斥条件比再训一个分类头更有效。报进度时按桶给 before / after，避免用一个 accuracy 掩盖高风险切片恶化。

## 追问

- **要不要全程一个大模型做意图？** 不必。ID / 口令规则先接住，其余小分类器或带 schema 的 LLM，低置信再上大模型或澄清。
- **澄清会不会伤害体验？** 会。只在不同解释会导向高代价不同动作时问；能用廉价检索消歧的先查。
- **memory 会不会让意图更准？** 确认过的偏好有帮助；未校验的摘要会让 router 固执地走旧任务。写入要门禁。
- **指标升了但客诉没降？** 多半是高风险切片被微平均淹没。按业务后果加权，假阳性单独设阈值。
