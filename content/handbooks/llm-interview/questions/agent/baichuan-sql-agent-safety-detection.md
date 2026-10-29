---
id: baichuan-sql-agent-safety-detection
section: agent
order: 113
level: A
title: 百川智能：SQL Agent 如何做安全检查，检测率应怎样衡量？
quick: >-
  执行前把 SQL 解析成
  AST，核对操作、表列白名单、调用者权限和预计成本；执行时再限制只读、时间和行数，高风险操作要审批。检测效果要同时报攻击召回率、正常查询误拦率、逃逸率和审核延迟，光报一个百分比说明不了问题。
tags:
  - Baichuan
  - SQL Agent
  - Security
  - Evaluation
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百川智能大模型实习一面 压力好大（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530'
    type: candidate-first-hand
---
## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习；具体团队原帖未披露
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B（公司、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“如何做的 sql 安全检查 检测率为多少”**

SQL 安全检查放在执行前：把 SQL 解析成 AST，核对操作类型、表列白名单、调用者权限和预计成本；执行时再用只读、限时、限行数的凭证 fallback，写操作要审批。检测率要先定义威胁模型，在攻击集和正常查询集上分别报攻击召回率、正常查询误拦率、逃逸率和审核延迟。原帖追问了检测率的数字，编一个百分比交差最容易被追穿。

关键词黑名单为什么不行，举个例子：`DROP` 可以拆进注释或者动态 SQL 里，注释、编码、空白变形都能绕过关键词；一条看似无害的 SELECT 照样能跨租户 join 把数据带出去。所以要解析成 AST 再做语义 policy，正则找 `DROP` 不够。校验 action 类型、表 / 列 allowlist、调用者的行列级权限、跨租户 join、敏感字段导出、子查询 / 函数逃逸和最大扫描成本，parser 解析失败就 fail-closed。默认发只读、限时、限行数的 credential；写操作先 `EXPLAIN` / dry-run 展示影响范围，再走显式审批、transaction 和 audit log。

LLM「先检查再执行」只能当一个信号，模型可以被 prompt 说服，gateway 不会。政策最终的执行点在 DB gateway，LLM 自检只是辅助。权限原则见 `agent-tool-permissions`，表格抽取的执行层见 `baichuan-complex-table-extract`。

检测率怎么测：建一个有标签的攻击集，覆盖越权、注入、数据外带、资源耗尽、破坏性写入，再建一个正常复杂查询集。每类报 recall、false positive / 正常阻断率、绕过率、p95 审核延迟，再加上线上人工复核。测试要包含改写、嵌套、编码和字段和类型规范（schema）漂移。面试官追具体百分比时，就说明这个数依赖攻击集怎么定义、业务分布是什么，给出评估协议比给一个孤立的数有用。

## 追问

**关键词过滤为什么不够？**
`DROP` 能拆进注释或动态 SQL，SELECT 也能跨租户外带数据，要靠 AST 加身份加成本一起判断。

**误拦正常分析查询怎么办？**
在正常集上单独报阻断率；复杂但合法的 OLAP 查询走审批，别一刀切拒绝。

**Agent 自己生成的 SQL 还要验吗？**
要。生成器和执行器必须分开，模型输出不可信。

**能报「检测率 99%」吗？**
没说明攻击集和误拦率就不能报。先定义威胁类型和分母，再给切片数字。
