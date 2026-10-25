---
id: pt-best-of-n-decomposition
section: posttrain
order: 29
level: S
title: Best-of-N 的提升中，生成器覆盖率与 Verifier / Selector 排序能力各贡献多少？如何分配算力？
quick: "把 Best-of-N 的提升拆成两部分：候选池里有没有正确答案（coverage），候选选择器（selector）能不能挑中它。先报 oracle-selection 上界，再报实际结果和上界之间的 selector gap；覆盖率低就改生成，gap 大就投验证器（verifier），盲目加大 N 只是在买测试时计算。"
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

我会把 Best-of-N 的分数拆成两件事来看：候选池里有没有正确答案，selector 能不能把它挑出来。前者是生成器的覆盖率，后者是 候选选择器（selector） 的排序能力。先画覆盖率，再画 oracle 上界，最后画实际 selector，三条线重合才谈加大 $N$；中间哪里有缺口，算力就投给哪个环节。

为什么要拆？Best-of-N 同时花了生成算力和选择算力。不拆开，你分不清该继续训生成器、该训 验证器（verifier），还是只是在买测试时计算。把榜上的 BoN 分数和 Pass@1 混在一起报，等于把测试时计算记成训练收益，产品上要在延迟和成本上还债。

举个例子。同一道可验证题，生成器在中等温度下采一批候选。池子里已经有正确的最终答案，可 RM 总挑最长、最像「逐步说明」的那条，而那条算错了。这时 coverage 高、actual 低，该先改 verifier 的校准、去掉长度偏置，把 $N$ 再翻倍没用。换一种情况：$N$ 条都在同一个错误的代数变形上打转，一条正确答案都没有，coverage 低，就该提高采样多样性，或者回去训生成器、上 on-policy 强化学习（RL）。BoN 在这里只是把同一个错误复制了很多遍。

## 三个量怎么定义、怎么读

每道题保留全部 $N$ 条候选，用一个和正在优化的 selector 独立的 oracle（可执行答案、更强的独立裁判、人类）标对错，然后同时报三个量。

Candidate coverage 是池子里至少有一条正确答案的题目比例，也就是生成器的上界，和 `pt-rejection-sampling-vs-rl` 里的 K-success 曲线是同一类诊断。Oracle selection 假设有一个完美 selector，总能挑出那条正确候选；池里没有正确候选就记失败，所以它 $\le$ coverage，在「每题最多一条满分」的设定下两者常常重合。Actual Best-of-N 是真实 verifier、奖励模型（RM） 或投票选出来的准确率，它和 oracle 之间的差就是 selector gap。coverage 回答「答案在不在池子里」，gap 回答「挑得准不准」。

把这三条随 $N$ 变化的曲线画出来，大致有三种读法。coverage 随 $N$ 慢慢上升、actual 贴着 coverage，说明 selector 已经够用，瓶颈在生成分布，应该改 sampling（温度、diverse beam）、训更好的 generator，或者接受更大的 $N$，把算力花在更复杂的 judge 上收益很小。coverage 已经饱和、actual 远远落后，通常是候选高度相关（$N$ 条几乎是同一条的改写）、verifier 校准差，或者 selector 偏爱冗长和套话，这时加大 $N$ 是在复制同一个错误，该投资过程监督、校准和去相关采样，见 `pt-reward-ood-failure`。actual 已经接近 oracle、oracle 本身却不高，说明生成器根本没采出正确解，BoN 没法从没有的东西里挑，先回去看 Pass@K 训练曲线和温度，换更大的 RM 没用。

几个实操细节。候选要在过滤之前就存下全量 $N$ 条和 oracle 标记，事后才能重放不同的 selector。三条曲线要和 token 成本画在同一张图上，再把 unique 候选数画成第四条，一眼就能看出名义 $N$ 有没有注水。温度、top-p、是否 diverse 采样会同时改 coverage 和候选相关性，要当作因子记进同一张表，别只扫 $N$。

相关候选会让「名义 $N$」远大于「有效 $N$」。看 unique 答案数、n-gram 重叠，看候选是不是总在同一条错误思路上打转。去相关可以换温度、换系统提示，或者加显式的 diversity 惩罚；不做的话，N-coverage 曲线会过早变平，让人误以为生成器已经饱和。过程奖励（Let's Verify Step by Step 一类）改变的是 selector 拿到的信息，不会自动提高 coverage。步骤看起来像样的错解会被 PRM 排得更靠前，gap 甚至可能变大，这和 `pt-reward-ood-failure` 说的「高分幻觉」是同一类失效。

## 算力怎么分

比较时把生成、judge、重试、聚合的 token 和延迟全部算进去，换成同一条准确率-成本曲线，它就是 `pt-reasoning-token-cost-frontier` 里边际收益那张图的测试时版本。

经验上，coverage 离 1 还很远，就把增量预算给 generator 或更大的 $N$；失败主要来自 gap，就把预算给 verifier、过程检查或独立裁判；两者都高但线上延迟太高，就降 $N$、做级联，或者蒸馏进单次生成。级联比固定大 $N$ 更像产品：先用小 $N$ 或短解码筛掉容易题，只对 selector 拿不准的题加采样，平均成本比「每题都走 $N$ 路」低。拿不准可以用候选间一致性或 RM 分差来定义，不必一上来就用最贵的过程裁判。

线上还要把 judge 的延迟算进 SLO。$N$ 路生成本来就贵，再串一个大 RM，首个 token 的等待时间可能先超标。必须用大裁判的话，做成异步，或者只对分差接近的题调用。coverage 在生成结束后马上就能用 oracle 算出来，别等 judge 跑完才发现池子里根本没有正确答案。「训练时没涨、测试时加大 $N$ 涨了」也别对外说成模型变强，这笔账要记在 serving 成本上。

## 追问

**多数投票算 selector 吗？**
算，它默认正确解是众数。有系统性偏差时，错解更一致（都抄同一条常见错误），投票会放大错误，coverage 看着还行、actual 很差。投票前先看 unique 答案分布。答案空间很小的题（选择题、是非题）更要小心，错选项也可能成为众数。

**oracle 能用正在训的 RM 吗？**
不能，那会把 selector gap 直接定义成零，得出「selector 已经完美」的假结论。gold 必须是可执行答案或独立的更强裁判。过程 RM 尤其不能当自己的上界，它会和生成器一起学「看起来在逐步推理」。

**N 到多少开始不划算？**
看 coverage 的边际增益和 unique 候选数，曲线变平、候选高度重复时，再加 $N$ 只增加延迟。没有万能数字。不同难度桶的拐点也不同，难题可能还在涨、简单题早就饱和了，要分开画。

**和训练时的 RS 什么关系？**
测试时的 BoN 是推理策略，RS 是把筛过的轨迹拿去做 监督微调（SFT）。coverage 低的时候两者都救不了，要先改善 on-policy 生成，见 `pt-rejection-sampling-vs-rl`。BoN 涨了、蒸馏进单次模型后又掉回去，说明收益主要来自测试时计算，应该记成成本，别写成「模型能力」。
