---
id: p3a-perplexity-durable-long-running-agentic-query-execution
section: design
order: 613
level: A
title: "Perplexity：长任务 Agent：数小时执行、断线续跑与进度流"
quick: "把任务、步骤和工具结果都持久化，worker 用租约取得执行权，每完成一个阶段就提交检查点，浏览器断开也不影响任务继续。"
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

## 思路

任务的生命周期不能再绑定在连接上。任务本身、它的每一个步骤以及工具调用结果都要写进持久存储；worker 通过租约获得某个任务的执行权，每完成一个阶段就提交一次检查点。worker 崩溃后，租约过期，别的 worker 可以从最近的检查点接着跑。

客户端通过一个进度事件日志来看进度，断开重连时带上游标，从上次看到的位置继续读。

工具调用可能有外部副作用（发邮件、下单），重试时要用幂等键防止重复执行。取消和重试本身也是状态变化，必须落到持久存储里，而不能只在内存里打个标记。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

练习设定：用户提交复杂问题，任务可以执行数小时；关闭浏览器后继续执行，重新连接时显示进度。工具、搜索和 LLM 都当作外部黑盒。

开场可以问：任务是否允许暂停和恢复，工具里有没有不可撤销的副作用，以及单个任务的成本上限。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. 用户提交后，立即创建一条持久 job 记录并返回 job id。
2. job 拆成步骤 DAG，状态存在状态库里。
3. 带租约的 worker 领取可执行的步骤。
4. 步骤通过工具适配器调用外部搜索、LLM 等。
5. 每个进展追加一条进度事件（append-only）。

浏览器通过 SSE 订阅进度事件，只是观察者，任务是否存活与它无关。

**2. 数据模型和状态变化。** job(id, user, `params_hash`, state, epoch)；step(id, inputs, `tool_call_id`, attempt, `result_ref`)；event(seq, type, body)。有副作用的工具调用使用稳定的 `tool_call_id` 作为幂等键。

**3. 追踪一次正常执行。** 用户提交“比较三家云厂商的 GPU 价格”，系统写入 job，state 为 running，返回 job id。worker W1 拿到租约，执行第一步“生成搜索计划”，结果写入 `result_ref`，追加事件 seq=1。接着三个搜索步骤并行执行，各自完成后追加 seq=2、3、4。用户此时关掉了浏览器，但 W1 继续工作。最后一步汇总生成报告，job 变为 done，追加 seq=5。用户第二天打开页面，客户端带 `last_seq`=0 重连，一次性补齐全部事件并显示最终报告。

**4. 失败、重复与恢复。** worker 在调用工具之后、提交结果之前崩溃，这一步可能会被重做；所以外部工具要支持幂等，不支持的就要人工协调。重连时客户端按 `last_seq` 补事件，重复的片段由客户端去重。取消时把 job 状态持久化为 cancelled，并阻止调度新步骤。

**5. 容量和验证指标。** 衡量恢复时间、重复副作用次数、最长未推进的 job、进度事件的滞后，以及单个 job 的成本。每一步记录 token 和工具调用预算，出现异常循环时触发终止。

### 面试追问与参考回答

**执行代码升级时，正在跑的任务怎么办？** 进行中的 job 固定使用提交时的 workflow 版本，新 worker 必须能读懂旧版本的状态。如果新旧不兼容，要么写迁移，要么保留旧版本的 worker 池直到旧任务跑完。不能让新代码盲目重新解释旧的检查点。

**worker 只是网络卡了一下，租约过期后又恢复了，会不会两个 worker 同时执行同一步？** 会有这个风险，所以靠 job 上的 epoch 做 fencing。新 worker 接手时 epoch 加一，提交结果时带上自己的 epoch，状态库只接受当前 epoch 的写入。旧 worker 恢复后提交会被拒绝，它发出的外部调用则由幂等键挡住重复效果。
