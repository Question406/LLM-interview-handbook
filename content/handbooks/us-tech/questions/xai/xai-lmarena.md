---
id: xai-lmarena
section: xai
order: 15
level: S
title: xAI：LMSYS Arena / 在线偏好，和离线榜的差，不要神化 Elo
quick: >-
  Arena 是众包成对偏好，不是能力的充分统计。平台已从在线 Elo 改成 Bradley-Terry 的全局
  MLE，并给置信区间。分数随提示混合、长度和文风、位置偏差、投票量一起动。离线榜测的是固定题；Arena 测的是谁更讨好当前匿名用户。Grok-3 博文里的 Elo 是快照，不是预训练真理。
tags:
  - xAI
  - LMSYS
  - Chatbot Arena
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Chatbot Arena — An Open Platform for Evaluating LLMs by Human Preference
    url: https://arxiv.org/abs/2403.04132
    type: primary
  - title: Chatbot Arena Elo system update (Bradley-Terry)
    url: https://lmsys.org/blog/2023-12-07-leaderboard/
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: https://x.ai/blog/grok-3
    type: primary
  - title: Length-Controlled AlpacaEval
    url: https://arxiv.org/abs/2404.04475
    type: secondary
---

## 题怎么来的

xAI 评测 / 研究岗会碰到 Grok 在 Chatbot Arena（LMSYS，后亦称 LMArena）上的排名。Grok-3 博文把早期版本（代号 chocolate）的 Elo 1402 写成「领先」。评委要听你 **会不会把 Elo 神化**：它是什么估计、偏差从哪来、和 MMLU / AIME 离线榜差在哪。论文锚点是 Chiang 等人 2024 的 Arena 平台文，以及 2023 年 12 月他们把在线 Elo 换成 Bradley-Terry 的说明。`realInterview: false`。预训练能公开讲什么见 `xai-grok-pretrain`；污染协议见 `align-eval-contam`。

## Elo 不是能力，BT 也只是成对偏好的 MLE

用户同时看到两个匿名模型，投票赢 / 输 / 平。早期排行榜用在线 Elo：一局一更新，顺序敏感，新模型分数抖。LMSYS 后来改成 Bradley-Terry：假设胜率只依赖固定强度 $s_i$，

$$
P(i \succ j)=\frac{e^{s_i}}{e^{s_i}+e^{s_j}},
$$

对全部对局做 MLE（平局当半胜）。再 bootstrap 出置信区间。新模型票少，区间宽，点估计交叉时「第一」没有统计意义。面试先画这条，再谈产品。

这估计的对象是 **当前用户、当前提示混合、当前展示样式下的偏好**，不是潜在智能。RLHF 也拟合类似的成对偏好——所以 Arena 和聊天产品相关，也所以它会被文风黑客：更长、更列表、更自信，离线推理题不一定更好。Length-controlled AlpacaEval 把长度偏差写进离线偏好；Arena 后来也有 style control 尝试把长度 / Markdown 残差掉。没有控制时，Elo 涨可能只是更啰嗦。

位置偏差：先展示的 A 往往更占优。匿名可以减少品牌，减不掉左/右。论文用专家抽检和众包一致性当信誉论证，不是证明无偏。

## 在线和离线：测的不是同一个东西

| | 离线榜（MMLU、HumanEval、AIME） | Arena |
| --- | --- | --- |
| 题 | 固定、可回归 | 活的，用户自带，分布漂移 |
| 分数 | 对错 / pass@k | 成对偏好 |
| 泄漏 | n-gram、教师、改写，见 `align-eval-contam` | 用户粘贴考题、刷票、识别模型文风 |
| 长度 | 通常不奖啰嗦 | 默认奖长文，除非做 style control |
| 用途 | 训练过程监控、能力切片 | 聊天产品是否讨人喜欢 |

Grok-3 博文同时报 AIME / GPQA / LiveCodeBench **和** Arena Elo。正确读法：前者是 STEM 切片（仍要问截止日、cons@k、是否 Think），后者是偏好切片。用 Elo 证明预训练数据配比，或用 AIME 证明「用户更喜欢」，都是跨指标走私。Arena 提示比 MMLU 更像真实聊天，但也更脏、更不稳定。

污染两边都有。离线：训练见过题面。在线：用户把明天的考试题贴进 Arena，模型若在预训练或后训练见过同类，投票像能力。Arena 题不可复现成稳定回归集，除非他们另发静态子集（Arena-Hard 一类）。内部决策应：离线切片 + 私有新鲜题 + 有限的在线偏好，而不是「Elo 第一就发版」。

不要神化的具体句子：

- 点估计 1402 没有带着当时的 CI 和对手集合，过一周提示混合变了，名次可以换。
- 票数不够时，「领先」可能只是区间重叠下的排序噪声。
- 人格更冲、更幽默的模型可以赢 Arena、在拒答和事实性上更差。xAI 公开叙事吃「最大求真」，Arena 吃的是点击偏好，两者不必一致。
- 公司博文是营销快照。面试引用要说「官方自报、当日排行榜」，不要说「所以 Grok-3 是最强基座」。

## 追问

- **为什么还要看 Arena？** 因为它抓到了静态榜抓不到的指令风格和开放式任务。当 **一个** 偏好传感器，和离线切片一起看。单独当北星会被长度和讨好优化。
- **BT 和 Elo 谁对？** 同一类强度模型；BT 全局估计更稳、CI 更诚实。在线 Elo 适合直播打分，不适合当论文主表。
- **内部能不能自建 Arena？** 能，但要解决刷票、员工识别自家模型、提示泄漏到训练集。员工 Arena 会偏内部口味。更干净的是盲测 + 预注册题库 + 长度控制。
- **Grok 在 Arena 赢了是否说明预训练更好？** 不能直接下这个结论。后训练、系统提示、工具（搜网）都会改投票。预训练主张仍只能用 `xai-grok-pretrain` 里那些公开事实，不要用 Elo 反推数据配比。
