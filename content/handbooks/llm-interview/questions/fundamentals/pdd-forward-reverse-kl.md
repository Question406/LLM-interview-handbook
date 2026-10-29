---
id: pdd-forward-reverse-kl
section: fundamentals
order: 141
level: S
title: 拼多多秋招：forward KL 和 reverse KL 有何区别？
quick: >-
  KL 的方向看期望在谁的分布下取：正向 $D_{\mathrm{KL}}(p\|q)$ 在教师或数据的样本上算，倾向
  mode-covering；反向在学生自己的样本上算，倾向 mode-seeking。OPD 由学生 sampling，压的是反向
  $D_{\mathrm{KL}}(\pi_S\|\pi_T)$；SFT 才是正向。
tags:
  - PDD
  - KL
  - '2026'
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 拼多多 - 大模型算法 秋招一面
    url: 'https://www.nowcoder.com/discuss/906953010406772736'
    type: candidate-first-hand
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：搜广推部门大模型算法岗
- 届别 / 流程：秋招；一面
- 面试时间：2026-07-15
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：“OPD 算法中的 forward KL/reverse KL 的区别”

区别在期望是在谁的分布下取。正向 $D_{\mathrm{KL}}(p\|q)$ 在教师或数据的样本上算，学生必须盖住教师的每个峰，倾向 mode-covering；反向 $D_{\mathrm{KL}}(q\|p)$ 在学生自己的样本上算，只罚学生跑到教师认为不可能的地方，倾向 mode-seeking。OPD（On-Policy Distillation）由学生 sampling、教师打分，所以压的是 reverse KL；SFT 才是正向。

原帖问的是 OPD，不是一堂抽象的散度课。按「谁减谁」去判断方向很容易错，sampling 方一说错，后面 mode-covering / mode-seeking 就全反了。

用两峰的教师来讲最直观。教师 $p$ 在 A、B 两个词上都有质量。正向 $D_{\mathrm{KL}}(p\|q)$ 要求学生在 A 和 B 上都给概率，否则 $p\gt 0,q\approx 0$ 的点会让 $\log(p/q)$ 爆掉，于是学生变糊，两个峰都盖住。反向 $D_{\mathrm{KL}}(q\|p)$ 只惩罚学生自己 sampling 到的点，学生锁住 A、几乎不去 B，只要不去 $p\approx 0$ 的区域就安全，于是更尖。这就是 mode-seeking 的来源，它不代表反向更优。

## 定义

$$
D_{\mathrm{KL}}(p\|q)=\mathbb{E}_{x\sim p}\big[\log p(x)-\log q(x)\big].
$$

习惯上 $p$ 是数据 / 教师、$q$ 是学生时，$D_{\mathrm{KL}}(p\|q)$ 叫正向：对 $p$ 出现过的点零容忍遗漏，平均上更「糊」。反向 $D_{\mathrm{KL}}(q\|p)$ 在学生自己的样本上取期望，惩罚 $q$ 跑到 $p\approx 0$ 的地方。两者都非负、不对称。

cross entropy $\mathrm{CE}(p,q)=H(p)+D_{\mathrm{KL}}(p\|q)$，和 forward KL 只差一个与 $q$ 无关的 $H(p)$，所以 SFT 最小化 cross entropy loss（CE），等价于最小化 forward KL。白板上别说出「CE 就是 reverse KL」。

## OPD、SFT、PPO 各压哪一边

判断方向时看 token 从谁的分布 sampling，loss 里谁减谁说明不了方向。SFT 和标准 KD 的样本来自数据或教师，最小化的是 $D_{\mathrm{KL}}(\pi_T\|\pi_S)$，正向、mode-covering。OPD 让学生自己 sampling 轨迹（rollout），教师只对学生走到的状态给逐步的 $\log\pi$，期望在 $\pi_S$ 下取，压的是反向 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$，作用是让学生少在教师认为不可能的地方瞎说；实现上常见用 `teacher_lp - student_lp` 当 advantage，期望上就是这条 reverse KL。PPO / RLHF 对 $\pi_{\mathrm{ref}}$ 的惩罚，样本来自当前策略，同样是反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，mode-seeking，防止策略漂到参考认为不可能的区域。

OPD 选反向，是因为学生已经站在自己的错误前缀上，教师只纠正「你现在走到的这一步」，不必强迫学生去覆盖教师轨迹上它从没访问过的状态。这和 exposure bias 说的是同一件事：监督要落在学生会走到的分布上。

方向写反的典型后果，是把 OPD 说成「向教师看齐所以是正向」，或者把 PPO 的 ref KL 说成「覆盖参考分布」。所以先钉住 sampling 分布，再报 KL 方向。

还有一处容易和 cross entropy 搅在一起。SFT 的 $\mathrm{CE}(p,q)$ 期望在数据（近似 $p$）上取，等价于 forward KL；有人把所有「$-\log q$」都叫 CE，再把 OPD 的 `teacher_lp - student_lp` 也叫 CE，方向就丢了。白板上先写期望的下标 $x\sim ?$，再写 KL 符号。RLHF 的 drift KL 同样是 $x\sim\pi_\theta$，所以是反向；PPO clip 相对的是 $\pi_{\mathrm{old}}$，那是信任域，和这条 distillation KL 是两回事。三套东西可以同时出现在一个训练脚本里，要能拆开讲。

## 追问

**正向会怎样？**
学生必须覆盖 $p$ 的全部支撑，平均概率被摊薄，样本更散。长尾格式也能学到，但更容易糊。

**两个 KL 能同时为零吗？**
能，当且仅当 $p=q$ 几乎处处成立。不对称意味着一边小、另一边可以仍然大，所以说「KL 已经很小」时必须报方向。

**和 $k_1/k_3$ 估计器什么关系？**
那是在 reverse KL 上选无偏 / 低方差的估计器，方向不变。见 `fund-kl-k1-k2-k3`。

**OPD 能不能改成正向？**
可以在学生轨迹上再算 $D_{\mathrm{KL}}(\pi_T\|\pi_S)$，但 sampling 仍是学生；严格的正向应该对着教师自己的前缀。实现上别只看 loss 的名字。

**和 OPSD 怎么区分？**
拼多多原问按外部 OPD / `teacher_lp - student_lp` 答反向。Zhao 的 OPSD 在学生前缀上写全 vocabulary 的 $D(p_T\|p_S)$，状态是 on-policy，下一 token 却是正向。两层要拆开说，见 `pt-opsd`。
