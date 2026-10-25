---
id: "ml101-anomaly-detection"
section: "diagnosis"
order: 10
level: "A"
title: "无监督异常检测怎么建立基线和评价？"
quick: "先定义什么异常值得处理，再用规则和简单统计建基线，比较 Isolation Forest、LOF 等方法。无标签时只能先看告警量、稳定性和抽样复核，少量可信标签到位后再按审核预算评估 precision、recall 和漏检代价。"
tags: ["ML101", "diagnosis"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "scikit-learn: Novelty and Outlier Detection"
    url: https://scikit-learn.org/stable/modules/outlier_detection.html
    type: primary
---

无监督异常检测先要确定异常的含义，再选模型。离群点是在当前数据里不合群；新颖性检测则先用相对干净的正常数据学习，再判断新样本。训练数据是否混有异常，会影响算法与评估方式。 [scikit-learn: Novelty and Outlier Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)

我会先做范围规则和单变量稳健统计基线，再比较 Isolation Forest 这类随机切分方法，或 LOF（局部离群因子）这种与附近密度比较的方法。比如交易额很大未必异常，对大客户正常、对长期小额用户却可疑，需要结合分组或上下文。

输出先当异常分数，阈值按审核容量和漏报成本选择。没有标签时，抽查高分、阈值附近和随机样本，观察告警量、分组偏差与时间稳定性；形成可信评价集后，在新时间段比较固定审核预算下的命中率和召回。

## 追问

**contamination 就是真实异常比例吗？**
通常是模型设阈值所用的配置，不能据此证明真实业务异常率。

**训练集分数很极端，说明模型有效吗？**
不够。还要看新数据表现，并确认是否只识别到尺度或缺失模式。

**LOF 能直接预测新样本吗？**
sklearn 需要用 `novelty=True` 的方式拟合，且新颖性预测接口应评估未见过的数据，不能与训练集的 `fit_predict` 混用。
