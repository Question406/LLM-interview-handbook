# Jiabao Ji × AFM：个人面试 Reference

专业术语使用英文，中文解释选择与原因。口述内容对应原题，完整 callout 和全部340题见 AFM-ANSWER-GUIDES.md。

---

## Jiabao Ji × AFM：个人研究、Benchmark 与面试 Reference


## 这份 reference 怎么用
基于2026-10-27核对的[主页](https://question406.github.io/)、公开 CV 和论文。这里的“我参与的工作”仅表示公开作者身份；“我具体负责什么”仍须你确认，不能从作者顺序推断。英文段落是面试参考表达。建议实验均是待做方案，不是已获得的结果。

你的匹配点是把一个能力缺口变成可验证的任务、数据与反馈。无需将自己包装成已经负责过整套大规模 AFM pre-training 平台的人。

## 最值得准备的六条线
| 优先级 | 相关公开研究 | 熟悉/可对照的 benchmark 或 setting | AFM 话题 | 深读入口 |
| --- | --- | --- | --- | --- |
| 1 | DeepAmbigQA | 自己的多跳歧义 QA；AmbigQA / ASQA / MuSiQue 作对照 | synthetic data、完整性、评测驱动诊断 | `afm-ref-qa-completeness` |
| 2 | HarnessLLM / HARDTESTGEN | 错误程序识别；LiveCodeBench、EvalPlus；固定题换 verifier | RL 奖励质量、verifier 盲点、困难负例 | `afm-ref-verifier-reward` |
| 3 | Skill Usage | SkillsBench 的递进检索设定；论文中的 Terminal-Bench 2.0实验 | 失败诊断、skill refinement、self-iteration | `afm-ref-skill-flywheel` |
| 4 | Speculate While You Reason | 部分 trajectories 预测下次调用；搜索 QA 和 tau-bench；tau2作扩展 | on-policy 训练信号、proxy reward、成本 | `afm-ref-joint-tool-rl` |
| 5 | VisualSkill | CUA-World / OSExpert-Eval；OSWorld 作跨模型补充 | multimodal 数据、对照实验、judge bias | `afm-ref-visual-setting` |
| 6 | ULD unlearning | TOFU 的 forget/retain；移除后的效用与再提取 | 治理、遗忘与保留权衡 | `afm-ref-unlearning-governance` |

列出的外部 benchmark 不等于你亲自运行过；每张卡会标明论文实际使用与建议扩展。先练前三条，再按面试官问题调用其余材料。

## 60秒总开场参考
> My research connects agent capability gaps with better supervision and evaluation. I have coauthored work on ambiguous multi-hop QA, executable verification, and agent skills. For this role, I would focus on how we define a failure precisely, construct verifiable examples, and check that improvements transfer beyond the data generator or evaluator. I am especially interested in turning failures into training signals while keeping evaluation independent. My direct experience is strongest in research settings; applying these ideas to a large-scale production data pipeline would be a next step.

这里没有声称你主导了每篇合作论文，也没有声称已有生产飞轮经历。追问具体责任时补一句 “My specific contribution was [真实职责]”，说出可展示的实验或代码。

## 原始面试要求怎样接
- **synthetic data 具体案例**：从 DeepAmbigQA 开场，讲任务可验证性与完整性，再讨论训练扩展；不能把 benchmark 合成直接当作已完成 SFT 收益。
- **benchmark debugging**：使用 QA 的漏分支，或 verifier 放过错误程序，给区分假设的 controlled substitution。
- **data flywheel / self-improvement**：用技能选择与 refinement 说明运行时迭代，再解释何时值得转成权重训练。
- **reward / preference**：以 verifiable reward 为实际研究案例，补 learned RM 需要人群、标签、calibration 与 OOD 验证的差别。
- **multimodal**：用 VisualSkill 的图文技能对照，讨论视觉证据、预算和评审方式。
- **privacy**：用 unlearning 研究谈评测限制，同时明确它不授予训练私有数据的许可。
- **See Around Corners**：可讨论“现有指标可能漏掉答案完整性/真实检索难度”的研究动机；没有事前时间线证据，就不要说自己提前预防了产品事故。

## 没有具体经验时的三种自然回答
**没做过 learned RM：** “I have worked on verifiable feedback rather than owning a production preference-modeling pipeline. A useful connection is verifier bias: a policy can optimize what the evaluator rewards without becoming more correct. For a learned RM, I would additionally examine annotator variation, calibration, and current-policy coverage.”

**没负责过超大规模 pre-training：** “My direct experience is closer to post-training and evaluation. For pre-training or mid-training, I would test whether the gap reflects missing coverage rather than behavior, and validate the data intervention with controlled continued-training experiments.”

**没做过线上私有反馈飞轮：** “I would use permitted aggregate failure categories to decide what to reproduce with licensed or synthetic data. I would not assume private user traces can be turned into global training examples.”

## 阅读顺序与最小产出
第一遍：读六张卡的 setting 和英文段落。第二遍：只深读前三条的论文方法、实验与限制，亲自挑一个失败样本。第三遍：每条用一张纸写任务、数据、监督、独立评测、负结果和你个人贡献。读懂资料后才使用“我了解该 setting”，真正运行后才说“我复现过”。

会前至少补齐：DeepAmbigQA 具体贡献__；一个真实错误__；合成 QA 质量检查__；HarnessLLM/HardTests 本人负责部分__；最熟悉的 RL 实现细节__；VisualSkill 本人贡献__；一个事前判断的时间证据__。这些信息公开资料无法可靠替你填写。

[公开研究入口](https://question406.github.io/)；本仓库的来源审计在 `content/sources/afm-personal-reference-2026-10-27/README.md`。论文版本与主页/CV 的发表状态有差异时，讲内容、按确定的版本引用，不混报成果状态。

## 进一步展开成数据 Pipeline

`afm-pipeline-overview` 串起 Skill/Harness、代码验证和 multimodal 工具操作三条具体设计：每条包含来源、数据契约、data quality checks、训练视图与 feedback loop。本册完整参考稿为 AFM-DATA-PIPELINE-EXAMPLES.md；正文不把建议方案称为个人实绩。


---

## 个人 Reference 1：DeepAmbigQA，如何把“漏答”变成 synthetic data 问题？


## 面试官可能这样问

你的研究里，有什么例子能说明你会怎么做 synthetic data 和评测？

## 可以这样回答

我会讲 DeepAmbigQA。这项工作里有一个很直观的问题：有些问题里的名字对应不止一个实体，模型可能只选了其中一个，然后给出一个完全正确、但不完整的答案。只检查它说出来的内容，很容易漏掉这种失败。

我们在这篇工作里研究了这类歧义和多跳问题。对这个岗位来说，我觉得有价值的是把“答案不够全”变成可以检查的数据问题：有哪些解释、每个解释需要找什么证据、最后应该包含哪些答案。这样比只让一个 judge 给整体印象分，更容易看清缺口。

如果继续往训练上做，我会先检查模型是没发现另一种解释，还是发现了却没找到证据。前者补消歧和分支探索的例子，后者补检索或证据整合。这个训练扩展是我的方案；论文里的 benchmark 工作，以及我本人负责的部分，需要分别讲清楚。

## 被追问时再展开

**面试官问你具体做了什么？** 回到你实际负责的数据生成、质量检查或实验模块，选一个真实决定讲清原因。公开作者名单无法替你补这一段。

## 技术备查

## 已核对的相关研究
[DeepAmbigQA](https://arxiv.org/html/2511.01323v1) 将 corpus 与知识图谱相连，构造可执行的复杂问答；公开数据为3600题。它直接支持你讨论答案完整性。你的 CV 把 Apple 实习主题写为 ambiguity-aware QA synthesis，但不能据此推断你负责了所有环节。

## 相关 benchmark 怎么区分
| 材料 | 要理解的 setting | 面试中的用途 |
| --- | --- | --- |
| [AmbigQA](https://aclanthology.org/2020.emnlp-main.466/) | 找出多种合理解释及对应答案，重写问题以消歧 | 说明歧义不是单一实体预测 |
| [ASQA](https://arxiv.org/abs/2204.06092) | 长答案应覆盖歧义问题的不同解释 | 区分文风流畅与事实覆盖 |
| [MuSiQue](https://arxiv.org/abs/2108.00573) | 组合具有依赖关系的单跳问题，减少多跳捷径 | 讨论真正用到中间证据 |

这是外部对照阅读，不表示你亲自复现过全部基准。

## 可以和面试官讨论的具体 setting（建议扩展）
构造一个许可知识库：同名的两个“Atlas”组织，每个关联不同奖项和年份。问“哪些 Atlas 相关作品在给定年限获奖？”在冻结快照内，保存解释分支、执行计划、实体 ID、全部答案和证据。例子是教学设计。

先做歧义有/无×单跳/多跳的2×2评测，再按答案集合大小 evaluation slices。报告实体级 precision/recall、集合 exact match、解释分支覆盖和证据支持；这些是建议指标，不能全部称为论文原指标。准确但漏答与胡乱多列答案要分开惩罚。

诊断依次给 oracle 解释、oracle 检索证据、oracle 中间结果，看哪个替换能恢复答案。干预分别补消歧、遗漏分支、跨证据集合操作和有依据的停止。按实体家族、模板/图结构及来源隔离开发和验收，别把题面改写当独立测试。KB 执行正确只保证快照内一致，还需抽查自然语言和外部事实。

## 英文60秒参考
> In DeepAmbigQA, we studied answer completeness in ambiguous multi-hop questions. The useful connection to data work is that a fluent answer can still omit valid interpretations. For a follow-up training setting, I would keep a structured answer set and supporting evidence, then separate ambiguity failures from retrieval and aggregation failures. I would first use oracle substitutions to identify the bottleneck, and only then generate targeted training examples. That extension is a proposal, rather than a training result I would claim from the benchmark paper.

## 高频追问与回答方向
**为什么不是把 search top-k 加大？** 更多证据不保证覆盖正确分支，也可能增加噪声；做预算受控的检索与聚合对照。
**合成答案真的全吗？** 只在定义的快照和查询域内保证，不能把知识库缺失误作现实中不存在。
**如何接 RM/bias？** 构造同样正确但覆盖不同的候选，分开标完整性、事实和冗长；一般 judge 可能奖励长而不全。独立实体集合检查不能由同一生成器自证。
**能讲 See Around Corners 吗？** 研究发现指标盲点可作线索；事前发现、推动行动与结果必须补真实时间线。

继续练 `dt-synth-reasoning`、`dt-benchmark-gap` 和 `afm-rm-length-causal-audit`。



---

## 个人 Reference 2：HarnessLLM／HardTestGen，奖励错了比模型弱更危险？


## 面试官可能这样问

你没有独立负责过 learned RM，怎么理解 reward modeling 里的数据问题？

## 可以这样回答

我比较直接的连接是代码验证。在我参与的测试生成研究里，我们关心的是：一个程序看起来能通过测试，它到底是不是真的正确？因为测试一旦漏掉某类错误，这些错误程序就可能被选进 training set，或者在 RL 里拿到正奖励。

我觉得这和 learned RM 有一个共同点：模型得到的是评审器的判断，而这个判断可能和我们真正想要的质量有差距。代码里可能是漏了长链这种 edge-case inputs，preference model 里可能是把回答长、语气自信当成质量好。

所以我会先看评审器在哪些样本上容易错，再决定补什么标签。然后用另一套独立检查验证模型有没有变好。我没有负责过生产级 preference model 的话，会直接说明这一点；我能深入讲的是验证反馈怎么影响数据选择和优化。

## 被追问时再展开

**那两种奖励能直接互换吗？** 不能。代码测试对应一个明确的功能要求；preference labels 还涉及谁来评、按什么标准评，以及分歧怎么处理。共同的问题是反馈可靠性，具体标签和验证办法仍然不同。

## 技术备查

## 已核对的相关研究
[HarnessLLM](https://arxiv.org/html/2511.01104v1) 生成可执行测试 harness，使用 SFT 和 RLVR；[HARDTESTGEN](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf) 构造更可靠的算法代码测试。两篇公开作者名单包含你，个人模块仍待确认。后者使用的 LiveCodeBench-105为特定版本的 C++标准输入输出子集，不能当作整个 LiveCodeBench。

## 最相关的对照资料
[EvalPlus](https://arxiv.org/abs/2305.01210) 展示扩充测试可以揭露原测试未发现的错误；[LiveCodeBench](https://arxiv.org/abs/2403.07974) 的时间化题目采集帮助讨论 contamination。时间较新不等于绝对无 contamination，运行时必须固定版本、时间窗和语言。

## 一个可深入的 setting（建议实验）
固定题库、候选代码、生成模型和预算；每题同时保存可信实现、多个错误算法和有效输入约束。对比随机测试、LLM 输入输出测试和 harness，区分无效输入、错误 oracle、false rejection 正确程序与 false acceptance 错误程序。

假设任务求树上路径长度：随机平衡树可能放过在链状树上超时的低效算法。困难测试要覆盖约束内的对抗结构，而非单纯变大。CPU 超时、编译器、运行 seed 和 sandbox 版本必须固定；资源问题不能混成逻辑错误。

用独立人工测试/可信实现建立审计标签，报告“判通过中真正正确的比例”和“错误程序被抓住的比例”，写清正负类定义。训练实验保持相同题、token 和算力，只替换 verifier，再比较独立代码生成质量；不要用训练奖励涨证明成功。评审器不完美时可设置弃权/专家复核，但阈值只用 development set 选。

## 英文60秒参考
> My connection to reward modeling is strongest through executable verification. In work I coauthored on test generation, the central issue is whether the feedback distinguishes correct programs from convincing wrong ones. This matters twice: it selects synthetic training data and it defines the optimization signal. To isolate verifier quality, I would hold the problems and candidate programs fixed, audit both false acceptance and false rejection, and then evaluate downstream learning independently. A learned preference model adds further concerns about annotators, calibration, and distribution shift.

## 高频追问与回答方向
**rule-based reward 不是客观的吗？** 执行可重复不意味着测试完整；测试契约、oracle 和资源限制同样可能有偏。
**和 learned RM 有何差别？** 执行标签针对定义的功能契约，learned RM 还拟合人类偏好；两者共同风险是优化者利用代理漏洞。
**模型改了自己的测试后通过了？** 测试与训练程序权限隔离，独立隐藏评价不可由策略修改；变更测试必须重新审计。
**如果所有 trajectories 都0或1？** 先判断任务难度与 verifier 覆盖，组内无相对信号时调整课程或冷启动，而非无条件放宽正确性。

继续练 `afm-rm-bestofn-overoptimization`、`afm-rm-prm-credit`、`dt-verifier-counterfactual`。



---

## 个人 Reference 3：Skill Usage，如何从评测失败构造 self-improvement feedback loop？


## 面试官可能这样问

你会怎么用模型失败推动下一轮数据改进？

## 可以这样回答

我会用 skill 的例子。给 agent 一条写得很好的 skill，它做得更好了，这还不能说明真实使用时也会更好，因为真实情况下它首先得找到这条 skill，还得判断什么时候用。

我们在相关研究里看了更接近这种使用方式的设置。对数据迭代来说，我会把任务失败和 skill 使用过程放在一起看。相关 skill 没找到，就先查检索；找到了却没用，要看选择；用了还是失败，再看它缺什么步骤，或者是不是没有适配当前任务。

下一轮我会围绕那个具体问题补数据，再换一批任务验证。这里也要分清两件事：把 skill 文件改得更好，是运行时改进；让模型本身学会选择和适配，需要另外的训练实验。我不会把前者的收益直接算成后者的证据。

## 被追问时再展开

**什么时候值得训进模型？** 当同一种行为在很多任务里反复有用，而且外部 skill 已经很清楚、模型仍然不会用时，我会考虑训练。经常变化的知识则可能更适合继续放在 skill 里。

## 技术备查

## 已核对的相关研究
[Skill Usage 研究](https://arxiv.org/html/2604.04323v1) 在 SkillsBench 上逐步引入干扰、检索和移除定制技能，并测试 refinement；论文还在 Terminal-Bench 2.0检验迁移。这里的运行时 skill 更新不是自动等于模型权重 self-training。

## 对照材料与版本
[SkillsBench 官方仓库](https://github.com/benchflow-ai/skillsbench) 用于理解任务与技能评测接口。Terminal-Bench 相关讨论以你论文的2.0设定为准，不混报旧版、不同 harness 或新排行榜。先读论文§3.3、§4，再追对应数据版本。

## 可讲的飞轮 setting（建议扩展）
任务输入→检索 skill→选择加载→执行→独立状态检查→归类失败→修订 skill→新任务验证。日志至少记 task_family、skill_id/version、retrieved_rank、loaded、tool-use trajectories、终局状态和运行预算。没有加载、检索不到和加载后不会用是不同的数据干预对象。

设计四个受控分支：no-skill、oracle 相关 skill、真实检索、真实检索＋refinement。固定模型与总预算，分别记录召回、加载、任务成功、耗时和 token。强制加载只是诊断上界，不是部署方案。若 oracle skill 也无收益，应先看内容和执行能力，不能继续只优化 retriever。

训练扩展需将改进保留到独立任务家族，保存失败与有效恢复片段，过滤任务答案 leakage。只有反复有用、压缩后可迁移的行为才考虑 SFT 或 RL；项目特有且会变化的知识可以留在外部 skill。预先设成本、跨任务收益和回归的停止条件。这是建议，不声称你论文已完成整个训练飞轮。

## 英文60秒参考
> A useful example is our work on skill usage under more realistic retrieval conditions. I would separate finding a relevant skill, deciding to load it, and adapting its content to the task. That makes the intervention testable: improving retrieval will not fix an execution bottleneck. The next step I would propose is to collect verified recovery trajectories and test whether the benefit transfers to new task families. I would distinguish runtime skill refinement from updating the model weights, because they change different parts of the system.

## 高频追问与回答方向
**skill load 率上涨就是模型更强？** 不一定，可能浪费 context；以独立任务成功和预算为目标。
**query-specific refinement 是否 leakage？** 利用当前指令本身不必然 leakage，使用隐藏答案、测试结果反复定制才有问题；训练型结论还要新任务验证。
**如何接 See Around Corners？** 可以讲为何理想化提供 skill 不能代表真实检索；若称提前发现产品风险，要补当时证据。
**与数据选择有什么关系？** 选择缺口决定采什么 trajectories，失败分层也决定是否值得再生更多同类 skill。

继续练 `dt-data-flywheel`、`dt-self-improve`、`dt-curriculum-moving-target`。



---

## 个人 Reference 4：Joint Agent–Speculator RL，预测正确是否就是好奖励？


## 面试官可能这样问

模型怎么用自己的 rollout 产生有用的训练信号？

## 可以这样回答

一个具体例子是我们做的下一次 tool calls 预测。agent 运行以后，会留下“在这段历史之后，它实际调用了什么工具”的记录。这些记录可以拿来训练预测器，而且比一个完全不同的模型生成的 trajectories，更接近当前 agent 的行为。

但我会特别注意，预测正确和任务正确不是一回事。假如 agent 本来就要调用一个错误工具，预测器猜中了，也不代表用户的任务完成得更好。所以我会同时看调用预测和最后的任务结果。

另一个问题是策略会变。训练了几轮以后，它的调用方式可能已经不同了，旧 trajectories 就没那么合适。我会保留 trajectories 对应的模型版本，并检查新策略上的表现。至于是否真的节省时间，还得算上预测开销和白做的调用，不能只拿命中率来推断。

## 被追问时再展开

**可以提前执行所有预测的工具吗？** 不能一概而论。只读查询和会创建订单、改文件的调用风险不同；写操作需要单独的执行条件和权限判断。

## 技术备查

## 已核对的相关研究
[Speculate While You Reason](https://arxiv.org/html/2607.25816v1) 从 agent 自身 rollout 提取下一 tool calls 目标，并进行双模式联合训练。公开实验覆盖 HotpotQA、MuSiQue、BrowseComp-Plus 及 tau-bench Airline/Retail。面试先核对你实际负责的训练、系统或评测部分。

[原始 tau-bench](https://arxiv.org/abs/2406.12045) 比较对话后的数据库目标状态，并讨论重复运行可靠性；[tau2-bench](https://arxiv.org/abs/2506.07982) 加入用户也能改变共享环境的双控制场景，适合做后续扩展，不能自动说是你已跑过的新域。$\mathrm{pass}^{k}$ 强调多次都可靠，和代码领域“至少一次成功”的 pass@k 含义不同。

## 最好聊的 setting（建议扩展）
每条样本是部分 trajectoriesh、后续实际调用 a、工具 schema 及环境快照。数据必须来自相应策略版本；只有 prefix 可供预测，未来 tool 结果不能进输入。policy update 后目标分布改变，记录生成 checkpoint，避免新策略训练只拟合过期目标。

分别评 exact-call match、任务成功、净 wall-clock、浪费调用和副作用。命中一个错误 agent 调用仍可能得到预测奖励；因此命中率不能替代任务质量。净收益约等于可隐藏的等待时间减去预测、误执行与取消成本，只有受控端到端测量才能给结论。

额外实验先限于只读且结果可缓存的工具；写操作预测可保留为候选，不默认预执行。比较固定外部预测器、同模型零样本、SFT、联合 RL；固定总预算并做新工具/参数域迁移，排查模型仅学 schema 字符串。不要将 tool calls 投机与 token-level speculative decoding 的分布保持证明混为一谈。

## 英文60秒参考
> In joint agent–speculator work, we use an agent's own trajectories to create supervision for predicting its next tool call. This is a concrete example of policy-dependent training data. For the broader data strategy, I would track policy versions and evaluate both prediction quality and downstream task success. Matching the agent is only a proxy: the agent itself may be wrong. I would also measure net latency and wasted calls, and treat speculative execution of state-changing tools as a separate safety constraint.

## 高频追问与回答方向
**反馈来自自己，为什么能变好？** 自身 rollout 提供分布匹配的监督目标，是否改进需要外部任务信号和独立评价；自我重复不是新增真值。
**只优化 Hit@1会怎样？** 可能偏向容易预测而无用的调用，需要任务约束及无进展调用审计。
**为什么不全部离线 DPO？** 取决于新策略候选覆盖、可验证反馈和探索需要，不是 DPO 天然不能做工具任务。

继续练 `dt-stale-rollout-incident`、`afm-rm-dpo-reference-shift`、`apple-spec-edge`。



---

## 个人 Reference 5：VisualSkill，怎么讲真实 multimodal 数据与评审偏差？


## 面试官可能这样问

你有什么 multimodal 相关的例子可以展开？

## 可以这样回答

我会用参与的 VisualSkill 工作来讲。界面操作里，有些东西用文字解释很费劲，一张图可能更直接，比如按钮在对话框的哪个位置。但图片也会占上下文，过期的截图甚至可能误导模型，所以我关心的是它在哪些任务上有实际帮助。

如果做对照，我会尽量让文字版和图文版来自同一份材料，用相同的 agent 和工具跑。否则图文版多知道了几个操作步骤，最后分数更高，也很难说是视觉信息带来的。

评价这里也有一个我觉得值得讨论的点：看截图给分，和检查文件、应用状态，测到的东西可能不同。一个表格外观很整齐，数字仍然可能填错。我会把这些结果分开看，再抽查它们不一致的任务。具体我本人负责了哪部分，面试时仍然按实际贡献来讲。

## 被追问时再展开

**这等于训练过 multimodal 模型吗？** 不一定。这是 multimodalagent、技能内容和评价的研究。有没有更新视觉模型权重，需要按实际实验回答。

## 技术备查

## 已核对的相关研究
[VisualSkill](https://arxiv.org/html/2606.18448v1) 从文档和 UI 探索构造图文技能，使用 CUA-World、OSExpert-Eval，并有 OSWorld 跨模型补充。你是公开共同作者；具体主导内容需自行补充。multimodal 对照和任务评价细节优先读论文§2、§3及附录 F。

[OSWorld 原始论文](https://arxiv.org/abs/2404.07972) 提供真实计算机任务与执行评价背景，但不同任务集、应用版本、观察/动作接口和 verifier 要分别固定，不能合并当一张排行榜。

## 可深入的 setting（建议实验）
选一个许可软件环境的“修改表格并导出 PDF”任务。技能样本含 topic、文字说明、截图 crop、动作前后状态和出处。将文档版、探索增强版分别做图文/文字配对，再加 no-skillbaseline。控制信息来源、agent、动作接口和总 context/时间预算；文字版需要描述同样的内容，不能人为删掉关键信息。

用正确截图、无关截图、过期 UI 截图作诊断，不把所有性能差都 attribution 视觉能力。分开查按钮定位、任务规划、工具 schema 和 context 压力。反馈环节只用训练任务的错误定位探索区域，再在新任务/新 UI 上验收，避免照着测试答案补文档。

本论文中 CUA-World 使用 VLM checklist 给部分分，OSExpert-Eval 为状态型成功检查。它们 normalization 到0–1后仍测量不同，平均分不等于相同成功概率。建议 sampling 人工核验，增加状态/文件内容检查，并报告视觉 judge 对漂亮但错误输出的偏好。可解释地并列报告两个基准，而非只看合并总分。

## 英文60秒参考
> My multimodal discussion would start from VisualSkill, where I am a coauthor. The broader question is whether visual reference material contributes grounded information beyond a text-only artifact. I would use matched-source controls, hold the agent interface fixed, and evaluate on tasks not used to patch the skills. I would also separate state-based success from visual-judge scores: putting both on a zero-to-one scale does not make them equivalent. Additional images can help, but they can also introduce stale information or context overhead.

## 高频追问与回答方向
**是不是 vision token 越多越好？** 不，按任务定位信息价值，测不相关/过期内容和预算开销。
**这算 multimodal 训练经验吗？** 是 multimodalagent 与数据 artifact 研究；是否训练了视觉模型权重按实际经历回答。
**怎样接合成训练？** 可提出将成功与恢复 trajectories 转为 SFT、用独立状态构造偏好；尚未做的训练结果明确标 proposal。

继续练 `afm-rm-multimodal-evidence`、`dt-mm-shortcut-audit`、`dt-multimodal-data`。



---

## 个人 Reference 6：Unlearning，如何把 forget/retain 研究接到数据治理？


## 面试官可能这样问

你的 unlearning 研究和 Apple 关心的数据治理有什么联系？

## 可以这样回答

我觉得最直接的联系是，数据要撤回以后，我们怎么知道模型的行为真的改变了。在 unlearning 研究里，一个很容易产生误解的结果是：原来的问题答不出来了，但换一种问法，信息又出来了。

所以我会同时看忘记和保留两边。目标信息是否还能通过改写或间接问题取出来，其他正常能力有没有受到影响。只看原问题的准确率下降，我觉得证据还不够。

如果接到实际数据流程，我还会先检查数据来源和版本。模型这次做了 unlearning，但下一轮训练又把同一来源加回来，问题仍然存在。我的研究可以支持我讨论这些评价和权衡；它不能自动证明我处理过用户私有数据，也不能保证一种方法删除了所有可能提取的信息。

## 被追问时再展开

**那 unlearning 能替代数据许可吗？** 不能。允许不允许收集和训练，应当在前面决定。unlearning 是已经训练之后可能采用的一种补救办法，还需要验证。

## 技术备查

## 已核对的相关研究
[Reversing the Forget-Retain Objectives / ULD](https://arxiv.org/html/2406.08607v1) 是你参与的 unlearning 工作，包含 TOFU 实验。[TOFU](https://arxiv.org/abs/2401.06121) 用虚构人物资料定义 forget/retain，提供与未训练目标数据的参考行为比较。这是受控研究任务，不是实际用户隐私删除的认证。

## 可谈的治理 setting（建议扩展）
从许可合成 corpus 开始，对实体家族指定撤回集合；同时保存来源版本、训练 shard、改写派生和评测任务。比较原模型、仅 retain 重训参考及 unlearning 模型，在原问法、改写、间接线索和适当的再提取攻击上看忘记程度，并看相邻实体与通用任务效用。

先明确威胁模型：只要求不直接生成，还是限制给定攻击者的提取？输出下降可能来自拒绝行为，而非所有内部信息都消失。误删相邻事实、遗忘后再次 fine-tuning 恢复、数据后续重摄入都应作为研究问题。具体攻击和阈值依产品政策与能力选择，不声称有限测试证明信息论删除。

接到 AFM 时谈三层：摄入前的许可与用途限制；数据版本和撤回传播；已训练模型上的补救与验证。不能因为有 unlearning 方法就先收集不允许的数据，也不能把 PCC 推理保护、differential privacy 和权重遗忘说成一项机制。

## 英文60秒参考
> My unlearning research gives me a way to discuss governance through measurable forget–retain tradeoffs. I would distinguish suppressing an answer from demonstrating that information is no longer recoverable under a defined threat model. For a data pipeline, I would first preserve provenance and prevent withdrawn sources from re-entering later versions. Model-side unlearning would be one remediation option to evaluate, rather than a replacement for permission or a guarantee that every trace has been removed.

## 高频追问与回答方向
**只看 forget 准确率降到零够吗？** 不够，要测改写、提取以及 retain 效用，并与合理参考对照。
**有真实用户数据经验吗？** 按实际经历回答；这条 reference 基于受控研究，不暗示做过 Apple 用户数据处理。
**DP 能直接代替 unlearning？** 两者目标与保证不同，需分别说明邻居关系、预算和撤回威胁模型。

继续练 `dt-privacy-feedback`、`dt-repro-lineage`、`dt-legal-capability`。



## References

- [Jiabao Ji — personal homepage](https://question406.github.io/)
- [Jiabao Ji — public CV](https://question406.github.io/assets/cv/cv.pdf)
- [DeepAmbigQA — public paper v1](https://arxiv.org/html/2511.01323v1)
- [HarnessLLM — public paper v1](https://arxiv.org/html/2511.01104v1)
- [HARDTESTGEN — ICLR 2026 proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/file/3c11cea35aa2e4797b2f239da378927b-Paper-Conference.pdf)
- [How Well Do Agentic Skills Work in the Wild — v1](https://arxiv.org/html/2604.04323v1)
- [Speculate While You Reason — v1](https://arxiv.org/html/2607.25816v1)
- [VisualSkill — v1](https://arxiv.org/html/2606.18448v1)
- [Reversing the Forget-Retain Objectives — v1](https://arxiv.org/html/2406.08607v1)
- [Apple Foundation Models Tech Report 2025](https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025)
- [AmbigQA — EMNLP 2020](https://aclanthology.org/2020.emnlp-main.466/)
- [ASQA: Factoid Questions Meet Long-Form Answers](https://arxiv.org/abs/2204.06092)
- [MuSiQue: Multihop Questions via Single-hop Question Composition](https://arxiv.org/abs/2108.00573)
- [EvalPlus: rigorous evaluation of generated code](https://arxiv.org/abs/2305.01210)
- [LiveCodeBench — original benchmark paper](https://arxiv.org/abs/2403.07974)
- [SkillsBench — official repository](https://github.com/benchflow-ai/skillsbench)
- [tau-bench — original benchmark](https://arxiv.org/abs/2406.12045)
- [tau2-bench — dual-control environment](https://arxiv.org/abs/2506.07982)
- [OSWorld — original benchmark paper](https://arxiv.org/abs/2404.07972)
- [TOFU: A Task of Fictitious Unlearning for LLMs](https://arxiv.org/abs/2401.06121)
