---
id: data-agent-trajectory-quality-gate
section: data
order: 214
level: S
title: Agent Trajectory 入库前应设哪些质量门槛？
quick: >-
  不只看最终成功。我会查 schema 合法、无越权、关键证据可追溯、无死循环或空转，再做去污和难度标签。失败轨迹按可学习类型分桶后才能进训练。只存 reward 大于零，会被「看起来忙」的长轨迹带偏。
tags:
  - Agent Data
  - Trajectory
  - Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: AgentBench
    url: https://arxiv.org/abs/2308.03688
    type: primary
---

这块容易直接答成「只存 $\mathrm{reward}\gt 0$」，或觉得成功率数据越干净越好。成功轨迹也可以含答案泄漏、偷看隐藏状态、或靠 flaky 环境偶然通过；失败轨迹整条丢掉，学生就不会恢复。`arl-trajectories` 讲为什么成功-only 在状态分布上不够；本题把那套思想落成入库门禁：静态校验、可回放、过程异常、失败分桶。AgentBench 一类评测已经表明：环境噪声和工具失败是常态，训练数据若只留完美演示，线上一偏就空转。

## 成功轨迹也会脏，先过静态与回放门

入库前至少五道门：

1. **Schema / 权限**：工具名、参数类型、是否越权；非法 call 不得当正 SFT。
2. **环境一致性**：同一环境 hash 下重放可复现；过期 API、flaky 通过要丢或重标。
3. **过程异常**：重复同一工具、无进展空转、步数虚高刷奖励。
4. **答案可验证**：最终结果能被独立 checker / 单元测试核对，别停在「看起来像做完」。
5. **敏感信息脱敏**：日志、检索片段、截图 OCR 里的 PII 出库前清掉。

成功但关键证据不可追溯（没引用到的文件、没真正读到的页面）按泄漏或投机降权。合成轨迹额外做自污染与教师偏差检查（`data-synthetic-self-contamination`）：教师把答案写进 thought、学生再学「先看答案再演戏」，会污染整个 agent 池。Verifier 过不了的轨迹（`data-verifier`）不要靠人工「感觉对」放行。

## 失败轨迹要分类，不是整桶当负例

失败按类型分桶：工具 API / schema 错、规划错、感知错、环境超时、权限拒绝。只有可学习的失败才进训练：near-miss 与 recovery 做正的修复后缀，first-error 当 rejected；不可回放、纯环境故障进诊断集，不进 SFT。这和 `arl-trajectories` 的切片一致：失败整条行为克隆会模仿错误动作。难度标签（步数、工具数、当前 policy 的 pass@$1$）要写进元数据，否则配比无法按桶调。

## 门禁怎么报，才算做过

对照至少四列：原始成功率、过门后条数、各失败桶占比、重放一致率。只报「过滤后 win-rate 更高」可能是把难例删光了。评测应主动注入 first-error，看恢复率，不要只回放教师成功路径。隐藏状态泄漏是 agent 数据特有坑：轨迹里出现用户不可见的 oracle、内部 ID、或评测脚本的标准答案，模型学会「抄环境」而不是用工具。入库要把 thought 与 observation 分开扫，命中隐藏字段整条拒收。最后我会补一句：门禁服务的是可学习信号，别把数据集洗成全绿；成功要可追溯、失败要可切片，空转长轨迹即使最终成功也该降权。

## 追问

- **为什么不能只存成功？** 部署一步走偏就进 OOD，没有 recovery。成功-only 是模仿学习 compounding error，详见 `arl-trajectories`。
- **成功但步数很长怎么处理？** 降权或当效率负例，避免学会「看起来忙」。最终对不等于过程对。
- **合成轨迹还要多哪几道门？** 教师版本、是否泄漏答案进 thought、与真源重叠（自污染）、能否在无教师提示下重放成功。
- **失败轨迹一律当 DPO rejected 可以吗？** 不可以。环境故障和规划错误的 credit 不同；先标 first-error 再决定 prefix / recovery / 整条丢弃。
- **和配比题怎么衔接？** 过门之后才有资格进 mix。脏成功占满 batch，后面再谈 curriculum 也是在优化噪声。
