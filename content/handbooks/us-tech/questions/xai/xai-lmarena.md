---
id: xai-lmarena
section: xai
order: 15
level: S
title: xAI：LMSYS Arena / 在线偏好，和离线榜的差，不要神化 Elo
quick: >-
  Arena 用匿名用户的成对投票估计偏好，平台已从逐局 Elo 更新改为 Bradley-Terry 全局 MLE，并给 confidence
  interval。分数受提示分布、长度、文风、位置和票数影响，我会把它和固定题离线切片、私有新鲜题一起看；Grok-3 的 Elo 只代表当时快照。
tags:
  - xAI
  - LMSYS
  - Chatbot Arena
  - Evaluation
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Chatbot Arena — An Open Platform for Evaluating LLMs by Human Preference
    url: 'https://arxiv.org/abs/2403.04132'
    type: primary
  - title: Chatbot Arena Elo system update (Bradley-Terry)
    url: 'https://lmsys.org/blog/2023-12-07-leaderboard/'
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: 'https://x.ai/blog/grok-3'
    type: primary
  - title: Length-Controlled AlpacaEval
    url: 'https://arxiv.org/abs/2404.04475'
    type: secondary
---

## 可以这样回答

我会把 Arena 作为聊天偏好指标，和离线能力切片一起看。比如回复更长、更自信，可能赢得投票，却没有更好地解出推理题。Grok-3 博文把早期 chocolate 版本的 Elo 1402 作为当时领先的证据，解释它要结合 Chiang 等人 2024 年的平台论文，以及 LMSYS 在 2023 年 12 月改用 Bradley-Terry 的说明。预训练公开信息见 `xai-grok-pretrain`，污染协议见 `align-eval-contam`。

用户同时看到两个匿名模型，投票赢 / 输 / 平。早期排行榜用在线 Elo：一局一更新，顺序敏感，新模型分数抖。LMSYS 后来改成 Bradley-Terry：假设胜率只依赖固定强度 $s_i$，

## 技术备查

我会把 Arena 作为聊天偏好指标，和离线能力切片一起看。比如回复更长、更自信，可能赢得投票，却没有更好地解出推理题。Grok-3 博文把早期 chocolate 版本的 Elo 1402 作为当时领先的证据，解释它要结合 Chiang 等人 2024 年的平台论文，以及 LMSYS 在 2023 年 12 月改用 Bradley-Terry 的说明。预训练公开信息见 `xai-grok-pretrain`，污染协议见 `align-eval-contam`。

## 先看分数估计的对象

用户同时看到两个匿名模型，投票赢 / 输 / 平。早期排行榜用在线 Elo：一局一更新，顺序敏感，新模型分数抖。LMSYS 后来改成 Bradley-Terry：假设胜率只依赖固定强度 $s_i$，

$$
P(i \succ j)=\frac{e^{s_i}}{e^{s_i}+e^{s_j}},
$$

对全部对局做 MLE（平局当半胜）。再 bootstrap 出 confidence interval。新模型票少时区间会宽，区间重叠的 point estimate 排序不足以证明「第一」。

这估计的对象是当前用户、当前提示混合、当前展示样式下的偏好。RLHF 也拟合类似的成对偏好，所以 Arena 和聊天产品相关，也所以它会被文风黑客：更长、更列表、更自信，离线推理题不一定更好。Length-controlled AlpacaEval 把 length bias 写进离线偏好；Arena 后来也有 style control 尝试把长度 / Markdown 残差掉。没有控制时，Elo 涨可能只是更啰嗦。

position bias：先展示的 A 往往更占优。匿名可以减少品牌，减不掉左/右。论文用专家抽检和众包一致性当信誉论证，不是证明无偏。

## 在线和离线怎么配合

| | 离线榜（MMLU、HumanEval、AIME） | Arena |
| --- | --- | --- |
| 题 | 固定、可回归 | 活的，用户自带，分布漂移 |
| 分数 | 对错 / pass@k | 成对偏好 |
| 泄漏 | n-gram、教师、改写，见 `align-eval-contam` | 用户粘贴考题、刷票、识别模型文风 |
| 长度 | 通常不奖啰嗦 | 默认奖长文，除非做 style control |
| 用途 | 训练过程监控、能力切片 | 聊天产品是否讨人喜欢 |

Grok-3 博文同时报 AIME / GPQA / LiveCodeBench 和 Arena Elo。前者是 STEM 切片（仍要问截止日、cons@k、是否 Think），后者是偏好切片。用 Elo 证明预训练数据配比，或用 AIME 证明「用户更喜欢」，都是把不同指标的含义混用。Arena 提示比 MMLU 更像真实聊天，但也更脏、更不稳定。

污染两边都有。离线：训练见过题面。在线：用户把明天的考试题贴进 Arena，模型若在预训练或后训练见过同类，投票像能力。Arena 题不可复现成稳定回归集，除非他们另发静态子集（Arena-Hard 一类）。内部决策时，我会组合离线切片、私有新鲜题和有限的在线偏好，让不同指标分别支持对应的发版判断。

读 Elo 时还要记得：

- point estimate 1402 没有带着当时的 CI 和对手集合，过一周提示混合变了，名次可以换。
- 票数不够时，「领先」可能只是区间重叠下的排序噪声。
- 人格更冲、更幽默的模型可以赢 Arena、在拒答和事实性上更差。xAI 公开叙事吃「最大求真」，Arena 吃的是点击偏好，两者不必一致。
- 公司博文是营销快照。面试引用要说「官方自报、当日排行榜」，不要说「所以 Grok-3 是最强基座」。

## 追问

**为什么还要看 Arena？**
因为它抓到了静态榜抓不到的指令风格和开放式任务。当一个偏好传感器，和离线切片一起看。单独当北星会被长度和讨好优化。

**BT 和 Elo 谁对？**
同一类强度模型；BT 全局估计更稳、CI 更诚实。在线 Elo 适合直播打分，不适合当论文主表。

**内部能不能自建 Arena？**
能，但要解决刷票、员工识别自家模型、提示泄漏到训练集。员工 Arena 会偏内部口味。更干净的是盲测 + 预注册题库 + 长度控制。

**Grok 在 Arena 赢了是否说明预训练更好？**
不能直接下这个结论。后训练、系统提示、工具（搜网）都会改投票。预训练主张仍只能用 `xai-grok-pretrain` 里那些公开事实，不要用 Elo 反推数据配比。

## 相关题

- [[align-arena]]：几乎是同一题的对齐岗问法，同样讲 selection bias、文风长度和区间，多了发版表和 MT-Bench 对照。
- [[anthropic-pref-bt]]：Arena 出分用的 Bradley-Terry 模型本身，以及平局和噪声标签怎么处理。
- [[align-llm-judge]]：用模型代替人投票时的偏差和协议，可以和 Arena 的人投票对照。
- [[align-length-bias]]：Arena 分数为什么随长度变，评测时怎么把长度拆开。

本卡依据公开材料整理，标记为 `realInterview: false`。
