---
id: baichuan-sql-agent-safety-detection
section: agent
order: 113
level: A
title: 百川智能：SQL Agent 如何做安全检查，检测率应怎样衡量？
quick: "执行前解析 SQL 的 AST，核对操作、表列白名单、调用者权限和预计成本；执行时再限制只读、时间与行数，高风险操作需要审批。检测效果要同时看攻击召回率、正常查询误拦率、逃逸率和审核延迟，不能只报一个百分比。"
tags:
  - Baichuan
  - SQL Agent
  - Security
  - Evaluation
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
- 原始措辞：**“如何做的 sql安全检查 检测率为多少”**

原帖问了检测率数字。常见误区是：编一个百分比交差。答法是威胁模型 + 攻击集/正常集上的 recall、误拦、逃逸、延迟。政策最终执行点在 DB gateway，LLM 自检只是辅助。权限原则见 `agent-tool-permissions`，表格抽取的执行层见 `baichuan-complex-table-extract`。

## 执行前拦截，不要靠黑名单

把 SQL 解析为 AST 再做语义 policy，而不是正则找 `DROP`。校验：action 类型、表/列 allowlist、调用者的行列级权限、跨租户 join、敏感字段导出、子查询/函数逃逸、最大扫描成本。默认只读、限时、限行数的 credential。写操作先 `EXPLAIN` / dry-run，展示影响范围，再显式审批、transaction 和 audit log。注释、编码、空白变形都能绕过关键词；parser 失败应 fail-closed。

## 「检测率」必须定义威胁模型

建立有标签的攻击集（越权、注入、数据外带、资源耗尽、破坏性写入）和正常复杂查询集，报告每类 recall、false positive / 正常阻断率、绕过率、p95 审核延迟及线上人工复核。测试包含改写、嵌套、编码和 字段和类型规范（schema） 漂移。LLM「先检查再执行」只能当信号：模型可以被 输入提示（prompt） 说服，gateway 不能。面试若追具体百分比，说明依赖攻击集定义和业务分布，应给评估协议而不是一个孤立数字。

## 追问

- **关键词过滤为什么不够？** `DROP` 可拆进注释或动态 SQL；SELECT 也能跨租户外带。要 AST + 身份 + 成本。
- **误拦正常分析查询怎么办？** 正常集上单独报阻断率；对复杂但合法的 OLAP 走审批而不是一刀切拒绝。
- **Agent 自己生成的 SQL 还要验吗？** 要。生成器与执行器必须分离；模型输出不可信。
- **检测率 99% 能报吗？** 没有说明攻击集和误拦率就不能报。先定义威胁类型和分母，再给切片数字。
