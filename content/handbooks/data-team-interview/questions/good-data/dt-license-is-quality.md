---
id: dt-license-is-quality
section: good-data
order: 14
level: S
title: 许可、opt-out、PII 为什么也算数据质量问题？
quick: "因为数据能否合法用于训练，本身就是质量条件。许可不合格、无法执行 opt-out，或含有不该使用的个人信息，即使提高了评测分数，也可能导致数据撤回和重训。应把这些约束放进数据选择流程，并追踪来源、拒绝记录、教师与合成种子。"
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

因为不能用于训练的数据，再有用也发布不了。所以数据选择要先满足许可和隐私条件：不合格的样本，效用按零处理。许可决定 $u(x)$ 有没有意义，要在选择阶段就标好，训练完再补就晚了。

## 为什么算质量问题

许可不合格的数据，可能让固定评测的分数提高，但到发布时必须撤回。前面的训练成本换不成可发布的收益，还可能增加召回成本。如果效用函数忽略许可，选中的可能恰好是写得最像教科书的盗版内容。所以好数据也必须可追溯、可发布，见 `dt-good-data-def`。

个人信息也是同样的道理。WIMBD 在常用网页集里发现了邮箱、电话等个人标识，模型可能学会补全这些信息；密钥泄漏更严重，见 `dt-secret-scan-code`。这既是数据质量问题，也可能直接变成产品事故。而且这类风险常到发布后才暴露，训练 loss 不会提醒你。

## 怎样放进数据流程

先明确可用来源：许可语料、公开或开源数据集、合规抓取的公开页面，再加上合成数据。抓取时不进登录墙和付费墙，并尊重 robots 中不允许用于模型训练的声明。Apple 公开的训练数据说明也是按这几类列出来源的。

然后让撤回真正可执行。URL 规范化（canon）和拒绝表匹配要用同一套规则，见 `dt-url-canon-code`。Bloom 过滤器不能单独执行撤回；opt-out 需要精确记录已禁止使用的条目，也就是「墓碑」记录。

合成数据也要追踪来源。教师如果接触过未经许可的页面，生成时可能把这些内容改写出来。WRAP 或教科书式合成都需要记录教师版本和种子来源，见 `dt-wrap-rephrase`。

## 和其他题的关系

HM 轮里能力与隐私的取舍，见 `dt-legal-capability`。Culture 轮中你主动停用的数据，也可能是许可或隐私不合格的数据，见 `dt-killed-dataset`。

## 追问

- 开源权重能当训练资源吗？要检查许可证和条款。能下载不代表能按计划使用；模型输出也要另行检查许可条件。
- 公开网页就等于可训练吗？不等于。还要检查 robots、付费墙，以及是否汇集了个人信息。
- 研究集里的用户对话怎么办？先确认有合规的收集渠道。没有的话，选择许可明确的研究集，或者用合成复现任务，见 `dt-userlog-contrast`。
