---
id: ali-tool-call-error-sft-rl
section: agent
order: 100
level: S
title: 阿里 26 校招：Agent 调工具不正确，选 SFT 还是 RL？
quick: >-
  先复现、按错误类型分桶，再选方法。模型不懂 schema 或调用格式，先改工具说明，再用 SFT
  教它正确调用；已经会调用，但工具选择、参数或多步决策不稳，且有可靠的环境反馈时，才考虑 RL。执行前的参数、权限和副作用检查，训练完也要保留。
tags:
  - Alibaba
  - 2026 Campus Recruiting
  - Tool Use
  - SFT
  - RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阿里26校招大模型算法二面45min（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/2c84e26c05664d52845959039cf99edd'
    type: candidate-first-hand
---
## 真题记录

- 公司：阿里巴巴
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 届校招；二面（45 分钟）
- 面试时间：原帖未披露；帖子发布于 2025-12-12
- 来源类型与可信度：牛客候选人原帖，A（公司、届别、岗位、轮次明确）
- 原始措辞：**“agent 调用工具不正确怎么办，采用 sft 或者 RL 怎么来解决”**

先查清楚错在哪，再决定用什么，一上来就说「上 GRPO」容易被追着问。模型看不懂 schema、JSON 写不对，属于没学会，先改工具说明、做 SFT、加 constrained decoding；已经能合法调用，只是工具选得不稳、多步决策老出错，环境又能给出可靠反馈，这时才轮到 RL。不管用哪种训练，执行前的 schema、权限和副作用检查都要留着。

举个例子，模型调退款工具时，有时把订单号填进了用户 id 字段，有时调了查询工具就直接结束。前一种是参数没依据当前观测填，后一种是选错了工具，治法不一样。所以第一步是复现问题，把调用轨迹拉出来分桶：模型没找到合适的工具或者没看懂描述；JSON 或函数名格式错；参数没有依据当前观测填写；选错工具；执行失败后没利用返回结果修正；反复重试退不出来。

schema 不熟、格式不合法、罕见的 API 版本，这些是 imitation gap，模型没见过正确的样子。优先把工具描述写清楚，补 targeted SFT，再上 constrained decoding。这类错误也缺少稳定、可验证的 reward，硬上 RL，模型会学到「乱调也像在努力」。契约本身怎么定见 `agent-schema-contract`。数据上，SFT 需要合法调用的正例，也需要常见非法格式的负例。

RL 适合另一类情况：模型已经能合法调用，要在多条 action 序列之间优化成功率、成本、步数或恢复策略，并且环境能给出可靠的 reward，比如任务成功、合法调用、预算。这时再补 online RL，前提是有可重置的环境，reward 按错误类型分别统计。过程奖励只奖可验证的事件，选对工具、参数合法、权限合规、结果被正确引用；JSON 写得漂亮、无意义地多走几步都不给分。同一面问到的过程奖励见 `ali-function-call-grpo-process-reward`，SFT 和 RL 在工具学习里的分工可以对照 `jd-toolformer-vs-rlhf`。没有环境，就先别做 online RL。

训练完也要留着 acceptance checks。非法调用必须在 executor 那里被拒，负奖励替代不了 ACL；执行点照样做参数验证、最小权限、幂等和高影响操作确认，超时与非 idempotent retry 见 `arl-retry`。离线按错误桶看任务成功、非法调用率、工具成本和回归集，上线后继续按错误类型看失败往哪里迁移。比如格式错下降了、选错工具上升了，说明模型学会了模仿调用格式，决策还有问题，这时再加 RL 才有依据。把所有失败都丢给同一种算法，是这题最容易被追打的答法。

## 追问

**格式错能不能靠 RL 修？**
通常不优先。动作空间里非法 JSON 太多，reward 很稀疏。先用约束 decoding 和 SFT 把合法调用学会。

**没有环境 reward 怎么办？**
先不上 online RL。用专家轨迹做 SFT，加拒答 / 合法调用分类器，或者人工给失败桶打点，等有了可执行的反馈再做 RL。

**RL 之后还出现越权调用？**
那是网关没做完，调奖励解决不了。policy 要在 executor 那里 fail-closed，见 `agent-tool-permissions`。

**和过程奖励怎么接？**
最终业务结果做 outcome 奖励，过程只奖可验证的中间事件，这样不容易被 reward hacking。见 `ali-function-call-grpo-process-reward`。
