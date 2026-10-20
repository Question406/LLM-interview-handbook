---
id: dt-license-is-quality
section: good-data
order: 14
level: S
title: 许可、opt-out、PII，为什么算质量问题，而不只是法务问题？
quick: "数据能否合法用于训练，也是质量条件。许可不合格、无法执行 opt-out，或含有不该使用的个人信息，即使提高评测分数，也可能导致数据撤回与重训。应把这些约束放进数据选择流程，并追踪来源、拒绝记录、教师与合成种子。"
companies:
  - apple
tags:
  - Apple
  - Privacy
  - Data Quality
  - License
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: About Applebot
    url: https://support.apple.com/en-us/119829
    type: primary
  - title: "What's In My Big Data?"
    url: https://arxiv.org/abs/2310.20707
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

数据选择要先满足许可和隐私条件。不能用于训练的样本，即使看起来很有用，也应按效用为零处理。许可决定 $u(x)$ 是否有意义，不能等训练完再补标签。HM 中能力与隐私的取舍见 `dt-legal-capability`。

许可不合格的数据，可能让固定评测得分提高，却在发布时必须撤回。前面的训练成本就无法换成可发布收益，还可能增加召回成本。如果效用函数忽略许可，就可能选中写得最像教科书的盗版内容。因此，好数据也必须可追溯、可发布，见 `dt-good-data-def`。

## 数据质量要包含使用条件

WIMBD 在常用网页集里发现了邮箱、电话等个人标识。模型可能学会补全这些信息；密钥泄漏更严重，见 `dt-secret-scan-code`。这既影响数据质量，也可能导致产品事故。

Apple 公开说明的来源包括许可语料、公开或开源数据集，以及 Applebot 抓取的公开页面。它不爬登录墙、付费墙，并尊重 robots 中不允许用于基础模型训练的要求。用户私有数据和交互默认不进入基础模型。

实现时，URL 规范化（canon）与拒绝表匹配要使用相同规则，见 `dt-url-canon-code`。Bloom 过滤器不能单独执行撤回；opt-out 需要精确记录已禁止使用的条目，也就是「墓碑」记录。

合成数据也要追踪来源。教师若接触过未经许可的页面，可能在生成时改写这些内容。WRAP 或教科书合成需要记录教师版本和种子来源，见 `dt-wrap-rephrase`。

Culture 轮中主动停用的数据，也可能是许可或隐私不合格的数据，见 `dt-killed-dataset`。这类风险常到发布后才暴露，训练 loss 不会提醒你。

## 追问

- 开源权重能作为训练资源吗？要检查许可证和条款。能下载不代表能按计划使用；模型输出还需要另行检查许可条件。
- 公开网页等于可训练吗？不等于。还要检查 robots、付费墙和是否汇集个人信息等。Apple 支持页说明了它会避开的内容。
- 研究集里的用户对话怎么办？不能默认存在可用的收集渠道。应选择许可明确的研究集，或通过合成复现任务，见 `dt-userlog-contrast`。
