---
id: "ml101-train-serve-skew"
section: "diagnosis"
order: 7
level: "A"
title: "训练与服务特征不一致时怎么定位？"
quick: "先取同一请求，逐阶段对比训练样本与在线特征：原始值、清洗、缺失处理、编码、时间窗口和模型版本。记录实际服务用过的特征，并在离线回放中比较预测，才能区分特征计算不一致与真实流量变化。"
tags: ["ML101", "diagnosis"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "Google ML Crash Course: Monitoring pipelines"
    url: https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring
    type: primary
  - title: "Google: Rules of Machine Learning"
    url: https://developers.google.com/machine-learning/guides/rules-of-ml
    type: primary
---

训练与服务特征不一致，要用同一条请求做对照，沿着特征生成过程找到最早的差异。先比较原始字段，再比清洗、默认值、编码、normalization 和特征顺序，最后确认模型与预处理版本一致。 [Google ML Crash Course: Monitoring pipelines](https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring)

Google 的工程建议包括记录实际服务时使用的特征，再拿来检查训练与服务差异。这样可以发现离线重算看不见的问题，例如训练端用完整一天的统计量，在线却只能看到请求发生前的数据，或两端对缺失值用了不同默认值。 [Google: Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml)

举个排查例子：用户年龄缺失，训练端填中位数，线上填 0；模型没有改，预测也会变化。我会固定模型，用记录的在线特征离线推一遍，再用离线重算特征推一遍，比较各字段和输出，修正计算后做回放及小范围验证。

## 追问

**线上分数分布变了，就能认定 skew 吗？**
不能。也可能是真实流量改变，要分别检查同请求计算一致性和整体输入分布。

**共用同一份代码就够吗？**
还要对齐数据源、时间窗口、配置和依赖版本，相同代码读到不同数据也会有差异。

**为什么特别关注时间？**
训练时若读到预测时刻之后的信息，会产生标签泄漏，离线看起来很好，线上却无法复现。
