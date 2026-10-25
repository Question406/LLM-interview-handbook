---
id: p3a-openai-webhook-delivery-system
section: openai
order: 647
level: A
title: "OpenAI：Webhook：十亿日事件与至少一次投递"
quick: "事件先写持久日志，再为每个目标分别记录 delivery 状态，按租户和目标分区投递。失败按指数退避加抖动重试，并用每目标并发上限与熔断隔离慢接收端。承诺至少一次，接收方按事件 id 去重；重试到期进死信，还要校验地址、签名和防重放。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · webhook-delivery-system"
    url: https://www.1point3acres.com/interview/problems/company/openai/webhook-delivery-system
    type: secondary
---

我会把事件和每个目标的 delivery 状态持久化，按租户与目标分区，由有限额的 worker 发送。投递承诺至少一次：超时可能是对方已经处理但响应丢了，所以仍要重试，接收方按事件 id 去重。

题目是租户注册回调 URL，系统可靠投递事件、处理重试并隔离失败接收端。练习假设每天十亿事件、每个事件可发多个目标、最长重试 24 小时，签名要可校验。开始确认同一目标是否要求事件有序。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

事件入口先写持久日志，再为各目标生成 delivery，放入按租户和目标分区的队列。Worker 带着并发和速率限额发外部 HTTP 请求，死信队列与重放工具独立部署。数据可以用 `event(id, type, version, payload)`、`delivery(event_id, endpoint_version, attempt, next_at, status)` 和 `endpoint(url, secret_version, rate)` 表示，幂等键为“事件 + 目标”。

比如订单系统产生 `order.paid`，日志落盘后发现租户有两个 endpoint，就生成两条 delivery。第一条用 `secret_version` 对时间戳和 body 签名，带事件 id 发 POST，收到 200 后记成功。第二个目标返回 503，就增加 attempt，把 `next_at` 设到指数退避加抖动后的时间，等待下一轮。

单个目标持续失败时熔断、低频探测，防止它占满 worker。超时仍按结果未知重试，重复由接收方消除。签名必须覆盖时间戳和 body 来防篡改与重放；endpoint 变更时明确旧 delivery 用哪个地址和密钥版本，还要校验实际访问目标，避免访问内网。

十亿除以 86400 约为每秒 11574 个事件，再乘平均 fanout 与重试放大系数才是投递压力。验证时看投递延迟、最老积压年龄、失败 endpoint 比例和重试成本。

## 追问

**怎样防止回调地址指向内网？**
注册时和每次跟随重定向时都校验最终目标，拒绝内部地址。只在注册时检查字符串，挡不住后续跳转。

**一个 endpoint 宕机一天，会拖慢别人吗？**
它的 delivery 留在自己的分区，熔断后只低频探测，其他租户照常消费。24 小时后仍失败就进死信，租户修好后用重放工具补投。
