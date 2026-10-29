# Apple Foundation Models 专项练习

已整理统一入口：[Apple 面试 Question Book](../apple-interview/README.md)。网页切换到 **Apple 面试题本**，可按章节浏览本手册、其他 Apple 标签题及补充 tensor 练习；原手册继续保留。

2026-10-26 累计新增 53 道专项题：第一批 12 道自拟练习，第二批 20 道自拟练习，以及 Chrome 原帖核对后的 21 道来源题／主题扩展。32 道自拟练习全部 `realInterview: false`；论坛批次共 19 道有可核对的候选人问题依据，2 道主题扩展为 `false`。题中的补充规模、接口和预算均明确标为练习约定，不代表 Apple 内部实现。

在资料库选择 **Apple Foundation Models · Data Team**，搜索标签 **AFM 专项 2026-10** 可以找到这 53 道题；搜索 **AFM 加练第二批** 可只看第二批 20 道，搜索 **一亩三分地继续检索** 可看上一轮 10 道，搜索 **Apple 面经继续检索第三轮** 可看新增的两道设计题。题面独立展示，参考答案默认折叠；共 23 道编程题可进入本地编程练习页，加载起始代码与默认测试。

## 第三轮：补充同一原帖的两道设计题

- [相册照片排序](questions/panel/p3a-apple-photo-ranking.md)：原帖明确排序对象；练习补充任务目标、duplicate clusters、事件覆盖、偏好信号与端上约束。
- [大型视频摘要系统](questions/panel/p3a-apple-video-summary-design.md)：原帖明确系统设计题；练习补充跨模态对齐、证据时间戳、层级汇总与评价。

两题来自已核对的 2024-09-05 Apple MLE 原帖 `1084615`，是此前未整理的两个问题，不计为发现新的帖子，也未确认属于 AFM。第三轮另查的职业讨论与受限 PM 经历没有产生新题，详见来源审计。

## 继续检索：新增 10 道

本轮另核对 10 个此前未收录的原帖，从其中 6 个提取可练习的问题或面试形式；4 个只留审计记录。没有发现可据此声称“新增 10 道 AFM Data Team 真题”的证据，团队限定见下表与题面。

| 题目 | 来源 | 原帖与扩展边界 |
| --- | --- | --- |
| [现场完成表格数据 ML 全流程](questions/tech-screen/dt-p3a-tabular-full-pipeline.md) | Apple MLE，2024-09-05 | 明确要求预处理、训练、指标、降维与可视化；逻辑回归／PCA 为练习选择 |
| [手写 K-fold CV](questions/tech-screen/dt-p3a-kfold-indices.md) | Apple DS，2025-12-19 | 明确手写 K-fold；余数、seed、索引接口为补充 |
| [BatchNorm 训练与推断状态](questions/tech-screen/dt-p3a-batchnorm-state.md) | AIML 视频组，2024-01-29 | 手写 BatchNorm、与 LN 区别和参数；运行统计细节为补充 |
| [手写二维 circular padding](questions/tech-screen/p3a-apple-cvml-circular-padding.md) | CVML，2025-05-21 | 明确 circular padding；二维、非对称、多圈和梯度为练习约定 |
| [标准化 kNN 完整流程](questions/tech-screen/p3a-apple-cvml-knn-pipeline.md) | CVML，2025-05-21 | 明确 kNN end-to-end；标准化与平票语义为补充 |
| [生成式图像如何评测](questions/panel/p3a-apple-cvml-image-evaluation.md) | CVML，2025-05-21 | 明确生成图像评价主题；具体情景与指标方案为扩展 |
| [面向对象 DAG 执行器](questions/tech-screen/p3a-apple-task-dag-code.md) | AIML Infra，2025-10-07 | 补全任务添加和依赖执行；完整类接口为重构 |
| [JSON 清洗与拒收统计](questions/tech-screen/p3a-apple-json-clean-code.md) | AIML Infra，2025-10-07 | 只披露 JSON 清洗处理；schema 与择优规则为练习约定 |
| [Flask 推理 API 契约](questions/panel/p3a-apple-flask-inference-contract.md) | AIML Infra，2025-10-07 | 原轮为 API 实现，本卡整理为接口与测试设计，不要求安装 Flask |
| [从公式实现可训练 layer](questions/tech-screen/dt-p3a-paper-gated-layer.md) | CV/ML 面试形式，2022-12-02 | 原帖未公开论文或 layer；门控公式自拟，`realInterview: false` |

本轮 CVML 帖子发帖于 2025 年，经历字段标 2024 年第四季度；表中是发帖日期，不能当作面试发生日。页面时间不另推断时区。优先练前五道与 DAG／JSON；论文 layer 用来练输入输出形状、参数注册和梯度验证。

## Chrome 核对的一亩三分地来源题

原帖核对的是候选人报告，并非 Apple 官方出题承诺。Foundation Model、Siri、AIML 研究和 IS&T 团队分别标注；不将其他 Apple 团队或历史面经当作本次 AFM Data Team 已确认原题。完整接口、场景和参考答案为手册整理，来源主题与扩展边界见各题。

| 题目 | 原帖团队与日期 | 核对到的范围 |
| --- | --- | --- |
| [小数时间预约的最大重叠数](questions/tech-screen/dt-p3a-decimal-calendar.md) | Foundation Model，2025-09-13 | 类似 LC732、小数时间；接口与 Decimal 约定为扩展 |
| [RAG 防幻觉与 evaluation](questions/panel/p3a-apple-afm-rag-deepdive.md) | Foundation Model，2025-09-13 | RAG 项目深挖及两项明确追问 |
| [两句话是否恰好差一次编辑](questions/tech-screen/dt-p3a-sentence-one-edit.md) | Siri response generation，2026-03-24 | 一次编辑、返回布尔值；字符单位等为扩展 |
| [TTL 缓存过期与删除](questions/tech-screen/dt-p3a-ttl-cache-contract.md) | IS&T Sr MLE，2026-03-25 | TTL 定义及删除时机；完整接口为扩展 |
| [为项目数据配比辩护](questions/panel/p3a-apple-aiml-mixture-defense.md) | 中国 AIML MLE，2025-08-14 | 为什么这样配、是否比较替代方案 |
| [为什么需要 reasoning](questions/senior/p3a-apple-research-why-reasoning.md) | AIML 研究团队，2025-09-13 | reasoning 进展、价值与研究交流主题 |
| [设计搜索系统](questions/panel/p3a-apple-siri-search-design.md) | Siri MLE，2021-08-17 | 原帖明确设计主题；搜索对象和规模为扩展 |
| [简单分类器的完整数据系统](questions/panel/p3a-apple-classifier-data-system.md) | Siri MLE，2021-08-17／2026-02-15 | 简单分类器系统，以及场景驱动的预处理与训练设计 |
| [Simplicity 与 Build Trust](questions/culture/p3a-apple-simplicity-trust-practice.md) | Siri MLE，2021-08-17 | 只公开文化主题，具体练习问法自拟，`realInterview: false` |

[来源核对记录与去重说明](../../sources/apple-forum-2026-10-26/README.md) 保留原帖链接、页面日期、可见范围及未披露内容。已有 k-means、MHA、attention 和 Siri 回复设计不重复建题，也不据这些帖子推算出现频率。

## 第二批：8 道编程加练

| 题目 | 建议限时 | 核心检查 |
| --- | --- | --- |
| [按 padding 后 token 预算组 batch](questions/tech-screen/dt-token-budget-batch-code.md) | 20 分钟 | 成本模型、超长拒收、尾批 |
| [多 rank／worker 分片](questions/tech-screen/dt-worker-shard-code.md) | 15 分钟 | 全局消费者编号、完整性与重复 |
| [固定缓冲区流式打乱](questions/tech-screen/dt-buffer-shuffle-code.md) | 20 分钟 | 惰性、有界缓冲区、近似随机性 |
| [任务家族配对 bootstrap](questions/tech-screen/dt-cluster-bootstrap-code.md) | 25 分钟 | 配对、组内相关、家族等权指标 |
| [带置信权重的 reward loss](questions/tech-screen/dt-rm-weighted-loss-code.md) | 20 分钟 | 权重分母、梯度与全零权重 |
| [温度蒸馏正向 KL](questions/tech-screen/dt-distill-forward-kl-code.md) | 25 分钟 | 方向、冻结教师、token reduction |
| [packed 因果注意力 mask](questions/tech-screen/dt-packed-attention-code.md) | 20 分钟 | 文档隔离、padding query、API 语义 |
| [pass@k 估计](questions/tech-screen/dt-passk-estimator-code.md) | 20 分钟 | 组合概率、任务等权、选择器限制 |

## 第二批：12 道场景与决策题

| 题目 | 练习重点 |
| --- | --- |
| [总分上涨但每个桶都退化](questions/panel/dt-simpson-release-metrics.md) | 固定权重、分母、路由与模型归因 |
| [异步 rollout 吞吐高但能力掉点](questions/panel/dt-stale-rollout-incident.md) | 策略年龄、奖励版本、环境漂移 |
| [WER 降低却更容易做错操作](questions/panel/dt-audio-semantic-regression.md) | 语义代价、语音分段诊断、授权音频 |
| [视频识物高分却分不清先后](questions/panel/dt-video-temporal-shortcut.md) | 帧采样、时序证据、源视频隔离 |
| [组内奖励相同，如何恢复学习信号](questions/panel/dt-zero-advantage-groups.md) | 奖励审计、难度、采样预算 |
| [学生进步后动态更新合成课程](questions/panel/dt-curriculum-moving-target.md) | 可学性、覆盖、盲测隔离 |
| [翻译与改写绕过污染扫描](questions/panel/dt-paraphrase-leakage-audit.md) | 来源链、语义候选、确认污染证据 |
| [两种好数据组合后反而掉点](questions/panel/dt-mixture-factorial-budget.md) | 因子实验、交互、预算控制 |
| [换 tokenizer 后 loss 与能力背离](questions/panel/dt-tokenizer-migration-gap.md) | 计量单位、缓存、截断、监督对齐 |
| [多语言偏好标签冲突](questions/panel/dt-preference-multilingual-conflict.md) | 原生语境、多维标签、合法分歧 |
| [发布前发现评测口径错误](questions/culture/dt-culture-eval-deadline.md) | 最小复现、协作、决策范围 |
| [小模型最佳配方无法迁移大模型](questions/senior/dt-senior-proxy-scale-reversal.md) | 跨规模证据、数据保留、一次大训练决策 |

## 先练技术筛选

| 顺序 | 题目 | 建议限时 | 核心检查 |
| --- | --- | --- | --- |
| 1 | [构造变长 SFT batch](questions/tech-screen/dt-sft-collate-code.md) | 25 分钟 | 截断、padding、监督位置、输入不变 |
| 2 | [计算回答 log probability](questions/tech-screen/dt-response-logprob-code.md) | 20 分钟 | shift、gather、序列求和、梯度 |
| 3 | [实现 DPO loss](questions/tech-screen/dt-dpo-batch-code.md) | 20 分钟 | 参考策略冻结、稳定计算、梯度方向 |
| 4 | [按有效 token 累积梯度](questions/tech-screen/dt-token-accum-code.md) | 25 分钟 | 不等长批次权重、空窗口、一次更新 |

每次闭卷完成一题，再用剩余时间补足为 45 分钟：先解释输入输出和手算例子，再运行测试，最后讨论规模、数据质量或训练边界。限时为训练建议，不是面试原题难度或出题概率的预测。

## 再练 Panel

| 题目 | 练习重点 |
| --- | --- |
| [工具选对，端到端却掉点](questions/panel/dt-tool-gap-factorial.md) | 中间结果替换、失败阶段定位、两次训练的预算 |
| [自动 judge 与人评反转](questions/panel/dt-judge-ranking-reversal.md) | 测量偏差、长度与位置效应、独立盲测 |
| [验证通过率 98% 仍伤泛化](questions/panel/dt-verifier-counterfactual.md) | 验证器审计、反事实样本、等预算消融 |
| [截图问答换 UI 就失败](questions/panel/dt-mm-shortcut-audit.md) | 视觉证据、模板捷径、渲染可见性 |
| [重跑数据导致小语种重复](questions/panel/dt-data-replay-incident.md) | 幂等产物、manifest 发布、训练恢复 |
| [隐私聚合看不到罕见失败](questions/panel/dt-private-tail-budget.md) | 长尾覆盖、授权种子、风险与频率区分 |

每题先用 5 分钟提出主要假设，再用 20 分钟画出诊断与干预方案，接着用 10 分钟接受追问，最后用 10 分钟复盘。参考答案是一种可辩护的方案；假设明确、实验能区分原因、预算可执行的其他方案也可以成立。

## Culture 和高层轮

- [提前预警只对了一半](questions/culture/dt-culture-falsifiable-warning.md)：用真实经历讲早期信号、最小验证、纠错与个人贡献。不得把题面模板改成虚构履历。
- [自训练三轮涨分，是否继续加预算](questions/senior/dt-senior-stop-selftrain.md)：先用 90 秒给决定，再讲改变决定的证据、下一笔预算和停止条件。

## 自评方法

每题从以下四项分别评为 0、1、2 分：0 表示没有处理，1 表示提到了但缺少证据或细节，2 表示能说明具体机制、例子与边界。这是个人练习标准，不是 Apple 评分表。

1. **问题定义**：输入、目标、分母、假设是否清楚。
2. **正确性或诊断**：代码能否通过有意义的测试；场景实验能否区分竞争假设。
3. **验证**：是否有独立对照、回归检查和不确定性说明。
4. **表达与取舍**：能否边做边解释，并在时间、算力、审核或隐私约束下作决定。

任一项为 0 时优先重练该部分。不要仅以看懂参考答案作为掌握标准。
