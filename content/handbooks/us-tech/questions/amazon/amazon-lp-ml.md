---
id: amazon-lp-ml
section: amazon
order: 7
level: S
title: Amazon：领导力原则怎么落到 ML 决策（上线门禁、客户数据、纠错）？
quick: >-
  上线门禁是 Insist on the Highest Standards 加 Customer Obsession：离线不够就别全量。客户数据是 Earn
  Trust：最小够用、可审计、可删。纠错是 Dive Deep 加 Backbone：指标掉了先停再查，不同意用数据吵，决定了就回滚或修。LP 不是
  STAR 背诵，是你怎么拒绝一次坏上线。
tags:
  - Amazon
  - Leadership Principles
  - MLOps
  - Launch Gates
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Amazon Leadership Principles
    url: https://www.aboutamazon.com/about-us/leadership-principles
    type: primary
  - title: Amazon Interview Process (7 steps to getting an offer)
    url: https://igotanoffer.com/blogs/tech/amazon-interview-process
    type: secondary
  - title: Amazon Bias for Action interview questions
    url: https://igotanoffer.com/en/advice/amazon-bias-for-action-interview-questions
    type: secondary
---

Amazon loop 里 Bar Raiser 不单独问「背 16 条」。技术轮结束会追：你为什么敢上线、数据从哪来、错了怎么办。公开面试指南都写 LP 贯穿每一轮。下面按 ML 决策落。三条线够用：门禁、数据、纠错。别把 16 条各讲一句。

## 上线门禁：Highest Standards，不是 Bias for Action 的挡箭牌

Customer Obsession 要求指标是客户的：购买、退货、零结果、政策误导、PII 泄漏，不是「AUC 高了 0.3 个点」。Insist on the Highest Standards 要求有书面门禁，例如：

- 离线：切片指标（头 / 尾 query、新 ASIN、标识符 query）都过线，见 `amazon-kendra-hybrid`、`amazon-cold-start`。
- 影子：线上打分对比，不改变排序，看漂移和延迟 p99，见 `amazon-p99-stream`。
- A/B：预注册主指标和护栏（退货、客服工单、延迟、Guardrail 漏拦）。护栏破了即使主指标赢也停。
- 回滚：一键切别名，模型版本和特征版本一起切，见 `amazon-feature-store`。

Bias for Action 在这里不是「没评完就推全量」。可逆的影子和 1% 实验才是行动；不可逆的全量是赌博。Frugality 也反对「再训一个大模型碰运气」。Are Right, A Lot 要你主动找会失败的切片，而不是只报平均值。

Have Backbone; Disagree and Commit：门禁没过，对业务说不。你反对的实验如果团队决定做，就帮它把护栏和回滚写严，而不是上线后冷笑。现场故事要有一次你挡过的上线，或一次你被数据说服后 commit。没有数字的 STAR 在 Amazon 很弱。

## 客户数据：Earn Trust 写进管道，不是写进 wiki

Earn Trust 和 Customer Obsession 叠在数据上：训练用的点击、对话、工单，客户默认你不会拿去训一个会背出他地址的模型。落到决策：

- **最小够用。** 精排不需要原始邮箱；PII 在进特征存储前打码或哈希。Bedrock 场景用 Guardrails 的敏感信息过滤，见 `amazon-guardrails`。
- **用途绑定。** Seller 工单不能随便进广告模型。标签和 ACL 跟特征走，不跟笔记本走。
- **可删可审计。** 用户删除请求要能从离线样本和线上特征里落地；说「已经训进权重了」是 Ownership 失败。
- **泄漏检查。** 用未来点击当特征、用测试 ASIN 的评测集进训练，都是 Earn Trust 对内部评测的背叛：你在骗自己和客户。

Ownership 表示数据质量告警是你的，即使管道是平台团队的。特征对不上就停模型，不要等业务发现推荐「突然变神」。Success and Scale Bring Broad Responsibility：日志里的对话可能含未成年人或医疗，规模本身构成义务，不是「有 ACL 就行」。

## 纠错：Dive Deep，然后 Deliver Results

指标掉了，Dive Deep 禁止停在「可能是季节性」。要切：哪些 query / ASIN / 市场、是否特征延迟、是否 ANN 索引版本错、是否 Guardrail 误杀。工具是日志、特征点时间、对照实验，不是再开一个大模型。

纠错决策树我面试会画：

1. 护栏破（安全、PII、延迟 p99）：立刻回滚，再查。这是 Insist on the Highest Standards。
2. 主指标掉、护栏还在：先缩流量，定位切片；新品探索过度走 `amazon-cold-start`，编码漂移走 `amazon-two-tower`。
3. 离线好、线上差：先查训练/服务偏移，见 `amazon-feature-store`，再怀疑模型。
4. 根因是标注或政策错：改门禁和数据，不是调学习率。

Learn and Be Curious 体现在事后：把失败 case 写进评测集，见 `amazon-titan-eval`。只修线上、不沉淀，下次还踩。Deliver Results 是客户指标回来，不是「我们发了 postmortem」。

Invent and Simplify：纠错时先问能否删掉一条会漂的特征，而不是再加一个校正模型。复杂校正叠在错的特征上，Ownership 会变成永远 oncall。

## 追问

- **Bias for Action 和门禁冲突怎么办？** 行动的对象是可逆实验和影子，不是跳过护栏。没数据时用小流量，不是用全站。
- **业务逼你用更激进的客户数据？** Earn Trust 优先。给一条最小特征和一条带 PII 的对照，用同样的离线增益证明不需要原文；仍要原文就升级审批和留存。有 Backbone 不等于情绪对抗。
- **回滚算不算 Deliver Results 失败？** 不算。保护客户是结果。失败是发现问题还继续放量。Bar Raiser 想听你回滚得有多快、事后门禁改了哪一条。
- **技术轮也问 LP 怎么办？** 把门禁、数据、回滚嵌进系统设计，不要最后五分钟另讲一个 STAR。评委听的是你会不会用原则做取舍。
