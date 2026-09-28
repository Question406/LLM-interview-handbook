---
id: meituan-three-stage-v3-r1
section: posttrain
order: 181
level: A
title: 美团秋招二面：为何要三阶段后训练？V3 到 R1 各自在解决什么？
quick: >-
  阶段按失败模式拆：SFT/冷启动解决格式与长链；RLVR
  用可验证奖励冲推理；必要时再偏好对齐补风格与安全。V3 偏基座与稳定训练，R1
  偏规则奖励驱动的 reasoning RL，不要把发布名当成算法名背。
tags:
  - Meituan
  - DeepSeek-R1
  - Post-Training
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法二面-秋招面经
    url: https://www.nowcoder.com/feed/main/detail/e72d861f57c1499393be6651f8611177
    type: candidate-first-hand
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“Post-Training 的工作机制，为什么要做三阶段训练？什么情况下应该用GRPO？为什么DeepSeek用了GRPO？如何从V3到R1？”**

三阶段按失败模式拆，不是玄学编号，也不是「SFT 完必须再接两段才算完整」。拆阶段是因为三种失败要用三种监督：格式不会、对错可验但示范不够、开放偏好无法写成 checker。把发布名 V3 / R1 当成算法名背，下一问「缺 verifier 怎么办」就会空。原帖四问应串成一条线：后训练按失败模式选监督 → 有 checker 且能成组采样才上 GRPO → DeepSeek 用规则奖励扩推理规模、省过程 RM → V3 先稳住基座，R1 再冲 reasoning RL。按失败模式选监督，再谈算法和发布名。

## 三种监督各管一类失败

**示范监督（SFT / 冷启动）** 解决格式、工具协议、可读长链。没有这一段，RL 采样出来的轨迹常常不可解析，奖励全是噪声：checker 读不到答案、工具调用对不上 schema。冷启动是给后续 RL 准备可进入 verifier 的分布，不是再做一次普通 SFT。**可验证 RL（GRPO / RLVR）** 在有 checker 时用组内相对优势冲正确率：数学、代码、字段校验适合，目标是「对」，不是「像示范」。**偏好对齐（DPO / RM+PPO）** 补开放性文采、安全、拒绝，这些没有唯一正确答案，硬套规则奖励会学到拒答或套话。

三阶段可以裁剪：没有 verifier 就不要硬上「第三段编号」；开放域没有成对偏好，DPO 也做不了事。顺序通常是先让输出可解析，再冲可验证正确率，最后用偏好修风格和安全。反过来会把奖励打在乱格式上，或用偏好对去学本该用 checker 的对错。业务里缺哪一类信号，就停在对应阶段，不要为了「像 R1」凑满三段。

## 何时 GRPO，为何 DeepSeek 用它

GRPO 的适用条件：奖励能自动复核、同一 prompt 能采出对错混合组、希望省一张和 actor 同规模的 critic。它解决的是显存和 baseline，不是「比 PPO 更新所以更好」。需要逐步价值估计、奖励稀疏且不能成组、或已有稳定 RM+critic 基建时，PPO 仍更合适。DeepSeek 路线用规则奖励扩推理规模，避免先训一张易 hack 的过程 RM：过程分一旦被套话骗，后续 RL 会放大错误过程。组内相对优势在可验证任务上足够形成对比，正好匹配「有 checker、要大规模 rollout」的约束。

组内全对全错会零梯度，这是 GRPO 的结构缺陷，要用动态采样、过滤空组或课程，而不是换一个发布名。Reward hacking（套格式骗校验）比 PPO 更依赖 verifier 质量，我会主动讲出来。

## V3 到 R1：基座稳了再冲推理 RL

V3 偏稳定 MoE 基座与通用训练：先有能训、能推、格式不崩的底盘，推理能力是「会一点」而不是靠大规模规则 RL 堆出来的。R1 偏在可验证任务上做大规模 reasoning RL，把长链推理从示范分布推进到规则奖励可规模化的区域。监督信号从示范变成可验证结果，不是换个名字就更强。R1-Zero 可以讨论「几乎不靠 SFT」，那是实验路线，不等于业务可以跳过格式监督。

业务里缺 verifier、缺可采样混合组时，不要照抄 R1 编号；先补 SFT 冷启动或规则引擎，再谈 GRPO。把 V3 说成「普通 SFT」、把 R1 说成「换了 GRPO」都太浅，要落到各自解决的失败：一个是稳定可训的底座，一个是可验证推理的规模化。

## 追问

- **可以两阶段吗？** 可以。开放客服常是 SFT+DPO；竞赛数学常是冷启动+RLVR。第三段只在有对应失败时才加。凑满三段不是完整，是浪费或引入错误监督。
- **为什么不先 RL 再 SFT？** 格式未立时奖励不可解析，RL 会强化乱码。冷启动是为了让 rollout 进得了 checker。R1-Zero 用可读性约束补了部分格式，业务上仍更稳妥先 SFT。
- **DeepSeek 为什么不用过程 RM？** 过程 RM 易被套话 hack，且要先标过程。规则奖励可审计、能规模化，这是选 GRPO+verifier 的同一逻辑。
- **GRPO 和 PPO 怎么选？** 有 critic 基建、要价值估计就 PPO；可验证、要省 critic、能成组采样就 GRPO。没有 checker 时不要为了省 critic 硬上 GRPO。
