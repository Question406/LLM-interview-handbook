---
id: sys-agent-canary-rollback
section: systems
order: 26
level: A
title: 如何为模型、system prompt、tool schema 与 retrieval index 的组合变更做 canary 和一键回滚？
quick: "把模型、prompt、schema、index 等组件组成不可变的发布版本，回滚时整组还原。先跑离线 golden 和对抗切片，再 shadow、小流量 canary；任务、安全、格式、P95 延迟和成本分别设门槛，并保留 snapshot、adapter 与回滚包。"
tags:
  - Canary
  - Rollback
  - Agent Operations
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Google SRE Workbook — Canarying Releases
    url: https://sre.google/workbook/canarying-releases/
    type: primary
---

我会把模型、system prompt、tool schema、retrieval index、policy 和 evaluator 的版本一起记录，并把这个组合当成发布和回滚单位。比如只把模型切回旧版，index 仍是新版，就会得到一个没测过的新组合。请求和 trace 都带组合版本，才能在回归时查清是哪个组件或哪种组合出了问题。

为模型、system prompt、tool schema、index snapshot、policy 各打 immutable version 和兼容性声明。schema 变更提供 adapter：新模型仍能读旧 tool 回包，旧流量也能打到新 schema 的兼容字段。index 用 snapshot id，而不是「当前线上那份」。没有组合版本，canary 指标再漂亮也无法定位。

在线请求写入 `model@prompt@schema@index`，和 trace / 日志对齐。出问题先按组合切片，再下钻单一组件。

发布时先跑离线 golden 与安全对抗集，再做不对外生效的 shadow replay，通过后上小流量 canary，逐步扩大。发布检查要同时比较：task completion、格式/工具错误、安全拒绝、人工升级率、P95 latency、每任务成本。只看平均 win rate 会漏掉「更会答但更会乱调工具、更贵、更不安全」。

上线前就要定好回滚线，让 SRE canary 的自动比较和自动停止机制执行。流量要从 1% 扩到 10% 再扩全量，每档都复用同一组 gate；中途某一档超过回滚阈值就停止，不要「再观察一下」把坏组合放更大。

回滚 artifact 包括整组版本、index snapshot、schema adapter。有外部副作用的 tool（下单、写库）使用幂等键、审计和 kill switch，避免半发布状态继续执行。只回滚模型、index 仍是新的，用户会看到「旧模型 + 新检索」的第三种组合，比不回滚更难查。发布记录里要能一键切回上一组已签名的 artifact，而不是靠人工修改四五个配置项。canary 期间的写操作最好打上版本标签，回滚后可按标签补偿或冻结。

## 追问

**为什么不能只回滚模型？**
其余组件仍是新版本，组合空间多出一个你没测过的点。必须整组还原。
**shadow 和 canary 差在哪？**
shadow 用线上流量打新组合但不对外输出；canary 真的服务一小部分用户。先 shadow 再 canary。
**安全指标为什么要单独设门？**
任务成功率涨、拒绝率掉，可能是更会越狱。和 win rate 拆开。
**index 怎么回滚？**
保留 snapshot，而不是倒着再跑一遍构建。构建不可逆、不可即时。
**tool schema 不兼容怎么发？**
先上 adapter 让新旧并存，再切模型；不要同一天改 schema 和模型，否则回滚要同时撤两处。
**只看平均 win rate 会漏什么？**
高风险切片（拒答、工具乱调、贵长尾）被均值淹没。gate 必须带安全和成本，不只是任务分。
