---
id: drustz-dc39086ad9e4d077d7
section: openai
order: 176
level: A
title: Designing Scalable Enterprise Chat System Like Slack
quick: >-
  original-structured-preparation-guide · Designing Scalable Enterprise Chat
  System Like Slack
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/dc3b2441-88b4-4b0d-90ae-da62b123262f
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 企业级 Slack：租户、权限与消息扩展

> 内容定位：Slack 题族和实时扩展追问有本地面经佐证；“enterprise”带来的租户隔离、审计与保留策略则主要依据当前公开标题补全。以下是原创系统设计准备，不表示会员原文一定要求全部功能。

## 题目要做什么

设计多租户企业聊天平台：workspace 内有公开/私有频道和 DM，支持实时收发、历史搜索、多设备、离线通知，并让企业管理员配置成员、权限、数据保留与审计导出。首轮先完成消息主链路，再选择一个组件深入。

## 数据或需求

所有资源都带 `tenant_id`，授权不能只在客户端检查。单频道消息按序，发送重试不重复落库；普通用户不能通过搜索、缓存 key 或对象存储 URL 读到其他租户数据。可设 99.99% 发送可用性、p99 实时延迟 500ms，并明确搜索索引允许秒级最终一致。

## 例子

员工从手机和电脑同时在线，在私有频道收到消息后用电脑读完。系统应推进用户级 read cursor、取消尚未发送的离线 push，但仍保留两个设备各自的连接确认位置。员工随后被移出频道，新请求必须立即拒绝；异步搜索索引也要过滤旧权限。

## 解法

数据面采用 gateway、message service、按 conversation 分区的 append-only log、消息数据库和 event bus。控制面管理 tenant、成员、频道 ACL、保留策略和加密密钥。发消息时先鉴权和幂等检查，再落日志并发布；DM/小频道用 push，大频道用共享日志加 pull，以避免百万级写扩散。

```text
AuthN -> tenant-aware AuthZ -> message log -> event bus
                                   |-> realtime delivery
                                   |-> search index
                                   |-> notification
                                   `-> audit/retention jobs
```



数据库主键从 `(conversation_id, seq)` 扩为 `(tenant_id, conversation_id, seq)`，缓存与队列 topic 同样包含租户。搜索文档保存 ACL version，查询时既做索引过滤，也在返回前二次鉴权。删除策略分软删除、法务保留和物理清除；审计日志独立、不可由普通用户修改。大客户可使用独立分片或加密 key，避免 noisy neighbor。

## 复杂度

单条消息持久写近似 `O(1)`；小频道 fan-out 为 `O(M)`，大频道共享写为 `O(1)`、分页读为 `O(K)`。搜索索引与消息量线性增长；ACL 逐成员检查会是 `O(M)`，应使用角色/组和版本化缓存降低热路径成本。

## 边界与验证

- 成员被移除与正在发送的消息存在竞态，要定义授权线性化点；
- 缓存 key 漏 `tenant_id` 是严重越权漏洞；
- 搜索、导出和通知都必须执行同样权限；
- 热门频道不能拖垮同分片其他租户；
- 合规删除与备份恢复的语义应提前说明。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/dc3b2441-88b4-4b0d-90ae-da62b123262f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
