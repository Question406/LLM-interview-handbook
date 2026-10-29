---
id: amazon-lp-ml
section: amazon
order: 7
level: S
title: Amazon：领导力原则怎么落到 ML 决策（release criteria、客户数据、纠错）？
quick: >-
  把 LP 放进具体 ML 决策里讲：上线先定客户指标和回滚 acceptance
  checks，客户数据做到最小够用、可审计、可删除，指标变差后按切片查根因。讲经历时说明你当时怎样取舍、采取了什么行动，以及数据证明了什么。
tags:
  - Amazon
  - Leadership Principles
  - MLOps
  - Launch Gates
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Amazon Leadership Principles
    url: 'https://www.aboutamazon.com/about-us/leadership-principles'
    type: primary
  - title: Amazon Interview Process (7 steps to getting an offer)
    url: 'https://igotanoffer.com/blogs/tech/amazon-interview-process'
    type: secondary
  - title: Amazon Bias for Action interview questions
    url: >-
      https://igotanoffer.com/en/advice/amazon-bias-for-action-interview-questions
    type: secondary
---

我会用一次具体的上线或纠错决策讲 LP：当时如何保护客户、依据什么判断可以上线、出现问题后如何处理。Amazon 的公开面试指南说 LP 贯穿每轮，Bar Raiser 会追问这些判断；单独背 16 条很难说明自己怎么做决定。

讲经历时，可以从〔填：一次你挡住上线，或被数据说服后支持实验的真实情境〕开始。先说受影响的客户指标，例如购买、退货、零结果、政策误导和 PII 泄漏。AUC 高了 0.3 个点还不足以回答客户是否受益。这里的 Customer Obsession 决定看什么结果，Insist on the Highest Standards 决定放行条件。

具体到 acceptance checks，我会先写清离线切片：头尾 query、新 ASIN、标识符 query 都要过线，见 `amazon-kendra-hybrid`、`amazon-cold-start`。然后用不改变排序的影子流量查特征漂移和 p99，再做预注册主指标与护栏的 A/B。退货、客服工单、延迟和 Guardrail 漏拦任何一项破线，即使主指标赢了也要停。模型、特征版本和索引别名一起回滚，见 `amazon-p99-stream`、`amazon-feature-store`。

Bias for Action 可以体现在可逆的影子和 1% 实验中。Are Right, A Lot 要求主动找失败切片，Frugality 则要求先验证问题，避免再训一个大模型碰运气。如果团队决定做自己反对的实验，Have Backbone; Disagree and Commit 意味着把分歧说清后，继续把护栏和回滚做好。这里补上〔填：你提出的依据、团队最后的决定、实验结果〕，用真实数字说明判断。

客户数据的取舍也能体现 Earn Trust。精排不需要原始邮箱时，在进入特征存储前打码或哈希；Bedrock 可配合敏感信息过滤，见 `amazon-guardrails`。Seller 工单的用途和 ACL 要跟着数据走，不能随意进入广告模型。删除请求要落实到离线样本和线上特征；未来点击或测试 ASIN 评测集也不能混进训练。Ownership 表示即使管道由平台团队负责，特征质量告警仍需要自己推动解决。对话中可能含未成年人或医疗信息，Success and Scale Bring Broad Responsibility 要求把规模带来的责任算进设计。

出现问题时，我会先按影响行动：安全、PII 或 p99 护栏破了立刻回滚；只有主指标下降则缩流量，再查 query、ASIN、市场、特征延迟、ANN 索引版本和 Guardrail 误杀。新品探索看 `amazon-cold-start`，编码漂移看 `amazon-two-tower`；离线好线上差先查 `amazon-feature-store`。日志、点时间回放和对照实验能帮助 Dive Deep，根因是标注或政策就改数据与 acceptance checks。Invent and Simplify 还意味着考虑删掉会漂移的特征，减少长期维护负担。

最后交代〔填：客户指标是否恢复、恢复用了多久、事后改了哪条 acceptance checks〕。Deliver Results 要落到客户结果，Learn and Be Curious 则落到把生产失败写回 `amazon-titan-eval` 的评测集。

## 追问

**业务要快上线，acceptance checks 又没过怎么办？**
先做可逆的小流量或影子实验。Bias for Action 可以缩短获取证据的时间，护栏仍要保留。

**业务坚持使用更激进的客户数据呢？**
先用最小特征与带 PII 的方案对照，比较离线增益。仍确需原文时升级审批、明确留存并留审计记录，用数据表达分歧。

**回滚算 Deliver Results 失败吗？**
回滚是在保护客户。应说明回滚速度和后续 acceptance checks 变化，发现问题后继续放量才会扩大损失。

**技术轮怎么体现 LP？**
把 acceptance checks、数据和回滚放进系统设计的取舍里。评委需要知道你如何用原则做决定，相关经历和结果要来自自己的实际工作。
