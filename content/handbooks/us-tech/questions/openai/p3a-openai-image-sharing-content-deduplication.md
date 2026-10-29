---
id: p3a-openai-image-sharing-content-deduplication
section: openai
order: 639
level: A
title: "OpenAI：图片共享：内容哈希去重与删除生命周期"
quick: "把用户的 asset 与内容 blob 分开，按内容哈希复用同一份字节，权限和文件名保存在各自的 asset。删除只移除引用，GC 延迟回收前再查活引用；并发上传用条件创建去重。"
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

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。

我会把用户的图片记录 asset 和字节内容 blob 分开：同样的字节只存一份，每个人仍有独立的文件名和权限。是否删除 blob 由真实引用关系决定，引用计数只做可修复的缓存。

练习支持上传、查看、下载、分享和删除，只要求字节完全相同去重，不做视觉近似去重。先确认是否需要缩略图和存储配额。

上传先写临时 blob，同时算 SHA256，然后以哈希为键条件创建 content，已存在就复用，最后在数据库事务里创建 asset 引用。模型是 `content(hash, size, blob, state)` 和 `asset(id, owner, content_hash, acl, deleted_at)`。下载先按 asset 鉴权，再发短期 URL，经 CDN 下发。

比如 A 上传 `cat.jpg`，哈希 h 尚不存在，就把临时 blob 转正、创建 content(h) 和 A 的 asset。B 上传相同字节但叫 `kitty.jpg`，条件创建发现 h 已存在，丢掉 B 的临时 blob，只新建指向 h 的 asset。两人的名字和权限独立，底层只有一份内容。

并发上传靠条件写或唯一约束收敛，数据库提交失败留下的孤儿 blob 由延迟 GC 回收。删除 asset 只移除对应引用，GC 真删前再确认没有活引用，跨数据库和对象存储的失败通过补偿及后台修复处理。

容量节省按唯一字节占比估算，上传次数不能直接代表存储量。监控孤儿 blob、断链引用、GC 延迟和鉴权绕过。

## 追问

**为什么引用计数归零不能立刻删？**
计数可能延迟，删除也可能与新引用并发。需要事务保护或延迟窗口，删前复查真实引用。复用时还应核对长度和字节，以防极少见的哈希碰撞。

**A 删了图，B 还能访问吗？**
能。A 只删除自己的 asset，content(h) 还有 B 的活引用，GC 会跳过。
