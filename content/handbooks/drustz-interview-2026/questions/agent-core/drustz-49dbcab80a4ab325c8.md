---
id: drustz-49dbcab80a4ab325c8
section: agent-core
order: 33
level: A
title: 06 · Evaluation 与 Security · 6. Security：把 tool output 当不可信输入 ⭐⭐
quick: 作者文档章节 · 06 · Evaluation 与 Security · 6. Security：把 tool output 当不可信输入 ⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/06_eval_security.md
    type: primary
---
## 6. Security：把 tool output 当不可信输入 ⭐⭐

威胁模型至少包括：

- [ ] 外部网页/文档中的间接 prompt injection
- [ ] agent 用用户权限执行用户没要求的动作（confused deputy）
- [ ] 跨租户 retrieval 或 memory 泄露
- [ ] tool result / trace / error 泄露 secret
- [ ] 下载并执行不可信代码
- [ ] 审批 UI 隐藏真实参数

控制清单：

- [ ] 权限在 executor/policy 层，不靠 prompt
- [ ] context 中标记数据来源与 trust level
- [ ] retrieval 前 ACL，输出 citation 后再验证 ACL
- [ ] side effect 先 proposal，审批绑定 exact args/hash/expiry
- [ ] sandbox、domain allowlist、文件/网络限制、资源限额
- [ ] logs 默认 redaction，大 payload 单独受控存储
- [ ] adversarial eval 同时测 task utility 和 attack success

> 高分句：权限永远在 executor/policy 层，不靠 prompt；审批必须绑定 exact args、hash 和 expiry。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/06_eval_security.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/06_eval_security.md)。作者整理资料；许可和第三方来源范围见阅读指南。
