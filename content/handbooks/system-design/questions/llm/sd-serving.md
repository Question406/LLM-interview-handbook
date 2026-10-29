---
id: sd-serving
section: llm
order: 25
level: A
title: LLM 推理服务：排队、KV、流式输出与取消
quick: >-
  假设长请求正在读取大量输入，同时已有用户还在等待下一个输出 token。服务需要管理排队、prefill、decode 和各请求的
  KV，而不是把每条请求独立丢给 GPU。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: vLLM：PagedAttention 原论文
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
  - title: Google SRE Book：Handling Overload
    url: 'https://sre.google/sre-book/handling-overload/'
    type: primary
---

## 题目描述

设计共享 LLM 推理服务，支持流式聊天与后台批任务。手册练习中输入可长短不一，生成长度有上限，需要租户配额、超时和取消。请输出网关、准入、调度、模型副本与 KV 管理架构，定义首 token 延迟、生成间隔和计费语义，说明模型重启、客户端断线与长请求挤占。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 假设长请求正在读取大量输入，同时已有用户还在等待下一个输出 token。
>
> **做法与原因：** 我会先跟踪一条请求：准入后排队，处理输入，分配 KV，逐步生成，再在结束或取消时释放状态。
>
> **检查与取舍：** 验证时同时看首个 token、后续 token 间隔和 throughput，并测试取消、OOM 和慢请求。

## 可以这样回答

假设长请求正在读取大量输入，同时已有用户还在等待下一个输出 token。服务需要管理排队、prefill、decode 和各请求的 KV，而不是把每条请求独立丢给 GPU。

我会先跟踪一条请求：准入后排队，处理输入，分配 KV，逐步生成，再在结束或取消时释放状态。Batching 可以提高利用率，但过多等待或过大的 batch 也会增加用户 latency。

验证时同时看首个 token、后续 token 间隔和 throughput，并测试取消、OOM 和慢请求。只有 throughput 数字，没有用户等待和资源释放的行为，还不足以说明服务可用。

## 技术备查

## 参考答案与设计讨论

将租户配额和资源准入放在执行前，按 token 与 KV 评估负载；流式生成需要处理取消、重试和公平性。

![LLM 推理服务：排队、KV、流式输出与取消：核心数据流](/system-design/serving.svg)

图展示核心数据流；权限、状态和故障恢复以正文约定为准。

### 不要只看请求 QPS

短问答与超长上下文占用的 prefill 计算、KV 和 decode 时间不同。入口校验上下文与最大生成长度，按资源估算准入，实时队列与批任务设置有界预算。监控 TTFT、生成间隔、总时延、throughput 与排队时间，不拿其中一个替代全部。

### 执行和缓存

引擎可以按迭代组合活跃请求，KV 按页管理。前缀缓存键要反映 token 序列、模型权重、位置语义与 adapter 等兼容条件；共享前缀也要遵守租户数据策略。会话转移到新副本可能要重算 prefill 或迁移状态。

### 失败、重试与计费

流已输出一半时不能无条件透明重试并拼接两段不兼容文本。用请求标识跟踪尝试，定义断线是继续还是取消；取消要从调度器摘掉并释放 KV。计费基于可审计执行记录去重，不能把 HTTP 重试直接当新的收费业务。

### 示例与关联

一条长批任务不应让短聊天无限等待；KV 水位过高时应拒绝或受控降级，不能继续接入直到 OOM。详见[ChatGPT 类服务](?book=us-tech&section=design&question=design-chat-serving)和[版本、灰度与回滚](?book=us-tech&section=design&question=design-prompt-mgmt)。

