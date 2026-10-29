---
id: kuaishou-dpo-vs-rm-train
section: posttrain
order: 145
level: S
title: 快手：DPO 训练和 PPO 的 reward model 训练一样吗？
quick: >-
  不一样。reward model（RM）训练是在偏好对上拟合一个标量打分器，训完冻结再交给 PPO；DPO 没有打分头，直接优化策略相对 reference
  model 的 log 比。数据可以是同一批偏好对，计算图、优化对象和失败模式都不同。
tags:
  - Kuaishou
  - DPO
  - Reward Model
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 快手日常实习大模型算法面经
    url: 'https://www.nowcoder.com/feed/main/detail/9d24592752804d2790557f81230df62d'
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“DPO 的训练和 PPO 的 reward model 的训练过程是否一样”**

不一样。RM 训的是一个打分器，策略不在这张图里更新；DPO 没有打分头，更新的就是 $\pi_\theta$。两者都可能用偏好对，所以很多人答「都用偏好对，所以一样」，可计算图、优化对象和失败模式都不同。原帖还连问了 GRPO / DAPO，最好准备一句话对比：有没有显式 RM、有没有在线 sampling，别把所有后训练都说成 RM 训练。

先看 RM。输入 $(x,y)$，输出 $r_\phi(x,y)$，用 Bradley-Terry 让 chosen 的分高于 rejected：

$$
\mathcal{L}_{\mathrm{RM}}=-\log\sigma\big(r_\phi(x,y_w)-r_\phi(x,y_l)\big).
$$

训完冻结 $\phi$，PPO / GRPO 的 sampling 轨迹（rollout）拿 $r_\phi$ 当奖励，通常再减一项 KL。策略 $\pi_\theta$ 不出现在 RM 的梯度里。RM 可以和 actor 同结构，但它优化的是打分间隔，跟生成似然无关。

RM 坏的方式是 overfitting、对长度敏感、out-of-distribution 乱打分，接着 PPO 就去钻奖励规则的空子，训练 reward 往上涨，真实偏好往下掉。这是「先 RM 后 RL」这条链路特有的病。好处是你手里有一张能审计的 $r_\phi$，可以单独测 RM accuracy、calibration、对抗样本，DPO 没有这条独立的曲线。RM 还要把人的偏好压成一个标量，这里有信息损失：安全、有用、简短几个目标揉进一个 $r_\phi$，PPO 只能追着这个标量的漏洞跑。这些虽然不是 DPO 的训练过程，却说明了「过程不一样」会怎样影响后面的 RL。

再看 DPO。它从同一个 BT 假设出发，再加上「最优策略和 RM 是对数线性关系」，把 $r$ 换成 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，loss 就落在 chosen / rejected 相对 reference model 的 log 比上。没有单独的 reward 头，一次直接更新 $\theta$。它绕开的是在线 RL 环和显式 RM，偏好数据照样要，reference policy 也照样要有一条。

DPO 坏的方式是概率比被拉得极大、chosen 的绝对 logprob 塌掉、语言漂移、越说越长，overfitting 的是策略本身。没有能单独评测的打分头，就更要靠 holdout 偏好和生成质量做 acceptance checks。假设不成立时，比如偏好不可传递、标注噪声高、最优策略并不满足那条闭式关系，DPO 照样能把 loss 降下去，学到的却不是你以为的那个 RM。

所以数据可以同源，过程不能说一样。一个先学 $r_\phi$ 再冻结；一个从头到尾不出现 $r_\phi$，只在假设里当它存在。放到一起比：RM+PPO 有显式打分器加在线 sampling；DPO 有偏好对，没有打分器，也没有 rollout；GRPO 常常不用 RM，用规则奖励加组 sampling。别说 DPO「包含了」RM 训练，它包含的只是 RM 的闭式假设。同一批偏好对可以既训 RM 做对照、又训 DPO，可 RM acc 高不代表 DPO 已经对齐，DPO loss 低也不代表 RM calibration 得好。

## 追问

**DPO 是不是隐式 RM？**
在 BT 加最优策略的假设下可以这么解释，但实现上没有能单独评测的打分头。

**PPO 的 RM 为什么要和 actor 分开？**
分开才能把打分器冻住，免得一边改策略一边改尺子。DPO 是把尺子折进了 $\pi_\theta$ 对 $\pi_{\mathrm{ref}}$ 的比里。

**能不能先训 RM 再当 DPO 的教师？**
可以做实验，但那就已经是用 RM 造偏好或造奖励了，算不上标准 DPO。

**两边的失败怎么区分？**
RM overfitting 表现为 PPO hacking；DPO overfitting 表现为 margin 极大、生成漂移。用现象说话，光说「overfitting」不够。
