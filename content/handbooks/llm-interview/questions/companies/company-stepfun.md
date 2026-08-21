---
id: company-stepfun
section: companies
order: 16
level: A
title: 阶跃星辰：大模型 / Agent 算法应重点准备什么？
quick: >-
  算法岗追 RLVR 策略、混合加训 vs continue SFT、Benchmark 分桶迭代、GRPO 组内优势；Agent 岗追工具奖励、
  ReAct 各块 I/O、trl / VeRL 调参。手撕出现过 top-p 与 GRPO。
tags:
  - StepFun
  - 真题导航
  - Agent RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f
    type: candidate-first-hand
  - title: 阶跃星辰agent算法面经分享
    url: https://www.nowcoder.com/feed/main/detail/d01a17cf25344f4bb73eff2dbbaf6eee
    type: candidate-first-hand
  - title: 阶跃星辰大模型算法实习面经
    url: https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3
    type: candidate-first-hand
---

阶跃面经偏「真的训过」：会问 SFT loss 起点、1T 与小模型差异、VeRL 类名与参数。准备一个可回放的 Agent 工具训练故事，比罗列框架名更有效。

## 准备主线

1. **后训练策略**：RLVR 的 verifier 与 fresh rollout；混合加训和 continue SFT 的适用条件。
2. **评测迭代**：Benchmark 按能力 / 难度 / 失败类型分桶，不把公开题直接当 reward。
3. **Agent 工具 RL**：奖励拆安全门、结果、过程与成本；数据配比保留难例和失败轨迹。
4. **ReAct 接口**：Plan / Action / Observation 各自输入输出长什么样，能否对齐日志 schema。
5. **公式**：GRPO 组内优势与 baseline；RL 训 MoE 的路由漂移，可对照 GSPO。

## 本手册真题卡

点击下面每条即可跳到对应题。

- 阶跃：RLVR 用什么策略，如何根据 benchmark 定位问题并迭代
- 阶跃：针对业务场景，怎样训练 Agent 调工具
- 阶跃：混合加训和 continue SFT 哪个效果好
- 阶跃：以 ReAct 为例，Plan / Action / Observation 的输入输出是什么
- 阶跃：GRPO 的优势值怎么算，baseline 是什么
- 阶跃：GAE 是什么？蒙特卡洛和 TD 有何差别
- 阶跃：RL 训练 MoE 有什么问题，GSPO 怎么改进
- 阶跃：训 1T 级模型和训小模型有何不同
- 阶跃：SFT loss 的起点数值和收敛该怎么看
- 阶跃：BF16 和 FP16 有什么区别
- 阶跃：RL 训 Agent 调工具时数据怎么配比
- 阶跃：用 VeRL 训搜索工具 Agent 时各类角色怎么设计
- 蔚来一面：TRL、veRL、Ray 各管哪一层，怎么选型？
- [[stepfun-adam|阶跃：Adam 的一阶 / 二阶矩怎么更新]]
- 阶跃：手撕 top-p 采样，边界怎么处理
- 阶跃星辰：手撕 GRPO 时 loss 和组内优势分别怎么写？
- 阶跃星辰：GPU 死锁是什么，训练里常见怎么踩到？
