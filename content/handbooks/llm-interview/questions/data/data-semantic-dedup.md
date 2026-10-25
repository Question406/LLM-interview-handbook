---
id: data-semantic-dedup
section: data
order: 10
level: A
title: Semantic Dedup 怎么做而不过度删除？
quick: "Embedding 相似只说明语义接近，证明不了训练信号重复，所以先用向量召回相似候选，再结合题意、答案或程序结构、推理模板和 metadata 判断是不是同一信号，最后在簇内挑代表。阈值按领域和数据价值分组校准，高价值的多解法数据要留下不同思路。"
tags:
  - Data
  - Dedup
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: SemDeDup — semantic deduplication at web scale
    url: https://arxiv.org/abs/2303.09540
    type: primary
---

我的做法是把 embedding 只当召回用：先拉出高相似的候选，再判断它们是不是同一个训练信号，最后在每个簇里挑代表留下。光凭 cosine 阈值一刀切，要么误删高价值的不同解法，要么留下一堆重复模板。

举个例子，同一道数学题的两种证法，题面向量几乎一样，但两条都该留；反过来，两个输入提示（prompt）措辞完全不同，解法模板却一模一样，这种就该合并。所以判断「是不是同一个 training signal」，要看题意、答案或程序结构、推理模板这三样是不是同时接近，只比题面向量不够。

## 先召回，再判是不是同一信号

典型的流水线是：embedding ANN 拉出高相似候选，用规则或 cross-encoder、小模型复核，然后聚类，每个簇留代表。判定时可以把 prompt embedding、答案或 AST、reasoning signature、来源 metadata 拼成联合特征。

顺序上，lexical / MinHash 近重复（`data-minhash`）先做，它便宜而且准，先把克隆砍掉；语义层只处理逃过 n-gram 的改写。监督微调（SFT）的 train/test 泄漏检查（`pdd-sft-template-dedup`）用的是同一套近邻，但决策更严：跨 split 的近邻默认可疑，簇内的多解法默认值得人工看一眼。

簇内挑代表时，别默认留最长或最新的那条。更稳的标准是通过了验证器（verifier）、有人工金标、覆盖了稀有约束、来源可信、长度适中。同一道数学题的三种证法，至少要留下两条不同的 proof signature；同一段客服话术只换了称呼，留一条就够了。

## 阈值按价值校准

阈值别全局一个 cosine。按领域、长度、是否可验证分组去扫，对照三列：去重后的 token 数、分层 holdout 增益、被删样本的人工抽检（误杀率）。扫的时候画「删除率 vs holdout」曲线找拐点，别照抄 SemDeDup 论文里的全局阈值，网页预训练和 SFT 指令的信息密度差了一个数量级。高价值的推理和多解法簇提高保留配额；模板改写、安全套话、低信息 FAQ 收紧。

过度删除的典型表现是留出集变得更容易了，分布外数据（OOD）上的多解法表现却在下降。所以发布时要报每个桶的删除率和误杀抽检，光说「去重了百分之多少」不够，把去重率当 KPI 会系统性地误杀稀有解法。语义去重删的是重复的梯度，目的不是把语料洗成单一风格。面试里如果对方说「cosine 大于 0.9 就删」，可以追问他们怎么做误杀抽检、多解法配额怎么定，没有这两样，就证明不了去重策略可靠。

## 追问

**相似但解法不同怎么办？**
保留多样性。按证明思路或算法签名再分一层组，每个簇可以留 $k$ 条代表，不必只留 1 条。

**和 MinHash 谁先做？**
lexical / MinHash 先做，它便宜又准，先砍克隆；语义层只处理改写。两套阈值分开校准。

**阈值怎么定？**
分组扫，看 holdout 增益和误杀抽检。SemDeDup 论文里的某个数，别直接拿来当自己的门槛。

**跨 split 的近邻怎么处理？**
训练侧可以讨论要不要留；评测侧默认按泄漏处理，见 `data-contamination`。
