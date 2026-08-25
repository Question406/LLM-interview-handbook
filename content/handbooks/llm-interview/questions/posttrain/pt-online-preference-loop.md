---
id: pt-online-preference-loop
section: posttrain
order: 26
level: S
title: 为什么 Offline DPO 做到后面常要引入 Online Preference Loop？
quick: >-
  固定偏好数据只覆盖旧策略会生成的区域。policy 变强后会走出 dataset support，离线 pair
  的边际信息下降；在线循环通过当前策略采样、标注或打分、再更新，持续补齐新分布，但也把 reward hacking 和标注质量带回系统。
tags:
  - DPO
  - Online RLHF
  - Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Iterative Preference Learning
    url: https://arxiv.org/abs/2312.11456
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

Offline DPO 稳定又便宜，但它比较的是数据集已经写下来的回答，不是当前策略还会说的话。模型更新后概率质量会推向未被标注的新区域；此时继续重复旧 pair，既可能没有信息，也可能把数据里的长度、风格偏差放大成「越训越像训练集里的赢家」。DPO 公式没坏，是 off-policy 偏好数据相对策略的 coverage 塌了。别答成「DPO 不如 PPO」：先说 support 错位，再谈要不要上在线循环。旧 pair 只覆盖旧策略会生成的区域；模型变强后走进未标注地带，离线间隔没有信息，还可能把长度和风格偏差写成定律。在线循环用当前策略采样再标注来补齐新分布，但也把 hacking 和标注质量带回系统，必须配独立人评和停止条件。

## 离线 pair 为什么会过期

DPO 的间隔来自 chosen / rejected 相对 $\pi_{\mathrm{ref}}$ 的 log-prob 差。这对 $(y_w,y_l)$ 是在某一代策略（或人工写手）的分布上采的。策略 $\pi_\theta$ 变强之后：

- 它不再生成 $y_l$ 那种明显差回答，旧负样本变成「太容易的负例」，梯度接近零。
- 它开始生成旧数据里没有的高分续写。这些区域没有偏好标签，DPO 既不能奖励也不能惩罚，等于对 OOD 输出无约束。
- 旧 pair 里的长度、礼貌、列表体若与「赢」相关，会被反复强化，出现 length hacking 或风格塌缩。

所以「DPO 后期 loss 很小、离线 eval 还行、线上变差」常常是标签分布落后于策略分布，不是学习率没调好。Iterative DPO / online preference 的动机就是让对比样本重新落在当前 $\pi_\theta$ 会碰到的区域上。可以想成覆盖问题而不是优化器问题：离线 DPO 的梯度只在旧 pair 的 chosen/rejected 方向上有信号；策略一旦走到数据集支撑之外，loss 再低也管不着新失败模式。这和 SFT 后期「训练 CE 很小但用户问题 OOD」是同一类错位，只是偏好数据比示范更脆：pair 还依赖「当时什么算差回答」。Iterative Preference Learning 一类工作反复强调：用当前策略重生候选，再标注，才能把偏好学习维持在 on-policy 附近。

## 在线循环补的是新分布，不是再训一遍旧数据

一个最小闭环是：

1. 用当前或近期 policy 为同一 prompt 采样多个候选；
2. 用人工、RM 或 verifier 生成带置信度的偏好（或 pairwise ranking）；
3. 以严格版本化的 policy、prompt、labeler 记录数据，再做受 KL / 质量门控的更新；
4. 保留固定 held-out human eval，检查 online reward 是否与真正质量一起提升。

关键是谁采样：候选必须来自当前（或近几代）策略，标注必须针对这些候选。把旧离线数据再混进去当 replay 可以，但不能替代新 pair。若 RM 只给标量分，仍建议落成 pair 或过滤低置信对比，避免把绝对分数的尺度误差写进 DPO margin。

版本化不是记账癖好：没有 policy checkpoint 与 labeler 版本，你无法复现「这一批 pair 相对哪一代策略是 on-policy」，出了 hacking 也无法回滚。Prompt 集也应冻结一份对照集，否则 online 看起来在涨，其实是题变容易了。采样要够多样性：同一 prompt 只抽两条极相近的回答，标注员给不出稳定偏好，DPO margin 会变成噪声。常见做法是温度或 nucleus 稍放开、过滤近重复，再送给 RM 或人。若用 RM 打分，低分差的 pair 应丢掉或降权，避免把校准很差的尺度写进间隔。在线循环的吞吐量往往受标注而不是反传限制，所以要先设计「哪些 prompt 值得采」。旧数据上已经饱和的题可以少采，策略新失败的题多采。

## 自己的 judge 给自己打分

Online loop 把 reward hacking 和标注质量重新请回系统。RM 若与策略联合漂移，双方会商定一套「高分但无用」的写法：更长、更列表、更安全套话。因此必须：

- 独立审计集：人工或更强 judge，不参与训练更新；
- 对抗样本与格式扰动：长度、重复、拒答、工具幻觉；
- 数据去重：避免同一高分模板被反复采样、反复标成 winner。

Online reward 升、held-out 人评不动，就该停循环、修 RM / 规则，而不是更频繁地训练。KL 到 $\pi_{\mathrm{ref}}$ 或到上一迭代仍有用，但解决不了「新区域的标签是假的」。在线不是免费的 on-policy 魔法，它只是把数据收集重新对准当前策略。还要防数据回放污染：同一高分模板被反复采、反复标成 winner，等于把 RM 的一个峰写成数据集定律。去重应按轨迹近邻或 n-gram，而不是只按 prompt id。安全与拒答要单独留固定离线集，online 循环默认会少采「无聊但正确」的拒答，时间一长策略在这些题上会回退。把 online 理解成「永远在刷新 pair」，而不设停止条件，是把补覆盖的药当成日常饮食。

何时可以继续纯离线：策略还在数据集支撑内、新采样的候选仍能被旧 pair 分出胜负、held-out 人评与离线指标一起动。一旦当前策略的多数样本对旧 rejected「毫无竞争」或落在未标注区域，就该切循环。把 coverage 错位讲清，比争论 DPO 和 PPO 谁更先进更重要。Offline DPO 便宜，是因为它把标注一次性做完；策略一走出数据集，这笔便宜就变成了无信号甚至负信号。Online loop 用当前策略重生候选来补支撑，同时把 RM hacking、共谋和去重问题请回来。所以切不切 online，看的是旧 pair 对当前样本还有没有边际信息，以及你有没有独立人评能拦住假奖励，而不是看训练 loss 是否还在下降。

## 追问

- **为什么不直接上 PPO？** 可以。Online DPO / iterative preference 是在保留 DPO 训练稳定性的同时补 coverage；PPO / GRPO 则用在线奖励直接优化。二者都要面对 RM hacking，差别在优化器而不是「要不要新数据」。
- **离线数据还能留吗？** 可以当 replay 或难例池，但要降权或按当前 log-prob 过滤已经无信息的 pair。全部丢掉会忘早期安全边界。
- **RM 更新频率？** 策略走得快、RM 不更新，就是用过期分数训新分布。RM 跟着策略一起无约束更新，则更容易共谋。常见做法是周期性用新人工 pair 重训 RM，并冻结一段时间。
- **如何判断该切 online？** 看当前策略样本在旧 RM / 旧 pair 上的置信度：大多数候选都「明显好于旧 rejected」或都落在未标注区域时，离线边际已经耗尽。
