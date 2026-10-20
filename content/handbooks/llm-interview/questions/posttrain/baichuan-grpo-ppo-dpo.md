---
id: baichuan-grpo-ppo-dpo
section: posttrain
order: 148
level: A
title: 百川智能：讲一下 GRPO，以及和 PPO、DPO 的差别？
quick: "GRPO 比较同一道题多个回答的得分来计算优势，省去价值评估模型（critic）。PPO 用奖励和价值估计计算优势，再裁剪策略更新；DPO 用离线偏好对优化策略相对参考模型的对数概率比。R1 类流程常先用 SFT 冷启动，再做 GRPO；选择取决于数据和奖励信号。"
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

这块容易把 R1 背成某家内部配方，或者把 GRPO / PPO / 直接偏好优化（DPO） 说成「谁更新谁更好」。公开叙事只有三步：先冷启动格式和基本推理，再用可验证奖励做基于组采样的强化学习（GRPO 一族），中间可能穿插拒绝采样。重点是奖励可执行加 online 探索，不是背超参。选型逻辑和蚂蚁那张卡相同，但这题必须能接上 R1 流程：为什么先做 SFT、为什么 DPO 不够、为什么可以省去 critic。答不到流程，只报三行公式，会被当成背手册。

## GRPO 白板：组相对，省 critic

同一输入提示采 $n$ 条回答，$n\gt 1$ 否则优势未定义，见 `sys-rl-group-n`：

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon},\qquad
\mathcal{L}=-\mathbb{E}\big[\min(\rho\hat A,\,\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)\hat A)\big].
$$

其中 $\rho=\pi_\theta/\pi_{\mathrm{old}}$。组均值代替 learned $V$，所以省 critic。失败模式要主动报：整组全对或全错则 $\hat A=0$，这一步白算；靠写长回答碰到正确结果；验证器有漏洞，就会强化利用漏洞的行为。KL 是可选的反向正则，期望在当前策略上取，见 `fund-kl-directions`。PPO 风格的 clip 在有利方向越界时会把该 token 的梯度打成 0，长 CoT 时这是已知问题，CISPO 改 clip 对象，见 `pt-cispo`。数学题常见 $n=8$ 到 $16$，先看非零优势组占比再加。

## PPO 与 DPO：信号从哪来

PPO：奖励模型或环境给 $r$，critic 给 $V$，GAE 降方差，四件套更重，适合复杂连续权衡。R1 类任务奖励往往是对/错，长 CoT 上训一张可靠 $V$ 又贵又易漂，所以不作为默认。DPO：不在线采样，直接拉 $\log(\pi_\theta/\pi_{\mathrm{ref}})$ 的 chosen / rejected 差，适合已有偏好对。推理任务示范覆盖不全，DPO 探不到新思维链，也更新不了「当时错了的那条」。R1 公开流程因此是 SFT 冷启动再 GRPO。冷启动不过关，组采样全是格式失败，优势一样为零。

## 追问

- **R1-Zero 呢？** 跳过 SFT 直接做可验证奖励强化学习（RLVR），格式检查更难通过，也更难获得有学习信号的组；多数业务仍要冷启动。
- **组全错怎么办？** 零梯度。换难度、升温、加 $n$，或 DAPO 滤零方差组，不要先加学习率。
- **和拒绝采样的关系？** RS 只留正例再 SFT，负例被扔；GRPO 负例提供 $\hat A\lt 0$，信息量不同。
- **为什么 PPO 可以 $n=1$？** 有 $V(s)$ 当 baseline。GRPO 故意不训 value，才必须 $n\gt 1$。
- **DPO 穿插在 R1 里干什么？** 对齐风格或安全，不能替代可验证奖励上的探索。有 pair 就用，没有就别硬造。
