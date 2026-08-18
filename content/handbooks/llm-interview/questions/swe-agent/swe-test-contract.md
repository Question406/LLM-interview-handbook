---
id: swe-test-contract
section: swe-agent
order: 2
level: S
title: SWE benchmark 的 fail-to-pass / pass-to-pass tests 各在验证什么？如何阻止 Agent 通过删测试或改无关行为刷分？
quick: fail-to-pass 验证 issue 修复的目标行为，pass-to-pass 保护原有行为不回归。还要保护测试完整性、限制 patch scope、加入隐藏测试和人工抽检；编译通过或单测变绿都不是唯一 verdict。
tags:
  - SWE-bench
  - Testing
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
---

fail-to-pass tests 在原提交上失败、修复后应通过，代表 issue 所述行为真正被修复。pass-to-pass tests 在修复前后都应通过，防止 Agent 为修一个 case 破坏相邻功能。

评测器必须检测 Agent 修改/删除测试、绕过断言、硬编码 issue 文本、关闭 lint 或把异常吞掉。可将 hidden tests、diff allowlist、变更范围审查、mutation testing 和人工抽检组合起来。

一个正确 patch 也可能没覆盖所有 edge case，所以报告应拆开：目标测试、回归测试、测试完整性、patch 可维护性和人工接受率。只报“tests passed”会鼓励奖励投机。
