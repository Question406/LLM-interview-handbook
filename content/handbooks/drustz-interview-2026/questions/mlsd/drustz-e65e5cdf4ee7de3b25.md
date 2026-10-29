---
id: drustz-e65e5cdf4ee7de3b25
section: mlsd
order: 114
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 11. 数据配比与 batching ⭐⭐
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 11. 数据配比与 batching ⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
## 11. 数据配比与 batching ⭐⭐

### 11.1 多域比例怎么定

| 方法 | 做法 | 什么时候用 | 失效方式 |
|---|---|---|---|
| **目标反推** | 按 eval / 产品分布配比 | 目标明确、eval 可信时的默认起点 | **eval 分布 ≠ 最优训练分布**。eval 上占 10% 的能力可能需要 30% 的训练数据才学得动 |
| **yield 驱动** | 按各域「非退化 prompt」的产出量分配 | 早期数据紧张时 | **会坍缩到最容易验证的域**（数学挤掉开放推理），因为可验证性和产出量正相关 |
| **学习进度驱动**（推荐做主机制） | 按各域近期 eval 提升速率分配（多臂老虎机 / prioritized replay 的思路） | 中后期 | **饿死慢域**：安全、长程任务提升慢但重要 → 必须设**比例下限** |
| **固定不动** | 拍一个比例训到底 | 只在做 ablation 需要控制变量时 | 无法响应漂移 |

**我会怎么组合**：`每域比例下限（保底） + 剩余份额用学习进度分配 + 一条冻结配比的 canary run 做对照`。最后那条 canary 很重要——**没有对照组的话，你无法区分「自适应配比有用」和「训练本来就会涨」**。

**跨域难度不可比是个真问题**：math 的 p=0.5 和 code 的 p=0.5 不是同一件事（code 的 verifier 更严、部分得分结构不同）。做法是**按域各自维护难度带和normalization统计量**，而不是全局用一个阈值。

### 11.2 Interleaved batching：为什么不能按域分 batch

| 做法 | 优点 | 问题 |
|---|---|---|
| **域同质 batch**（一步全是 math，下一步全是 code） | 调度简单（同域 verifier 延迟一致，sandbox 可批量复用） | ① 梯度方向逐步切换，产生**振荡**，且优化器的近期记忆偏向最后见到的域；② reward 尺度分域不同 → 每步的 advantage 尺度跳变，和 Adam 的二阶矩估计相互作用（它适应得比域切换慢）；③ 任何 per-batch normalization（advantage std、token 级 loss 归一）变成**域条件的**，跨步不可比 |
| **Interleaved（样本级混合，推荐）** | 梯度平稳、normalization统计量可比、每步都是「平均任务」 | **verifier 延迟差异巨大**：数学正则是微秒级，代码 sandbox 是秒级 → 慢 verifier 会 stall 整步 |

**解法**：在样本级 interleave，同时**把生成和验证解耦**——rollout 写入队列，verifier 池异步消费，训练步从「已验证完成」的缓冲区取数据。这样慢 verifier 只增加端到端延迟，不阻塞每步。代价是引入了轻微的 off-policy 滞后（缓冲区里的样本来自上一两个 checkpoint），需要作为一个显式参数控制（缓冲深度 ↔ off-policy 程度的取舍）。

**一句话**：interleaved batching 的动机不是「多样性好听」，是**normalization统计量的可比性**。GRPO 的 advantage 在组内归一，但 batch 级的 loss 归一、gradient clipping、优化器状态都是跨组共享的——域同质 batch 会让这些共享量在域之间来回跳。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
