---
id: pt-cold-start-to-multistage-rl
section: posttrain
order: 31
level: S
title: 既然 R1-Zero 能纯 RL，为什么生产配方仍常用 cold-start CoT、RL、rejection sampling、二次 RL？
quick: >-
  R1-Zero 证明的是可验证奖励下纯 RL 能放大强 base 的推理，生产还要可读、可解析、能对齐、不丢通用能力，目标多了阶段就多。cold start
  先给格式、语言和基本解题 support；RL 扩探索、优化 奖励分数（reward）；rejection sampling
  回收高质量轨迹并混入通用数据；二次 RL 再对齐通用能力和可读性。
tags:
  - Reasoning RL
  - Cold Start
  - Curriculum
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
---

因为 R1-Zero 回答的是「纯 RL 能不能涌现长思考」，生产配方要回答的是「能不能读、能不能解析、能不能对齐、通用能力掉没掉」。目标多了，阶段就多了。把论文里的存在性实验当成部署处方，是这题最常见的坑。cold start 要做，是因为 outcome 奖励分数（reward） 对语言混杂和格式崩几乎没反应，RL 在数学上并不需要演示；后面每一段都在补一种 Zero 故意没去优化的瓶颈。

举个例子。R1-Zero 的输出经常中英混杂、步骤之间跳着走，可只要最后答案对了，照样拿满分，因为 outcome reward 只看结果。这样的输出产品上没法用。

## 四段各修一个瓶颈

DeepSeek-R1 的生产路径是四段课程，每段的目标都不一样。

第一段是 cold-start SFT。用少量可读的长 chain of thought（CoT，即分步推理过程），把策略拉进「能被解析、语言一致、格式能拿到 reward」的区域。R1-Zero 混语言、可读性差，原因是 outcome reward 不惩罚这些表面问题，它解题的能力并没有问题。没有 cold start，后面 验证器（verifier） 的有效样本率会很低：格式错了就是零奖励，探索预算全浪费在解析不了的轨迹上。即使用户能接受长思考，混中英、没有标记的跳跃推理也上不了线。所以 cold start 是给 reward function 补一层「人能看懂」的先验，用不着再做一遍全量指令微调。

第二段是 reasoning RL，在可验证任务上做 on-policy 搜索，目标是提高解题能力，产品属性留到后面。奖励尽量干净，正确性加一点轻量的格式分，让策略在 cold-start 附近找到更长、更有用的搜索。机制还是 search-selection-amplification，见 `pt-r1zero`。这一段最怕奖励泄漏和长度 hacking：格式分太重会变成套模板，过程分太松会写空洞的步骤。verifier 要比 Zero 实验更严，因为经过 cold start，模型已经会「写得像是对的」。

第三段是 rejection sampling 加混合 SFT。RL 之后策略能产出高质量的推理轨迹，但分布偏数学和代码。RS 把验证过的成功轨迹冻结成监督数据，再混入写作、事实问答、翻译、安全拒答这些非推理数据。这一步做的是 support 回收和能力混合，和 RL 是两回事。RS 只能从已有候选里筛，覆盖率低时筛出来的数据又少又窄，见 `pt-rejection-sampling-vs-rl`。非推理数据的比例要单独扫：太少，二次 RL 之前通用能力就掉了；太多，刚搜到的解题路径会被冲淡。RS 数据还要去重、控长度，免得把最长的成功轨迹复制成新的长度先验。

第四段是二次 RL，在更宽的任务和偏好目标上再对齐：有用、无害、可读、不 over-refusal。推理能力已经有了，这一段防止模型「只会刷题、不会聊天」。偏好奖励噪声大，更新要更保守，还要继续混入可验证题，免得把第一段搜到的解题路径优化没了。产品指标和推理基准要同一天看，光看对齐 leaderboard 不够。

## 生产为什么不直接用 R1-Zero

R1-Zero 的价值在于证明机制：base 的长尾里已经有成功的推理，verifier 负责选，policy gradient 负责放大。生产还要语言一致、指令遵循、安全拒答、长度可控（`pt-reasoning-token-cost-frontier`），以及通用能力不回退（`pt-safety-capability-regression`）。这些目标的奖励噪声比「答案对不对」大得多，用同一套稀疏的 outcome reward 硬冲，往往会牺牲可读性和安全。

cold start 还有一个常被忽略的作用：给 RL 一个可解析的状态分布。on-policy 方法只能优化自己访问过的状态，一开始格式全崩，后面奖励再密也帮不上。这和 `pt-on-policy-distillation` 同源，都是先让学生生成能被有效评分的轨迹。

实验上，四个阶段别合成一条曲线。至少分开报格式率、语言混杂率和可解析率，看 cold start 有没有生效；报 Pass@1 / Pass@K、思考长度和熵，看 RL 是在探索还是只在刷长度；报 RS 之后 held-out 覆盖率和非推理任务有没有回退；报二次 RL 之后的 instruction-following 和安全评测。只看最终基准，就不知道瓶颈在 seed quality、reward、sampling 轨迹（rollout） 还是 data mixing。四段绑在同一个 job 里「一起涨」，事后也说不清格式是 SFT 修好的还是 RL 碰巧学会的。阶段 gating 写成明确的 go / no-go：格式率不达标不进 RL，Pass@K 没抬起来不进 RS，非推理任务回退太深不进二次 RL。这样每个阶段解决了什么问题，才有证据。

常见的错配有三种。一是把 RS 当成 RL 的同义词。RS 从已有候选里筛，没法让策略访问新状态，正确轨迹覆盖率低、或者问题要连续多步探索的时候，筛完还是那几种成功模式，必须回到 on-policy。二是把 cold start 做成大规模指令 SFT，把聊天、安全、知识问答一次灌进去，后面 reasoning RL 的信号被风格先验稀释，也更难归因。三是二次 RL 只用偏好模型、丢掉可验证任务，推理能力会从「会搜索」退回到「说得像在搜索」。

多阶段还会放大 `sys-rl-infra` 里的 rollout、verifier 和权重同步成本。阶段切错时，先查有效 reward 率（解析失败、组方差为零），再查算法。

## 追问

**cold start 要多少数据？**
论文用的是「数千条」量级、可读的长推理过程，远小于一个完整的 SFT 语料库。格式、语言和解题 support 比数量重要。质量差的长推理会把错误格式锁进先验，后面 RL 会更高效地放大它，所以宁可挑题、重写，也别用噪声示范灌满。

**RS 和 RL 能互相替代吗？**
不能。RS 是离线筛选，正确轨迹稀少、需要连续状态探索时还得 on-policy。RS 适合回收已经稳定的成功样本，创造不了新的解题路径。覆盖率已经高的时候，先 RS 再小步 RL，比一上来就大规模 rollout 省。

**二次 RL 会不会把推理冲掉？**
会，如果奖励里推理信号太弱的话。推理任务要继续占一定比例，盯住通用和推理的 Pareto，别只看聊天分。安全拒答变好了、数学掉点了，说明混合比出了问题，谈不上「对齐成功」。回退时先查非推理数据比例，再查偏好模型是不是在奖励套话。

**能用 distillation 代替 cold start 吗？**
可以当作另一条进入 support 的路（`pt-on-policy-distillation`），但仍要有可读的 teacher model（teacher），格式问题照样要解决。teacher 自己混语言，学生会更快学会混语言。teacher 覆盖不到的题型，distillation 也解决不了，那部分仍要靠 RLVR。
