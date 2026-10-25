---
id: p3a-perplexity-durable-long-running-agentic-query-execution
section: design
order: 613
level: A
title: "Perplexity：长任务 Agent：数小时执行、断线续跑与进度流"
quick: "把 job、步骤、工具结果和进度事件写入持久存储，让 worker 用租约领取步骤并提交检查点。浏览器只是订阅进度，断线后任务继续；worker 故障由其他 worker 接手，副作用靠幂等键和 epoch 防止重复。"
companies:
  - ai-labs
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · durable-long-running-agentic-query-execution"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/durable-long-running-agentic-query-execution
    type: secondary
---

## 题目

现有的 ask 服务把任务状态放在内存里，浏览器一断开任务就丢了。要求把它改造成持久执行：一个复杂查询可能跑几个小时，用户关掉浏览器后任务照常完成，重新打开时还能看到进度。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），属于网站对候选人报告的二手整理，没有逐条核对原帖，网站收录也不代表公司官方确认；规模数字、SLO 和故障情景是手册补的练习约定。


## 思路与执行过程

我会把任务生命周期从浏览器连接中独立出来。job、步骤和工具结果都写入持久存储，worker 用租约取得执行权，每完成一个阶段就提交检查点。这样任务跑几个小时、用户关掉页面，任务仍然继续；worker 崩溃后，其他 worker 等租约过期，再从最近检查点接手。

先确认任务能否暂停恢复、工具有没有不可撤销副作用，以及单个任务的成本上限。搜索、LLM 和工具都当外部黑盒。提交请求时创建持久 job，返回 job id，再把工作拆成步骤 DAG，由带租约的 worker 领取可执行步骤，通过工具适配器执行。每次进展追加 append-only 事件，浏览器用 SSE 订阅，断线重连带游标继续读取。

数据可以分为 job(id, user, `params_hash`, state, epoch)、step(id, inputs, `tool_call_id`, attempt, `result_ref`)、event(seq, type, body)。`tool_call_id` 保持稳定，作为有副作用调用的幂等键。取消和重试也是需要持久化的状态变化，不能只改内存标记。

比如用户提交“比较三家云厂商的 GPU 价格”，系统写入 running 的 job 并返回 id。worker W1 领取租约，先生成搜索计划，结果写到 `result_ref`，追加 seq=1。三个搜索步骤并行完成，追加 seq=2、3、4。用户此时关浏览器，W1 继续汇总报告，完成后 job 变成 done，追加 seq=5。第二天用户带 `last_seq`=0 重连，就能补齐事件并显示报告。

worker 如果在工具执行后、提交结果前崩溃，这一步可能重做，所以发邮件、下单等外部副作用必须由幂等接口保护，不支持幂等的要人工协调。客户端按 `last_seq` 补事件，重复片段自行去重。取消时持久化 cancelled，阻止新步骤调度。

验证时看恢复时间、重复副作用次数、最长未推进 job、事件滞后与每个 job 的成本。每一步还要记 token 和工具预算，异常循环触发终止。

## 追问

**代码升级时，正在跑的任务怎么办？**
让 job 固定使用提交时的 workflow 版本。新 worker 要能读旧状态；不兼容时做迁移，或者保留旧 worker 池直到旧任务完成，避免新代码重新解释旧检查点。

**旧 worker 网络恢复后，会不会和接手者同时执行？**
可能。所以 job 上要有 epoch 做 fencing：新 worker 接手先递增 epoch，状态库只接受当前 epoch 的结果提交。旧 worker 的写入会被拒绝，它已发出的外部调用仍由幂等键挡住重复效果。
