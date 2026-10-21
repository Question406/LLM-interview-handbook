---
id: dt-tool-error-recover
section: posttrain-data
order: 11
level: S
title: 工具失败之后怎么改，这种轨迹为什么比再堆 10 万成功 JSON 值钱？
quick: "因为只训成功 JSON，模型从没见过合法的失败，遇到 stderr 就可能谎称「已经办好了」。恢复轨迹要覆盖参数错误、空结果、权限拒绝和超时，示范改参数、有限重试或诚实停止。失败那一跳不当正例，恢复后的正确调用当正例，工具报错不计生成损失；报错要来自真实环境，失败比例也要控制。"
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

因为只训成功 JSON 的模型从没见过合法的失败。遇到 stderr 时它没有可学的行为，往往会声称「已经办好了」。所以要专门准备失败后的恢复轨迹：根据报错改参数、换合适的工具，或者诚实说明无法完成。

## 为什么恢复路径更值钱

只训成功的主要执行路径，模型不知道失败后该怎么办。τ-bench 里很多违反政策的情况，都出在失败后乱补。跨次 $\mathrm{pass}^{k}$ 也更容易因为恢复路径不稳定而掉分，见 `dt-tau-passk`。`dt-traj-quality` 讲过被放弃的尝试不能当正确答案，这张卡把它写成可以训练的配方。

## 要覆盖哪些失败

- 参数类型错误或缺字段：示范根据 schema 和报错修改调用，继续用原来那个工具。
- 空结果：示范放宽查询或询问用户，不要把「查不到」当成「不存在」写进回复。怎么核对证据见 `dt-grounding-data`。
- 权限或范围不足：示范拒绝写入，并说明缺什么权限，不要换一个没有鉴权的接口硬写。
- 超时或 5xx：示范有限次重试，然后降级。无限重试会把轨迹占满。
- 注入型观测结果（observation）：示范把它当数据处理，不执行里面的指令，见 `dt-tool-inject`。

## 怎么进损失（loss）

失败那一跳的错误调用不能当 assistant 正例。如果想教模型「别这样做」，用偏好数据里的 lose，或者单独的负向交叉熵损失（CE）。恢复之后的正确调用是正例，用户最终看到的诚实回复也是正例。stderr 作为工具反馈保留在上下文里，但用 mask 排除它的生成损失。

恢复轨迹可以让标注员回滚、改一步、再接着跑，AFM 2025 报告里的被放弃的尝试就是这样来的；没有标注员时，可以让环境故意注入失败。报错必须来自真实环境，不能让教师「想象一段 stderr」，否则学生学不到真实的报错格式。注入的失败比例也要管：全是失败，模型会变得不敢调用工具。这和安全拒答是同一个配比问题，见 `dt-safety-refuse`。

## 追问

- **成功轨迹里要不要留一次失败？** 要。只有成功的主要执行路径太脆。但只留一小段其他尝试，不要把任务本身做砸。
