---
id: drustz-288e3fe3da50b31e3d
section: mlsd
order: 199
level: A
title: 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 2. Step 1：选仓库（这一刀性价比最高）
quick: 作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 2. Step 1：选仓库（这一刀性价比最高）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md
    type: primary
---
## 2. Step 1：选仓库（这一刀性价比最高）

```bash
cd labs/swe_data && python github.py
```



### 三条拿数据的路

| 路 | 怎么拿 | 限制 | 适合 |
|---|---|---|---|
| REST/GraphQL API | `api.github.com` | 认证后 5000 req/h | 几百个仓库 |
| **GH Archive** | BigQuery 或下载每小时 `.json.gz` | 无 | **全量元数据** |
| **本地 clone** | `git clone --filter=blob:none` | 无 | **拿 patch 内容** |

> **SWE-rebench V2 的做法值得直接抄**：用 GH Archive 拿元数据
> （issue 正文、PR 讨论、commit SHA、license、语言），
> 然后**分布式 map-reduce 克隆仓库、从本地 git 历史直接取 patch**，
> 完全绕开 API 速率限制。这样处理出 **21,000 个仓库 / 58 万个候选实例**。
>
> **不要用 API 逐个拉 diff** —— 那是这条 pipeline 最经典的自杀方式。

### 筛选阈值（各家实际用的）

| | SWE-smith | SWE-rebench V2 |
|---|---|---|
| 来源池 | PyPI 下载量前 5000 的包 | GH Archive 全量 |
| star | **≥ 1000** | 高资源语言 **≥25**；长尾语言 ≥10 |
| issue | — | closed issue **≥15**；长尾 ≥1 |
| license | — | **必须宽松许可** |
| 排除 | **SWE-bench 的 12 个测试仓库** | 同 |
| 结果 | 128 个仓库 | 21,000 个仓库 |

⭐ **最值得记的一个数**：SWE-rebench V2 量化过，
**这套阈值保留约 20% 的仓库，却覆盖约 80% 的任务** ——
需要搭环境的仓库数直接降到 1/5。

**任务产出是极度长尾的**，所以正确的顺序是：先给 `yield_score` 高的仓库搭环境。
代码里 `score_repo()` 给了一个可用的打分。

### 三个容易漏的过滤

```python
if meta.get("fork"):
    reject("是 fork —— 会和上游产生重复实例")
if meta.get("archived"):
    reject("已归档 —— 环境多半装不上")
if lic not in PERMISSIVE:
    reject("非宽松许可 —— 训练数据的法务风险")
```



---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
