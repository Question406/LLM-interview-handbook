---
id: sec-memory-persistence-recovery
section: memory
order: 22
level: A
title: "清空 chat history 后仍然复发：如何评估持久攻击与恢复？"
quick: "我会先列出 session 外还保存了什么：memory、retrieval index、工具缓存、生成文件和经验记录。清空聊天只能删除其中一层状态。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
  - "2026 Research"
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: "A Practical Memory Injection Attack against LLM Agents (MINJA)"
    url: "https://arxiv.org/abs/2503.03704"
    type: primary
  - title: "Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents"
    url: "https://arxiv.org/abs/2604.02623"
    type: primary
---

## 题目描述

系统已经修复当次 injection，但下一次新 session 做类似任务时又出现相同行为。

需要讨论：定位持久状态与恢复范围，定义 time-to-recovery、retained utility 和复发指标。

## 回答思路

> **Situation：** 系统已经修复当次 injection，但下一次新 session 做类似任务时又出现相同行为。  
> **Task：** 定位持久状态与恢复范围，定义 time-to-recovery、retained utility 和复发指标。  
> **Approach / Why：** 逐一重置 memory、cache、workspace 与经验库，结合 lineage 查找污染后代。  
> **Result / Check：** 用多个未见 triggers 与正常任务测试恢复，而不是只重跑原 payload。

## 可以这样回答

我会先列出 session 外还保存了什么：memory、retrieval index、工具缓存、生成文件和经验记录。清空聊天只能删除其中一层状态。

恢复实验可以逐层 reset，观察哪一层消失后违规才停止，再根据 lineage 找到由污染内容派生出的记录。只删原始网页，已经总结到 memory 的后代可能仍在。

最后要同时评估复发和有用记忆损失。全部清空可能恢复安全，却抹掉正常个性化；选择性回滚则要证明没有留下可触发的污染。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 先执行一次受控污染，再开启多次新 sessions，插入相似与不相似的正常任务。
- **Baselines / Ablations：** 比较 chat-only reset、整库清空、按 source 删除、按 dependency lineage 回滚。
- **Metrics 与判读：** 测 recurrence rate、恢复所需交互、retained benign memory utility 和误删范围。

## 追问与容易误判的地方

“没有在一组触发器上复发”属于有限覆盖结果。应明确测试了哪些未来任务，以及持续观察的 horizon。

## 论文依据与适用范围

- [A Practical Memory Injection Attack against LLM Agents (MINJA)](https://arxiv.org/abs/2503.03704) · 2025 · research paper。
- [Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents](https://arxiv.org/abs/2604.02623) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
