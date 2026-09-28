---
id: baichuan-table-agent-data-augmentation
section: data
order: 102
level: A
title: 百川智能：表格 Agent 的数据怎样增强，数据量如何确定？
quick: >-
  从真实表结构、公式依赖、脏数据和用户意图出发，生成可执行任务，再用 spreadsheet engine / verifier 校验结果。增广要覆盖 schema 改名、空值、日期货币、跨表引用和错误修复，同时避开模板重复、答案泄漏和不真实的工具轨迹。规模看有效任务和覆盖度，别报原始条数。
tags:
  - Baichuan
  - Table Agent
  - Data Augmentation
  - Verifier
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习；具体团队原帖未披露
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B（公司、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“agent表格数据如何增强的 数据量是多少”**

错法：报一个「十万条」，或把同一模板换列名两边都放。表格 Agent 的有效样本是可执行四元组：用户指令、起始工作簿、工具轨迹、可用引擎重算的目标。我一般先从脱敏真实表抽 schema、公式依赖图和操作分布，再增广；答案不能写在注释或指令里。

## 增广算子必须能被引擎打回

有效变换：列名 / 单位改写、插入空值与异常、日期货币格式、跨 sheet lookup、汇总 / 排序 / 透视、公式修复、多步编辑。每条由 spreadsheet engine 重算，检查目标单元格、公式范围和未破坏的 invariant（合计行、外键）。过不了 verifier 的合成轨迹直接丢。按表结构族、操作类型、长度、难度切分，同一模板禁止同时出现在 train/test。额外保留失败轨迹，专门训纠错，但要标成 `repair` 桶，免得污染成功分布。

## 规模用学习曲线，不用原始条数

报告：去重后 executable tasks、每类覆盖率、verifier pass rate、有效 action tokens。扩样规则：向长尾结构族加数据，若 holdout task success 仍升且锚点任务不掉，才继续；边际增益 $\lt$ 阈值就停。对照实验只开一类增广（例如只加空值），看该类升、日期类是否掉，避免「条数涨、能力平」。

面试里把规模说成「先覆盖操作×结构族的格子，再沿学习曲线加长尾」，不要先报一个整数。同帖的线上指标构造见 `baichuan-online-eval-data`：离线增广解决覆盖，线上事实表解决分母。表格任务的 process reward 还必须能被同一引擎重放，否则增广会变成不可验证的轨迹模仿。

## 追问

- **数据量是多少？** 没有通用数字。用去重可执行任务和覆盖率回答，并出示学习曲线。
- **换列名算新样本吗？** 若公式依赖与目标未变，对测试是泄漏。要按结构指纹去重切分。
- **没有引擎能不能合成？** 不能当正样本。无 verifier 的轨迹只进候选，抽检后再用。
