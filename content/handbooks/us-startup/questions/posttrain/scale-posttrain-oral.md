---
id: scale-posttrain-oral
section: posttrain
order: 1
level: S
title: Scale：MLE 第一面是后训练八股，公开帖没写出问了哪几条
quick: >-
  如果面试官让我讲 post-training，我会从手上有什么反馈说起：有合格示范可以做 SFT，有成对偏好可以考虑 DPO 或 RM，有可执行检查可以用
  verifier 提供 reward。
tags:
  - Scale AI
  - Post-training
  - DPO
  - RLHF
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Scale AI 完整版挂经，2026 年 1–3 月 MLE
    url: 'https://www.1point3acres.com/bbs/thread-1163920-1-1.html'
    type: candidate-first-hand
  - title: 'Staff MLRE, Agent Post-training'
    url: 'https://job-boards.greenhouse.io/scaleai/jobs/4625337005'
    type: primary
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: 'DeepSeekMath, GRPO'
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
---

## 回答思路

> **问题与场景：** 如果面试官让我讲 post-training，我会从手上有什么反馈说起：有合格示范可以做 SFT，有成对偏好可以考虑 DPO 或 RM，有可执行检查可以用 verifier 提供 reward。
>
> **做法与原因：** 例如代码修复能在独立测试中判对错，未必需要先训练一个 RM；开放写作的好坏则可能需要人工偏好与 rubric。
>
> **检查与取舍：** 最后用独立质量与原能力回归验证。

## 可以这样回答

如果面试官让我讲 post-training，我会从手上有什么反馈说起：有合格示范可以做 SFT，有成对偏好可以考虑 DPO 或 RM，有可执行检查可以用 verifier 提供 reward。

例如代码修复能在独立测试中判对错，未必需要先训练一个 RM；开放写作的好坏则可能需要人工偏好与 rubric。PPO、GRPO 的选择要接着讨论 baseline、rollout 与计算成本。

最后用独立质量与原能力回归验证。这是针对公开方向的准备回答，来源只证实存在 post-training 问答，没有披露具体考题。

## 技术备查

这份公开面经确认了两轮的主题：第一面问后训练八股，第二面由 hiring manager 聊项目；具体八股题藏在积分后面。准备这轮时，我会按手里有什么数据来讲方法：有演示做 SFT，有偏好对考虑 reward model 加 PPO 或 DPO，有验证器考虑 RLVR。

帖子在一亩三分地，2026 年 1–3 月，Machine Learning Engineer，博士，全职，猎头联系。Onsite 之后挂了，作者说公司没告诉他挂在哪一轮，他自己猜是行为面。他原话说技术面「毫无技术含量」：第一面 post training 八股，第二面 hiring manager 聊他现在的项目。帖子后半要积分，公开摘要就停在这儿。

回帖里有人问了三件帖子里看不到答案的事：ML coding 用 PyTorch 还是 NumPy；是给现成的 Transformer 让你加 feature，还是从头写；sampling 是不是 top-k。还有人直接问「八股都问了什么」。这些是读者的猜测，楼主没确认过题面。汇总站上的「手写 nucleus sampling」「手写 causal attention」我也没收进这张卡。能参考的是 Scale 自己的 Agent Post-training 岗位，上面写明要会 RLHF、RLVR、PPO、GRPO，以及过程奖励和结果奖励。那是招聘要求，跟这帖的逐字题对不上号，过程奖励和结果奖励见 `scale-process-outcome`。

面试官让我讲后训练，我会每一步先说需要什么数据。手里有带标准答案的演示 $(x, y^{\ast})$，就做 SFT，损失是每个 token 的 negative log likelihood。麻烦在演示贵，而且很多时候「更好」写不出一个唯一的 $y^{\ast}$。

只有好坏对 $(x, y_w, y_l)$ 的时候，先训一个 Bradley-Terry reward model：

$$
P(y_w \succ y_l \mid x) = \sigma\big(r(x,y_w) - r(x,y_l)\big)
$$

再用 PPO 优化策略。PPO 要在显存里同时放策略、reference model、reward model、value network。reward model 还会被策略钻空子，表现是静态偏好集上的准确率在涨，线上人评在掉。

同一批偏好对也可以做 DPO，训练时没有单独的 reward model：

$$
\mathcal{L} = -\mathbb{E}\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)} - \beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big)
$$

DPO 没有 on-policy 探索。偏好对要是来自另一个模型，$\pi_{\mathrm{ref}}$ 又是你要训的这个基座，隐式奖励就对不上。

有验证器的时候，比如单测、数学对错、工具返回值的字段和类型是否符合 schema，就用 RLVR，奖励是验证器给的 0/1，不必先训 reward model。GRPO 对同一题抽一组回答，优势用组内均值和标准差算，不再训 value network。最后可以补一句：Scale 卖的经常就是这三样的上游，偏好对、评分细则、可验证的环境。

## 追问

**reward model 离线更准了，策略却更差，怎么回事？**
离线那批对是旧分布。策略离开那批对之后，reward model 会把长、空、格式漂亮的回答打高。我会先 on-policy 真正 sampling 出来的回答上让人再打一轮分，再把长度和奖励的相关系数画出来。

**$\beta$ 怎么选？**
太大，策略贴着 reference model，偏好学不动；太小，不被偏好的回答（rejected）的概率可能被压得过低，chosen 也不一定升高。所以我会报训练前后两边的平均 log probability，光报 loss 看不出来。

**top-k 是他们的 coding 题吗？**
这帖没有确认。要是临场让写 sampling，我先把 temperature 除在 logits 上，再做 top-k 截断、renormalization。nucleus 是按概率从大到小累加到 $p$ 再截断，和 top-k 是两种截法，别写成同一个 if。
