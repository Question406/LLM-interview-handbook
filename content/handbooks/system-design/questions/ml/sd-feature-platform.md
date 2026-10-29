---
id: sd-feature-platform
section: ml
order: 22
level: A
title: 特征平台：事件时间、回填与训练服务一致性
quick: 假设一个训练样本使用了下单后才得到的信息，而线上预测发生在下单前。离线训练看起来很准确，部署后却拿不到同样的 feature。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Feast：Point-in-time joins
    url: 'https://docs.feast.dev/getting-started/concepts/point-in-time-joins'
    type: primary
  - title: Google：Rules of Machine Learning
    url: 'https://developers.google.com/machine-learning/guides/rules-of-ml'
    type: primary
---

## 题目描述

设计同时支持实时推荐和离线训练的特征平台。输入有用户行为事件、实体键、预测时间与特征定义；事件可能迟到、重复和回填。输出应包括在线点查、历史训练集构建、版本升级与删除传播，并解释按事件时间和数据实际可用时间避免未来信息泄漏。请给出一次10:00预测的具体例子。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 假设一个训练样本使用了下单后才得到的信息，而线上预测发生在下单前。
>
> **做法与原因：** 我会按事件时间保存和查询 features，让 training 能重建当时实际可见的信息。
>
> **检查与取舍：** 再比较 training 与 serving 的 feature 定义、新鲜度和缺失处理。

## 可以这样回答

假设一个训练样本使用了下单后才得到的信息，而线上预测发生在下单前。离线训练看起来很准确，部署后却拿不到同样的 feature。

我会按事件时间保存和查询 features，让 training 能重建当时实际可见的信息。Backfill 也必须遵守这个规则，而不是用今天的最新值覆盖历史。

再比较 training 与 serving 的 feature 定义、新鲜度和缺失处理。既要检查模型分数，也要检查某地区、某用户类型是否经常拿到过期或空 features。

## 技术备查

## 参考答案与设计讨论

从预测发生时可知的信息重建训练特征，在线与离线共用定义与版本，点查延迟和新鲜度分别设目标。

### 时间语义先于存储选型

只按事件时间早于10:00过滤还不一定够：某条9:59事件可能10:02才到达。如果训练目标是精确复现线上当时所见，还要记录可用时间、处理延迟或使用线上快照。特征的 window boundaries 和是否包含当前事件必须明确。

### 两条路径使用同一份定义

批流计算产出带版本特征，在线存储按实体与特征视图点查，离线存储保留历史以做 point-in-time join。回填写入新版本或可追溯批次，避免直接覆盖历史事实。默认值与缺失标志在训练和服务保持一致。

### 升级与验证

抽样请求日志回放同一实体、同一时点和版本，与线上记录比较缺失率、值偏差和新鲜度。热键用批量点查、受控缓存与请求合并；扩容与删除也要传播到缓存和历史训练导出。

### 示例与关联

10:01才发生的停留时长不能用于10:00预测；9:59发生但10:02到达的事件，也不能用于复现10:00实时可见特征。详见[特征平台原有完整讨论](?book=us-tech&section=design&question=design-feature-store)。

