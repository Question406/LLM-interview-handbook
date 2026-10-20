---
id: design-feature-store
section: design
order: 9
level: A
title: 设计：特征平台，点查延迟、训练一致性
quick: >-
  在线点查有 p99 预算，离线关联特征时，要保证只用事件发生当时已知的数据。同一份变换代码服务两条路径。泄漏（用了标签之后的特征）会让线下指标骗人。监控在线/离线同一 key 的值是否漂移，比再上一个特征更要紧。
tags:
  - Feature Store
  - Meta
  - Google
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Feast documentation
    url: https://docs.feast.dev/
    type: primary
  - title: Meet Michelangelo — Uber’s Machine Learning Platform
    url: https://www.uber.com/blog/michelangelo-machine-learning-platform/
    type: primary
  - title: System Design in a Hurry
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

Meta / Google 排序、Uber Michelangelo、Amazon 个性化，MLE 系统设计常把「模型」问成「特征怎么来的」。Feast 把 online / offline 拆开；Michelangelo 强调生产化。白板要的是点查 p99、时间点正确、训练-serving 一致。推荐和广告的特征查询往往耗尽打分的延迟预算，见 `design-recsys`、`design-ads-rank`。

## 两条路径，一份定义

我会先问：实体（用户 / 物品 / 请求）、QPS、点查 p99、特征新鲜度（毫秒级计数还是天级画像）、是否跨机房。然后禁止「训练用 Spark 随手 join、线上用另一套 SQL」。

- **离线。** 训练表按事件时间取特征：只允许 $t_{\mathrm{feat}} \le t_{\mathrm{event}}$，并落在特征窗口内。这叫 point-in-time join。用「当时能看到的信息」复现线上，而不是用当天结束的聚合。
- **在线。** 按实体 key 点查：Redis / 自研 KV，value 是 typed 特征向量或按 view 拆开。批量 mget，避免 N+1。热 key（头部用户）要本地缓存 + 单飞。
- **定义。** 特征 view：实体、窗口、源表、变换函数、TTL。变换代码同一份（同一 UDF / 同一版本号）。版本写进训练样本和线上请求日志，回放才能对上。

```python
def pit_lookup(rows, as_of, window_s):
    # rows: (ts, value) 已按 ts 升序
    lo = as_of - window_s
    picked = None
    for ts, val in rows:
        if ts < lo:
            continue
        if ts > as_of:
            break
        picked = val
    return picked  # None 表示缺失，走默认或丢样本
```

缺失不是 0。计数类填 0 可能有意义，embedding 类填 0 是另一种语义，要在 schema 里声明，并在训练和 serving 用同一个默认。

## 延迟、新鲜度、一致性

点查 p99 是排序 p95 的大头。手段：列裁剪（模型只用到的 view）、压缩、分片按实体、流水线预取（召回阶段就带物品特征）、预算内降级（丢掉最不重要的实时特征，避免整次打分失败）。超时返回必须标记 `feature_stale=1`，模型或规则走保守路径。

新鲜度 SLO 按特征分级：实时点击计数秒级；人口统计可以天级。流式写入要用事件时间，处理乱序和重复。窗口计数（过去 1h 点击）在线和离线窗口要对齐，差一个「是否含当前事件」就会漂。

训练-serving 监控：抽样同一 `(entity, request_id)`，比线上日志里的值和离线回放值。相对误差超阈告警。往往比再加一个特征更管用。Schema 演进：加字段要默认值；改语义要新名字，不要原地改 `click_1h` 的定义。

失败模式：泄漏（join 了点击之后的停留时长当特征预测这次点击）；时钟（处理时间和事件时间混用）；热 key 请求让 KV 服务过载；embedding 表没随物品上架更新；两个模型共用一个 view 但一个以为是标准化后的值。泄漏会让离线 AUC 很好、上线平或更差，和随机 split 分子数据是同一类错，见 `gdm-ml-design`。

漂移监控不必复杂：每分钟抽 N 个 `request_id`，比线上日志里的特征向量和离线 PIT 回放。相对误差超阈告警，并按 view 拆，才能知道是实时计数漂了还是 embedding 表没刷。热 key 用本地 LRU + 单飞，避免头部用户让 KV 服务过载，拖高全站 p99 延迟。

## 指标

点查 p50/p95/p99、缺失率、过期率、在线/离线漂移率、回放成功率、训练 job 因 PIT join 倾斜导致的延迟。特征重要性要能下线无用 view，否则 KV 只涨不降。权限：用户删除数据后特征 TTL 和删除传播要有 SLA，不能只删日志不删 KV。

## 追问

- **为什么不训练时直接读在线 KV？** 历史回放需要对过去时间点的值，在线 KV 只有现在。没有离线 store 就无法复现。
- **实时特征和 batch 特征谁优先？** 按 freshest-available 但带版本；混用要在样本里记下用了哪路，否则漂移无法归因。
- **点查 p99 超了砍什么？** 先砍交叉最大、增益最小的实时特征；召回阶段预取物品特征。不要先换模型结构。
- **和 检索增强生成（RAG） 向量库是一回事吗？** 都是检索，但特征平台强调时间点和一致变换；向量库强调召回质量。别把 ANN 当 PIT join。
