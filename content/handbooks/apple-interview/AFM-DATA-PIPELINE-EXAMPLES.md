# AFM：三条 Data Pipeline

专业术语使用英文，中文解释选择与原因。口述内容对应原题，完整 callout 和全部340题见 AFM-ANSWER-GUIDES.md。

---

## 三条可讲到底的数据 Pipeline：Skill／Harness、Code 与 multimodal Tool Use


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


---

## Pipeline 1：从 Skill 检索与执行失败，造出可训练的适配 trajectories


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



---

## Pipeline 2：从正确解、错误解与困难测试，构造代码 post-training 数据


## 面试官可能这样问

怎么给 coding 模型做一条 synthetic datapipeline？你觉得最容易出问题的是哪一步？

## 可以这样回答

我最担心的是我们生成了很多代码，测试也都通过了，但里面其实有错解。如果这些代码拿去做 SFT，或者测试结果拿来做 RL 奖励，模型反而会越来越擅长通过不完整的测试。

所以我会先从一批题意和正确解比较可信的题开始。每道题生成几个候选解，然后针对常见错误补测试。比如树上的题，随机生成的树可能都比较平衡，一个低效算法看起来也能跑完；换成很长的链，它的问题才会暴露。这时我需要补的是这种输入，而不只是继续生成更多随机树。

不过，测试更严格也不一定更好。我还要拿确认正确的程序跑一遍，看看有没有错误 assertion、非法输入，或者机器太慢造成的误判。等这两边都检查过，再用测试筛 SFT 数据，或者给当前模型的代码打奖励。

最后我会固定训练题和训练预算，只换测试这一个因素，看模型在另一批题上是否更好。训练时的通过率涨了，只能说明它更会过这套测试；我还想知道代码能力有没有真的提高。

## 被追问时再展开

**错误程序从哪来？** 优先用模型实际写错的程序，因为它们更接近训练时会遇到的错误。也可以人为改出 edge-case bugs，但要先确认改出来的程序确实错了。

**两个程序都通过，preference labels 怎么给？** 我不会仅凭哪个解释更长来选。功能上还分不出好坏，就先保留这种不确定；如果要比较效率，需要额外的、可靠的性能测量。

## 英文口述参考

The part I would be most careful about is the verifier. If the tests let a wrong solution pass, that solution can become SFT data or receive a positive RL reward.

I would start with problems and reference solutions I trust, generate candidate programs, and add tests for the mistakes those programs make. A simple example is a tree problem where random balanced trees fail to expose an algorithm that becomes too slow on a long chain. I would also run known-correct programs through the tests, because a bad assertion or an unrealistic timeout can reject good code.

Once the tests look reliable, I would use them for data selection or rewards. To measure the benefit, I would keep the training problems and compute fixed, change the verifier, and evaluate on separate problems.

## 技术备查

## 公开参考与设计假设
[HarnessLLM](https://arxiv.org/html/2511.01104v1) 研究可执行 harness 生成；[HARDTESTGEN](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf) 强调代码测试对 post-training 反馈的影响。[EvalPlus](https://arxiv.org/abs/2305.01210) 可作为扩充测试的参照。以下具体任务与流水线是建议设计，不声称你已实现全部环节。这里 harness 指代码测试器。

## 1. 任务：树上所有节点到根的距离和
输入合法的根树，边权均为1，输出所有节点到根距离的总和。路径型树、星形树、平衡树、不同节点编号构成测试家族。根树契约、N 范围、I/O 协议和资源约束先写清。

链状树有 N 个节点时答案为 $N(N-1)/2$。一个逐节点回溯祖先的算法在平衡树上可能不显得慢，但在长链上是二次工作量。因此“随机测过了”未必验证复杂度。例子用于教学，不是声称论文指定了本接口。

## 2. Pipeline 与 data quality checks
`许可题目/可信实现 → 按题目家族切分 → 多策略生成候选解 → 产生定向错误程序 → 合成harness和困难输入 → 验证输入/答案/资源 → 双向审计verifier → 构造训练视图 → 独立代码评测`

| 阶段 | 输入与输出 | 关键检查 |
| --- | --- | --- |
| 题目规范化 | 题意、约束、I/O、可信实现、许可 → 版本化任务 | 相同题翻译/改写/代码近克隆同 split；不能将评价题扩写进训练 |
| 候选解 | 不同模型/温度/算法 → 正确、逻辑错、复杂度错程序 | 保留生成策略版本；独立核实正解，不能靠投票称其可信 |
| 错误解 | 真实失败与定向变异，如漏根、off-by-one、慢算法 | 变异应符合语法；未证实错误的标 unknown，不能默认负例 |
| 测试生成 | 题目契约＋错误模式 → 输入生成器与 assertion | 树必须连通无环且编号合法；禁止非法输入制造“抓错” |
| oracle | 小规模穷举/独立实现/可证明结构 → 正确结果 | 大链可用解析式；普通大输入参考实现仍要审计 |
| verifier 审计 | 正确/错误/unknown 程序与测试 → 双向混淆表 | 分清 false acceptance 错误、false rejection 正确、测试自身错误、非确定超时 |
| 下游训练 | 合格解/trajectories/偏好/任务环境 → 版本化 manifest | 训练与隐藏验收测试分开，策略无权修改 validator |

超时由固定硬件、编译器与资源预算判定；不稳定接近阈值的案例先复跑或隔离。若环境失效，则标环境错误而非程序错误；不能靠更短 timeout 假装 verifier 更强。

## 3. 数据样本与 hard examples
```json
{
  "task_id": "root-distance-001",
  "task_family": "tree-distance",
  "split": "train",
  "candidate_id": "ancestor-walk",
  "program_hash": "example:slow-v1",
  "generator_checkpoint": "example-coder-v0",
  "test_family": "long-chain",
  "input_valid": true,
  "oracle": "closed_form_unit_chain",
  "observed": { "small_correct": true, "large_case": "timeout" },
  "label": "complexity_failure_under_fixed_budget",
  "label_source": "sandbox-plus-audited-oracle"
}
```

[示意 JSONL](/apple-prep/pipelines/code_verifier.jsonl)展示正确解、复杂度错与 unknown 三类。这里没有附实际程序和运行产物，不能当作可直接训练的标签。

## 4. 训练的三种视图
**SFT**：先从许可 seed 题 sampling 多解，用经过审计的测试筛选；对通过且过程可接受的解做 rejection sampling fine-tuning。训练数据保留来源/题目/算法家族和负例审计统计，避免只选简单树导致单一课程。若训练的是 test generator，示范应是有效生成器与可信核验逻辑，而非只给标准答案。

**Preference / RM / DPO**：同题同约束下，选择有效且通过独立测试的解优于被证实逻辑或复杂度失败的解。两个都通过时不凭长度强造标签；可以按可靠测量的资源与可维护性分维度，但不得混淆功能正确和风格。可另建 verifier 偏好：合法、低 false rejection、能抓困难错解的 harness 优于非法输入或错误 assertion。

**Online RL**：sampling 当前 coder 并执行奖励；测试生成器的目标还需约束对正确程序的 acceptance rate 与输入合法性，不能只奖励 kill 错误程序数量。coder、test generator、checker 三者权限和版本独立；若共同迭代，保留不参与它们适配的审计池，防止共同钻漏洞。

## 5. 怎样证明不是“测试更难，所以看起来更好”
先固定候选代码，比较 verifier 的 false accept/false reject 和每秒有效判定；再固定题目、初始模型、训练 token 与算力，只替换 verifier，评独立新题代码成功率。不要只在新测试上报告通过率，或用训练奖励选完 checkpoint 再把该奖励当验收。

代码生成和测试生成器要对不同模型产生的错误迁移；样本按错误算法/模板和题目家族隔离。对真正新题的结论需说明语言、时间窗、checker 版本与限制。

## 6. 下一轮数据怎么补
若随机树全过而长链失败，补复杂度敏感结构及相同算法在其他题型的负例；若正确程序被 false rejection，先修 oracle/资源契约；若新 coder 钻过固定测试，更新开发侧测试并保留新隐藏家族。rule-based reward 也会有分布偏差，执行可重复不代表覆盖完整。

## 90秒英文参考
> I would build the code pipeline around a problem, trusted solutions, realistic wrong solutions, and tests that distinguish them. For example, random trees may fail to expose a quadratic algorithm that breaks on a long chain. Before using tests to select SFT data or reward RL, I would check input validity, oracle correctness, false acceptance, and false rejection. I would then hold the training problems and compute fixed, change only the verifier, and evaluate on independent problems. The important data product is reliable feedback, not simply a larger number of tests.

## 追问
**两个解都过了就一样好吗？** 功能证据相同，不足以凭文风定真偏好；更强测试或资源/维护目标需独立定义。
**奖励稀疏怎么办？** 用课程、可靠 SFT 和更可学任务调整，不将未知正确性当正奖励。
**你的真实经历怎么说？** 可以从参与的公开 verifier 研究谈出发点，再把本方案称作后续设计。



---

## Pipeline 3：从票据截图到表格操作，合成 multimodal Tool-Use 数据


## 面试官可能这样问

举一个 multimodaltool-use 的数据 pipeline。你会怎么收集、怎么判断数据好不好？

## 可以这样回答

我会选一个比较容易检查结果的任务，比如给 agent 一张票据截图，让它把日期、币种和总额填进表格，再导出文件。这样既要读图，也要实际操作软件，最后还有一个可以检查的结果。

最开始我会用合成票据。先确定日期和金额，再把它们渲染成不同样式的图片，所以我知道正确答案是什么。让 agent 在固定的软件环境里操作，记录它每一步看到的截图和接下来的动作。结束以后，我直接检查导出的表格，不能因为 agent 说“已经完成”就算成功。

如果金额填错了，我会先看它是把图读错了，还是知道金额却填错了格子。比如小计是115，总额是128.50，它填了115，这更像是字段理解的问题；如果它正确说出了128.50，却输入到日期那一格，问题就更接近界面操作。这两种错误，我会补不同的数据。

训练时先用实际完成、过程也合理的 trajectories。评价时换一批票据布局，而不只是换金额。如果换个排版就不会了，说明它可能记住了位置，没有真正学会找总额。这条 pipeline 是我会设计的扩展；和我参与的 VisualSkill 工作可以连接起来讲，但不能把这套票据实验说成已经做过。

## 被追问时再展开

**为什么不用 OCR 加脚本？** 我会把它作为 baseline。如果固定票据模板用 OCR 就能很好解决，那没有必要强行做复杂 agent。这个例子更适合需要理解变化的页面、再跨软件完成操作的场景。

**数据怎么扩大？** 我会根据真实失败补变化，比如小计和总额很接近、日期格式不同、表格需要滚动。先确认是哪一种变化带来错误，再生成对应的新样本，而不是只把同一个模板复制很多遍。

## 英文口述参考

I would use a task with an outcome I can check, such as reading a receipt image, entering the date and total into a spreadsheet, and exporting the file.

I would begin with synthetic receipts, so I know the correct fields before rendering the image. During collection, I would record the screenshot the agent saw before each action. Afterwards, I would inspect the exported spreadsheet. The agent saying it succeeded would not be enough.

If it failed, I would separate reading errors from action errors. Entering the subtotal instead of the total suggests a different data problem from reading the amount correctly but typing it into the wrong cell. I would collect examples for the failure I actually observed, and test on new receipt layouts to see whether the model learned more than a fixed screen position.

## 技术备查

## 新找到的公开材料
[AgentTrek](https://arxiv.org/abs/2412.09605) 提供教程收集、任务化、replay 及 trajectories 评价的公开路径；[官方项目页](https://agenttrek.github.io/)可继续找代码与数据。它使用 VLM 评价，不等于 trajectories 被形式化证明正确。

下面的票据→表格流程是建议扩展，不是 AgentTrek、OSWorld 的指定任务，也不是你的既有实验。[VisualSkill](https://arxiv.org/html/2606.18448v1) 用于衔接你参与的图文技能研究，[OSWorld](https://arxiv.org/abs/2404.07972) 用于理解真实软件的状态验收。

## 1. 具体任务与 tool interface 与 permissions
给 agent 一张合成票据截图，要求在本地表格模板填写商户、日期、币种、含税总额，并导出报销 CSV。例子字段为商户 Atlas、日期2026-10-02、币种 USD、总额128.50。不能把小计115.00当总额，也不能按 locale 把1,280.50误读成1.28050。

动作接口为读取截图、点击、输入、滚动、快捷键及等待；工具返回只包含运行时可见信息。verifier 侧可以检查合成真值和最终文件，agent 不能读取隐藏 CSV 答案/底层数据库。若另开文件读取或 OCR 工具，单独作为 action space 条件做对照，不能混报为纯视觉能力。

## 2. Pipeline 与产物
`许可教程/人工演示 → 结构化任务spec → 合成票据与真值 → 按布局/任务家族切分 → 在冻结软件环境回放 → 对齐截图和动作 → 字段/状态/权限核验 → 过程清洗 → SFT/偏好/RL视图 → 未见布局验收 → 定向生成难例`

| 阶段 | 中间产物 | data quality checks |
| --- | --- | --- |
| 任务 seed | 许可教程或人工标注的操作目标、前置条件、工具范围 | UI 版本、数据用途与可执行性明确；教程不是最终真值 |
| 票据生成 | structured seed、render 参数、截图、字段真值 | 真值对照渲染结果，检查截断/模糊/遮挡；无法辨认时需澄清，不硬标可解 |
| 家族切分 | vendor/layout family、locale、字段组合、软件模板 | 同底图/布局 near-duplicates 及派生 trajectories 同 split；新 seed 不自动代表新布局 |
| 多 trajectories 采集 | policy checkpoint、初态、动作前截图、tool 输入输出、结束状态 | reset 一致；前一轮输入的文件不能遗留到下一 attempt |
| 对齐 | obs_id、frame 时间、viewport/DPI、action 时间、state 版本 | 必须动作前可见的帧；过期截图、错位坐标或不稳定工具记录隔离 |
| 独立验收 | 导出 CSV 解析、字段对比、目标路径、无额外写入 | 不由 agent 自报成功；可接受多条合法操作路径，不硬贴唯一 click 序列 |
| 训练清洗 | 成功、失败、恢复、越权、不可判定 | 终局成功但改错其他单元格/读取隐藏状态的 trajectories 不能自动入选 |

## 3. 一步样本与权限分离
```json
{
  "task_id": "receipt-021",
  "task_family": "receipt-to-sheet",
  "split": "train",
  "obs_id": "frame-004",
  "screenshot_ref": "example://receipt-021/before-004.png",
  "viewport": { "width": 1280, "height": 800, "scale": 1 },
  "pre_state_version": 3,
  "action": { "tool": "gui.type_text", "arguments": { "text": "128.50" } },
  "post_state_version": 4,
  "supervision": { "assistant_action": true, "observation_loss": false },
  "artifact_status": "schema_example_not_collected_trace"
}
```

核验侧另存 `expected_fields`、渲染 seed、隐藏输出检查及关键错误，不与模型 prefix 拼接。`gui.type_text`是本例自定义工具名，不宣称某公开框架提供此接口。[示意 JSONL](/apple-prep/pipelines/mm_tool_use.jsonl)给出完成、错读金额、截图错位三种记录。

## 4. 如何验证“真的看图并正确用工具”
先核对图像是否有可辨识真值，再分别做：正确截图、只改总额的成对截图、去掉必要视觉证据、给 oracle 字段、给 oracle 点击目标。它们用于区分读图/语义、grounding 和执行规划；不能只看一次遮图掉分就下 causal 结论。

主要验收是导出文件的字段正确、任务完成、无额外修改；截图 VLM 评分只能作为补充。只有已知币种/locale 才能正确 normalization 金额和日期，缺少证据时澄清是合格行为。按金额、小数、日期、币种、滚动和错误恢复 evaluation slices，警惕视觉 judge 偏爱格式漂亮但数字错误的产物。

## 5. 三类训练样本
**SFT**：保留合法成功与经过审计的恢复操作；输入包括当时截图、指令、允许的历史工具结果，loss 只监督 assistant 动作/回答。不把环境截图、工具回包或私有真值当作要模型生成的目标。随机一条 trajectories 的坐标不能直接贴到不同 viewport 上。

**Preference / RM / DPO**：从同一票据、模板与初态分别 rollout，正确导出胜过错金额但流畅总结；两条都正确时再比较重复操作和成本。若比较同一 prefix 后的分支，必须重置到相同状态再执行。跨任务随意配 success/fail 会 leakage 难度和长度，不能当作纯质量偏好。

**RL**：将渲染器、软件快照与独立 checker 打包成可重置环境，current policy 在线操作。终局成功是主要奖励，越权和破坏文件是约束；中间“填满一格”只能是经验证的辅助项，避免鼓励填错也得分。若过程缺少足够可验证状态，先用 SFT 冷启动与可学任务，不拼凑伪奖励。

## 6. data flywheel 与规模
如果读图 oracle 恢复，补字段易混淆布局；如果 oracle 字段仍失败而 oracle 点击恢复，补 UI grounding；如果点击也正确却导出错位置，补多步状态检查与文件流程。每轮按确认的失败家族造新任务，保留正常短流程与澄清任务；不只放大错误最多的重复模板。

截图以对象 hash 保存，manifest 只放引用，按可见 viewport 和应用版本 deduplication/分桶；大规模采集 worker 独立环境、超时恢复和幂等 attempt 记录。报告每千条独立合格 trajectories 的成本及 hard examples 收益，而不是只报生成量。图像含私人内容的部署不能默认把反馈加入 training data，研究环境使用许可或合成材料。

最终在未见布局、应用模板和不同分辨率上，与同模型同预算的 no-training/随机合成/定向合成对照。记录端到端任务、字段正确、非法副作用、时间与视觉 token 成本；训练环境涨分而新布局不涨时，先排查模板记忆和 checker 漏洞。

## 90秒英文参考
> For multimodal tool use, I would build a receipt-to-spreadsheet pipeline. A structured seed would generate the receipt image and private ground truth. The agent would see screenshots and interact with a fixed GUI tool interface, while a separate verifier would inspect the exported file. Every action would be aligned with the screenshot visible before it. I would use matched image edits and oracle substitutions to distinguish visual extraction from grounding and planning failures. Verified trajectories could support SFT, resettable branches could form preference pairs, and the same task generator could support online RL with held-out layout families.

## 追问
**为什么不直接用 OCR 加脚本？** 这是有价值的强 baseline；若结构化输入已够，不必强行 VLM。只有需要视觉判别和 GUI 操作的任务才测本 pipeline 额外价值。
**教程 replay 与模型自主执行有何不同？** 教程可用于采 seed，训练/验收不能永久提供测试题逐步答案；保留无指导的新任务评价。
**可以说是你的 multimodal 项目吗？** 这条是方案，VisualSkill 里实际做过的内容按真实职责连接。



## References

- [Skill Usage in Realistic Settings](https://arxiv.org/html/2604.04323v1)
- [HarnessLLM](https://arxiv.org/html/2511.01104v1)
- [HARDTESTGEN — ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf)
- [AgentTrek — paper](https://arxiv.org/abs/2412.09605)
- [VisualSkill](https://arxiv.org/html/2606.18448v1)
- [EvalPlus](https://arxiv.org/abs/2305.01210)
- [AgentTrek — official project](https://agenttrek.github.io/)
- [OSWorld](https://arxiv.org/abs/2404.07972)
