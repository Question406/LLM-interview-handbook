---
id: p3a-anthropic-sd-q5-data-infrastructure
section: anthropic
order: 626
level: A
title: "Anthropic：数据基础设施：接入、处理与分级访问"
quick: "我会把原始数据、处理结果和服务快照分层管理，每次处理记录输入版本、代码和权限来源。这样失败可重跑，数据能追溯，删除请求也能沿血缘传到派生数据和缓存。"
companies:
  - anthropic
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · sd-q5-data-infrastructure"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/sd-q5-data-infrastructure
    type: secondary
---

## 题目

设计一个大规模数据摄取和处理系统，服务不同的利益相关方，并处理不同的敏感级别。题卡给出的详细规格有限。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖，原题详细规格有限；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

规格有限时，先澄清四件事：数据从哪里来、多久更新一次、能否重放，以及谁能看什么。然后把系统分成原始层、处理层和服务层。

每个数据集记录血缘、schema 版本和质量检查结果，失败的批次可以重跑。权限和删除要求必须一路传播到所有派生数据，不能只管原始层。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

每天 10TB 数据，批处理和流处理混合。研究、分析和生产三类用户有不同的访问需求。要求支持血缘、重放、删除和敏感级别控制。

开始回答时复述这些范围，问面试官删除请求的时限要求，以及研究用户能否接触原始数据。

我会先确认来源、更新频率、能否重放和访问范围，再把原始层、处理层、服务层分开。题卡规格有限，练习暂定每天 10TB、批流混合，研究、分析和生产用户分别授权；删除时限、研究能否读原始数据还要继续澄清。

比如一天的数据按 `source_offset` 不可变地落到 landing，校验发现 0.1% 的行缺字段，就隔离这些行并记录问题，其余进入标准化任务。`job_run` 记录 code、config 和 `input_versions`，产出 curated 的新 version，继承来源的 classification 和 acl。检查全部通过才原子切换 manifest，让研究快照和在线服务读到新数据。

数据集要记录 dataset、version、schema、classification、acl、retention、血缘和质量检查结果。调度元数据与数据存储分开，每份派生数据都能追到输入和代码，这也是失败后按相同输入版本重跑的基础。更正数据生成新版本，保留可追溯的变化。

权限和删除沿血缘传播到派生数据集及缓存。固定版本让研究可复现，但受删除影响的训练、评测快照必须标记失效；审计可以保留标识，不能留可还原内容的数据。

每天 10TB 平均约 116MB/s，峰值和重处理还要另留预算。验证时看新鲜度、完整性、schema 漂移、失败批次重跑耗时，以及跨权限访问次数。

### 面试追问与参考回答

**怎样让研究既可复现又满足删除要求？**
研究使用固定版本的 manifest，并设置受控的保留期。删除时保留用于审计的标识，但不保留能还原内容的数据；受影响的训练和评测快照明确标记为失效。

**上游改了 schema 怎么办？**
校验阶段按登记的 schema 版本检查，发现不兼容的变更就隔离这批数据并告警，而不是让下游任务读到错位的字段。兼容的新增字段登记为新 schema 版本后再放行。
