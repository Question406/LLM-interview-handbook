---
id: sd-search-crawler
section: general
order: 18
level: A
title: 设计搜索与爬虫：抓取、索引和更新
quick: 抓取按域调度，内容与 URL 分别去重；索引异步构建并带版本发布，查询只读取完整可用的索引版本。
companies: []
tags:
  - System Design
  - 设计练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-25T00:00:00.000Z
sources:
  - title: Designing Data-Intensive Applications：作者资料
    url: 'https://dataintensive.net/'
    type: primary
  - title: Google SRE Book：Handling Overload
    url: 'https://sre.google/sre-book/handling-overload/'
    type: primary
---

## 题目描述

设计面向指定网站集合的搜索服务：从种子 URL 抓取公开页面，建立关键词索引，支持更新与删除。手册练习假设每天抓1000万页，允许分钟级索引新鲜度，不抓登录后内容。请输出 frontier、抓取流水线、索引发布、查询排序与缓存架构，说明礼貌限速、重定向、重复内容和 worker 故障。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 参考答案与设计讨论

抓取按域调度，内容与 URL 分别去重；索引异步构建并带版本发布，查询只读取完整可用的索引版本。

### 抓取调度不是普通队列

URL frontier 按域分组，统一管理抓取间隔、robots 规则与并发。下载、解析、链接发现和存储各自扩容。URL 规范化只能删除明确不会改变内容语义的部分，不能把所有查询参数都去掉。重定向后重新校验域和目标地址。

### 索引与查询

页面元数据保存抓取时间、状态、内容摘要与版本；URL 去重和内容去重独立。解析后的文档进入倒排索引，分段构建并原子切换可见版本。查询先做词项召回，再打分与权限/删除过滤；网页可能已删除时缓存也要逐步失效。

### 故障与容量

抓取任务用租约恢复，重复下载可以接受但索引更新按文档与版本幂等。慢域单独限流，不让它阻塞全局队列。按页面实际压缩大小、索引放大和保留历史估存储，不用网页条数直接估内存。

### 示例与追问

两个 URL 指向相同正文，只存内容的一份副本并保留两个映射；同一 URL 更新后新版本替代旧索引。新索引构建失败时继续服务旧完整版本。关联：[Microsoft 爬虫摘要](?book=us-tech&section=microsoft&question=p3a-microsoft-web-crawler-system-design)。

