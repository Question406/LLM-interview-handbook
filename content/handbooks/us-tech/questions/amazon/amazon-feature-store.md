---
id: amazon-feature-store
section: amazon
order: 8
level: A
title: Amazon：特征存储一致性，训练/服务特征偏移？
quick: >-
  同一特征定义、同一变换、按 event time 做点时间拼接。线上读最新，训练读「标签时刻之前」的历史。窗口、时区、缺失填充、模型版本有任何一处各写各的，离线
  AUC 就是假的。SageMaker Feature Store 的 online / offline 只是底座，对齐是你的管道。
tags:
  - Amazon
  - Feature Store
  - Training-Serving Skew
  - SageMaker
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Create, store, and share features with Feature Store
    url: https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store.html
    type: primary
  - title: Amazon SageMaker Feature Store
    url: https://aws.amazon.com/sagemaker/ai/feature-store/
    type: primary
  - title: Feature Store storage configurations
    url: https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store-storage-configurations.html
    type: primary
---

Recs / 风控 / 搜索精排岗把这题当 ML 系统常识。SageMaker Feature Store 公开文档把训练-服务偏移写成它要解决的问题：online 低延迟最新值，offline S3 追加历史，两边一起开才会同步。Amazon 面试要你讲清仍会偏的地方：点时间、窗口、双写。不是「我们用了 Feature Store」就能过。Leadership Principles 落点是 Dive Deep 和 Ownership：偏移是事故，不是调参。门禁见 `amazon-lp-ml`。

## 两种时间，两种读法

一条特征要有 `record_id`（asin / customer_id）和 `event_time`。Online store 只留最新，给实时推理。Offline 是追加历史，给训练和回放。训练若读「现在的 online」，等于用未来的加购次数预测昨天的点击，泄漏。正确是点时间：标签发生在 $T$，特征只能用 $t \le T$ 的最后一条。

官方强调 offline 的 point-in-time query，就是为了这个。自己用 Spark 拼也行，契约不能少：

$$
x_e(T)=\mathrm{last}\bigl\{x:\mathrm{id}(x)=e,\ \mathrm{event\_time}(x)\le T\bigr\}
$$

处理时间（写入 Feature Store 的时钟）不等于 event time。流式任务晚到 10 分钟，训练若按处理时间切，会丢迟到的点击或塞进错窗口。线上聚合「过去 10 分钟交易次数」必须和训练 SQL 同一窗口、同一迟到策略。窗口一边 10 分钟一边 7 天，是最常见的假提升。

缺失值：线上没有记录时填 0，训练丢行，模型学到的是两套分布。冷启动 ASIN 尤其惨，见 `amazon-cold-start`。填充规则要写进特征定义，两边调用同一函数。

## 还会偏的，Feature Store 不会替你挡

**变换双写。** 训练在 notebook 里 `log1p`，线上服务忘了；训练用品牌词表 v3，线上还在 v2。Store 存的是数值，不审你的语义。做法：变换代码打版本，训练作业和推理容器读同一镜像；词表当特征的一部分一起发布。

**聚合定义漂移。** 「7 日购买次数」是否含退货、是否按 marketplace 切、时区用 UTC 还是当地。搜索和推荐共用信号时更容易各写各的。一个 feature group 一个定义，别复制列。

**索引 / 模型版本。** 双塔 item 向量也是特征。模型周更、ANN 索引日更，线上 query 塔新、item 索引旧，就是 `amazon-two-tower` 里的编码漂移。特征组和索引别名要绑在同一发布单元。

**时钟和主键。** 用户跨设备 id 对不上；同一 ASIN 大小写；event_time 用秒对毫秒。点时间会拼错行，看起来像模型变差。

**权限和 PII。** online 给在线服务，offline 给训练。ACL 不同。原始 PII 不该进可被广告模型扫的 group，见 `amazon-guardrails`。

```python
def pit_lookup(hist, entity, t):
    # hist: list of (event_time, value), sorted
    rows = [v for ts, v in hist if ts <= t and entity]
    return rows[-1] if rows else None  # same fill as serving
```

真正的作业用 Feature Store / Athena 的时间旅行 API。面试画的是这个不变量，不是 SDK 方法名。

监测：同一批线上请求，把当时读到的特征向量落一份，过后再用 offline 按请求时间重放拼接，逐列比。差的列就是偏移。这比再刷一次 AUC 有用。p99 变差也可能是 online 热 key，不是模型，见 `amazon-p99-stream`。

## 追问

- **能不能训练也读 online？** 不能当训练集。online 没有历史，也没有点时间。最多拿来做「现在 vs 训练分布」的漂移监控。
- **只开 offline 行不行？** 训练行，实时推理每次扫 S3 不行。只开 online，训练没有历史，做不了点时间。两边都开，还要你保证写入是一次摄入、双路同步，而不是两份作业。
- **发现偏移先回滚模型还是先修特征？** 护栏破了先回滚模型别名。根因是特征就修管道、冻结错误版本、把失败样本放进评测。修完再放量，不要在脏特征上接着训。
- **和双塔 ANN 掉点是同一类问题吗？** 同一类「训练看到的分布 ≠ 线上看到的分布」。那边是邻居集合，这边是特征值。都要用同一发布单元对齐，见 `amazon-two-tower`。
