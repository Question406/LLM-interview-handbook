---
id: kuaishou-dpo-cautions
section: posttrain
order: 163
level: A
title: 快手：DPO 训练要注意什么？
quick: >-
  偏好对只在关键属性上有差异、控制长度 bias、盯 chosen 概率不要塌、$\beta$
  不要过小。数据脏或 rejected 其实更好时，DPO 会学反；它也补不了需要探索的工具轨迹。
tags:
  - Kuaishou
  - DPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手大模型LLM二面分享-日常实习
    url: https://www.nowcoder.com/feed/main/detail/058475a3d9204493bc145510c72e10f1
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型 LLM 日常实习
- 届别 / 流程：日常实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-03-31
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“在进行DPO训练时，通常有哪些关键的注意事项？是否了解过GRPO”**

这块容易把 DPO 当成「更先进的 PPO」或「丢进去就能对齐」。DPO 在静态偏好对上直接改政策，数据一脏就学反；它也探索不了没见过的工具轨迹。注意事项全是在管对比是否干净、分布别漂、chosen 别塌。同帖还问 GRPO，要主动对比：有 verifier 就上组采样 RL，DPO 管不了没见过的成功路径。不要说 DPO 替代了在线探索。

## 1. 数据：对比要单因素，长度和标注是第一杀手

Chosen / rejected 最好只差正确性或安全，不要一篇长一篇短还混着风格、emoji 和拒答。否则

$$
\mathcal{L}_{\mathrm{DPO}}=-\log\sigma\Big(\beta\big(\Delta\log\pi_\theta-\Delta\log\pi_{\mathrm{ref}}\big)\Big)
$$

会把长度、套话当成偏好。其中 $\Delta\log\pi=\log\pi(y_w\mid x)-\log\pi(y_l\mid x)$。Rejected 其实更好、标注反了，梯度方向整体反号，比「对不够多」更致命。长度归一、硬负样本（同长度、同风格、只错关键事实）比再堆对更有用。参考模型冻结，chat 模板与线上一致，否则 log 比在训一套、推一套，margin 毫无意义。

快手这类内容场景还要防「更刺激、更长、更标题党」被标成 chosen。那是产品偏好泄漏进 DPO，上线会更啰嗦或更擦边。数据审查要比调 $\beta$ 优先。

## 2. 优化：盯 chosen 曲线，$\beta$ 和学习率联动

训练中同时画 chosen / rejected 的 logprob，以及隐式奖励间隔。Chosen 往下掉是常见病：$\beta$ 过小、学习率过大、或对在「拉开差距」而不是「抬高 chosen」，rejected 掉得比 chosen 更快，loss 很好，生成质量变差。$\beta$ 过小则相对 ref 的约束弱，政策漂；过大则几乎不更新。不要用训练 loss 单独早停。

失败模式还包括语言漂移、拒答过猛、越说越长、通用能力掉。Holdout 偏好准确率、盲评 win-rate、长度、安全题要一起看。DPO 过拟合没有一张可审计的 RM 曲线，更要靠生成门禁。参考模型中途更换等于改坐标系，旧 margin 不可比，一般冻结 SFT 当 $\pi_{\mathrm{ref}}$。

## 3. DPO 管不到的交给 GRPO；二者不是升级关系

有自动 verifier、需要探索新轨迹时上组采样 RL。DPO 只能在已有 $y_w,y_l$ 里拉差距，工具调用的正确参数若从未出现在 chosen 里，DPO 不会发明它。DPO 之后若同题采样几乎相同，再接 GRPO 会零优势，要先看组内 reward 方差和 unique response 比例。PPO vs DPO：离线偏好直接改政策 vs 在线打分加采样；不要说 DPO 是更先进的 PPO。

方法失败：偏好覆盖不到的安全长尾、必须搜索的推理题、标注噪声高的创意内容。这些该换数据或换算法，而不是把 $\beta$ 再扫一轮。

## 追问

- **Chosen logprob 掉了还能用吗？** 先降学习率、加大 $\beta$、检查长度 bias；holdout 掉了就回滚，不要用「loss 还在降」说服自己。
- **要不要定期换 $\pi_{\mathrm{ref}}$？** 一般冻结。换 ref 等于改坐标系。
- **IPO / SimPO 解决什么？** 参考依赖和长度等变体；先把数据弄干净，再换损失名。
- **了解 GRPO 吗？** 有 verifier 就组采样；组全对全错零梯度。DPO 和 GRPO 的数据假设不同，不要混成「都是后训练」。
