---
id: pt-cold-start-to-multistage-rl
section: posttrain
order: 31
level: S
title: 既然 R1-Zero 能纯 RL，为什么生产配方仍常用 cold-start CoT、RL、rejection sampling、二次 RL？
quick: 纯 RL 证明了探索可行，不代表它是最稳的产品配方。cold start 先提供格式、语言与基本解题 support；RL 扩探索和优化 reward；rejection sampling 回收高质量轨迹；二次 RL 再对齐通用能力和可读性。
tags:
  - Reasoning RL
  - Cold Start
  - Curriculum
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

R1-Zero 证明的是「可验证奖励下，强 base 也能被 RL 放大推理」，不是「生产应该删掉 SFT」。把论文里的存在性实验当成部署处方，是这题最常见的坑。我会讲清：Zero 回答「纯 RL 能不能涌现长思考」，生产配方回答「可读、可解析、可对齐、还能保持通用能力」，目标集合更大，所以阶段更多。Cold start 不是因为 RL 数学上需要演示，而是因为 outcome reward 对语言混杂和格式崩溃几乎无感；后面每一段都在补一种 Zero 故意没优化的瓶颈。

## 每一阶段修的是不同瓶颈

DeepSeek-R1 的生产路径是四段课程，不是把同一目标重复四遍。

**Cold-start SFT。** 用少量可读的长 CoT，把策略拉进「能被解析、语言一致、格式能拿到 reward」的区域。R1-Zero 会混语言、可读性差，不是因为 RL 不会解题，而是 outcome reward 不惩罚这些表面缺陷。没有 cold start，后续 verifier 的有效样本率会很低：格式错了等于零奖励，探索预算浪费在不可解析轨迹上。可读性还影响产品：即使用户能接受长思考，混中英、无标记的跳跃推理也无法上线。Cold start 等于给奖励函数补了一层「人类可消费」的先验，而不是再做一遍全量指令微调。

**第一段 reasoning RL。** 在可验证任务上做 on-policy 搜索。目标是提高解题能力，不是把所有产品属性一次对齐。奖励应尽量干净（正确性加轻量格式），让策略在 cold-start 附近发现更长、更有用的搜索。机制上仍是 search-selection-amplification，见 `pt-r1zero`。这一段最怕的是奖励泄漏和长度 hacking：格式分过重会变成套模板，过程分过松会写空洞步骤。Verifier 要比 Zero 实验更严，因为 cold start 已经会「写得像对的」。

**Rejection sampling + 混合 SFT。** RL 之后策略已经能产出高质量推理轨迹，但分布仍偏数学和代码。RS 把验证过的成功轨迹冻成监督数据，再混入写作、事实问答、翻译、安全拒答等非推理数据。这一步是 support 回收与能力混合，不是又一次 RL。RS 只能筛选已有候选：覆盖率低时筛出来的数据又少又窄，见 `pt-rejection-sampling-vs-rl`。混入非推理数据的比例要单独扫：太少则二次 RL 之前通用能力已经掉，太多则把刚搜到的解题路径冲淡。RS 数据要去重、控长度，避免把最长的成功轨迹复制成新的长度先验。

**第二段 RL。** 在更宽的任务和偏好目标上再对齐：有用性、无害性、可读性、不过度拒绝。推理能力已经有了，这一段防止「只会刷题、不会聊天」。偏好奖励噪声大，更新要更保守，并继续混入可验证题，避免把第一段 RL 搜到的解题路径优化没。产品指标和推理基准要同一天看，不能只看对齐 leaderboard。

## 为什么生产不直接用 R1-Zero

R1-Zero 的价值是机制证明：base 的长尾里已有成功推理，verifier 做选择，policy gradient 做放大。生产还要语言一致性、指令遵循、安全拒答、长度可控（`pt-reasoning-token-cost-frontier`）和通用能力不回退（`pt-safety-capability-regression`）。这些目标的奖励噪声远大于「答案对不对」。用同一套稀疏 outcome reward 硬冲，往往会牺牲可读性和安全。

Cold start 还有一个常被忽略的作用：给 RL 一个可解析的状态分布。on-policy 方法只能优化自己访问过的状态；一开始格式全崩，后续再密的奖励也帮不上。这和 `pt-on-policy-distillation` 同源：先让学生走到有信号的区域。

## 怎么拆实验

不要把四段糊成一条曲线。至少分开报：

- 格式率、语言混杂率、可解析率（cold start 是否生效）
- Pass@1 / Pass@K、思考长度、熵（RL 是否在探索，而不是只刷长度）
- RS 后 held-out 覆盖率与非推理任务是否回退
- 二次 RL 后 instruction-following 与安全评测

只看最终基准，无法知道瓶颈是 seed quality、reward、rollout 还是 data mixing。把四段绑在同一条 job 里「一起涨」，事后无法回答「格式是 SFT 修好的还是 RL 碰巧学会的」。阶段门控要写成明确的 go / no-go：格式率不达标不进 RL，Pass@K 不抬不进 RS，非推理回退过深不进二次 RL。否则多阶段只是把同一锅粥煮四次。

## 常见错配

把 RS 当成 RL 的同义词是第一错。RS 从已有候选里筛选，不改变策略访问新状态的能力；正确轨迹覆盖率低、或问题需要连续多步探索时，筛完还是那几条成功模式，必须回到 on-policy。第二错是 cold start 做成大规模指令 SFT：把聊天、安全、知识问答一次性灌进去，后面 reasoning RL 的信号被风格先验稀释，也更难归因。第三错是二次 RL 只用偏好模型、丢掉可验证任务，推理能力会从「会搜索」退回「会说得像在搜索」。

现场可以补一句基础设施：多阶段会放大 `sys-rl-infra` 里的 rollout、verifier、权重同步成本。阶段切错时，先查有效 reward 率（解析失败、组方差为零），再查算法。

## 追问

- **Cold start 要多少？** 论文用的是「数千条」量级可读长链，不是再做一个完整 SFT 语料库。格式、语言、解题 support 比堆数量重要。质量差的长链会把错误格式锁进先验，后面 RL 会更高效地放大它。宁可选题、重写，也不要用噪声示范灌满。
- **RS 和 RL 能互相替代吗？** 不能。RS 是离线筛选；正确轨迹稀、需要连续状态探索时仍要 on-policy。RS 适合回收已经稳定的成功样本，不适合创造新的解题路径。覆盖率已经高时，先 RS 再小步 RL，比一上来大规模 rollout 更省。
- **二次 RL 会不会把推理冲掉？** 会，如果奖励里推理信号太弱。推理任务要继续占比例，并盯通用与推理的 Pareto，而不是只看聊天分。安全拒答变好但数学掉点，说明混合比而不是「对齐成功」。回退时先查非推理数据比例和偏好模型是否奖励套话。
- **能不能用蒸馏代替 cold start？** 可以当作另一条进 support 的路（`pt-on-policy-distillation`），但仍要有可读 teacher；它不是免费跳过格式问题。Teacher 自己混语言，学生会更快学会混语言。蒸馏也解决不了「teacher 覆盖不到的题型」，那些仍要 RLVR。
