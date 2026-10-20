---
id: scale-posttrain-oral
section: posttrain
order: 1
level: S
title: Scale：MLE 第一面是后训练八股，公开帖没写出问了哪几条
quick: >-
  2026 年初一位博士 MLE 的第一面被他自己叫做 post-training 八股，第二面是 hiring manager 聊现有项目。
  八股的原话在公开帖里被藏了。回帖问 sampling 是不是 top-k、代码是 PyTorch 还是 NumPy，楼主没在可见部分回答。
tags:
  - Scale AI
  - Post-training
  - DPO
  - RLHF
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Scale AI 完整版挂经，2026 年 1–3 月 MLE
    url: https://www.1point3acres.com/bbs/thread-1163920-1-1.html
    type: candidate-first-hand
  - title: Staff MLRE, Agent Post-training
    url: https://job-boards.greenhouse.io/scaleai/jobs/4625337005
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 真题记录

一亩三分地，2026 年 1–3 月，Machine Learning Engineer，博士，全职，猎头。Onsite 之后挂了，作者说没告诉他挂在哪一轮，自己猜是行为面。原话是技术面「毫无技术含量」：第一面 post training 八股，第二面 hiring manager 聊他现在的项目。帖子后半要积分，公开摘要停在这里。

回帖在问三件帖子里看不见答案的事：ML coding 用 PyTorch 还是 NumPy；是给现成 Transformer 让你加 feature，还是从头写；sampling 是不是 top-k。另有人直接问「八股都问了什么」。这些是读者的猜测，不是楼主确认的题面。汇总站上的「手写 nucleus sampling」「手写 causal attention」我没有收进这张卡。

Scale 自己的 Agent Post-training 岗位写明要会 基于人类反馈的强化学习（RLHF）、基于可验证奖励的强化学习（RLVR）、PPO、GRPO，以及过程奖励和结果奖励。那是招聘要求，不是这帖的逐字题。过程奖励和结果奖励见 `scale-process-outcome`。

## 八股我会按数据讲

面试官说「讲后训练」时，我按这条链路讲，每一步先说需要什么数据。

有标准答案的演示 $(x, y^{\ast})$，做监督微调（SFT），损失是每个 token 的负对数似然。演示贵，而且「更好」往往写不出唯一的 $y^{\ast}$。

只有好坏对 $(x, y_w, y_l)$ 时，先训 Bradley-Terry 奖励模型：

$$
P(y_w \succ y_l \mid x) = \sigma\big(r(x,y_w) - r(x,y_l)\big)
$$

再用 PPO 优化策略。PPO 同时在显存里放策略、参考模型、奖励模型、价值网络。奖励模型会被策略钻空子：静态偏好集上的准确率上升，线上人评下降。

同一批偏好对也可以做直接偏好优化（DPO），训练时没有单独的奖励模型：

$$
\mathcal{L} = -\mathbb{E}\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)} - \beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big)
$$

DPO 没有 on-policy 探索。偏好对若来自另一个模型，而 $\pi_{\mathrm{ref}}$ 是你要训的这个基座，隐式奖励对不上。

有验证器时（单测、数学对错、工具返回值的字段和类型是否符合 schema）用 RLVR，奖励是验证器的 0/1，不必先训奖励模型。GRPO 对同一题抽一组回答，优势用组内均值和标准差，不再训价值网络。Scale 卖的经常是这三样的上游：偏好对、评分细则、可验证的环境。

## 追问

**奖励模型离线更准，策略反而更差？** 先在策略真正采样的回答上让人再打分。离线对是旧分布。策略离开那批对之后，奖励模型会把长、空、格式漂亮的回答打高。长度和奖励的相关系数先画出来。

**$\beta$ 怎么选？** 太大时策略贴着参考模型，偏好学不动。太小则 不被偏好的回答（rejected）的概率可能被压得过低，chosen 也不一定升高。我会报训练前后两边的平均对数概率，不只报 loss。

**top-k 是不是他们的 coding 题？** 这帖没有确认。若临场要写采样，我会先写 temperature 除在 logits 上，再 top-k 截断后重新归一化。nucleus 是按概率从大到小累加到 $p$ 再截断。不要把 top-k 和 top-p 写成同一个 if。
