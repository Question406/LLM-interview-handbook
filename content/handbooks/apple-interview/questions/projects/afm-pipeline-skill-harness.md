---
id: afm-pipeline-skill-harness
section: projects
order: 8
level: S
title: Pipeline 1：从 Skill 检索与执行失败，造出可训练的适配 trajectories
quick: 我会先看 agent 为什么没用好现成 skill：是没找到、没选，还是照着做也失败。原因不同，要补的数据也不同。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Data Pipeline 实例
  - AFM 2026-10-27
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Skill Usage in Realistic Settings
    url: 'https://arxiv.org/html/2604.04323v1'
    type: primary
---

## 面试官可能这样问

如果让你收集一批数据，教 agent 更好地使用 skill，你会怎么做？

## 可以这样回答

我会先找一批已经能自动验收的任务，让 agent 带着现有 skill 跑一遍。比如让它整理一份有重复记录的 CSV，最后检查输出的统计有没有把重复数据算进去。这样我知道任务到底做对没有，也能回头看它用了哪条 skill。

接下来我想分清楚失败发生在哪。有时相关 skill 已经搜出来了，agent 却没打开；有时它打开了，但是文档里的列名和当前文件对不上。前一种情况，我会收集选择 skill 的例子；后一种情况，就收集把已有方法改到当前任务上，以及出错后怎么恢复的 trajectories。把这些混在一起，只说“多收一些成功数据”，很难知道模型学到了什么。

开始时我会先做一轮 SFT，用实际跑对、过程也合理的 trajectories 教这些行为。新一轮再看没见过的任务组合有没有变好。如果只在原来的 CSV 格式上提高，我会怀疑它记住了模板。等任务和检查方法比较稳定，再考虑在线 RL；这个阶段最重要的是先确认我收的数据确实对应那个失败原因。

## 被追问时再展开

**怎么知道是检索的问题，还是模型不会做？** 我会直接给它一条确认相关的 skill 再跑。如果这样能做对，先查检索和选择；如果仍然失败，就看 skill 内容和执行过程。这个对照比直接重训便宜。

**需要记录哪些东西？** 我最先要的是任务、当时能看到的信息、搜到和打开的 skill、tool calls，以及最后的检查结果。具体存储字段我会在实现时补齐，先保证能用一条记录解释一次失败。

## 英文口述参考

I would start with tasks that already have a reliable checker, and run the agent with the skills it currently has. What I want to understand is why the skill did not help. Did the agent fail to retrieve it, choose not to open it, or use it incorrectly?

Those cases need different data. If the skill was available but ignored, I would collect examples of when to load it. If the agent loaded it but could not adapt it, I would collect successful adaptations and recovery attempts. I would start with supervised training on verified traces, then check whether the improvement transfers to new tasks. Before collecting more data, I would also try giving the agent the right skill directly. That tells me whether retrieval is actually the bottleneck.

## 技术备查

## 公开参考与设计假设
[Skill Usage 研究](https://arxiv.org/html/2604.04323v1) 区分更真实的 skill 检索条件并研究 refinement。下面的 CSV 任务、数据字段和训练 feedback loop 是建议方案，不是论文复现或已做过的生产系统。这里 harness 指 agent 运行框架。

## 1. 任务：从脏 CSV 生成可核验的分语言质量报告
输入一个许可/人工生成 CSV，字段含 doc_id、language、quality、text；要求先按 doc_iddeduplication，按约定保留最新版本，排除缺失质量分，再输出每种语言的有效数、均值与拒收原因。这里的规则写入任务契约，不让 teacher 自己猜。

变体覆盖：缺失值、零条有效记录、low-resource 语言、相同 ID 更新、数据顺序和不同列名。预期输出由独立参考计算器生成，置于 verifier 侧，agent 不能读到。训练与验收按规则组合/输入模式家族分开，不只改 random seed。

## 2. Pipeline 和中间产物
`许可文档/仓库 → skill去重与版本化 → 任务家族切分 → skill检索 → 选择加载 → sandbox执行 → 状态/输出核验 → 轨迹质量审查 → 训练视图 → 独立评测 → 定向补数据`

| 阶段 | 做什么 | 保留的产物和 data quality checks |
| --- | --- | --- |
| 来源 | 收人工 seed、许可操作文档及可用 skill；登记依赖版本 | skill_id、出处、许可、适用条件、content hash；不能默认公开即允许训练 |
| skill 规范化 | 提取输入/输出/前置条件和示例，移除无关安装日志 | 每条 skill 独立跑 smoke task；同内容不同仓库合并，不把坏示例当监督 |
| 任务生成 | 从规则组合生成 CSV 和 instruction，先冻结 split | task_family、seed、数据与环境 hash；排除无解或含糊规则 |
| 采 trajectories | 冻结 harness；从同一初态用不 on-policy/检索条件 rollout | retrieved IDs/rank、loaded IDs、修改内容、工具输入输出、状态版本 |
| 结果核验 | 检查报告的 schema、实体 deduplication、计数/均值、拒收原因 | 结构化结果比对；失败分数据、skill、工具、环境四类 |
| 过程审核 | 检查是否读答案、乱改输入、依赖隐藏状态 | 保留合法成功或有效恢复，丢弃投机取巧的成功 |

## 3. 一条训练样本长什么样
下面是设计字段，不是实测日志。`observation`是当时可见状态，`private_verifier`只在核验侧保存，训练输入必须剥离。

```json
{
  "task_id": "csv-014",
  "task_family": "dedup-latest-missing",
  "split": "train",
  "env_version": "csv-env-v1",
  "harness_version": "agent-v1",
  "policy_checkpoint": "example-policy-v0",
  "retrieved_skill_ids": ["groupby-v2", "dedup-v1"],
  "loaded_skill_ids": ["groupby-v2"],
  "outcome": { "schema_ok": true, "duplicate_count_ok": false, "success": false },
  "failure_mode": "dedup_skill_not_loaded",
  "next_intervention": "add_selection_and_recovery_tasks"
}
```

完整的[示意 JSONL](/apple-prep/pipelines/skill_harness.jsonl)包含成功与失败样本；trajectories 标识与 hash 均为占位符。

## 4. 先诊断，再决定造什么数据
- **找不到相关 skill**：给 oracle 候选后恢复，说明应补索引、query 与检索 hard negatives；不能直接推断需要更多 SFT。
- **检索到了但没加载**：固定候选，只替换加载选择；补“何时该用哪条 skill”的决策与无关 skill 负例。
- **加载了仍失败**：oracle skill 也失败时，查内容、前置条件与执行；补列名适配、版本变化、缺失值处理和正确恢复 trajectories。
- **skill 本身错误**：先修文档/验证 skill，不把其引导的失败全部归给策略能力。

不能按 retrieval recall 单独选最好方案；强制加载只用于诊断。只改 harness 也可能改变结果，所以 harness、tool schema 和模型必须分别做版本与 ablation study。

## 5. 怎样转成 SFT／Preference／RL
**SFT**：选输入可见、过程可接受的成功 trajectories，监督 assistant 的加载选择、适配和 tool calls；用户/工具观察不计目标 loss。若保留恢复片段，包含模型当时确实可见的失败反馈，不把事后答案塞回 prefix。动态 tool 结果作为环境观测，而非让模型照抄生成。

**Preference**：从相同初始 CSV 和同一任务采两个完整候选；正确处理重复/缺失的 trajectories 胜过看似完整却统计错的 trajectories。正确性与权限优先，随后比较不必要加载和成本。近似等质、只风格不同的对按协议 tie 或 soft labels，不强制选长链路。

**RL**：使用可重置 CSV 任务与独立参考输出，current policy 在线 sampling。任务正确性作主要反馈，违规独立约束，成本项必须避免鼓励省掉必要步骤。这里的旧 trajectories 用于任务设计或冷启动，不能直接伪装成 on-policygradient 样本。

## 6. 验收与下一轮
对比 no-skill、固定相关 skill、实际检索、检索＋refinement；保持模型、总 context/inference budget 与训练量可比，额外开销单独报。看真实报告正确率、deduplication/缺失 evaluation slices、跨列名/版本迁移、时间和 token；加载率只是诊断指标。

如果某规则组合仍弱，下一轮补该家族的新数据和恢复，不复用 blind 题。若 oracle skill 已恢复而检索持续无效，预算先投检索与选择；若所有条件都无效，先查任务可解性与工具。

## 90秒英文参考
> I would start with an executable task, such as producing a language-level quality report from a CSV with duplicates and missing values. The harness would log which skills were retrieved, loaded, and adapted. An independent checker would validate the report, rather than asking the agent whether it succeeded. I would use oracle-skill substitutions to separate retrieval from selection and execution failures. Verified trajectories would become SFT data; comparable branches from the same initial state could become preference pairs. For RL, I would sample fresh rollouts in resettable tasks and evaluate on held-out rule combinations.

## 追问
**为什么不直接训最终 report？** 只监督结果可能学不到加载/适配与恢复，tool-use trajectories 监督能定位可操作行为；是否有用仍需 ablation study。
**如何防止学会总加载所有 skill？** 数据要有无需 skill/无关 skill 任务，报告质量与成本一起评，不能只奖励 load。
**与个人经历怎样衔接？** “This is a pipeline I would build based on our skill-usage findings.” 真实负责部分另行补充。

