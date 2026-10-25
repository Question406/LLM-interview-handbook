---
id: pt-test-time-search-topology
section: posttrain
order: 28
level: S
title: 固定推理预算时，并行采样、顺序反思、Verifier rerank、list-wise merge 应怎样公平比较和选型？
quick: "比较的是整套推理系统，采样次数 $N$ 不是统一的货币。固定总 token、模型调用次数、实际耗时和验证器（verifier）成本，再分别报候选覆盖率、选择器和合并器的质量、尾延迟；拓扑按题目能不能验证、中间能不能打分、动作能不能回滚来选。"
tags:
  - Test-time Search
  - Verifier
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Scaling Test-time Compute for LLM Agents
    url: https://arxiv.org/abs/2506.12928
    type: primary
  - title: Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters
    url: https://arxiv.org/abs/2408.03314
    type: primary
---

公平比较要锁总预算，别锁采样次数 $N$：总生成 token、模型调用次数、实际耗时、验证器（verifier）和工具费用都固定下来，再看「生成 + 选择 + 合并 + 环境交互」整套系统的表现。选型时先问三件事：中间状态能不能打分、终局能不能验证、动作能不能回滚，答完拓扑基本就定了，用不着从论文名字出发。

为什么 $N$ 不能当统一的货币？并行采样、顺序反思、prefix 搜索、verifier rerank、list-wise merge，各自消耗的 token、调用次数和耗时差得很远。白板上记一笔账就清楚：总预算 $B$ token，一条长反思把 $B$ 用完，没有对照样本；$N$ 条短样本每条 $B/N$，有覆盖但每条更浅；verifier 每次还要 $c$ token，实际能用于生成的额度是 $B - N_{\mathrm{ver}}c$。不把 $c$ 算进去，rerank 看起来就像「免费变强」。另一个常见错误，是把数学题上 Best-of-N 的成绩直接外推到带副作用的工具 Agent。`pt-best-of-n-decomposition` 已经拆过 coverage 和候选选择器（selector），这张卡往下问一步：预算锁定以后，哪种拓扑该上哪类题。

## 每种拓扑适合什么题

并行采样适合答案能独立生成、事后能投票或验证的题，覆盖靠多样性，选择靠 vote 或 verifier。顺序反思适合后一步能用上前一步失败信息的题，比如错因、测例、工具报错，样本之间相关性高，但信息能复用。prefix-level search 要求中间状态能打分（PRM、单元测试、部分证明），适合可以剪枝的搜索树。rerank 的上限是候选池里已经有正确解，selector 只决定能不能把它捡出来。list-wise merge 还额外依赖模型能不能忠实整合证据、不引入新错，池子里没有正解时，merge 常常会「圆」出一个错答案。

大致的规律是，终局可验证的题（数学、单测）偏向并行加 verifier；需要改计划的 Agent 偏向顺序或树搜索。有没有中间分可用，看 `pt-prm-orm-critic`，它决定了能不能做 prefix 搜索。没有中间分还去做深树搜索，等于拿终局奖励做低效的 credit assignment。

## 实验怎么报

锁定预算之后，我会分开报这几样：generator 的 oracle upper bound（池子里有正解时的上界）、真实 selector 和上界之间的 gap、候选之间的相关性（相关性高，并行就是浪费）、P50 / P95 latency、每个成功任务的平均成本。只报最终准确率，会把「换了个更贵的拓扑」写成「推理变强了」。`pt-best-of-n-decomposition` 里 coverage / oracle / actual 三条曲线在这里照样适用，只是横轴从 $N$ 换成「已花的预算」。单题要不要继续想归 `pt-adaptive-thinking-budget` 管，这张卡管的是预算在拓扑之间怎么切。

看结果时，候选相关性高，说明并行的边际覆盖接近零，该去改温度、改提示，或者换成顺序反思来引入新信息。selector gap 大，钱就该投在 verifier 校准上，继续加采样没用。

## 工具环境还要算副作用

数学上的拓扑不能直接搬到 Agent。工具分支会写文件、发请求、改外部状态，所以搜索的成本里要算上 reset、sandbox、状态快照，还要看动作能不能回滚。不能回滚时，盲目并行等于把事故面放大，应该先规划再执行，或者把搜索限制在只读仿真里。尾延迟也要盯：并行的 P50 好看，P95 可能被最慢的 verifier 或工具拖垮，服务 SLO 先爆。

如果要画一张选型表，行放「可验证 / 有中间分 / 可回滚」，列放并行、顺序、prefix、rerank、merge。预算口径统一成 token + 调用 + 实际耗时，再去比准确率和 P95。

## 追问

**为什么固定 $N$ 不公平？**
不同拓扑单次尝试的 token 和外部调用能差一个数量级，$N$ 根本不是同一种货币。一条长反思，和十条短样本加 verifier，花掉的 $B$ 完全不同。

**rerank 没涨分，先查什么？**
先查 oracle coverage。池子里没有正解，换再强的 selector 也救不了，应该回头改生成或改拓扑。coverage 已经饱和、actual 还不涨，才是 selector 或校准的问题，见 `pt-best-of-n-decomposition`。

**merge 什么时候有害？**
候选互相矛盾又没有 verifier 时，模型会折中出一个新错误，还不如挑一条。只有证据能对齐、又有一致性检查的时候，merge 才值得花钱。

**和训练时的强化学习（RL）怎么分工？**
训练改善的是提议分布，测试时的拓扑决定这笔预算怎么花。分布很差的时候，先别堆 $N$。控制器（`pt-adaptive-thinking-budget`）负责单题要不要升级拓扑，不负责在错误的货币上比较算法。
