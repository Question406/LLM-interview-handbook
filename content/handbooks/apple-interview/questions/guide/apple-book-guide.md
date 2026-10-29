---
id: apple-book-guide
section: guide
order: 0
level: S
title: Apple 面试 Question Book：怎么选题、怎么练、怎样判断来源？
quick: >-
  技术二面先练 cumsum／matrix／mask、Python 与 ML Coding 和 data pipeline；Panel 再练合成、评测、偏好与
  multimodal。原帖题、主题扩展、公开研究和跨公司迁移分别保留来源，不能用题本数量推算出题频率。
companies:
  - apple
tags:
  - Apple
  - 备考路线
  - Question Book
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-26T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

这本手册将当前仓库内的 Apple 公司标签题、整本 Apple Foundation Models Data Team 备考资料，以及为 tensor 编程补选的迁移题组织到同一个入口。完整题目、答案、测试和原帖出处均可在本册查看，不需要依靠日期标签筛选。

## 技术二面先练什么

按下面顺序闭卷写代码，并说明 shape、edge cases、complexity 与测试：

1. `apple-mask-position-ids`：从有效位置生成 position IDs。
2. `apple-starts-doc-mask`：由文档起点生成 doc IDs、段内位置和可见性 matrix。
3. `apple-mask-pack-unpack`：用 cumsum、scatter、gather 压缩并恢复特征。
4. `coding-packed-lm` 与 `code-packed-mask`：长度 prefix sum 及文档隔离。
5. `dt-packed-attention-code` 与 `coding-attn-mask`：padding、causal 和文档条件，解释不同 padding query 契约。
6. `dt-p3a-tabular-full-pipeline`：跑通预处理、训练、测试和指标；随后练数据过滤、deduplication 与 sampling。

`code-linear-attn`、`p3a-openai-numpy-1nn-wx-b` 与 `p3a-openai-autograd-hillis-steele-scan` 用于进阶 matrix 运算。最后一题来自 OpenAI 的站内二手题卡，不能称作 Apple 原题。相关题仍保留原公司标题和来源。

## Panel 怎么选

data pipeline、合成、评测、偏好与 multimodal 章节覆盖 Panel 主线。每次选一个具体能力缺口，先提出竞争假设，再设计能区分原因的实验，最后给数据干预、独立评价与回归标准。不要只背算法名称。

Agent／系统设计用于串联数据生成、工具执行与部署约束。项目与 Culture 使用你自己的经历，分别准备 90 秒、5 分钟与深挖版本。来源中的故事与示例不能改写成个人履历。

## 怎样看来源

- **候选人原帖核对**：只能支持作者报告过的题目或主题，具体团队、时间与可见范围见题面。
- **站内二手面经**：没有完整原帖核对时保留这一限制。
- **主题扩展与通用练习**：接口、数字、场景和参考答案由本手册补充。
- **研究与跨团队迁移**：用于准备 Apple 数据岗相关能力，原公司与论文归属不变。

“真实面经”标记可能只表示题型有候选人报告依据，不表示详细手册接口逐字公开。需要精确判断时，展开 source attribution 与适用范围；不能把不同团队合并统计为 AFM 出题概率。

## 内容与练习入口

本册对已有题采用源题引用，原手册内容更新后，重新构建会同步到本册。每道引用题末尾可回到原手册。编程练习在本册可直接加载原始实现、起始代码与测试。不同手册的掌握进度仍分别记录，原有深链和草稿保留。

全题目录与每题要点在本册 README；来源核对记录仍位于 `content/sources/apple-forum-2026-10-26/`。新收录题可通过 `npm run apple:sync` 更新引用清单与总结，再运行内容构建。

## AFM 原始要求的实战补全

先做 `afm-mock-screen-a` 和 `afm-mock-screen-b`，分别检验完整 PyTorch 训练和偏好建模。两套各45分钟，不要求一场把所有扩展代码都写完。

随后用 `afm-mock-debug-tools` 和 `afm-mock-debug-reward` 的 CSV/JSONL 附件诊断，练从原始证据到数据干预；`afm-case-endtoend` 用同一截图工具任务串起合成、评测、偏好、隐私与 pre/mid/post 阶段选择，并提供缩小的可运行 self-iteration 实验。

`afm-personal-evidence-pack` 是待填写的项目、失败、See Around Corners、multimodal 和论文模板；它不代表个人材料已经完成。最后用 `afm-panel-rubric` 连练五场45分钟，再用 `afm-director-mock` 练30分钟决策。评分为自练约定，不是 Apple 标准。

Reward/Bias 本次新增20题：先练相对奖励、soft labels 及评分范式，再练 RMpipeline、基准与下游质量、过度优化、长度/顺序/家族/迎合/群体偏差，最后练主动标注、集成、PRM、DPO、multimodal 与安全取舍。每题来源保留原始论文，不算 Apple 面经。
