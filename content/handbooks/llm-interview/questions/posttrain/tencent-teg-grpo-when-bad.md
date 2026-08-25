---
id: tencent-teg-grpo-when-bad
section: posttrain
order: 207
level: S
title: 腾讯 TEG：什么情况下使用 GRPO 效果会不好？构造数据要符合什么要求？
quick: >-
  奖励不可靠、组内几乎无方差、任务不可验证、或示范格式都未建立时 GRPO 差。数据上要可打分、难度有梯度、同
  prompt 多样本可区分，并严格防泄漏与刷分捷径。
tags:
  - Tencent
  - TEG
  - GRPO
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯TEG大模型算法暑期实习一面分享
    url: https://www.nowcoder.com/feed/main/detail/9e335a807ea44e3fafb0d1ab4a7f2fe7
    type: candidate-first-hand
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary-paper
---

## 真题记录

- 公司：腾讯 TEG
- 岗位：大模型算法暑期实习；一面
- 原始措辞：**“什么情况下使用 GRPO 效果会不好”**；**“使用 GRPO 时，构造数据要符合什么要求”**

腾讯 TEG 一面这题，这块容易背「GRPO 省 critic、组内标准化」却说不清何时失效。GRPO 的信号完全来自同一 prompt 下组内相对优势；奖励噪声、组内无方差、或策略还不会格式时，优势要么是噪声要么全是 0，算法再省 critic 也学不动。数据要求不是「多采几条」，而是让组内可区分、可复核、难易有梯度。把这题答成 PPO 对比可以，但必须先承认：差的不是「没有 value」，而是相对优势没有可学方向。

## 哪些条件下 GRPO 会差

1. **奖励噪声大 / 可 hack**：开放生成只靠弱 LLM-as-judge，组内排序不稳，策略会刷文风和长度。
2. **组内无区分度**：题过易或过难，全对或全错，标准化后优势为 0，算力打在无效 group 上。
3. **基础能力不足**：格式、工具 schema、解题模板都不会，应先 SFT / 冷启动，而不是直接稀疏 RL。
4. **采样分布离线太远**：prompt 与上线域差太远，组内对比学到的是域外捷径。

GRPO 适合可验证任务（数学、代码、结构化约束）。偏好已有、无可验证 oracle 时，离线 DPO / SimPO 往往更稳，不要为了「在线」硬上 GRPO。原理见 `pt-grpo`，全对全错见 `byte-grpo-all-same-zero-adv`。开放生成若必须上 GRPO，先把可执行约束从生成里拆出来当主奖励。

## 数据要让组内可打分、可区分

当作 checklist 答：

- 每条有**可复核**成功标准：规则、单测、结构化字段，而不是不可复核的 CoT 观感；
- 同一 prompt 能采出**有方差**的组，过易过难都要过滤或改难度；
- 覆盖目标难度与失败模式，不要只堆易题把 reward 刷满；
- train / eval 隔离，防题面与标准答案泄漏；
- 记录 reward 定义版本，改规则后旧轨迹不能混训。

过程分只覆盖可观测里程碑。反例集专门打 hacking：空程序、恒真断言、超长空话。构造时还要控制同一模板的复述比例，避免组内多样本其实是同一种错法。DAPO 用动态采样丢掉全对/全错组，是同一诊断的工程化，见 `xiaohongshu-dapo-vs-grpo`。上线分布要在数据里占到足够份额：只用竞赛题训出来的相对优势，迁不到客服或检索问答。我会把「何时差」和「数据清单」分成两段答，不混成一段 GRPO 介绍。

## 追问

- **为何不用 GRPO 而用 DPO？** 已有偏好对、无可执行 oracle、或需要离线稳定对齐时，DPO 更合适。
- **组变大能否救无方差？** 不能。全错组再大也是 0；要降难度、加示范或换 verifier。
- **弱 judge 能不能当奖励？** 可以当辅助，但主信号必须可复核，否则组内排序会漂。
- **数据最少要看哪些统计？** 有效 group 比例、组内奖励标准差、格式合规率、holdout 与训练 reward 是否同向。泄漏和规则改版混训也会让 GRPO「看起来差」，先查数据版本再改算法。
