---
id: us-leveling
section: overview
order: 3
level: B
title: E4 / L5 / L6 在 LLM 岗面里，评委预期差在哪？
quick: >-
  初级要独立改对模块、能讲清复杂度；中级要能在正确性和系统约束之间做权衡，并推动接口；更高级要能定义评测、
  预判失败模式、把并行 / 数据 / 产品风险说成可执行计划。同一道 GQA，三个级别答的不是同一个深度。
tags:
  - 级别
  - 备考
  - 行为面
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Levels.fyi engineering levels
    url: https://www.levels.fyi/
    type: secondary
  - title: Hello Interview — leveling and expectations
    url: https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
    type: secondary
---

可以按独立负责的范围理解级别差异：初级把模块做对，中级能协调接口和系统约束，更高级能把模糊目标变成评测、容量和风险计划。美国大厂的职级名字不统一，例如 Google L3-L6、Meta E4-E6、Amazon SDE1-SDE3，因此下面用同一道题对照回答深度，避免硬套名称。

## 同一道题，三级答法

以 逐 token 生成（decode） 显存为例。

- **偏新毕业 / L3-L4：** 写出 $KV \propto H_{\mathrm{kv}} \cdot T \cdot d$，能手写一步 cache，知道 GQA 是减 $H_{\mathrm{kv}}$。公式对、代码对，就过线。
- **中级：** 主动提 batch、paged attention、量化 cache、prefill/decode 分离。能说「这里优化带宽而不是 FLOPs」。先说清正确性不变量，再谈加速。
- **更高级：** 会问产品约束：最长上下文、并发会话、SLA、回滚策略。能设计评测（有 cache vs 无 cache greedy 对齐），能讲容量规划，能指出谁该做 kernel、谁该做调度。

系统设计同理。初级画出检索-生成；中级加上新鲜度、权限、引用；高级加上多租户配额、评测切片、失败时的人工升级。

## 行为面用实际贡献说明范围

行为面可以用真实经历说明：怎样把模糊问题收成可验证目标，数据不够时如何决定是否上线，以及自己和他人的贡献分别是什么。像「主导万卡集群」这样的描述，只有确实做过、能回答细节时才使用。

## 追问

**跨级投怎么办？**
按目标级别准备系统深度，电面仍按模块正确性打底。系统讲得很满但 attention 写错，仍然挂。
**Scientist 和 Engineer 级别语言？**
Scientist 多讲假设和证据；Engineer 多讲接口、故障和可维护性。同一篇论文，两种岗追问点不一样。
