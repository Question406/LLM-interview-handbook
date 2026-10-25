---
id: jd-jmeter-params
section: systems
order: 191
level: B
title: 京东 Agent 二面：JMeter 压测参数具体怎么设？
quick: "我会先明确压测哪一层、目标 QPS 和成功标准，再设线程数、ramp-up、持续时间和断言。线程数可以用目标 QPS 乘平均整轮时延估算；Agent 还要分别记录首 token、整轮和工具耗时，并统计错误、限流与超时。"
tags:
  - JD
  - JMeter
  - Load Test
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 27暑期实习-京东Agent开发二面分享
    url: https://www.nowcoder.com/feed/main/detail/6af1c8611e434bbe8ba9cfa2bd0eaf18
    type: candidate-first-hand
  - title: Apache JMeter User Manual
    url: https://jmeter.apache.org/usermanual/test_plan.html
    type: primary
---

## 真题记录

- 公司：京东
- 团队 / 岗位：Agent 开发
- 届别 / 流程：27 暑期实习；二面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“JMeter 压测的具体参数是怎么设置的？”**

我会先说清压的是网关、编排层还是模型服务，再定目标 QPS、延迟和成功标准，最后填 JMeter 参数。这样每个参数都有理由，测出来的曲线也能指向具体组件。

Agent 的一次请求可能先流式返回 token，再等待工具，最后才结束。首 token 很快、整轮很慢是完全可能的，所以要分别记录首包、整轮和工具耗时，再配合错误率和限流比例看容量。平均响应时间会掩盖 p99 和 5xx。

## 先定目标再填线程

数字假设要开口说。例如：目标 50 QPS、错误率 $\lt 1\%$、网关 p95 $\lt 800\,\mathrm{ms}$、首 token p95 $\lt 1.5\,\mathrm{s}$、整轮 p95 $\lt 8\,\mathrm{s}$。没有这组数，后面的线程数没有锚。

线程约等于目标并发：若平均整轮 4 s、要 50 QPS，粗算并发 $\approx 50\times 4=200$（Little's law）。Thread Group 的 Number of Threads 对这个量级，不是随便填 1000。Ramp-up 拉 1-2 分钟，避免启动尖峰被当成容量上限。Scheduler 持续时间至少覆盖预热（模型 CUDA graph、连接池、缓存变热）和一段稳态；过短只测到冷启动。Loop 用「持续 $T$ 秒」而不是固定 10 次，否则长尾请求还没回来测试就停了。

## 检查业务成功，并拆开各层耗时

HTTP 200 不够：要 JSON 业务码、必填字段、工具是否超时。流式接口分别打时间戳：首 token、工具往返、最终包。Sampler 超时必须大于工具 SLA，否则 JMeter 自己掐断，模型侧还在跑，错误率被测歪。

流量要切片：只压检索、只压模型、整条 Agent 分开报。混在一起优化会指错组件。参数化用 CSV 多样化 query，避免同一输入提示 把 prefix cache 打满、QPS 虚高。连接：HTTP Keep-Alive、连接池大小和网关限流对齐；压测机本身不要先成为瓶颈（单机线程过多、带宽不够就加 slave）。

限流触发率要单独报：被 429 的比例不是「成功」，也不是纯粹失败，是容量边界。和线上一致的超时 / 熔断配置才有意义；压测环境把 timeout 开到 60 s，线上 8 s 掐断，数字不可比。



报告里要有 QPS、错误率、p50/p95/p99、首 token、整轮、限流比和超时比，才能看清吞吐与长尾。Agent 还要报工具失败是否被编排吞掉（看起来 200、其实没调成）。对比优化前后必须同脚本、同数据、同预热。说清压的是哪一层：网关、编排、vLLM/SGLang、还是 Redis。工具用录制回放、模型走真实 serving，避免使下游过载又测不到超时。本手册超时空返回卡负责「失败怎么对用户说」，本题负责「参数怎么设才测得到那个失败」。

## 追问

**线程数怎么来的？**
目标 QPS $\times$ 平均整轮时延（Little's law），再加余量。ramp-up 避免启动尖峰被当成容量上限。不要背「通常 200 线程」。整轮变长时要重算线程，否则实际 QPS 达不到目标。
**为什么要分首 token 和整轮？**
用户体感在首包，GPU 成本和工具超时在整轮。只报平均 RT 会把流式体验和好坏工具混在一起。两个百分位都要，再加错误率和 429。
**断言只查 200 行不行？**
不行。Agent 常 HTTP 200 但业务码失败、字段空、工具超时被编排吞掉。断言要落到 JSON 和必填字段，否则压测在报成功、线上在报空答。
**压多久？**
覆盖 CUDA graph / 连接池预热，再跑到 KV 池和缓存变热甚至变冷。几分钟打满平均没有意义，长尾和限流要在稳态里出现。
**JMeter 适合压 LLM 吗？**
适合压网关和编排 QPS。模型侧更常用专用 serving 压测，把并发、输入长度、输出长度分开扫。要说明压的是哪一层，混在一起的平均值很难指导优化。
