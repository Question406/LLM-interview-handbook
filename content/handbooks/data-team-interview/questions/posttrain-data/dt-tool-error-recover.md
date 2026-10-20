---
id: dt-tool-error-recover
section: posttrain-data
order: 11
level: S
title: 工具失败之后怎么改，这种轨迹为什么比再堆 10 万成功 JSON 值钱？
quick: "训练恢复路径，覆盖参数错误、空结果、权限拒绝和超时。模型应改参数、有限重试或诚实停止。失败调用不能作正例，正确恢复可作正例，工具错误输出不计生成损失；使用真实环境错误，并控制失败比例。"
companies:
  - apple
tags:
  - Apple
  - Tool Use
  - Trajectory
  - SFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Toolformer
    url: https://arxiv.org/abs/2302.04761
    type: primary
  - title: "τ-bench: A Benchmark for Tool-Agent-User Interaction"
    url: https://arxiv.org/abs/2406.12045
    type: primary
---

专门准备失败后的恢复轨迹：根据错误改参数、换合适工具，或诚实说明无法完成。训练只有成功 JSON，模型遇到 stderr 时可能没有合适行为可学，反而声称「已经办好了」。

不这么选的理由：只训成功成功的主要执行路径，模型没见过合法失败。τ-bench 的政策违反很多来自失败后乱补。跨次 $\mathrm{pass}^{k}$ 更伤在恢复路径不稳定，见 `dt-tau-passk`。`dt-traj-quality` 说被放弃的尝试别当正确答案，这张把它写成可训配方。

苹果：AFM 的被放弃的尝试就是干这个的。人回滚、改一步、再续跑。没有标注员时，环境可以故意注入失败。用户日志不进基础模型，失败的尝试在合成环境里注入。

## 要覆盖的失败类

参数类型错误或缺字段时，示范根据 schema 和报错修改调用，而不是转向无关工具。

空结果。示范：放宽查询或问用户，不要把空当「不存在」写进事实回复。如何核对证据，见 `dt-grounding-data`。

权限 / 范围。示范：拒写，解释缺什么权限。不要换一条没有鉴权的接口硬写。

超时 / 5xx。示范：有限次重试，然后降级。无限重试会占满轨迹。

注入型 观测结果（observation）。示范：当数据不当指令，见 `dt-tool-inject`。

## 怎么进 损失（loss）

失败那一跳的错误调用：若你要教「别这样」，用偏好 lose 或单独的负 交叉熵损失（CE），不要当 assistant 正例。恢复之后的正确调用：正例。用户最终看到的诚实回复：正例。stderr 作为工具反馈保留，但用 mask 排除它的生成损失。

合成注入比例要管。全是失败，模型变得不敢调。和安全拒答同一配比问题，见 `dt-safety-refuse`。

## 追问

- **用教师「想象一段 stderr」行吗？** 不行。要用真环境吐的报错，否则学生学不到真实格式。
- **成功轨迹里要不要留一次失败？** 要。纯成功成功的主要执行路径太脆。控制在一小段其他尝试路径，不要把任务做砸。
- **端上工具失败？** 同样配方，示范更短，最终要能离线拒。
