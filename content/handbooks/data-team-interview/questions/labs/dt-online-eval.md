---
id: dt-online-eval
section: labs
order: 56
level: A
title: Perplexity：线上评测记什么、抽什么、怎么 A/B？
quick: "线上评测用来发现失败类型、验证产品收益和成本。记录版本、延迟和工具行为是否合法，按失败类型分层抽查；A/B 尽量只换权重，正确率、安全和延迟分开报。用户原文进训练要有明确授权，补数据就用许可研究集复现失败，或者做验证过的合成。"
companies:
  - apple
tags:
  - Perplexity
  - Evaluation
  - Privacy
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

线上评测回答的是「产品表现怎样、缺口在哪」，它负责发现失败类型、验证收益和成本。下一轮要补的训练样本，靠研究集复现或验证过的合成来拿，见 `dt-data-flywheel`、`dt-privacy-feedback`。Arena 这类综合分也替代不了安全护栏。

比如一个搜索问答产品换了新权重，线上看到「答案没有得到检索块支持」这类错误变多了。下一步是把这类失败在研究集上复现出来，再据此造训练数据，用户的原始搜索词不直接拿去训。

产品指标和训练来源要分开，是因为有些方案默认把生产日志拿去做下一轮 SFT，这要看用户授权和数据政策。以 Apple 公开的训练数据说明为例，「帮助改进」这个 opt-in 默认是关闭的。即使有授权通道，也应该先按约定汇总成失败类型，把用户搜索词原文直接加进预训练会越过授权范围。

具体做法上，元数据只记必要的：请求 id、模型哈希、提示模板版本、延迟、工具调用是否合法、是否触发拒答，内容能不落盘就不落盘。抽查按失败类型分层，检索类产品可以自动检查答案有没有得到检索块支持，再按这个错误类型统计。做 A/B 时固定提示模板和解码参数，尽量只换权重，分别看正确率、安全和延迟。延迟和正确率要分开报，搜索结果对了但慢了 2 秒，整体体验仍可能变差。

题型参考 Perplexity、Cohere 的公开面试指南，两家都会问线上评测和发布检查。

## 追问

**只抽用户点过赞的请求行不行？**
不行，会漏掉实际出错的类型，所以要按失败类型分层抽。

**改写、重试、复制这类隐式反馈能当偏好吗？**
可以在用户授权的用途内当弱偏好信号。把原文回传用于 DPO 需要单独的授权，见 `dt-userlog-contrast`。

**没有点击数据怎么办？**
用自动切片加定期 user study。空日志训不出满意度模型。

**A/B 样本太少怎么办？**
先在固定研究集上做配对检验，线上只验证方向。小流量上的少量涨分可能只是噪声。
