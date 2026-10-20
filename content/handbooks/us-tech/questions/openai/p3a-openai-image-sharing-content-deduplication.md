---
id: p3a-openai-image-sharing-content-deduplication
section: openai
order: 639
level: A
title: "OpenAI：图片共享：内容哈希去重与删除生命周期"
quick: "把逻辑图片记录和内容 blob 分开存，用内容哈希定位 blob，并靠引用关系决定 blob 什么时候可以删除。"
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
  - title: "1Point3Acres · OpenAI · image-sharing-content-deduplication"
    url: https://www.1point3acres.com/interview/problems/company/openai/image-sharing-content-deduplication
    type: secondary
---

## 题目

设计一个图片分享服务，支持上传、查看、下载和删除。要求完全相同的字节内容只存一份。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

关键是把"用户的一张图片"（逻辑记录）和"一份字节内容"（blob）分开。不同用户上传同样的字节，各自有自己的 asset 记录、文件名和权限，但都指向同一个按内容哈希定位的 blob。

blob 能不能删，由引用关系决定：删除一个用户的引用，不能删掉别人仍在引用的 blob。并发上传同一内容时用条件写入去重；数据库和对象存储之间的失败，需要补偿和后台修复来兜底。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

用户上传图片、分享和删除；字节完全相同的文件只存一份。逻辑图片可以有不同的文件名和权限。不要求视觉近似去重。

开始回答时复述这些范围，问面试官是否需要缩略图、是否有存储配额。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. 上传服务先把文件写成临时 blob，同时计算 SHA256。
2. 以哈希为键条件创建 content 对象；已存在就复用。
3. 在数据库事务里创建 asset 引用。

下载时先按 asset 做授权，再生成短期 URL，经 CDN 下发。

**2. 数据模型和状态变化。**

- `content(hash, size, blob, state)`
- `asset(id, owner, content_hash, acl, deleted_at)`

引用表是真相来源，引用计数只是可修复的缓存。

**3. 走一遍重复上传。** 用户 A 上传 `cat.jpg`，服务算出哈希 h，content 表里没有 h，于是把临时 blob 转正并创建 content(h)，再创建 A 的 asset。之后用户 B 上传同一份字节、文件名叫 `kitty.jpg`：哈希同样是 h，条件创建发现已存在，B 的临时 blob 被丢弃，只新建一条指向 h 的 asset。两人各自看到自己的文件名和权限，存储里只有一份字节。

**4. 失败、重复与恢复。**

- 并发上传同一哈希时，靠条件写或唯一约束收敛到一个 content。
- 数据库提交失败留下的孤儿 blob，由延迟 GC 回收。
- 删除 asset 只删这一条引用；GC 删除 blob 前要再次确认没有活引用。

**5. 容量和验证指标。** 节省的存储按唯一字节占比计算，不要用上传次数直接估。监控孤儿 blob 数、断链引用、GC 延迟和鉴权绕过。

### 面试追问与参考回答

**为什么不在引用计数归零时立刻删除 blob？** 删除和新的引用可能并发发生，计数也可能有延迟，立刻删会误删。需要事务保护或延迟窗口，删前再复查一次真实引用。另外哈希碰撞虽然极少，复用前也应校验长度和字节。

**用户 A 删了图，用户 B 的同一张图还能访问吗？** 能。A 删除的只是自己的 asset 记录，content(h) 仍被 B 的 asset 引用，GC 复查时会看到这条活引用而跳过。
