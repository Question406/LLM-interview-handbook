---
id: kuaishou-dpo-vs-rm-train
section: posttrain
order: 145
level: S
title: 快手：DPO 训练和 PPO 的奖励模型训练一样吗？
quick: "不一样。奖励模型（RM） 训练是对偏好对拟合标量分；直接偏好优化（DPO） 直接优化政策的 log 比，没有单独打分头。数据都可能是偏好对，但图、目标和失败模式不同。"
tags:
  - Kuaishou
  - DPO
  - Reward Model
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手日常实习大模型算法面经
    url: https://www.nowcoder.com/feed/main/detail/9d24592752804d2790557f81230df62d
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“DPO的训练和PPO的奖励模型的训练过程是否一样”**

常见误区是：答「都用偏好对，所以一样」。数据形态可以相似，计算图、优化对象和失败模式不同。RM 训的是打分器，政策不在这张图里更新；直接偏好优化（DPO） 没有打分头，更新的就是 $\pi_\theta$。原帖还连问 GRPO / DAPO，准备好用「有没有显式 RM、有没有在线采样」一张表对比，不要把所有后训练都说成 RM 训练。

## 1. RM：拟合标量，冻结后再给 PPO

输入 $(x,y)$，输出 $r_\phi(x,y)$。Bradley-Terry 让 chosen 分高于 rejected：

$$
\mathcal{L}_{\mathrm{RM}}=-\log\sigma\big(r_\phi(x,y_w)-r_\phi(x,y_l)\big).
$$

训完冻结 $\phi$，PPO / GRPO 的 采样轨迹（rollout） 用 $r_\phi$ 当奖励（常再减 KL）。政策 $\pi_\theta$ 不出现在 RM 的梯度里。RM 可以和 actor 同结构，但优化目标是打分间隔，不是生成似然。失败：RM 过拟合、对长度敏感、分布外乱打分，随后 PPO 会 钻奖励规则的空子，训练 reward 上涨、真实偏好掉。这是「先 RM 后 RL」链路特有的病：你有一张可拿去审计的 $r_\phi$，也可以单独做 RM accuracy、校准、对抗样本；DPO 没有这张独立曲线。

RM 还承担「把人的偏好压缩成标量」的信息损失。多目标（安全、有用、短）揉进一个 $r_\phi$ 时，PPO 只能追这个标量的漏洞。这不是 DPO 训练过程，但解释了为什么「过程不一样」会影响后面的 强化学习（RL）。

## 2. DPO：闭式消掉 $r$，直接改政策

从同一 BT 假设加「最优政策与 RM 的对数线性关系」出发，DPO 把 $r$ 换成 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，loss 落在 chosen / rejected 相对参考模型的 log 比上。没有单独 reward 头，一次更新 $\theta$。它绕开的是在线 RL 环和显式 RM，不是绕开偏好数据，更不是绕开「要有一条参考政策」。

失败：概率比被拉到极大、chosen 绝对 logprob 塌、语言漂移、越说越长。过拟合的是政策本身。没有可单独评测的打分头，更要靠 holdout 偏好与生成质量门禁。假设不成立时（偏好不可传递、标注噪声高、最优政策并不满足那条闭式），DPO 仍会降 loss，学到的不是你以为的 RM。

因此：数据可以同源，过程不可以称为一样。一个先学 $r_\phi$ 再冻结；一个永不出现 $r_\phi$，但在假设里假装它存在。

## 3. 和 GRPO 放在同一张对比表里

口诀：RM+PPO 有显式打分器加在线采样；DPO 有偏好对、无打分器、无 rollout；GRPO 常无 RM、用规则奖励加组采样。不要说 DPO「包含了」RM 训练，它包含的是 RM 的闭式假设，不是那张训练图。同一批偏好对可以既训 RM 做对照，又训 DPO，但 RM acc 高不代表 DPO 已对齐，DPO loss 低也不代表 RM 校准好。

## 追问

- **DPO 是不是隐式 RM？** 在 BT 加最优政策假设下可以这么解释，但实现上没有可单独评测的打分头。
- **PPO 的 RM 为啥要和 actor 分开？** 分开才能冻住打分器，避免一边改政策一边改尺子；DPO 把尺子折进了 $\pi_\theta$ 对 $\pi_{\mathrm{ref}}$ 的比。
- **能不能先训 RM 再当 DPO 的教师？** 可以做实验，但那已经不是标准 DPO，而是用 RM 造偏好或造奖励。
- **失败怎么区分？** RM 过拟合表现为 PPO hacking；DPO 过拟合表现为 margin 极大、生成漂。用现象说话，不要只说「过拟合」。
