---
id: pt-test-time-search-topology
section: posttrain
order: 28
level: S
title: 固定推理预算时，并行采样、顺序反思、Verifier rerank、list-wise merge 应怎样公平比较和选型？
quick: "比较的对象是完整推理系统，而不是“采样次数”。固定总 token 数、模型调用次数、实际耗时和 验证器（verifier） 成本；再按候选覆盖率、选择器质量、合并器质量和尾延迟拆开，依据题目是否可验证决定拓扑。"
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

测试时搜索的选型对象是「生成 + 选择 + 合并 + 环境交互」整条系统，不是「$N$ 次采样谁分高」。并行采样、顺序反思、prefix 搜索、验证器（verifier） rerank、list-wise merge 消耗的 token、调用次数和实际耗时完全不同。常见误区是：固定 $N$ 比较拓扑，或把数学题上的 Best-of-N 成绩外推到带副作用的工具 Agent。`pt-best-of-n-decomposition` 拆 coverage 与 候选选择器（selector）；本题进一步问：预算锁定后，哪种拓扑该上哪类题。

## 拓扑各自吃哪类题

- **并行采样**：答案可独立生成，后验能投票或验证。覆盖靠多样性，选择靠 vote / verifier。
- **顺序反思**：后一步能利用前一步的失败信息（错因、测例、工具报错）。相关样本多，但信息可复用。
- **prefix-level search**：中间状态能打分（PRM、单元测试、部分证明）。适合可剪枝的搜索树。
- **rerank**：收益上限是候选池里已经有正确解；selector 只决定能不能捡到。
- **list-wise merge**：额外依赖模型能否忠实整合证据、不引入新错。池中无正解时，merge 常会「圆」出一个错答案。

可验证终局（数学、单测）更偏并行 + verifier；需要改计划的 Agent 更偏顺序或树搜索。`pt-prm-orm-critic` 决定你有没有中间分可用，从而能不能做 prefix 搜索。没有中间分却做深树搜索，就是在用终局奖励做低效 credit assignment。

白板记账：设总预算 $B$ token。一条长反思用掉 $B$，没有对照样本；$N$ 条短样本各 $B/N$，有覆盖但每条更浅；再扣掉 verifier 每次 $c$ token，实际生成额度是 $B - N_{\mathrm{ver}}c$。不把 $c$ 算进去，rerank 会看起来「免费变强」。

## 实验锁的是总预算，不是 $N$

一次长轨迹、十条短轨迹、十次 verifier 调用的成本不同。比较时应固定：总生成 token、模型调用次数、实际耗时、verifier / 工具费用。然后分别报告：

- generator 的 oracle upper bound（池中有正解时的上界）
- 真实 selector 与上界的 gap
- 候选间相关性（高相关则并行浪费）
- P50 / P95 latency
- 每成功任务的平均成本

只报最终准确率，会把「换了更贵的拓扑」写成「推理变强」。`pt-adaptive-thinking-budget` 管单题要不要继续想；本题管预算在拓扑之间怎么切。`pt-best-of-n-decomposition` 的三条曲线（coverage / oracle / actual）在这里仍然适用，只是横轴改成「已花预算」而不是 $N$。

相关性高时，并行的边际覆盖接近零，应改温度、改提示、或改顺序反思来引入新信息。selector gap 大时，钱应投 verifier 校准，而不是继续加采样。

## 工具环境多记一笔副作用

不要把数学拓扑直接搬到 Agent。工具分支会写文件、发请求、改外部状态。搜索必须计入 reset、sandbox、状态快照和动作可回滚性。不可回滚时，盲目并行等于放大事故面；应先规划再执行，或把搜索限制在只读仿真里。尾延迟也很关键：并行在 P50 好看，P95 可能被最慢的 verifier 或最慢的工具拖死，服务 SLO 先爆。

先问「中间能不能打分、终局能不能验证、动作能不能回滚」，再问「预算主要该给生成还是给选择」。答完这四问，拓扑几乎被决定，不必从论文名字出发。选型表：行是「可验证 / 有中间分 / 可回滚」，列是并行、顺序、prefix、rerank、merge。预算口径统一为 token + 调用 + 实际耗时后再比准确率和 P95。

## 追问

- **为什么固定 $N$ 不公平？** 不同拓扑单次尝试的 token 和外部调用差一个数量级，$N$ 不是同一货币。一条长反思和十条短样本加上 verifier，花的 $B$ 完全不同。
- **rerank 没涨分先查什么？** 先查 oracle coverage。池里没有正解，换更强 selector 也救不了，应回头改生成或改拓扑。coverage 已饱和而 actual 不涨，才是 selector / 校准问题，见 `pt-best-of-n-decomposition`。
- **merge 什么时候有害？** 候选互相矛盾且无 verifier 时，模型会折中出新错误，不如挑一条。merge 只在证据可对齐、且有一致性检查时值得花钱。
- **和训练时 强化学习（RL） 怎么分工？** 训练改善提议分布；测试时拓扑决定这笔预算怎么花。分布很差时，先别堆 $N$。控制器（`pt-adaptive-thinking-budget`）负责单题是否升级拓扑，不负责在错误货币上比较算法。
