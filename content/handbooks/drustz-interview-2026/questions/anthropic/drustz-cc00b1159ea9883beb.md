---
id: drustz-cc00b1159ea9883beb
section: anthropic
order: 86
level: A
title: Efficient Model Deployment in a Cluster
quick: >-
  original-structured-preparation-guide · Efficient Model Deployment in a
  Cluster
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/c91f8ed2-4407-459f-a433-a15fbf1de741
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Efficient Model Deployment in a Cluster

## 证据边界

本地保存的详细题面与公开同题预览共同确认：约 500GB 模型要按需复制到 100–1000 台 GPU 主机；外部源总带宽 10Gbps，每台内部网络 10Gbps full-duplex；所有主机最终都要有完整且校验通过的副本，并能容忍节点失败。这里讨论的是**模型文件分发**，不包含在线 inference API、请求 batching 或把权重加载进 GPU 显存。

## 可读需求与分发流程

用户指定 `model_id/version` 和目标主机集合，系统返回 deployment ID，可查看每台主机进度并取消。Coordinator 读取不可变 manifest，把 500GB 切成带 SHA-256 的 chunks，选择拓扑并下发；seed 从对象存储拉取，每获得一块立刻向下游发送；接收方落盘、校验、转发，最后校验全局 manifest hash 后原子发布版本目录。

```text
POST /deployments {model:"m:v7", targets:[w1...w1000]}
S3 --chunk0--> W1 --chunk0--> W2 --chunk0--> ...
S3 --chunk1--> W1 --chunk1--> W2 --chunk1--> ...  （同时进行）
worker heartbeat: {have_bitmap, rx_bps, tx_bps, bad_chunks}
```



## 解法与架构

外网只下载一份，内部采用 rack-aware pipeline；full-duplex 使中间节点能同时接收下一块和转发上一块。Coordinator 持久化 deployment、manifest、拓扑和每节点 chunk bitmap；worker agent 支持断点续传、临时文件与校验后 rename。纯链简单且带宽利用高，但中间失败影响大：心跳超时后把前驱直接接到后继，后继按 bitmap 向任意持有者补块。规模更大或故障率更高时改成多 seed/BitTorrent 式 swarm，稀有块优先并限制每节点上传并发。

## 容量推导

10Gbps≈1.25GB/s，外部传完 500GB 的理论下界是 `400s`。store-and-forward chain 的近似完成时间为 `F/B + (N-1)·C/B`。100 台、1GB chunk 时约 `400+99×0.8=479s`，约 8 分钟；1000 台则约 20 分钟。把 chunk 降到 256MB，1000 台传播尾巴约 `999×0.205=205s`，总计约 10 分钟，但 chunk 数、校验和元数据开销上升。磁盘顺序写也必须持续至少 1.25GB/s，否则 NVMe 才是真瓶颈。

## 边界与故障测试

测试 seed、中间、尾节点分别崩溃；Coordinator 主备切换；chunk 丢失、重复、乱序、hash 错；磁盘满/慢盘；跨 rack 链路降速；目标列表动态加入/移除；同一版本重复部署的去重；取消后临时文件回收；旧 manifest 与新模型混用。验证已完成节点可成为补块源、重试不重复计费/占空间、任何主机只有在全局校验成功后才切换 `current` symlink。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/c91f8ed2-4407-459f-a433-a15fbf1de741)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
