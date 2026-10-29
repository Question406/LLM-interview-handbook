---
id: kuaishou-dpo-cautions
section: posttrain
order: 163
level: A
title: 快手：DPO 训练要注意什么？
quick: >-
  DPO 最要紧的是数据：偏好对只在关键属性上有差别、控制长度 bias，再盯住 chosen 概率别塌、$\beta$ 别太小。数据脏或 rejected
  其实更好时，DPO 会学到相反的偏好；需要探索的工具轨迹它也补不了，那是 GRPO 的事。
tags:
  - Kuaishou
  - DPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 快手大模型LLM二面分享-日常实习
    url: 'https://www.nowcoder.com/feed/main/detail/058475a3d9204493bc145510c72e10f1'
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型 LLM 日常实习
- 届别 / 流程：日常实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-03-31
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“在进行 DPO 训练时，通常有哪些关键的注意事项？是否了解过 GRPO”**

DPO 训练我最先看数据，其次看 chosen 曲线。它在静态偏好对上直接更新策略，数据一脏就学反，也探索不了没见过的工具轨迹。所以要检查三件事：偏好对是不是只在目标属性上有差别、生成分布有没有偏离 reference model、chosen 概率有没有大幅下降。把 DPO 当成「更先进的 PPO」或者「丢进去就能对齐」，面试官会追着问。

先说数据。Chosen 和 rejected 最好只差在正确性或安全上。比如一篇长、一篇短，还混着风格、emoji 和拒答，那

$$
\mathcal{L}_{\mathrm{DPO}}=-\log\sigma\Big(\beta\big(\Delta\log\pi_\theta-\Delta\log\pi_{\mathrm{ref}}\big)\Big)
$$

就会把长度和套话当成偏好学进去，其中 $\Delta\log\pi=\log\pi(y_w\mid x)-\log\pi(y_l\mid x)$。更致命的是标注反了，rejected 其实更好，梯度方向整体反号，比「对不够多」严重得多。做长度归一、加硬负样本（同长度、同风格、只错一个关键事实），比继续堆偏好对的数量有用。reference model 要冻结，chat 模板和线上一致，否则训练和推理用的表示不一样，偏好间隔就反映不了线上效果。

快手这类内容场景还要防一种情况：「更刺激、更长、更标题党」的回答被标成 chosen。这是产品偏好漏进了 DPO，上线后模型会更啰嗦或者更擦边。所以审数据要排在调 $\beta$ 前面。

再说优化。训练时同时画 chosen 和 rejected 的 logprob，以及隐式奖励间隔。Chosen 往下掉是常见病，原因可能是 $\beta$ 太小、学习率太大，或者模型在「拉开差距」，没去「抬高 chosen」：rejected 掉得比 chosen 快，loss 很好看，生成质量却变差。$\beta$ 太小，相对 ref 的约束就弱，策略会偏离 reference model；太大又几乎不更新。别拿训练 loss 单独决定早停。

其他失败还有语言漂移、拒答过猛、越说越长、通用能力往下掉，所以 holdout 偏好准确率、盲评 win-rate、长度、安全题要一起看。DPO 没有显式 reward model 的评分曲线，overfitting 了更要去看实际生成的结果。reference model 中途换掉等于换了坐标系，旧的 margin 就没法比了，一般冻结 SFT 模型当 $\pi_{\mathrm{ref}}$。

同帖还问了 GRPO，这里要主动对比。有自动 verifier、又需要探索新轨迹时，用组 sampling RL。DPO 只能在已有的 $y_w,y_l$ 之间拉开差距：工具调用的正确参数从来没出现在 chosen 里，DPO 不会凭空发明它。DPO 之后如果同一道题 sampling 出来几乎都一样，再接 GRPO 会是零优势，要先看组内奖励方差和 unique response 比例。PPO 和 DPO 的区别是一个在线打分加 sampling、一个用离线偏好直接更新策略，两者之间谈不上升级关系，别说 DPO 替代了在线探索。

还有些情况 DPO 本来就管不到：偏好覆盖不到的安全长尾、必须搜索的推理题、标注噪声很高的创意内容。这些该换数据或者换算法，把 $\beta$ 再扫一轮没用。

## 追问

**Chosen logprob 掉了还能用吗？**
先降学习率、加大 $\beta$、查长度 bias；holdout 也掉了就回滚，别用「loss 还在降」说服自己。

**要不要定期换 $\pi_{\mathrm{ref}}$？**
一般冻结。换 ref 等于换坐标系。

**IPO / SimPO 解决什么？**
它们是针对参考依赖和长度的变体。先把数据弄干净，再考虑换损失。

**了解 GRPO 吗？**
有 verifier 就做组 sampling；组内全对或全错时梯度为零。DPO 和 GRPO 的数据假设不同，别混成一句「都是后训练」。
