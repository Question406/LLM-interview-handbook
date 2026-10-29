---
id: byte-r1-reward-two-stage
section: posttrain
order: 202
level: S
title: 字节 26 秋招：DeepSeek-R1 的奖励（规则 vs RM）以及两阶段如何开展？
quick: >-
  R1 的推理 RL 主要靠规则检查答案对不对、格式对不对；reward model 留给没有 checker 的开放对齐，比如 helpfulness
  和安全。阶段按要修的失败来排：先冷启动 SFT 把长推理和格式教稳，再上大规模可验证奖励的 RL 提正确率，最后按需补风格和安全。
tags:
  - ByteDance
  - DeepSeek-R1
  - RLVR
  - 2026 Campus
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 26届秋招｜字节大模型算法岗面经（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/029a292419294b4a8227acde5a00124b'
    type: candidate-first-hand
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
---

## 真题记录

- 公司：字节跳动
- 届别：26 届秋招；二面提及
- 原始措辞：**“Deepseek r1 里面的奖励（reward function 和 reward model），1阶段，2阶段如何开展”**

R1 的推理训练主要用规则奖励，数学看最终答案、代码跑测试、再加一点格式检查；reward model（RM）只在开放对齐这种没有唯一 checker 的地方用。阶段我会按「每段在修哪种失败」来讲，背「1 阶段、2 阶段」的编号，面试官一追问就露馅。把 RM 直接接到数学 RL 上，是这道题最容易被追打的答法。

先说两种奖励为什么分开用。规则奖励就是 reward function：数学最终答案、代码测试、格式标签、工具调用是否成功，由 checker 或 sandbox 给出 $0/1$ 或者分级分。它噪声低、能扩规模，可覆盖不了开放题的文采和主观偏好。R1 路线里 reasoning RL 的主信号就是这类 RLVR，正确性为主、格式为辅。他们没拿神经网络过程 RM 当推理的主奖励，怕 chain of thought（CoT，即分步推理过程）被教成「看起来像推理」。

reward model 是在偏好对上拟合一个标量 $r_\phi(x,y)$，适合 helpfulness、安全、拒答风格这些。它标注贵，策略还会对着 $r_\phi$ 的漏洞刷分，所以只在开放域没有唯一 checker 时才用。配方里两者别混：可验证任务用规则，开放对齐再用 RM 或 DPO；过程 RM 可以当辅助，替代不了可执行的 outcome。

两种奖励坏的方式也不一样，面试时分开讲，比背一句「R1 不用 RM」准得多。规则奖励在开放题上没法定义；格式分给重了，模型会刷标签；checker 泄漏，比如答案就在 prompt 里、测试用例能猜出来，RL 就学捷径。RM 的问题是 out-of-distribution 给胡话高分、偏爱长回答、和业务偏好对不上。所以 R1 的推理主路径不用容易被 hack 的神经奖励，开放对齐那块仍然可能用偏好模型。

再说阶段。第一段是冷启动 SFT，用人写或筛过的长推理过程，修「不会长推理、格式崩、语言读不懂」。没有这段，纯 RL 也能涨分，R1-Zero 就是这么做的，可读性和稳定性都差，解析一失败，有效奖励率就被打穿。冷启动的目的是给后面的验证器（verifier）一个能解析的状态分布，用不着再做一遍全量指令微调。

第二段是大规模 reasoning RL：组 sampling 加规则奖励，冲可验证的正确率，修的是「示范以外的正确路径不会探索」。这里组内得有对有错，全对或全错时 $\hat{A}=0$，这批就白算了。奖励尽量干净，格式只做轻量 gating。第三段视需要做对齐后处理，rejection sampling 再 SFT、偏好对齐，补风格、安全和拒绝，修「只会刷题不会说话、乱答」。这一段要是把可验证题丢了，推理会从「会搜索」退回到「说得像在搜索」。

落到业务上，先确认三件事：有没有可靠的 verifier、组 sampling 规模够不够、有没有熵、长度、违规这类崩溃监控。没有 verifier 就别说自己在做 R1 第二阶段；格式还没稳就上 RL，解析噪声会把优势变成随机符号。比如字段抽取有 schema checker，就相当于规则奖励；客服话术没有 checker，就该走 RM 或 DPO，别硬套 R1 的编号。字节问这题，往往也想听你能不能把「阶段」翻译成自己的业务。

阶段切错了也有典型症状：冷启动做成了大规模聊天 SFT，后面 reasoning RL 的信号被风格先验稀释；RL 做成了刷格式；对齐只优化偏好，数学往回掉。所以 gating 要写成 go / no-go，格式率不达标不进 RL，pass@k 没抬起来不进下一阶段。

## 追问

**R1-Zero 为什么能跳过 SFT？**
基座本身已经有推理的胚芽，奖励又能自动核验。代价是语言和格式更脏，不适合直接当产品。

**过程 RM 能不能当主奖励？**
可以当辅助的 dense 信号，主信号还是要可验证，不然 PRM 自己也会被 hack。

**R1-Zero 都能涨分了，生产为什么还要多阶段？**
R1-Zero 证明的是存在性：强基座加可验证奖励，纯 RL 也能涌现长思考。产品的目标多得多，要可读、可解析、能对齐，通用能力也不能掉，所以生产上还是多阶段。

**你们业务对应哪一段？**
按失败模式答：不会格式就是冷启动的问题，正确率卡在平台就是 RLVR 的问题，风格和安全差就补偏好。别报「我们做了第二阶段」。

**规则奖励和格式奖励怎么加权？**
正确性为主，格式只做 gating 或者给个小系数。格式权重一大，模型就交空标签和套话。
