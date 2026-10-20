---
id: pt-kl-too-large-too-small
section: posttrain
order: 224
level: A
title: 对齐为什么必须加 KL？系数太大或太小会怎样？
quick: "KL 限制策略偏离参考模型，有助于减少利用奖励漏洞和语言质量下降的问题。$\\beta$ 太大：策略贴死 $\\pi_{\\mathrm{ref}}$，奖励不提高。太小：KL 飙升、变长空话、安全回退。要同时看 reward、KL、熵、长度，而不是只刷分。"
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

美团 Agent 整理帖原问：**「KL 散度具体怎么加？太大或太小有什么问题？」** 快手等面经也会问「对齐为什么离不开 KL」。别把 KL 答成「正则随便加一点」。没有相对冻结参考的反向 KL，策略会为讨好有噪奖励偏离 SFT 模型通常会生成的回答范围：重复、注水、安全回退、钻奖励规则的空子。太大贴死参考，太小护栏形同虚设。怎么加：对冻结 SFT 做 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，可扣进奖励、单独加入损失，或写进 DPO 的 $\beta$ 间隔。太大则 KL 近零、奖励不提高，像没有从强化学习中学到改善；太小则 KL 飙升、变长空话、安全回退。要同时看 reward、KL、熵和长度，而不是只刷分。

## 怎么加：惩罚的是当前策略相对参考的偏离

对齐里要加的是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，$\pi_{\mathrm{ref}}$ 通常是冻结 SFT。期望在当前策略上取：跑到参考几乎不会说的地方，$\log(\pi_\theta/\pi_{\mathrm{ref}})$ 会出现数值异常。这就是防胡话、防黑奖的护栏，方向见 `pt-rlhf-why-reverse-kl`。

实现三条路，数学上同一项：

- PPO-RLHF：扣进 token 奖励 $r-\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$；
- GRPO：常单列进 loss（如 $k_3$）；
- DPO：写进 $\beta\log(\pi/\pi_{\mathrm{ref}})$ 间隔，不再显式算奖励。

也可以自适应 $\beta$，把实测 KL 控制在目标范围内，见 `pt-adaptive-kl-controller`。注意这与 PPO clip / 相对 $\pi_{\mathrm{old}}$ 的 trust-region 不是同一项，见 `pt-trust-region-vs-drift-kl`。Mask 必须只盖生成段：把输入提示算进 KL，会把「读懂问题」当偏离来罚。

没有这项时，少量偏好模式会被过拟合到失去通用能力：奖励模型（RM） 喜欢的列表体、过长道歉、表面礼貌，会迅速占满采样。KL 是把优化限制在参考还能解释的区域内。怎么加：奖励在哪采样，KL 就在哪采样。PPO / GRPO 用 $\pi_\theta$ 采样轨迹，就要用反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$。把它改成对 SFT 文本计算交叉熵损失（CE），期望跑到参考上，护栏变成 covering，该丢掉的峰丢不掉，该挡住的胡话也挡得不对。$\beta$ 与奖励归一化绑在一起：同一数字，在 $r\in[0,1]$ 和未归一的 RM 分数上完全不是同一约束，所以不能跨实验抄 $\beta$。

## $\beta$ 太大：贴死参考，像没做 RL

$\beta$ 过大时，KL 项主导梯度，有效步长被罚没。曲线上典型画像：

- 对 $\pi_{\mathrm{ref}}$ 的 KL 接近 0，策略几乎不离开 SFT；
- proxy reward 平、或只在噪声范围内抖；
- 熵不降也不升，生成风格与 SFT 无差别。

看起来训练很稳，其实 RL 没有发生。加大学习率或 clip 范围往往无效，因为惩罚项抵消了策略偏离参考模型带来的收益。这时应减小 $\beta$、放宽 KL target，或检查 奖励尺度是否过小（同一 $\beta$ 在不同 reward 归一化下有效约束完全不同）。Gold 指标若本来就靠 SFT，KL 很小加上 reward 不动，不要误报成「对齐成功」。

现场不要说「KL 越小越好」。KL 接近 0 只说明贴着参考；参考本身不够好时，这是失败而不是胜利。调试顺序我一般先确认 reward 有信号（离线 RM 或规则分在 SFT 样本上能分开好坏），再减小 $\beta$。否则你会把「奖励是平的」误诊成「KL 太大」。若减小 $\beta$ 后 KL 仍接近 0，查学习率、clip、response mask 和是否误把 KL 加在了整段序列上。若减小 $\beta$ 后 reward 立刻飞、长度暴涨，说明原来 $\beta$ 其实在干活，要的是温和下调而不是去掉。太大的画像是「像没做 RL」，不是「训练崩溃」。崩溃更常是太小的那一侧。

## $\beta$ 太小：钻奖励规则的空子 与语言崩坏

$\beta$ 过小或直接去掉 drift 项，策略为讨好有噪奖励走极端。常见现象：

- 实测 KL 持续飙升，离开 SFT 的 token 级 log-ratio 变大；
- 长度暴涨、重复 n-gram、空话和列表注水，因为 RM 常把「更长更完整」当高分；
- 安全拒答回退、乱说话仍拿高分，即跑到参考低概率、proxy 高分的区域；
- 熵先升后塌：先大范围探索，再集中到一种利用奖励漏洞的输出模式。

这就是 collapse：训练 reward 很好看，held-out 人评、指令遵循和安全评测一起掉。只报「reward 高了」等于没监控。验收必须同时看 reward、KL、熵、长度、拒答率、人工胜率。KL 大且 gold 掉，是漂移；KL 很小且 gold 不动，是没学。只有 reward 升、KL 可控、熵未塌、人评同步，才像在对齐。

分组统计比看全局均值重要：某一类安全题 KL 独涨，可能是参考很少拒答、对齐其实在起作用；解题类 KL 稳而套话类 KL 飞，才是 hacking。按意图切片，再决定加 $\beta$ 还是修奖励。长度要单独画：reward 与长度一起升、人评不动，优先当 length hacking，加 $\beta$ 只是治标，根因在奖励。熵塌陷时策略会反复同一句，KL 可能仍看起来还行（锁在参考的一个峰上），所以 KL、熵、长度、人评缺一不可。

美团原问里的「怎么加」对应实现位置（奖励里减、loss 里加、DPO 间隔里藏），「太大太小」对应上面两幅画像。不要把 PPO clip 的松紧答成 $\beta$ 的大小：那是另一套相对 $\pi_{\mathrm{old}}$ 的约束。现场若只能调一个旋钮，优先同时看 reward 与 ref-KL 是否反向运动；同向都升或都降，才需要分组统计查是不是切片问题。

## 追问

- **太大 / 太小的判据是什么？** 太大：KL 接近 0 且 reward 平，像没做 RL。太小：KL 飙升、变长空话、安全回退、人评掉。不要用单一阈值，用这组曲线一起读。Gold 掉而 KL 很小，是参考不够好，该换数据而不是再加大 $\beta$。
- **和 clip 重复吗？** 不重复。Clip 限制相对 $\pi_{\mathrm{old}}$ 的单次更新；这里的 $\beta$ 限制相对 $\pi_{\mathrm{ref}}$ 的长期漂移。只留一个会漏掉另一种失败。见 `pt-trust-region-vs-drift-kl`。
- **自适应 $\beta$ 能否代替手调？** 能把 KL 钉在目标带上，但目标带本身仍要选。目标过小等于「太大」，目标过大等于「太小」，controller 只是少一次手工改系数，见 `pt-adaptive-kl-controller`。
- **基于可验证奖励的强化学习（RLVR）也必须大 KL 吗？** 不一定。可验证奖励较干净时可以更松，以便探索长尾正确路径；奖励一噪，松 KL 就是最快的 hacking 配方，见 `pt-kl-direction-and-exploration`。太大太小的画像在 RLVR 上同样适用，只是「太小」更先表现为 checker 被刷。
