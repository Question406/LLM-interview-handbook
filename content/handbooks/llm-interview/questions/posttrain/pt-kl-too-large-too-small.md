---
id: pt-kl-too-large-too-small
section: posttrain
order: 224
level: A
title: 对齐为什么必须加 KL？系数太大或太小会怎样？
quick: "KL 把策略拴在冻结的 SFT 参考附近，防止它为了讨好有噪的奖励去钻漏洞、把语言写坏。$\\beta$ 太大，策略贴死 $\\pi_{\\mathrm{ref}}$，奖励不涨，像没做 RL；太小，KL 飙升，开始变长、说空话、安全回退。判断时 reward、KL、熵、长度要一起看。"
tags:
  - KL
  - RLHF
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 【面试真题】美团Agent 方向面经整理
    url: https://www.nowcoder.com/discuss/881209147377664000
    type: secondary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---
对齐要加 KL，是因为奖励模型有噪声，没有护栏的话，策略会为了讨好奖励一路偏离 SFT 模型通常的说话范围，开始重复、注水、安全回退、钻奖励规则的空子。$\beta$ 太大，策略贴死参考，奖励不涨，等于没做 RL；太小，护栏形同虚设。所以 $\beta$ 不能凭感觉加一点，要看 reward、KL、熵、长度这几条曲线一起判断。

美团 Agent 整理帖的原问是「KL 散度具体怎么加？太大或太小有什么问题？」，快手等面经也会问「对齐为什么离不开 KL」。我会按怎么加、太大什么样、太小什么样这个顺序答。

## 怎么加：罚的是当前策略相对参考的偏离

要加的是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，$\pi_{\mathrm{ref}}$ 通常是冻结的 SFT 模型。期望在当前策略上取，策略跑到参考几乎不会说的地方，$\log(\pi_\theta/\pi_{\mathrm{ref}})$ 就会变得很大，这就是防胡话、防黑奖励的护栏，为什么是这个方向见 `pt-rlhf-why-reverse-kl`。没有这一项，少数几种偏好模式会被过拟合到通用能力都丢掉，奖励模型（RM）喜欢的列表体、过长的道歉、表面礼貌，很快就会占满采样。

落到实现上有三条路，数学上是同一项。PPO-RLHF 把它扣进 token 奖励，$r-\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$；GRPO 常把它单独放进 loss，比如用 $k_3$ 估计；DPO 把它写进 $\beta\log(\pi/\pi_{\mathrm{ref}})$ 的间隔里，不再显式算奖励。也可以用自适应 $\beta$，把实测 KL 控制在一个目标范围内，见 `pt-adaptive-kl-controller`。

有几个细节容易答错。这一项和 PPO clip、相对 $\pi_{\mathrm{old}}$ 的 trust-region 是两回事，见 `pt-trust-region-vs-drift-kl`。mask 只盖生成段，把输入提示也算进 KL，等于把「读懂问题」当成偏离来罚。奖励在哪采样，KL 就在哪采样：PPO / GRPO 用 $\pi_\theta$ 采样轨迹，就用反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$；换成对 SFT 文本算交叉熵损失（CE），期望就跑到参考上去了，护栏变成 covering，该丢的峰丢不掉，该挡的胡话也挡不对。还有 $\beta$ 和奖励的归一化是绑在一起的，同一个数，在 $r\in[0,1]$ 和没归一化的 RM 分数上是完全不同的约束，所以 $\beta$ 不能跨实验照抄。

## $\beta$ 太大：贴死参考，像没做 RL

$\beta$ 过大时，KL 项主导了梯度，有效步长被罚没了。曲线上的样子是：对 $\pi_{\mathrm{ref}}$ 的 KL 接近 0，策略几乎没离开 SFT；proxy reward 是平的，或者只在噪声范围里抖；熵不升不降，生成风格和 SFT 看不出差别。看着训练很稳，其实 RL 根本没发生。这时候调大学习率或 clip 范围往往没用，惩罚项把偏离参考带来的收益都抵掉了。该做的是减小 $\beta$、放宽 KL target，或者查一下奖励尺度是不是太小。

KL 越小越好这种话现场别说。KL 接近 0 只说明贴着参考，参考本身不够好的时候，这是失败。gold 指标本来就靠 SFT 撑着，KL 很小、reward 又不动，也别报成「对齐成功」。

调试的顺序我一般是先确认 reward 有信号，比如离线 RM 或者规则分在 SFT 样本上能分开好坏，再去减 $\beta$，不然会把「奖励是平的」误诊成「KL 太大」。减了 $\beta$ 以后 KL 还是接近 0，就去查学习率、clip、response mask，以及是不是把 KL 加在了整段序列上。减了 $\beta$ 以后 reward 一下子飞起来、长度暴涨，说明原来的 $\beta$ 其实在干活，要温和地往下调，别直接去掉。太大的样子是「像没做 RL」，训练崩溃更常出现在太小那一侧。

## $\beta$ 太小：钻奖励规则的空子，语言崩坏

$\beta$ 太小或者干脆去掉 drift 项，策略会为了讨好有噪的奖励走极端。实测 KL 持续往上走，离开 SFT 的 token 级 log-ratio 越来越大；长度暴涨，重复 n-gram、空话、列表注水，因为 RM 常常把「更长更完整」当高分；安全拒答回退，乱说话还拿高分，也就是跑进了参考低概率、proxy 高分的区域；熵先升后塌，先大范围乱探，再收拢到一种专门利用奖励漏洞的输出。

这就是 collapse：训练 reward 很好看，held-out 人评、指令遵循和安全评测一起掉。所以只报「reward 高了」等于没监控，验收要同时看 reward、KL、熵、长度、拒答率和人工胜率。KL 大而且 gold 在掉，是漂移；KL 很小而且 gold 不动，是没学；reward 在升、KL 可控、熵没塌、人评同步变好，才像是在对齐。

分组统计比看全局均值更有用。比如某一类安全题的 KL 单独在涨，可能是参考模型很少拒答，对齐正在起作用；解题类 KL 稳、套话类 KL 飞，那才是 hacking。按意图切片看清楚，再决定是加 $\beta$ 还是修奖励。长度要单独画一条，reward 和长度一起升、人评不动，先按 length hacking 处理，加 $\beta$ 只治标，根子在奖励。熵塌的时候策略会反复说同一句，KL 却可能看着还行，因为它锁在参考的某一个峰上，所以 KL、熵、长度、人评少一样都看不全。

回到美团的原问，「怎么加」对应的是实现位置：奖励里减、loss 里加、DPO 间隔里藏；「太大太小」对应上面两种样子。别把 PPO clip 的松紧答成 $\beta$ 的大小，那是另一套相对 $\pi_{\mathrm{old}}$ 的约束。只能盯一个信号的话，我会先看 reward 和 ref-KL 是不是反向运动；两者同向一起升或一起降，再分组查是不是某个切片的问题。

## 追问

**太大和太小分别怎么判断？**
太大是 KL 接近 0、reward 平，像没做 RL；太小是 KL 飙升、变长说空话、安全回退、人评掉。别用单一阈值，这组曲线要一起读。gold 在掉而 KL 很小，说明参考本身不够好，该换数据，再加大 $\beta$ 没用。

**和 clip 是不是重复了？**
不重复。clip 限制的是相对 $\pi_{\mathrm{old}}$ 的单次更新，$\beta$ 限制的是相对 $\pi_{\mathrm{ref}}$ 的长期漂移，只留一个就会漏掉另一种失败，见 `pt-trust-region-vs-drift-kl`。

**自适应 $\beta$ 能代替手调吗？**
能把 KL 钉在目标带里，但目标带本身还是要选。目标定得太小就等于 $\beta$ 太大，定得太大就等于太小，controller 只是省了一次手工改系数，见 `pt-adaptive-kl-controller`。

**基于可验证奖励的强化学习（RLVR）也要大 KL 吗？**
不一定。可验证奖励比较干净时可以松一点，方便探索长尾里的正确路径；奖励一旦有噪声，松 KL 就是最快的 hacking 配方，见 `pt-kl-direction-and-exploration`。太大太小的样子在 RLVR 上同样成立，只是「太小」会先表现为 checker 被刷。
