---
id: p3a-openai-design-url-shortener
section: openai
order: 646
level: A
title: "OpenAI：短链接：生成、重定向、缓存和扩展"
quick: "短码可以由唯一 id 编码，也可以随机生成并检测碰撞；跳转先查缓存，再查持久映射。先约定过期、禁用和目标修改规则，才能确定缓存失效与 301 / 302 的语义。"
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
  - title: "1Point3Acres · OpenAI · design-url-shortener"
    url: https://www.1point3acres.com/interview/problems/company/openai/design-url-shortener
    type: secondary
---

## 题目

设计一个短链服务：把长 URL 转成短码，并提供可靠的重定向。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。

短链用持久映射保存 code 到长 URL 的关系，跳转先查缓存再回源。短码可以编码全局唯一 id，也可以随机生成后检测碰撞；选择前先确认自定义 alias、过期和目标修改的需求。

练习支持创建、跳转、过期和可选自定义 alias，写读比假设 1:100，跳转 P99 &lt;50ms。开场再确认点击统计和链接修改是否在范围内。

写路径由创建 API 生成唯一 id 或随机短码，再写数据库。读路径经过本地缓存、共享缓存，最后回源。比如用户提交长 URL，服务把下一个唯一 id 编成 7 位短码，写入 mapping 后返回。第一次点击两级缓存都未命中，数据库确认没过期、没禁用，网关写回缓存并返回 302 和 `long_url`；之后点击即可命中缓存。点击分析异步发送，不阻塞跳转。

数据模型可以是 `mapping(code, long_url, owner, expires_at, status, version)`。自定义 code 用唯一约束防重复，随机碰撞就重试或改用唯一 id。禁用状态参与缓存版本，禁用时主动撤回热点缓存；命中缓存也要检查过期。热点需防缓存击穿，并预留滥用处理接口，数据库慢时不能给未知 code 返回任意默认 URL。

一亿次日跳转平均约 1157 次/秒，峰值另作假设。按热点分布估缓存容量，监控命中率、回源量和恶意重定向。

## 追问

**用 301 还是 302？**
目标可修改时用 302 或短期缓存；永远不变可以用 301，但浏览器缓存后很难撤回，要和产品契约一致。

**自增 id 会让别人枚举短链吗？**
会。需要一定私密性时，可以先对 id 可逆混淆再编码，或用足够长的随机码，并承担碰撞检测成本。
