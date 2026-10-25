---
id: company-stepfun
section: companies
order: 16
level: A
title: 阶跃星辰：大模型 / Agent 算法应重点准备什么？
quick: "阶跃算法岗会追基于可验证奖励的强化学习（RLVR）策略、混合加训 vs continue 监督微调（SFT）、Benchmark 分组统计迭代、GRPO 组内优势；Agent 岗会追工具奖励、ReAct 各块 I/O、trl / VeRL 调参。手撕出现过 top-p 和 GRPO。"
tags:
  - StepFun
  - 真题导航
  - Agent RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
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

阶跃面经偏「真的训过」，会问监督微调（SFT）损失（loss）的起点、1T 和小模型有什么不同、VeRL 的类名和参数。我会准备一个能复现训练过程和结果的 Agent 工具训练案例，这比罗列框架名有用。

比如面试官问「你这个 SFT 的 loss 起点是多少、后来怎么收敛的」，真训过的人能直接讲出曲线，只读过文档的人这里就会卡住。

## 准备主线

1. 后训练策略要讲清基于可验证奖励的强化学习（RLVR）的验证器（verifier）和用当前策略新采样的轨迹，以及混合加训和 continue SFT 各自适合什么条件。
2. 评测迭代时，Benchmark 按能力、难度、失败类型分组统计，公开题不直接拿来当奖励分数（reward）。
3. Agent 工具强化学习（RL）的奖励拆成安全门、结果、过程和成本，数据配比里保留难例和失败轨迹。
4. ReAct 接口要说清 Plan / Action / Observation 各自的输入输出长什么样，能不能对齐日志的字段和类型规范（schema）。
5. 公式会问 GRPO 的组内优势和 baseline，以及 RL 训 MoE 时的路由漂移，可以对照 GSPO。

## 本手册真题卡

下面每条点进去就能跳到对应题。

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
