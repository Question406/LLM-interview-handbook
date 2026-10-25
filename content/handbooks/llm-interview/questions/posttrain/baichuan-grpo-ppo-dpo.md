---
id: baichuan-grpo-ppo-dpo
section: posttrain
order: 148
level: A
title: 百川智能：讲一下 GRPO，以及和 PPO、DPO 的差别？
quick: "GRPO 对同一道题采多个回答，用组内得分的相对高低算优势，所以省掉价值评估模型（critic）。PPO 用奖励和价值估计算优势再裁剪更新，DPO 用离线偏好对优化策略相对参考模型的对数概率比。R1 类流程常先 SFT 冷启动再做 GRPO，选哪个取决于数据和奖励信号。"
tags:
  - Baichuan
  - GRPO
  - PPO
  - DPO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“r1模型有了解么 说一下流程”**；**“grpo算法说一下 ppo和dpo”**

GRPO 对同一道题采多条回答，用组内得分的相对高低算优势，所以不用训练价值评估模型（critic）；PPO 靠奖励模型和 critic 算优势，直接偏好优化（DPO）不采样，直接吃离线偏好对。这题我会接到 R1 的流程上讲：为什么先做 SFT、为什么 DPO 不够、为什么可以省掉 critic。只报三行公式、讲不出流程，会被当成背手册。

R1 的公开叙事只有三步：先冷启动格式和基本推理，再用可验证奖励做组采样强化学习（GRPO 一族），中间可能穿插拒绝采样。重点在奖励可执行加上 online 探索，超参不用背，也别把它说成某家的内部配方。三个算法也别排成「谁更新谁更好」。

GRPO 的白板是这样的：同一个输入提示采 $n$ 条回答，$n\gt 1$，否则优势没有定义，见 `sys-rl-group-n`：

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon},\qquad
\mathcal{L}=-\mathbb{E}\big[\min(\rho\hat A,\,\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)\hat A)\big].
$$

其中 $\rho=\pi_\theta/\pi_{\mathrm{old}}$。比如一道数学题采了一组回答，有对有错，对的那几条优势为正、被推高，错的为负、被压低，基线就是组均值，用不着学一个 $V$。失败模式要主动讲：整组全对或全错时 $\hat A=0$，这一步白算；模型可能靠写长回答碰到正确结果；验证器有漏洞，就会强化利用漏洞的行为。KL 是可选的反向正则，期望在当前策略上取，见 `fund-kl-directions`。PPO 风格的 clip 在有利方向越界时会把该 token 的梯度打成 0，长 CoT 上这是已知问题，CISPO 改的是 clip 的对象，见 `pt-cispo`。数学题常见 $n=8$ 到 $16$，先看非零优势组占比，再决定要不要加。

PPO 的信号来自奖励模型或环境给的 $r$，critic 给 $V$，GAE 降方差，四个模型一起跑，更重，适合复杂的连续权衡。R1 这类任务的奖励往往只有对和错，在长 CoT 上训一张可靠的 $V$ 又贵又容易漂，所以不当默认。DPO 不在线采样，直接拉开 chosen 和 rejected 的 $\log(\pi_\theta/\pi_{\mathrm{ref}})$ 差，适合已经有偏好对的情况。推理任务的示范覆盖不全，DPO 探不到新的思维链，也更新不了「当时错了的那条」。所以 R1 的公开流程是 SFT 冷启动再 GRPO。冷启动没过关，组采样全是格式失败，优势照样为零。选型逻辑和蚂蚁那道题一样，按信号来。

## 追问

**R1-Zero 呢？**
它跳过 SFT 直接做可验证奖励强化学习（RLVR），格式检查更难通过，也更难拿到有学习信号的组。多数业务还是要冷启动。

**组全错怎么办？**
那一步是零梯度。换难度、升温、加 $n$，或者用 DAPO 滤掉零方差组，别先加学习率。

**和拒绝采样是什么关系？**
RS 只留正例再做 SFT，负例被扔掉；GRPO 的负例提供 $\hat A\lt 0$，两者的信息量不一样。

**为什么 PPO 可以 $n=1$？**
因为它有 $V(s)$ 当 baseline。GRPO 故意不训 value，所以必须 $n\gt 1$。

**DPO 穿插在 R1 流程里干什么？**
对齐风格或安全，替代不了在可验证奖励上的探索。有 pair 就用，没有就别硬造。
