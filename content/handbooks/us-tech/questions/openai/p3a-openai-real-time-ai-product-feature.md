---
id: p3a-openai-real-time-ai-product-feature
section: openai
order: 635
level: A
title: "OpenAI：实时 AI 产品：流式响应、准入与成本"
quick: "实时 AI 服务先按 token 成本做准入，再用有界队列和流式输出控制等待；分别测排队、TTFT 和完整响应时延。请求记录与事件流分开保存，支持按序号续传、幂等重试和取消。流量涨十倍时先限成本、减输出或降级，再按实测 token 吞吐扩 GPU。"
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
  - title: "1Point3Acres · OpenAI · real-time-ai-product-feature"
    url: https://www.1point3acres.com/interview/problems/company/openai/real-time-ai-product-feature
    type: secondary
---

我会先按 token 成本做准入，控制队列长度，再把生成结果持续流给用户。延迟要拆成排队、首 token（TTFT）和完整响应来看；输出 4000 token 与 50 token 的请求消耗差很多，QPS 无法单独反映 GPU 压力。

题目是面向大量用户的实时或流式 AI 功能，并追问流量变十倍。练习用写作助手举例：峰值 1000 请求/秒，平均输出 1000 token，首 token P95 &lt;1 秒，支持取消。开始确认用户等级，以及是否允许降级到小模型。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

客户端用 SSE 发起请求，鉴权和准入层根据 token 预算决定接收、排队或拒绝；接收后进入有界队列，再由模型路由交给 serving 集群。请求创建记录和生成事件流分开存，客户端凭 request id 和事件序号断线续传。

Request 记录用户、参数快照、token 预算、状态和已计费用量。状态从 accepted、queued、running 到 completed / cancelled / failed，部分输出要标成未完成。用户点“润色”时，客户端带幂等键请求；准入层扣减用户和全局预估预算，入队后开始生成，每个 token 带递增序号推送，第一个到达时记录 TTFT。结束后按实际用量计费并记 completed。

队列超出预算就拒绝，或告诉用户预计等待时间。用户取消要传到模型侧，及时回收 KV cache。断线重连按序号去重，同一个幂等键不能静默创建一次新生成；客户端也要区分尚未输出的失败与已经部分输出的失败。

容量需求是 1000 × 1000，即每秒 100 万输出 token，GPU 数要用目标模型每卡实测吞吐换算。定位时一起看 token 吞吐、队列长度和 GPU 饱和度，监控 TTFT、TPOT、排队时延及取消后浪费的 token。

## 追问

**流量变成十倍怎么办？**
先按用户和成本限流，降低输出预算或换小模型，然后再扩 GPU。无界队列会把当前过载拖成长超时。

**生成到一半断网，回来看到什么？**
带 request id 和最后序号重连，有事件流就断点续传。若生成已经因断开取消，展示已收部分并标为未完成，让用户决定是否重新生成。
