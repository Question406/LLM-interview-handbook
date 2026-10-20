---
id: p3a-openai-webhook-delivery-system
section: openai
order: 647
level: A
title: "OpenAI：Webhook：十亿日事件与至少一次投递"
quick: "webhook 投递用持久队列记录每个事件对每个目标的投递状态，失败按指数退避加抖动重试，并给每个目标设并发上限隔离坏接收端。"
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

## 题目

设计一个 webhook 投递系统：租户注册回调 URL，系统可靠地把事件投递过去，处理重试，并隔离失败的接收端。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

持久队列保存事件本身和"每个事件对每个目标"的投递状态。失败按指数退避加抖动重试；每个目标有并发上限，这样一个慢接收端不会拖累所有租户。

投递语义是至少一次，接收端靠事件 id 去重。超过重试上限的进入死信。另外要讲清楚三项安全措施：请求签名、防重放和目标地址校验。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

每天十亿个事件，每个事件可能有多个目标，至少一次投递，重试最长 24 小时。租户注册回调地址，并要求校验签名。

开始回答时复述这些范围，问面试官是否需要保证同一目标的事件顺序。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. 事件进入入口，写入持久日志。
2. 为每个目标生成 delivery，放进按租户和目标分区的投递队列。
3. 带限额的 worker 发起外部 HTTP 请求。

死信队列和重放工具独立部署。

**2. 数据模型和状态变化。**

- `event(id, type, version, payload)`
- `delivery(event_id, endpoint_version, attempt, next_at, status)`
- `endpoint(url, secret_version, rate)`

幂等键是"事件 + 目标"。

**3. 走一遍一次投递。** 租户的订单系统产生 `order.paid` 事件，写入日志后，系统发现这个租户注册了两个 endpoint，于是生成两条 delivery。worker 取到第一条，用当前 `secret_version` 对时间戳和 body 签名，带上事件 id 发 POST；对方返回 200，delivery 标记为成功。第二个 endpoint 返回 503，这条 delivery 的 attempt 加一，`next_at` 设为退避加抖动之后的时间，等待下一轮。

**4. 失败、重复与恢复。**

- 超时属于结果未知，仍然重试；接收方按事件 id 去重。
- 退避加抖动；单个 endpoint 持续失败就熔断，隔离开。
- 签名覆盖时间戳和 body；endpoint 变更后，要明确旧 delivery 用哪个版本的地址和密钥。

**5. 容量和验证指标。** 十亿除以 86400 约为每秒 11574 个事件，还要乘以平均 fanout 和重试放大系数。监控投递延迟、积压中最老消息的年龄、失败 endpoint 比例和重试成本。

### 面试追问与参考回答

**怎样防止有人把回调地址指向内网？** 注册时和每次跟随重定向时都要校验最终访问的目标，拒绝内部地址。不能只在注册时检查一次字符串就允许任意跳转。

**一个 endpoint 宕机一整天，会不会拖慢别人？** 不会。它的 delivery 在自己的分区里排队，熔断后 worker 只按低频探测它，其他租户的分区照常消费。24 小时后仍未成功的 delivery 进入死信，租户修好后可以用重放工具补投。
