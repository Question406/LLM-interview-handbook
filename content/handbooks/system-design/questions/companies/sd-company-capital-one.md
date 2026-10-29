---
id: sd-company-capital-one
section: companies
order: 30
level: A
title: Capital One：模型部署、监控与50ms 延迟排查
quick: 既有记录披露了模型上线、监控和50ms 要求；先确认 latency measurement，再沿数据、特征、模型与网络定位瓶颈。
companies:
  - capital-one
tags:
  - System Design
  - 设计练习
  - 已存原帖核对记录
  - 公司练习
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-25T00:00:00.000Z
sources:
  - title: Capital One MLE VO过经
    url: 'https://www.1point3acres.com/interview/thread/1155534'
    type: secondary
---

## 题目描述

仓库已核对的 Capital One MLE 面经涉及模型部署、监控和50ms 延迟要求。请将一个训练好的分类模型接入业务 API，输出版本化部署、特征获取、预测与监控链路，并给出超过延迟要求后的排查顺序。原帖摘要未明确50ms 是模型耗时、端到端、平均值还是分位数，应先澄清，不能擅自补成 p99。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 参考答案与设计讨论

既有记录披露了模型上线、监控和50ms 要求；先确认 latency measurement，再沿数据、特征、模型与网络定位瓶颈。

### 依据与 applicability limits

来源为2025-11-21发布的“Capital One MLE VO 过经”，仓库2026-10-22核对记录提到 Set B 部署、监控和50ms 要求，没有给出完整基础设施约束。本轮继续沿用该记录，模型与数据规模不视为原帖披露。

### 最小上线方案

先固定模型与特征 schema 版本，服务接收有身份与时间语义的输入，获取所需特征，做预处理与预测后返回结果。记录输入质量、版本、延迟和业务后验标签，模型产物先验证再灰度；缺失特征的默认行为与训练一致。

### 怎么查慢在哪里

用端到端 trace 拆开排队、网络、特征点查、预处理、模型执行和序列化。区分冷启动与稳态、平均与尾部、单次与批量；再用连接复用、特征预计算、模型简化或缓存等方案逐个验证。先做测量，不能默认所有延迟都来自模型计算。

### 示例与追问

测出特征查询35ms、模型5ms，其余20ms，总60ms；只把模型压到2ms 仍不满足50ms，需处理关键路径。缓存若会破坏特征新鲜度或权限，不能只为延迟上线。对应`sd-observability-rollout`与`sd-training-platform`。

