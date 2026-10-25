---
id: ml101-ab-testing
section: probability
order: 10
level: A
title: "A/B 测试怎么避免样本污染和提前偷看？"
quick: "A/B 测试先选不易互相影响的随机化单位，固定分组并按相同单位做分析；同一用户跨组、处理组影响对照组都会破坏解释。事前约定主指标、样本量和停止规则，不能每天用普通固定样本 p 值，显著了就停。需要提前决策时采用预先设计的序贯方法。"
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Microsoft Research: A/B Testing Across Products"
    url: https://www.microsoft.com/en-us/research/articles/a-b-testing-across-products/
    type: primary
  - title: "Microsoft Research: During-Experiment Trustworthiness"
    url: https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-during-experiment-stage/?trk=article-ssr-frontend-pulse_little-text-block
    type: primary
---

我会先固定“谁被随机分组、谁可能影响谁”，再规定什么时候下结论。实验污染改变了两组实际接受的处理，边看边用普通阈值决定停止则改变了误报率，两者要分别处理。

用户级实验要让同一个用户持续留在同一组，跨端身份和分流日志也要一致。如果同一团队的用户会共享配置，或处理组行为会改变对照组看到的内容，用户级的独立分析就可能失效；可以考虑团队级等集群随机化，并在集群层面估计不确定性。随机化让处理分配在设计上不依赖潜在结果，但有限样本仍有波动，干扰和错误曝光也不会自动消失。[Microsoft 的跨产品实验说明](https://www.microsoft.com/en-us/research/articles/a-b-testing-across-products/)强调随机化单位和独立性假设。

比如试一个协作文档功能，同一团队里 A 组编辑产生的内容也会被 B 组看到。即使分流是随机的，对照也接受了部分功能影响。按团队分组能减少这种污染，但有效独立单位变成团队，不能把每次页面访问都当作新样本扩大样本量。

停止规则也要预设。普通固定样本检验的 p 值保证针对约定分析时点；每天算一次，第一次 $p<0.05$ 就宣布成功，整套流程的假阳性率就不再自动受 0.05 控制。可以预先固定时长与样本量，或使用有明确误报控制的序贯边界等方法。[Microsoft 的实验中监控指南](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-during-experiment-stage/?trk=article-ssr-frontend-pulse_little-text-block)明确要求反复观测时处理多重检验和提前偷看。

我还会先检查分流比例异常、曝光埋点和指标分母，再解释业务效果。最终同时报均值差、区间和预设检验结果，别把随机分流后的某个活跃子集直接当成完整实验人群。

## 追问

**实验中完全不能看仪表盘吗？**
可以监控数据质量和重大故障。关键是不能把未经校正的反复显著性检查当作普通固定样本检验的最终决策规则。

**用户有很多次访问，样本量按访问数算吗？**
通常不能直接这样算。访问在用户内相关，统计单位应与目标指标和随机化单位匹配，必要时按用户聚合或使用集群标准误。

**处理组真正使用功能的人更少，要只比较使用者吗？**
不能直接这么筛。是否使用可能受到处理影响，筛后就丢了随机化保证。先报告按原分组的效果，使用者效应需要额外的识别方法和假设。
