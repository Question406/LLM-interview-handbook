---
id: pt-online-preference-loop
section: posttrain
order: 26
level: S
title: 为什么 Offline DPO 做到后面常要引入 Online Preference Loop？
quick: >-
  固定的偏好数据只覆盖旧策略会生成的区域，策略变强后走出 dataset support，离线 pair 的边际信息就耗尽了。在线循环用当前策略
  sampling、标注或打分、再更新，持续把新分布补上；但它也把钻奖励规则的空子和标注质量问题带回系统，要配独立人评和停止条件。
tags:
  - DPO
  - Online RLHF
  - Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Iterative Preference Learning
    url: 'https://arxiv.org/abs/2312.11456'
    type: primary
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
---
离线 DPO 做到后面要上在线循环，是因为偏好数据覆盖不到当前策略了。离线 pair 比较的是数据集里已经写下来的回答，策略更新以后，概率质量会推到没被标注过的新区域，这时候继续重复旧 pair，要么没信息，要么把数据里的长度、风格偏差放大成「越训越像训练集里的赢家」。DPO 公式本身没坏，坏的是 off-policy 偏好数据相对策略的 coverage。所以我不会答成「DPO 不如 PPO」，先讲 support 错位，再谈要不要上在线循环。

一个常见的现象是：DPO 后期 loss 很小，离线 eval 也还行，线上却变差了。这多半是标签分布落后于策略分布，调学习率解决不了。

## 离线 pair 为什么会过期

DPO 的间隔来自 chosen 和 rejected 相对 $\pi_{\mathrm{ref}}$ 的 log-prob 差，这对 $(y_w,y_l)$ 是在某一代策略或者人工写手的分布上采的。$\pi_\theta$ 变强以后会出现三件事。它不再生成 $y_l$ 那种明显很差的回答，旧负样本成了「太容易的负例」，梯度接近零。它开始写出旧数据里没有的高分续写，这些区域没有偏好标签，DPO 既奖励不了也惩罚不了，也就约束不住这些 out-of-distribution（OOD）输出。旧 pair 里的长度、礼貌、列表体如果和「赢」相关，会被反复强化，出现 length hacking 或者风格塌缩。

可以把它想成覆盖问题。离线 DPO 的梯度只在旧 pair 的 chosen/rejected 方向上有信号，策略一走出数据集的支撑范围，损失（loss）再低也管不着新的失败模式。这和 SFT 后期「训练 CE 很小、用户问题却是 OOD」是同一类错位，只是偏好数据比示范更脆，因为 pair 还依赖「当时什么算差回答」。Iterative DPO 和 online preference 的动机，就是让对比样本重新落在当前 $\pi_\theta$ 会碰到的区域上；Iterative Preference Learning 一类工作也反复强调，要用当前策略重新生成候选再标注，preference learning 才能维持在 on-policy 附近。

## 在线循环补的是新分布

最小的 feedback loop 是这样：用当前或近期的 policy 给同一个 prompt 采多个候选；用人工、reward model（RM）或者验证器（verifier）给出带置信度的偏好或 pairwise ranking；把 policy、prompt、labeler 的版本都记下来，再做一次受 KL 和 data quality checks 控的更新；同时保留一份固定的 held-out human eval，检查在线奖励是不是和真实质量一起在涨。

关键是谁 sampling。候选要来自当前或者近几代策略，标注要针对这些候选。旧离线数据可以混进来当 replay，但新 pair 少不了。RM 只给标量分的话，最好还是落成 pair，或者把低置信的对比过滤掉，免得把绝对分数的尺度误差写进 DPO margin，分差很小的 pair 直接丢掉或降权。

版本化也不是为了记账。没有 policy checkpoint 和 labeler 版本，就复现不了「这一批 pair 是相对哪一代策略 on-policy 的」，出了 hacking 也回滚不了。prompt 集也要冻一份对照集，不然在线指标看着在涨，其实是题变容易了。sampling 要有多样性，同一个 prompt 只抽两条很像的回答，标注员给不出稳定的偏好，DPO margin 就成了噪声，常见做法是把温度或 nucleus 稍微放开、过滤近重复，再交给 RM 或人。在线循环的 throughput 通常卡在标注上，backpropagation 不是瓶颈，所以要先想好哪些 prompt 值得采：旧数据上已经饱和的题少采，策略新出现失败的题多采。

## 自己的 judge 给自己打分

在线循环会把钻奖励规则的空子和标注质量问题重新请回系统。RM 如果和策略一起漂，两边会「商量」出一套高分但没用的写法，更长、更多列表、更多安全套话。所以要有一份独立审计集，由人工或更强的 judge 来打，不参与训练更新；要有对抗样本和格式扰动，覆盖长度、重复、拒答、工具 hallucination；还要去重，免得同一个高分模板被反复采、反复标成 winner，把 RM 的一个峰写成数据集里的定律。去重按轨迹近邻或 n-gram 做，只按 prompt id 去不干净。安全和拒答要单独留一份固定的离线集，因为在线循环默认会少采那些「无聊但正确」的拒答，时间一长，策略在这些题上会退步。

online reward 在涨、held-out 人评不动，就该停下循环去修 RM 或规则，更频繁地训练没用。对 $\pi_{\mathrm{ref}}$ 或上一轮迭代的 KL 还是有用的，但解决不了「新区域的标签是假的」。在线循环不是免费的 on-policy 魔法，它只是把数据收集重新对准了当前策略。

什么时候还可以继续纯离线？策略还在数据集支撑范围内、新采的候选还能被旧 pair 分出胜负、held-out 人评和离线指标一起动，就可以。一旦当前策略的大多数样本对旧 rejected「毫无竞争」，或者落在没标注过的区域，就该切到循环。判断依据是旧 pair 对当前样本还有没有边际信息、有没有独立人评能拦住假奖励，训练 loss 还在不在降说明不了这个。

## 追问

**为什么不直接上 PPO？**
可以上。Online DPO / iterative preference 是在保留 DPO 训练稳定性的前提下补 coverage，PPO / GRPO 是用在线奖励直接优化。两者都要面对钻 reward model 空子的问题，差别在优化器，新数据两边都要。

**离线数据还能留吗？**
可以当 replay 或者难例池，但要降权，或者按当前 log-prob 把已经没信息的 pair 过滤掉。全部丢掉的话，早期学到的 security constraints 会忘。

**RM 多久更新一次？**
策略走得快、RM 不更新，就是在用过期的分数训新分布；RM 跟着策略一起无约束地更新，又更容易共谋。常见做法是周期性地用新的人工 pair 重训 RM，然后冻结一段时间。

**怎么判断该切 online 了？**
看当前策略的样本在旧 RM、旧 pair 上的置信度。大多数候选都明显好于旧的 rejected，或者都落在没标注的区域，离线数据的边际信息就已经用完了。
