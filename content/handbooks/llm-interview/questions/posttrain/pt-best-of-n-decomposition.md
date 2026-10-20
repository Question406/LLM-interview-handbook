---
id: pt-best-of-n-decomposition
section: posttrain
order: 29
level: S
title: Best-of-N 的提升中，生成器覆盖率与 Verifier / Selector 排序能力各贡献多少？如何分配算力？
quick: "把 Best-of-N 拆成「候选池有没有正确答案」和「selector 能否挑中它」。先报告 oracle-selection 上界，再报告 候选选择器（selector） gap；若覆盖率低就增加或改善生成，若 gap 大就投资 验证器（verifier），而不是盲目增大 N。"
tags:
  - Best-of-N
  - Verifier
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: OpenAI — Solving Math Word Problems
    url: https://openai.com/index/solving-math-word-problems/
    type: primary
  - title: Training Verifiers to Solve Math Word Problems
    url: https://arxiv.org/abs/2110.14168
    type: primary
  - title: Let's Verify Step by Step
    url: https://arxiv.org/abs/2305.20050
    type: primary
---

别把「N 越大分越高」讲成模型变强。Best-of-N 同时花了生成算力和选择算力；不拆开，你分不清该继续训生成器、该训 验证器（verifier），还是只是在买测试时计算。面试官若追问「提升从哪来」，正确顺序是先画覆盖率、再画 oracle 上界、最后才是实际 候选选择器（selector）。三者重合，才谈增大 $N$；中间出现缺口，钱就要用于改进出现问题的环节。把最终榜上的 BoN 分数和 Pass@1 混报，等于把测试时计算记进训练收益，产品上会在延迟和成本上还债。

## 把分数拆成 coverage 和 selection

对每道题保留全部 $N$ 条候选，并用与正在优化的 selector 独立的 oracle（可执行答案、更强独立裁判、人类）标记对错。三个量必须同时报：

- **Candidate coverage**：池子里至少有一条正确答案的比例。这是生成器的上界，和 `pt-rejection-sampling-vs-rl` 里的 K-success 曲线是同一类诊断。
- **Oracle selection**：假设完美 selector，从池子里总能挑出那条正确候选时的准确率。没有正确候选时记失败，因此它 $\le$ coverage，两者在「每题最多一条满分」的设定下常常重合。
- **Actual Best-of-N**：真实 verifier / 奖励模型（RM） / 投票选出的准确率。与 oracle 的差就是 **selector gap**。

coverage 回答「答案在不在池子里」；gap 回答「挑得准不准」。只报最终 BoN，等于把两件事捆死。向面试官要白板时，先画三条随 $N$ 变化的曲线再开口，比先报一个分数更难被追问到说不清。三条曲线缺一条，结论就站不住。实验记录里这三条要和 token 成本画在同一张图上，否则仍会把测试时计算说成模型变强。把 unique 候选数画在第四条轴上，能立刻看出名义 $N$ 有没有注水。实现上不要在过滤后才存候选：必须留全量 $N$ 条和 oracle 标记，才能事后重放不同 selector。用正在优化的 RM 当 oracle，gap 会被定义成零，实验会得出「selector 已经完美」的假结论。生成端的温度、top-p、是否 diverse 采样，都会同时改 coverage 和候选相关性，要当作因子记进同一张表，而不是只扫 $N$。

## 三条曲线怎么读

画 $N$-coverage、$N$-oracle、$N$-actual。读法比调 $N$ 重要：

- **Coverage 随 $N$ 缓慢上升，actual 贴着 coverage。** Selector 已经够用，瓶颈在生成分布。应改善 sampling（温度、diverse beam）、训更好的 generator，或接受更大 $N$；把算力用于更复杂的 judge 上收益很小。
- **Coverage 已饱和，actual 远远落后。** 候选高度相关（$N$ 条几乎是同一条的改写）、verifier 校准差、或 selector 偏好冗长/套话。这时增大 $N$ 是在复制同一错误。应投资过程监督、校准、去相关采样，而不是盲目加候选，见 `pt-reward-ood-failure`。
- **Actual 接近 oracle，但 oracle 本身不高。** 生成器根本没把正确解采出来。BoN 不能从没有的东西里挑。先回去看 Pass@K 训练曲线和温度，而不是换一个更大的 RM。

相关候选会让「名义 $N$」远大于「有效 $N$」。看 unique 答案数、n-gram 重叠、是否总在同一条错误思路上打转。过程奖励（Let's Verify Step by Step 一类）改变的是 selector 的信息，不自动提高 coverage。去相关可以用不同温度、不同系统提示、或显式 diversity 惩罚；不去做，N-coverage 曲线会过早变平，让人误以为生成器已经饱和。

## 算力怎么分配

比较时要把生成、judge、重试、聚合的 token 和延迟全部计入，换算成同一条准确率-成本曲线，和 `pt-reasoning-token-cost-frontier` 的边际收益是同一张图的测试时版本。

经验决策：coverage 离 1 还很远 → 把增量预算给 generator 或更大 $N$；gap 占了大部分失败 → 把预算给 verifier / 过程检查 / 独立裁判；两者都高但线上延迟过高 → 降 $N$、级联（先短生成再对不确定题加采样）、或蒸馏进单次生成。不要用「训练时没涨、测试时加大 $N$ 涨了」对外宣称模型变强。那是买测试时计算，账要记在 serving 成本上。级联比固定大 $N$ 更接近产品：用小 $N$ 或短解码先筛容易题，只对 selector 不确定的题加采样，这样平均成本低于「每题都 $N$ 路」。不确定度可以用候选间一致性或 RM 分差定义，不必一上来上最贵的过程裁判。

## 一个定性例子

同一道可验证题，生成器在中等温度下采一批候选。若池子里已经出现正确最终答案，但 RM 总挑最长、最像「逐步说明」的那条，而那条算错了，coverage 高、actual 低，应优先投入资源改进 verifier 校准和去长度偏置，而不是把 $N$ 再翻倍。若 $N$ 条都在同一个错误代数变形上打转，一条正确答案都没有，coverage 低，应改采样多样性或回去训生成器 / 上 on-policy 强化学习（RL），BoN 只是把同一错误复制多遍。

过程奖励改变 selector 的信息密度，不自动提高 coverage：步骤看起来像样的错解会被 PRM 排得更靠前，gap 甚至变大。这和 `pt-reward-ood-failure` 的「高分幻觉」是同一类失效。线上还要把 judge 延迟算进 SLO：N 路生成已经贵，再串一个大 RM，首个 token 的等待时间可能先超标。若必须用大裁判，做成异步或只对分差接近的题调用，不要每条候选都走一遍完整过程模型。Coverage 诊断应在生成结束后立刻用 oracle 算，不要等 judge 跑完才发现池子里根本没有正确答案。

## 追问

- **多数投票算 selector 吗？** 算，而且假设正确解是众数。系统性偏差下，错解更一致（都抄同一条常见错误），投票会放大错误，coverage 看起来还行、actual 很差。投票前先看 unique 答案分布。答案空间很小的题（选择题、是非）更要小心：错选也可能形成众数。
- **Oracle 能用正在训的 RM 吗？** 不能。那会把 selector gap 定义成零。Gold 必须是可执行答案或独立更强裁判。过程 RM 尤其不能当自己的上界，它和生成器会一起学「看起来逐步」。
- **N 多少开始不划算？** 看 coverage 的边际增益和 unique 候选数。曲线变平且候选高度重复时，再加 $N$ 只增加延迟。不要背一个万能数字。不同难度桶的拐点不同，难题可能仍在涨、简单题早已饱和，要分开画。
- **和训练时 RS 的关系？** 测试时 BoN 是推理策略；RS 是把筛过的轨迹拿去 监督微调（SFT）。coverage 低时两者都救不了，要先改善 on-policy 生成，见 `pt-rejection-sampling-vs-rl`。BoN 涨、蒸馏进单次模型后掉回去，说明收益主要在测试时计算，应写进成本而不是「模型能力」。
