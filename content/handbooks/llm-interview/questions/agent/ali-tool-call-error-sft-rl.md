---
id: ali-tool-call-error-sft-rl
section: agent
order: 100
level: S
title: 阿里 26 校招：Agent 调工具不正确，选 SFT 还是强化学习？
quick: >-
  先按错误归因：不懂 schema 或格式，先修 tool spec 和 SFT；会调用但选择、参数或多步决策不稳，且有可靠环境反馈时再上
  RL。无论哪种训练，执行前都必须做 schema、权限和副作用校验。
tags:
  - Alibaba
  - 2026 Campus Recruiting
  - Tool Use
  - SFT
  - RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里26校招大模型算法二面45min（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/2c84e26c05664d52845959039cf99edd
    type: candidate-first-hand
---
## 真题记录

- 公司：阿里巴巴
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 届校招；二面（45 分钟）
- 面试时间：原帖未披露；帖子发布于 2025-12-12
- 来源类型与可信度：牛客候选人原帖，A（公司、届别、岗位、轮次明确）
- 原始措辞：**“agent调用工具不正确怎么办，采用sft或者强化学习怎么来解决”**

二面别一上来赌「上 GRPO」。工具调错是一篮子失败，先复现切桶，再决定修 spec、SFT 还是 RL。同面过程奖励见 `ali-function-call-grpo-process-reward`。训练不取代执行前的 schema、权限和副作用校验。

## 先切错误桶

按轨迹切：tool discovery / description 看不懂；JSON / 函数名格式非法；参数没 grounded 到当前观测；选错工具；执行失败但 observation 没被利用；陷入 retry loop。schema 不熟、格式不合法、罕见 API 版本，是 imitation gap：优先把工具描述写清楚、补 targeted SFT、上 constrained decoding。这类错误没有稳定可执行 reward，RL 会学到「乱调也像在努力」。契约本身见 `agent-schema-contract`。

## 什么时候才上 RL

模型已能合法调用，但要在多条 action 序列间优化成功率、成本、步数或恢复策略，并且环境能给出可靠 reward（任务成功、合法调用、预算），才补 online RL。过程奖励只奖可验证事件：选对工具、参数合法、权限合规、结果被正确引用；不要奖 JSON 漂亮或无意义多步。非法调用必须在 executor 被拒，不能靠把负奖励当 ACL。超时与非幂等重试见 `arl-retry`；SFT vs RL 的工具学习分工也可对照 `jd-toolformer-vs-rlhf`。

## 训练之后仍要闸门

无论 SFT 还是 RL，执行点仍做参数验证、最小权限、幂等与高影响确认。离线按错误桶、任务成功、非法调用率、工具成本和回归集同时验收；上线后再看同类失败是否从「格式错」变成「决策错」。把所有失败丢给同一种算法，是这题最容易被追打的答法。数据上，SFT 需要合法调用的正例和常见非法格式的负例；RL 需要可重置环境和按桶定义的 reward。没有环境就先不要 online RL。上线后继续按桶看失败迁移：格式错下降而选错工具上升，说明 imitation 过了、决策还没过，这时再加 RL 才有依据。先归因，再选算法；executor 校验永远在训练之外。

## 追问

- **格式错能不能靠 RL 修？** 通常不优先。动作空间里非法 JSON 太多，reward 稀疏。先约束解码和 SFT 把合法调用学会。
- **没有环境 reward 呢？** 先不要 online RL。用专家轨迹 SFT、拒答/合法调用分类器，或人工对失败桶打点，等有可执行反馈再 RL。
- **RL 之后还出现越权调用？** 那是网关没做完，不是奖励没调好。policy 在 executor fail-closed，见 `agent-tool-permissions`。
- **和过程奖励怎么接？** 最终业务结果做 outcome，过程只奖可验证中间事件，避免奖励 hacking。见 `ali-function-call-grpo-process-reward`。
