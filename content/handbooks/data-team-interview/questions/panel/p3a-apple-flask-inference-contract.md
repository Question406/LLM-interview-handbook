---
id: p3a-apple-flask-inference-contract
section: panel
order: 81
level: A
title: 一亩三分地 Apple AIML Infra：模型推理 Flask API，先把什么契约定义清楚？
quick: >-
  将 HTTP
  校验、预处理、模型推理和输出序列化分开，模型随进程启动加载并固定版本。先验证输入与离线结果一致，再检查超时、并发和资源；返回200不代表模型真正算对，也不能每次请求重新加载权重。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - AFM 专项 2026-10
  - 一亩三分地
  - Model Serving
  - Flask
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-26T00:00:00.000Z
sources:
  - title: 苹果AIML infra engr全套（候选人原帖）
    url: 'https://www.1point3acres.com/bbs/thread-1149108-1-1.html'
    type: interview
  - title: Flask — Testing applications
    url: 'https://flask.palletsprojects.com/en/stable/testing/'
    type: primary
  - title: Flask API
    url: 'https://flask.palletsprojects.com/en/stable/api/'
    type: primary
---

## 题目描述

**source attribution 与适用范围：**2026-10-26 经 Chrome 核对，原帖发布于 2025-10-07 14:14:15。Apple AIML Infra 候选人报告现场要求写 Flask API 部署模型推理，但没有披露模型类型、端点、输入 shape、并发指标或测例。该轮原本是实现题；本卡将其转为接口与测试设计练习，不声称拥有原始代码，也不称为 AFM 团队题。

**手册扩展约定：**已有 CPU 文本质量分类器和对应 tokenizer，输入为一批公开文档文本，输出每条“可保留”的概率。设计 `POST /predict`：请求包含非空 texts 字符串数组，每批最多 32 条，每条最多 4,000 个字符；成功时返回顺序对齐的 scores 与 model_version。超限或类型不符应得到明确错误，模型异常不能伪装成正常分数。规模和 schema 均为练习约定。

请说明请求契约、模型生命周期、离线一致性、test assumptions 与 deployment constraints。建议先用 5 分钟定义契约，再用 20 分钟设计，最后 10 分钟追问。

## 解题思路与参考答案

先把接口转换成可测试的行为。明确是单条还是批量、是否允许空文本、长度按字符还是 token 计量，以及错误如何区分。这里按题目限制字符数量，但进入模型前仍需检查分词后的实际 token 长度，不能把字符上限当成显存或上下文上限。

### 四层结构与模型生命周期

HTTP 层负责 Content-Type、JSON 结构与状态码；预处理层使用与训练一致的分词、截断与 normalization；推理层接收 tensor 并返回对应分数；序列化层把结果变成 JSON 可表示的 Python 数值，并保留输入顺序。

每个服务进程启动时加载一次固定模型与 tokenizer，初始化失败就不应通过就绪检查。若使用 PyTorch，应切换 eval 模式，并在 inference 时关闭 gradient 记录；这两项作用不同，不能互相替代。不要在每个请求里下载或重建模型。服务多个进程时，每进程可能各有一份权重，需要评估内存，不能只按单进程估算。

### 错误、并发和状态

请求格式不合法与模型内部异常分开处理，不把异常字符串或输入全文直接返回或写入日志。只记录诊断必需的版本、耗时、批量大小和错误类别；某批失败是整体失败还是允许部分成功，必须事先声明。本题采用整批成功或整批错误，避免输出与输入错位。

批处理能提高 throughput，但动态组批引入等待时间。先测单条与批量延迟，再决定队列长度和并发上限，避免无限排队或多个请求争用同一模型状态。HTTP 重试也会占用推理资源，即使预测没有写入副作用，也需要请求标识和负载治理。

### 怎么测试确实正确

先用固定 small model 或替身函数测试协议：传两条文本，检查返回顺序、分数数量、model_version 与类型。再在加载真实模型后，用固定输入比较离线分数和服务分数，在合理数值容差内一致；检查是否意外改变了截断、padding 或阈值。

Flask 的 test client 可在不启动真实网络服务的情况下测试请求、JSON 响应和状态码。edge cases 包括空 batch、32 条与 33 条、单条长度恰好上限与超限、非字符串元素、无效 JSON，以及模型抛错。最后用独立负载测试验证峰值内存、p95 延迟与失败率；单元测试不能证明服务容量。

## 面试追问

**API 返回200就能交付吗？** 不够。需要检查概率值合法、条数与顺序匹配、模型版本正确，以及与离线推理一致。特别容易漏掉框架 Tensor 到 JSON 的类型转换。

**健康检查和就绪检查一样吗？** 不一样。进程能应答不代表模型权重加载成功或依赖可用；就绪应反映是否能接收真实推理任务。

**Flask 开发服务器能直接承担生产负载吗？** 应使用合适的生产 WSGI 服务与部署配置，先明确进程、线程和模型资源关系；开发环境中跑通接口不能替代部署验证。

**这题怎样服务数据岗准备？** 数据过滤与合成验证往往要被其他流水线调用；明确 batch、版本、分数语义与错误契约，能避免 data pipeline 把推理失败误判成低质量样本。
