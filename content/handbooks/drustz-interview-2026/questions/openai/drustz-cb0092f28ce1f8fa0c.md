---
id: drustz-cb0092f28ce1f8fa0c
section: openai
order: 153
level: A
title: CICD and GPU Utilization
quick: original-structured-preparation-guide · CICD and GPU Utilization
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
      https://www.1point3acres.com/interview/problems/3460d47c-d129-46a8-bac1-c6e9698acb04
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# CI/CD 与 GPU Utilization

> 旧正文覆盖通用多租户 CI/CD，却没有 GPU placement、兼容性和利用率优化。本指南补齐标题核心。

## Pipeline

提交后依次执行：CPU lint/unit test → 可复现容器构建 → CUDA/driver 兼容矩阵 → GPU smoke test/训练 → 制品签名 → 灰度部署。普通 Docker build 放 CPU pool，避免昂贵 GPU 空等。

## GPU Scheduler

任务声明 GPU 型号、数量、显存、拓扑、预计时长和是否允许共享。调度器使用 quota + fair queue、bin packing 与 gang scheduling；MIG/time-slicing 只给允许共享且隔离要求匹配的任务。

收集 DCGM/NVML 和 profiler 指标：SM utilization、显存、HBM 带宽、PCIe、data-loader wait。根据瓶颈调整 batch、mixed precision、gradient accumulation、pinned memory、异步拷贝或 data workers，不能只看一个“GPU %”。

OCI image、锁定的 CUDA/cuDNN/driver matrix、Kubernetes CRD 和云 adapter 支持 Python/C++ 及多云可移植。

## 复杂度与边界

队列操作约 `O(log jobs)`；有资源索引时选节点约 `O(log workers)`，复杂约束可能扫描 `O(workers)`。覆盖 OOM、spot preemption、驱动不兼容、GPU 节点丢失、缓存污染、数据隔离、非确定训练和跨云制品复制。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/3460d47c-d129-46a8-bac1-c6e9698acb04)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
