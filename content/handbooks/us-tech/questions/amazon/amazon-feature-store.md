---
id: amazon-feature-store
section: amazon
order: 8
level: A
title: Amazon：特征存储一致性，训练/服务特征偏移？
quick: "训练和服务要共用特征定义与变换，训练再按 event time 取标签发生前的历史值。SageMaker Feature Store 的 online 保存最新值、offline 追加历史，但窗口、缺失填充和发布版本仍要由管道统一。可以记录线上特征，再按请求时间离线重放，逐列查偏移。"
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

避免训练/服务偏移，要让两边使用相同的特征定义和变换，并且让训练只读到预测当时已经发生的事件。比如预测昨天的点击，若取的是今天的加购次数，离线 AUC 会很好看，线上却根本拿不到这些未来信息。

SageMaker Feature Store 的 online store 提供低延迟的最新值，offline store 在 S3 追加历史；两边一起开启才会同步。Recs、风控和搜索精排都会遇到这类一致性问题，存储之外仍要检查时间、窗口和写入管道。

## 先对齐时间和特征含义

一条特征要有 `record_id`（asin / customer_id）和 `event_time`。Online 留最新值供实时推理，offline 留历史供训练和回放。标签发生在 $T$ 时，训练应取 $t \le T$ 的最后一条记录；这就是官方所说的 point-in-time query。用 Spark 自己拼接也要满足同一条件：

$$
x_e(T)=\mathrm{last}\bigl\{x:\mathrm{id}(x)=e,\ \mathrm{event\_time}(x)\le T\bigr\}
$$

这里处理时间只是写进 Feature Store 的时钟，和事件发生时间不同。流任务晚到 10 分钟，按处理时间切训练集就可能漏掉点击，或者把它放进错误窗口。线上「过去 10 分钟交易次数」和训练 SQL 要共用窗口及迟到策略；一边取 10 分钟、一边取 7 天，测到的提升就不可信。

接着核对缺失值和变换。线上没有记录填 0、训练却丢行，模型看到的就是两套分布，冷启动 ASIN 尤其受影响，见 `amazon-cold-start`。填充规则应写进特征定义，两边调用同一函数。训练里做了 `log1p`、服务忘了做，或训练用品牌词表 v3、线上还用 v2，也会产生偏移。可以把变换代码打版本，让训练作业和推理容器读同一镜像，词表随特征一起发布。

聚合的业务含义也要统一。「7 日购买次数」是否含退货、是否按 marketplace 切分、时区取 UTC 还是当地，都应写清。搜索和推荐共用信号时，一个 feature group 保持一个定义，避免复制一列后各自修改。主键和单位也要检查：跨设备用户 id、ASIN 大小写、event_time 的秒和毫秒，任何一处不一致都可能拼错行。

## 再对齐发布版本，并用回放验证

双塔 item 向量也是特征。模型周更、ANN 索引日更时，新 query 塔可能碰上旧 item 索引，形成 `amazon-two-tower` 中的编码漂移。特征组和索引别名要作为同一发布单元管理。

下面的代码表达的是「只取时刻之前的最后一个值」：

```python
def pit_lookup(hist, entity, t):
    # hist: list of (event_time, value), sorted
    rows = [v for ts, v in hist if ts <= t and entity]
    return rows[-1] if rows else None  # same fill as serving
```

实际作业使用 Feature Store / Athena 的时间旅行 API。验证时，记录一批线上请求当时读到的特征向量，再让 offline 按原请求时间重放拼接，逐列比较。这样能直接找到偏移的列。p99 变差还可能来自 online 热 key，需要另查 `amazon-p99-stream`。

权限也属于发布契约：online 给在线服务，offline 给训练，两边 ACL 可以不同。原始 PII 不应进入可被广告模型扫描的 group，见 `amazon-guardrails`。在 Leadership Principles 中，这类事故对应 Dive Deep 和 Ownership；上线门禁见 `amazon-lp-ml`。

## 追问

**训练能直接读 online 吗？**
不能把它当历史训练集。Online 没有历史和点时间语义，最多用于比较当前线上分布与训练分布。

**只开一边行不行？**
只开 offline 可以训练，但实时推理每次扫描 S3 不合适；只开 online 又缺少历史。两边都开时，还要确保一次摄入后双路同步，避免两份独立作业各写各的。

**发现偏移先修特征还是先回滚？**
护栏破了先回滚模型别名。若根因在特征，冻结错误版本、修管道，并把失败样本加入评测；修好后再放量。

**这和 ANN 掉点有什么共同点？**
两者都要对齐训练和线上看到的分布。ANN 的差异在邻居集合，这里的差异在特征值，发布时都要统一版本，见 `amazon-two-tower`。
