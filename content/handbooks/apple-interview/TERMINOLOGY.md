# 术语约定

专业术语直接用英文，中文解释具体含义、选择理由和例子。常见缩写第一次出现时可以写全称，例如 reward model (RM)、supervised fine-tuning (SFT)。

| 讨论内容 | 使用的术语 |
| --- | --- |
| 训练阶段 | pre-training、mid-training、continued pre-training、post-training |
| 训练方法 | SFT、DPO、RLHF、RLVR、knowledge distillation |
| 数据处理 | data pipeline、data mix、deduplication、decontamination、data augmentation |
| 标注和奖励 | annotation guidelines、preference pairs、soft labels、reward model、verifier |
| 评价和实验 | evaluation slices、ablation study、calibration、held-out evaluation set |
| 退化或偏差 | negative transfer、overfitting、model collapse、length bias、position bias、sycophancy |
| 序列与张量 | tensor、matrix、causal mask、prefix sum、gradient accumulation |
| 解码 | beam search、speculative decoding、rejection sampling、acceptance rate |
| 训练目标 | negative log likelihood、log likelihood、cross entropy、surrogate loss |
| 概率与估计 | likelihood ratio、log probability、importance sampling、confidence interval |
| RL 机制 | policy gradient、advantage estimation、value function、credit assignment、reward shaping |
| 优化与数值 | gradient clipping、gradient accumulation、weight decay、normalization、standardization |

其中“负对数似然”统一写为 **negative log likelihood**，按需要保留 NLL 缩写。其他常见名词的英文写法见 [共享术语表](../../terminology-english.json)，适用于所有题本。标题、摘要、回答思路和正文采用同一表达；代码注释与 docstrings 可同步改写，函数名、变量名和测试数据保持准确。

容易混淆的词按语境区分：

- **inference / reasoning**：运行模型、延迟和设备预算使用 inference；数学、多跳问题的思考能力使用 reasoning。
- **release gate / held-out evaluation set**：前者是发布检查条件，后者是一套独立评价数据，不都叫“门禁”。
- **baseline / regression tasks / regression data**：baseline 是对照方法；后两者用于检查或保留已有能力。研究案例的出发点直接说“相关研究”，不叫“研究锚点”。
- **validation / verification**：validation set 用于开发和模型选择；verifier 检查答案、程序或环境状态是否满足规定条件。
- **replay / on-policy rollout**：旧记录的 replay 和 current policy 的新采样不是同一种数据。

避免用模糊的中文隐喻代替具体机制，按语境选择术语：

| 表达的实际含义 | 使用的表达 |
| --- | --- |
| 数据是否符合质量要求 | data quality checks / quality criteria |
| 模型是否满足发布要求 | release criteria / regression checks |
| 一组用于最终验收的数据 | held-out evaluation set |
| 编程中的特殊输入与异常情况 | edge cases / edge-case behavior |
| 文档、序列或分块的分隔位置 | document boundaries / sequence offsets / chunk boundaries |
| 允许哪些操作、访问哪些资源 | authorization rules / access restrictions |
| 方法在哪些情况下适用 | applicability / limitations / constraints |
| 模型当前能处理的能力范围 | capability limits；讨论训练前沿时使用 capability frontier |
| 数据与评估持续改进 | feedback loop；说明反馈如何改变下一轮数据 |
| 保留旧能力的数据或评估 | replay data / regression data / regression evaluation |
| KL 相对哪个分布计算 | reference policy / reference distribution |
| GiGPO 中重复出现的环境状态 | anchor state |
| 失败后的替代路径 | fallback / human escalation |
| 指标怎样计算或标签怎样定义 | metric definition / evaluation protocol / label definitions |

不要把上述词机械互换。mandatory checks 是必须执行的检查，fallback 是失败后的替代路径；两者作用不同。中文用于说明动作和原因，例如“通过检查后加入训练”，不写成“过门后回流”。

可执行代码、接口名、公式、URL、测试输入输出等字面内容保留原样；注释与 docstrings 中的专业术语可按本表改写。来源标题和不属于专业术语的普通中文，也不作无差别替换。

“簇”按语境使用 cluster、task family、failure category 或 source group。数据库语境使用 clustered index / clustering key；不要把任务家族或失败类型一律叫 cluster。
