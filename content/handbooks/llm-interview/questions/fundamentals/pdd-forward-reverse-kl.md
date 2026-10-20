---
id: pdd-forward-reverse-kl
section: fundamentals
order: 141
level: S
title: 拼多多秋招：正向 KL 和反向 KL 有何区别？
quick: "方向看期望在谁的分布下取：正向 $D_{\\mathrm{KL}}(p\\|q)$ 倾向 mode-covering，反向倾向 mode-seeking。OPD 由学生采样，压的是反向 $D_{\\mathrm{KL}}(\\pi_S\\|\\pi_T)$；SFT 才是正向。"
tags:
  - PDD
  - KL
  - "2026"
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多 - 大模型算法 秋招一面
    url: https://www.nowcoder.com/discuss/906953010406772736
    type: candidate-first-hand
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：搜广推部门大模型算法岗
- 届别 / 流程：秋招；一面
- 面试时间：2026-07-15
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：“OPD算法中的 正向KL/反向KL 的区别”

常见误区是：按「谁减谁」判断方向，而不是按期望在谁的分布下取。原帖问的是 OPD（On-Policy Distillation），不是抽象散度课。说错采样方，后面 mode-covering / mode-seeking 会全反。

## 两个 KL 的定义与几何

$$
D_{\mathrm{KL}}(p\|q)=\mathbb{E}_{x\sim p}\big[\log p(x)-\log q(x)\big].
$$

习惯上 $p$ 是数据 / 教师，$q$ 是学生时称正向 $D_{\mathrm{KL}}(p\|q)$：对 $p$ 出现过的点零容忍遗漏，学生必须把教师的每个峰都盖住，倾向 mode-covering，平均上更「糊」。反向 $D_{\mathrm{KL}}(q\|p)$ 在学生自己的样本上取期望，惩罚 $q$ 跑到 $p\approx 0$ 的地方，倾向锁住主峰、丢掉其他模式（mode-seeking）。

两者都非负、不对称。交叉熵 $\mathrm{CE}(p,q)=H(p)+D_{\mathrm{KL}}(p\|q)$，差一个与 $q$ 无关的 $H(p)$，所以监督微调（SFT）最小化交叉熵损失（CE） 等价于最小化正向 KL。白板不要把「CE 就是反向 KL」说出口。

## OPD / SFT / PPO 分别压哪一边

判断方向时，要看 token 从谁的分布采样，不能只看 loss 中谁减谁。

- SFT / 标准 KD：样本来自数据或教师，最小化 $D_{\mathrm{KL}}(\pi_T\|\pi_S)$，正向、mode-covering。
- OPD：学生自己采样轨迹（rollout），教师只对学生走到的状态给逐步 $\log\pi$。期望在 $\pi_S$ 下取，压的是反向 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$，少在教师认为不可能的地方瞎说。实现上常见 `teacher_lp - student_lp` 当 advantage，期望上就是这条反向 KL。
- PPO / 基于人类反馈的强化学习（RLHF） 对 $\pi_{\mathrm{ref}}$ 的惩罚：样本来自当前策略，同属反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，mode-seeking，防止漂到参考认为不可能的区域。

方向写反的典型后果：把 OPD 说成「向教师看齐所以是正向」，或把 PPO 的 ref KL 说成「覆盖参考分布」。先钉采样分布，再报 KL 方向。

几何上可以用两峰教师来讲。教师 $p$ 在 A、B 两个词上都有质量。正向 $D_{\mathrm{KL}}(p\|q)$ 要求学生在 A 和 B 都给概率，否则 $p\gt 0,q\approx 0$ 的点会让 $\log(p/q)$ 爆掉，于是学生变糊，两个峰都盖住。反向 $D_{\mathrm{KL}}(q\|p)$ 只惩罚学生自己采样到的点：学生锁住 A、几乎不去 B，只要不去 $p\approx 0$ 的区域就安全，于是更尖。OPD 选反向，是因为学生已经在自己的错误前缀上，教师只纠正「你现在走到的这一步」，不必强迫覆盖教师轨迹上从未被学生访问的状态。这和 exposure bias 是同一句话：监督要落在学生会走到的分布上。

和交叉熵不要搅。SFT 的 $\mathrm{CE}(p,q)$ 期望在数据（近似 $p$）上取，等价正向 KL。有人把「$-\log q$」都叫 CE，再把 OPD 的 `teacher_lp - student_lp` 也叫 CE，方向就丢了。白板先写期望的下标 $x\sim ?$，再写 KL 符号。RLHF 的 drift KL 同样是 $x\sim\pi_\theta$，所以是反向；PPO clip 相对的是 $\pi_{\mathrm{old}}$，那是信任域，不是这条蒸馏 KL。三套东西可以同时出现在一个训练脚本里，要能拆开。

## 追问

- **为什么反向更「尖」？** $q$ 自己采样，碰到 $p\approx 0$ 会被重罚，于是丢掉次峰。这是 mode-seeking 的来源，不是「反向更优」。
- **正向会怎样？** 必须覆盖 $p$ 的全部支撑，平均概率被摊薄，样本更散，长尾格式也能学到，但更容易糊。
- **两个 KL 能同时为零吗？** 当且仅当 $p=q$ 几乎处处。不对称意味着一边小另一边可以仍大，所以「KL 已经很小」必须报方向。
- **和 $k_1/k_3$ 估计器？** 那是在反向 KL 上选无偏 / 低方差估计，不改变方向。见 `fund-kl-k1-k2-k3`。
- **OPD 能不能改成正向？** 可以对学生轨迹再算 $D_{\mathrm{KL}}(\pi_T\|\pi_S)$，但采样仍是学生；严格正向应对着教师自己的前缀。实现上别只看 loss 名字。
- **和 OPSD？** 拼多多原问按外部 OPD / `teacher_lp - student_lp` 答反向。Zhao 的 OPSD 在学生前缀上写全词表 $D(p_T\|p_S)$，状态 on-policy、下一 token 却是正向。两层拆开，见 `pt-opsd`。
