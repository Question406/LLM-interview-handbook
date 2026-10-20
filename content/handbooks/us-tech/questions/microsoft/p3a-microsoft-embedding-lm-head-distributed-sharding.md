---
id: p3a-microsoft-embedding-lm-head-distributed-sharding
section: microsoft
order: 610
level: A
title: "Microsoft AI / Copilot：Embedding 与 LM Head 分片及通信"
quick: "先写清输入输出张量的布局，再分别计算词表轴切分和隐藏轴切分各需要怎样的路由、聚合和通信量。"
companies:
  - microsoft
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · embedding-lm-head-distributed-sharding"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/embedding-lm-head-distributed-sharding
    type: secondary
---

## 题目

词表矩阵大到单张 GPU 放不下，需要把 Embedding 和 LM Head 分片到多张卡上。比较按词表轴切和按隐藏维切两种方式：每种切法下前向怎么算、要传多少数据、推理时 top-k 或采样怎么做。

> 来源：一亩三分地 Microsoft 题卡摘要（2026-10-18 读取），属于网站对候选人报告的二手整理，没有逐条核对原帖，网站收录也不代表公司官方确认；摘要也没有明确此题就是 MAI 的题。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

先把张量布局写清楚：Embedding 输入是 token id，输出是 B×H 的特征；LM Head 输入是 B×H 的隐藏状态，输出是 B×V 的 logits。然后针对每种切法算三件事：数据怎么路由到对应分片、结果怎么聚合、各需要传多少字节。

- Embedding 按词表切时，每个 rank 只存一段 token id 范围，需要先判断 token 属于哪个 rank，再把查到的向量送回并恢复原顺序。
- LM Head 按词表切时，每个 rank 只算出本地那一段词表的 logits，要得到全局 top-k 或归一化概率，就必须跨 rank 聚合。

讨论里还要带上两点：热门 token 集中在某些分片会造成负载不均；如果 Embedding 和 LM Head 共享权重（weight tying），两边的切分方式必须对齐。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

练习设定：词表 V = 100 万，H = 4096，FP16 权重约 8.192 GB；假设单卡只能给这个矩阵分 4 GB，所以至少要切成两片。输入是一个 token batch，推理时需要 top-k。

先问面试官：只关心推理还是也要训练、batch 大小大概多少、是否有 weight tying、采样需要精确的 softmax 分布还是 top-k 就够。

### 一套可展开的参考答案

**1. 架构与关键路径。** 两种切法的通信布局不同：

- Embedding 按词表行切：每个 token 路由到存有该行的 rank，取出 H 维向量后再按原顺序拼回。
- Embedding 按 hidden 切：每个 rank 存全部词表的一段特征维，各自查出局部特征，再沿 hidden 维拼接。
- LM Head 按词表列切：每个 rank 用完整的隐藏状态乘本地那一段权重，输出本地 logits。

**2. 数据模型和状态变化。** 每个 rank 保存自己负责的分片范围、offset 和模型版本。同一个 batch 里重复出现的 token 可以先在本地去重，再 gather，减少通信。有 weight tying 时，Embedding 和 LM Head 的分片映射必须一致，否则同一行权重会落在不同的 rank 上。

**3. 追踪一次前向。** 设两张卡，rank 0 存 token id [0, 500000)，rank 1 存 [500000, 1000000)。一个 batch 里 token 为 [12, 700001, 12]：先去重得到 {12, 700001}，12 发往 rank 0，700001 发往 rank 1；两边各回传一个 4096 维向量，按原位置还原成 3×4096 的输入。经过 Transformer 后，最后的隐藏状态广播给两个 rank，各自算出 50 万维的本地 logits 并取本地 top-k，最后合并两份 top-k 得到全局 top-k。

**4. 失败、重复与恢复。** 某个分片节点缺失时，不能随便拿别的版本的权重顶上。请求携带模型 epoch，所有 rank 必须对齐同一个版本。跨节点的 collective 要设统一的超时，并且能整体失败退出，避免一个 rank 挂住导致其他 rank 永远等待。

**5. 容量和验证指标。** Embedding 的通信量要比较两部分：发送 token id 的字节，以及回传 B×H 特征的字节。LM Head 如果只要 top-k，只需合并各 rank 的本地 top-k；但完整的 softmax 或采样还需要先归约全局最大值和 sumexp。

### 面试追问与参考回答

**分布式采样怎么做？** 一种做法是先算出每个分片的概率质量，按质量选中一个分片，再在该分片内采样，这和从完整分布采样等价。也可以用其他等价的分布式策略。但不能只从全局 top-k 里抽样，同时声称这是完整的 softmax 采样。

**为什么 softmax 需要先归约最大值？** 为了数值稳定，每个 rank 计算 $\exp(z_i - m)$ 时要用同一个全局最大值 $m$。做法是先 all-reduce max 得到 $m$，各 rank 再算本地 $\sum \exp(z_i - m)$，最后 all-reduce sum 得到分母。这样每个 token 只需传两个标量，而不用把 V 维 logits 全部汇总到一处。
