---
id: afm-pipeline-overview
section: projects
order: 7
level: S
title: 三条可讲到底的数据 Pipeline：Skill／Harness、Code 与 multimodal Tool Use
quick: >-
  把三条 pipeline 分别落到技能选择与适配、代码 verifier、截图驱动工具操作。每条都有任务、数据契约、data quality
  checks、训练视图、独立评价和反馈迭代；已公开方法和建议扩展分别说明。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Data Pipeline 实例
  - AFM 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Skill Usage in Realistic Settings
    url: 'https://arxiv.org/html/2604.04323v1'
    type: primary
  - title: HarnessLLM
    url: 'https://arxiv.org/html/2511.01104v1'
    type: primary
  - title: HARDTESTGEN — ICLR 2026
    url: >-
      https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf
    type: primary
  - title: AgentTrek — paper
    url: 'https://arxiv.org/abs/2412.09605'
    type: primary
  - title: VisualSkill
    url: 'https://arxiv.org/html/2606.18448v1'
    type: primary
---

## 三条线怎么选
这是一组面试方案，不是已运行的数据生产系统，也不是你的新增项目经历。英文段落采用“I would”，真实做过的部分再按你的贡献改写。

先分清两种 harness：**agent harness**负责上下文、skill 加载、工具和状态机；**test harness**负责生成输入、调用代码并验证行为。第一条训练 agent 如何用 skill，第二条训练代码与测试，第三条训练 multimodal 工具操作。

| pipeline | 具体任务 | 主要数据产品 | 最有价值的面试问题 | 详细入口 |
| --- | --- | --- | --- | --- |
| Skill＋agent harness | 从含重复、缺失值的 CSV 生成分语言质量报告 | skill 库、检索/加载记录、经过执行验证的 trajectories 与恢复片段 | 检索、选择、适配哪个环节缺监督？ | `afm-pipeline-skill-harness` |
| Code＋test harness | 算法题的正确解、错误解和能区分它们的测试 | 可信解、困难输入、verifier、SFT/偏好/在线 RL 任务 | 测试通过为何不等于代码正确？ | `afm-pipeline-code-verifier` |
| Multimodal＋tool use | 从合成票据截图填表并导出文件 | 对齐截图/动作 trajectories、证据字段、终局状态与偏好分支 | “像成功”与“状态真的正确”如何分开？ | `afm-pipeline-mm-tool-use` |

第三条新增公开参照为[AgentTrek](https://arxiv.org/abs/2412.09605)：从教程收集、任务化到实际 replay 并评价 trajectories。其 VLM 评价不提供形式化正确性保证；下面的状态核验与训练 feedback loop 是我们的设计扩展。你自己的 Skill Usage、HarnessLLM/HardTestGen 与 VisualSkill 用作最直接的研究衔接。

## 共同的数据契约
一条样本至少保存：`source_id`、许可及用途、`task_id`、`task_family`、`split`、任务生成器/工具 schema/环境/verifier 版本、初始状态 hash、策略 checkpoint、sampling 配置、观察动作时间序列、独立核验结果和标签来源。生成 manifest 先确定家族切分，再做扩写；同一 seed、改写、布局或代码近克隆不能跨训练与验收。

原始 trajectories 是证据，不是直接可训练数据。保留 immutable raw，再产生版本化的 SFT、preference 和 RL manifest：

| 视图 | 保留什么 | 什么不能混进输入 |
| --- | --- | --- |
| SFT | 被核验且过程可接受的动作/回答，明确 loss mask | verifier 隐藏状态、未来工具结果、答案文件 |
| Preference/RM/DPO | 相同任务与初态的可比候选、评价维度及标签置信 | 将不同任务的成功/失败强配成一对 |
| RL | 可重置任务、明确权限、独立奖励与预算；采集 current policyrollout | 把离线旧 trajectories 当作当前 on-policysampling |

成功终局不自动意味着整段适合 SFT；先审计失败、回滚、越权和无效动作，再决定筛整段还是训练经过核验的恢复片段。反馈优先更新任务/失败模式覆盖；不因某来源样本多就无限提高它的 mix 权重。

## 小规模启动与规模化怎么讲
先用少量人工核验 seed 建立 oracle、edge cases 和独立 evaluation set，再多次 rollout 估计任务难度。记录每层流失：候选→可执行→合法输入→独立通过→过程合格→deduplication→训练。数量先报实际统计，不预写通过率。

扩展后按 task 或 environment snapshot 分片，worker 重试用稳定的任务/attempt ID 避免重复记账；对象存储保存大截图和 trajectories，manifest 保存 hash。deduplication 以任务家族和内容为单位，不能仅按文件名。数据版本、data mix、撤回依赖和训练 checkpoint 要可追溯；坏环境进入隔离队列，不冒充模型失败。

实验固定模型、训练 token/算力与 inference budget，先做低成本诊断，再做一项定向数据干预。独立任务成功、关键错误、long-tail 和成本一起报。development set 可以迭代，最终 blind set 只用于验收；公开 benchmark 反复调过后不能继续当未见真值。

## 面试中可用的总开场
> I would organize the pipeline around executable tasks and independently verified outcomes. For skills, I would separate retrieval, selection, and adaptation. For code, I would audit the verifier before using its output as a reward. For multimodal tool use, I would align screenshots with actions and validate the resulting application state. The raw traces would then be converted into separate SFT, preference, and online-RL views, with task-family splits and versioned provenance throughout.

[示例 JSONL 说明](/apple-prep/pipelines/README.md)。附件只是合成的数据契约示意；图片、环境与程序 hash 均为占位符，不是已采集可训练数据。
