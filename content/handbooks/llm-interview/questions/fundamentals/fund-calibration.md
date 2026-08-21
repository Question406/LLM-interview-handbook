---
id: fund-calibration
section: fundamentals
order: 19
level: S
title: 模型 Accuracy 很高但 Calibration 很差，产品决策会出什么问题？
quick: >-
  准确率只计对错，不检查置信度是否可信。若 0.9 置信度的样本实际只对 0.6，基于阈值的拒答、人工转交、风险控制和 best-of-N
  都会系统性误判；应结合 reliability、Brier/log loss 与业务成本选阈值。
tags:
  - Calibration
  - ML
  - Decision
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: On Calibration of Modern Neural Networks
    url: 'https://arxiv.org/abs/1706.04599'
    type: legacy-reference
---

Accuracy 只问「对不对」，不问「报 0.9 时是否真有九成把握」。两个模型 top-1 相同，过度自信的那个会把拒答、人工转交、自动写操作和 best-of-N 全部推到错误一侧：该拦的放行，该放行的浪费坐席。面试陷阱是把准确率当成决策质量——产品用的是概率，不是名次。

## Reliability diagram 与 ECE 陷阱

校准问的是：模型说置信度 $p$ 的那一桶样本，经验正确率是否接近 $p$。Reliability diagram 横轴是预测置信度分桶，纵轴是桶内 accuracy；完美校准落在对角线上，点在线下方是过度自信（现代网络的常见形态，见 Guo et al., 2017）。只报一个 ECE 数字不够：你必须能指出「0.9 那一桶实际只有 0.6」。

ECE 是各桶 $|acc(b)-conf(b)|$ 按样本量加权。坑很多：桶数、等宽 vs 等频会改数字；概率堆在 $0.9$ 附近时少数桶吃掉误差；它对高风险尾部不单独惩罚。可以刷好看的做法包括少开桶、合并高置信桶、只评容易题。Brier score 与 NLL 对整段概率更敏感，应和 diagram 一起报，并按领域、难度、语言、时间切片——全局 ECE 好看、安全题或新域崩了，产品仍然不能上自动档。

## 阈值必须按成本定，不是 0.5

决策边界应由代价矩阵决定，而不是默认 $0.5$。漏过一次高风险写操作（错转账、错发邮件、错删）远贵于多转一次人工；低风险检索可以更松。校准差时，「看起来很稳」的 0.9 可能只对 0.6，阈值形同虚设。best-of-N 若用未校准分数选赢家，会系统性偏爱自信、完整、但错的候选。高风险动作除了更高阈值，往往还要独立 verifier 或人类确认，不能单靠 softmax。

上线后阈值要随分布漂移重估：同一数字在昨天的 in-domain 上合理，在新意图、新语言上可能过松。把「覆盖率 $c$ 时的精度」和业务代价一起看，比只看 accuracy 更能回答「能不能自动」。

## Temperature scaling 修的是解释，不是知识

温度缩放 $q_i=\mathrm{softmax}(z_i/T)$ 便宜，常能拉直 in-distribution 的 diagram，但不创造知识：OOD、提示域切换、工具结果分布变了，$T$ 会失效。校准集必须独立于训练/验证，并随线上分布滚动更新。它不提高 accuracy，更不能替代权限与确认。把温度缩放当「模型变可靠了」，是把后处理说成能力。

现场落地先画一张 reliability 图再谈阈值：点出高置信桶的实际正确率，列出拒答/转人工/自动执行三档的代价，再决定数字。没有这张图，accuracy 再高也只是分类器成绩，不是产品决策质量。校准监控要进周报，和延迟、安全投诉并列，而不是训练结束时算一次 ECE。面试收口：accuracy 回答「会不会做题」，calibration 回答「敢不敢自动」；没有 diagram 和代价，就没有阈值。

## 追问

- **ECE 怎么被刷好看？** 少桶、合并高置信桶、只报容易题。要求同时看 diagram、最高置信尾部桶和 Brier/NLL；数字能刷，图上的弯不好藏。
- **OOD 怎么办？** 先做域外检测再拒答或转人工。温度缩放只在校准分布附近有意义，OOD 上 $T$ 不能当信心。
- **和 accuracy 一起报什么？** reliability 图、Brier/NLL、按切片的覆盖–精度曲线，以及每档阈值对应的业务代价（漏放 vs 误拒）。没有代价，阈值只是拍脑袋。
- **Temperature scaling 之后还要重训吗？** 一般不必。它是验证集上拟合的一个 $T$，不改表示；分布一变就要重估 $T$，不是一劳永逸。
