---
id: drustz-b0eb57d074bc8e7c1b
section: forum-notes
order: 111
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 4: Data Structure Design'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 4: Data Structure Design'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Step 4: Data Structure Design

How we store information in the database.

**1. Manifest (The Map)**
Shared with all workers so they know what to download.

```go
type Manifest struct {
    ModelID        string
    NumChunks      int
    Chunks         []ChunkInfo
    GlobalChecksum string     // SHA256 hash
}
```



**2. Worker State (The Status)**
Stored in the Coordinator's memory (or Redis/etcd).

```go
type WorkerState struct {
    WorkerID           string
    Status             WorkerStatus
    ChunksReceived     []int      // List of chunk IDs owned
    DownstreamWorker   string     // Who do I send data to?
    UpstreamWorker     string     // Who do I get data from?
}
```



**Storage Choices:**

- **etcd:** Use this for the Coordinator state. It handles failures well.
- **Local Disk:** Workers save the file chunks here.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
