---
id: dt-license-is-quality
section: good-data
order: 14
level: S
title: 许可、opt-out、PII 为什么也算数据质量问题？
quick: >-
  因为能不能合法用于训练，本身就是质量条件。许可不合格、opt-out 执行不了、或者带着不该用的 personally identifiable
  information (PII)，评测分再高也可能被迫撤回重训。所以要把这些约束放进数据选择流程，追踪来源、拒绝记录、teacher 和合成 seed。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Datasets used for Apple Intelligence
    url: 'https://www.apple.com/legal/ai-regulations/training-data/'
    type: primary
  - title: About Applebot
    url: 'https://support.apple.com/en-us/119829'
    type: primary
  - title: What's In My Big Data?
    url: 'https://arxiv.org/abs/2310.20707'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

不能用于训练的数据，再有用也发布不了。所以数据选择要先满足许可和隐私条件，不合格的样本效用按零算。许可决定了 $u(x)$ 有没有意义，要在选择阶段就标好，训练完再补就晚了。

举个例子，如果效用函数不管许可，选中的很可能恰好是写得最像教科书的盗版内容。它确实能让固定评测的分数涨，可到发布时必须撤回，前面的训练成本换不来可发布的收益，还可能加上召回成本。所以好数据也必须可追溯、可发布，见 `dt-good-data-def`。

personally identifiable information (PII) 是同一个道理。WIMBD 在常用网页集里发现了邮箱、电话等个人标识，模型可能学会把这些补全；密钥 leakage 更严重，见 `dt-secret-scan-code`。这既是数据质量问题，也可能直接变成产品事故，而且常常到发布后才暴露，训练 loss 不会提醒你。

## 怎样放进数据流程

我会先把可用来源定清楚：许可 corpus、公开或开源数据集、合规抓取的公开页面，再加上 synthetic data。抓取时不进登录墙和付费墙，尊重 robots 里不允许用于模型训练的声明。Apple 公开的训练数据说明也是按这几类列来源的。

然后让撤回真的能执行。URL 规范化（canon）和拒绝表匹配用同一套规则，见 `dt-url-canon-code`。Bloom 过滤器不能单独执行撤回，opt-out 需要精确记下已禁止使用的条目，也就是「墓碑」记录。

synthetic data 也要追来源。teacher 如果接触过未经许可的页面，生成时可能把这些内容改写出来，所以 WRAP 或教科书式合成都要记录 teacher 版本和 seed 来源，见 `dt-wrap-rephrase`。

## 追问

**开源权重能当训练资源吗？**
先查许可证和条款。能下载不代表能按计划使用，模型输出也要另外检查许可条件。

**公开网页就等于可以训练吗？**
不等于。还要查 robots、付费墙，以及是否汇集了 personally identifiable information (PII)。

**研究集里的用户对话怎么办？**
先确认有合规的收集渠道。没有的话，选许可明确的研究集，或者用合成复现任务，见 `dt-userlog-contrast`。

**HM 问能力和隐私怎么取舍，怎么接？**
可以从这题的「不合格样本效用为零」讲起，取舍的展开见 `dt-legal-capability`。Culture 轮问你主动停用过的数据，也可能就是许可或隐私不合格的那批，见 `dt-killed-dataset`。
