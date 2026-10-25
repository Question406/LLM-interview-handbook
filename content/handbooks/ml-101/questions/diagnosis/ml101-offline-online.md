---
id: ml101-offline-online
section: diagnosis
order: 1
level: S
title: "离线表现很好，上线效果却差，怎么排查？"
quick: "先确认评价口径和线上流程一致，再检查泄漏、切分是否模拟上线、训练与服务特征是否相同，以及数据和标签分布是否变化。用具体错误样本和分群指标定位原因，每次验证一个假设，再决定修数据、阈值还是模型。"
tags:
  - Machine Learning
  - diagnosis
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Common pitfalls and recommended practices"
    url: https://scikit-learn.org/stable/common_pitfalls.html
    type: primary
  - title: "Dive into Deep Learning: Environment and Distribution Shift"
    url: https://d2l.ai/chapter_linear-classification/environment-and-distribution-shift.html
    type: primary
---

我会先复现一批线上请求，按实际预测时点重建输入，再比较离线与服务输出。这样能先区分是实现和数据流程不一致，还是模型本身面对了更难的人群。

例如离线预测取消订单用了事后更新的“最终支付状态”，上线预测时这个字段还没有。先做按时点取值的回放，重新切分评估，就能判断高分是否来自未来信息。若输入一致但输出不同，再核对特征顺序、缺失默认值、标准化版本和模型版本。

流程一致后，按时间、渠道、新老用户等切片，看误差集中在哪里。新渠道用户变多可能改变输入分布，政策变化也可能改变同类输入对应的标签。用近期、标签已经成熟的数据重新评估，区分真实效果下降与标签延迟。

最后检查模型指标与产品目标的关系。排序变好但审核阈值不合适，可能增加无效工作；产品曝光方式变化也会改变反馈。把每个排查假设对应到一批样本和一次可复现比较，再采取修复。

## 面试追问

**没有及时标签，怎么监测？**
可以先看输入缺失、范围、渠道比例、预测分布和服务错误，但这些只说明流程或分布发生变化。真实效果仍需要延迟标签、抽样人工评价或合适实验。

**发现分布变化就立即重训吗？**
先查变化原因和业务影响。采集故障应修流程，阈值问题可能重新验证规则就够了；需要重训时也要用符合新场景的数据验证。
