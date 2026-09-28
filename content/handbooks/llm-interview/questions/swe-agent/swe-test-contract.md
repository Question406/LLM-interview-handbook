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
updatedAt: 2026-08-21
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
---

「测试全绿」不是 SWE 评测的 verdict。Agent 可以删断言、改测试、硬编码 issue 编号、把异常吞掉，或者为修一个 case 拆掉相邻功能。测试合同要讲清：哪些测试代表目标行为，哪些保护回归，测试文件本身是否不可篡改。编译通过、lint 变绿、测试数量增加，都只是旁路信号。

## 两类测试在验什么

`FAIL_TO_PASS` 在 base commit 上失败、打上候选 patch 后应通过，对应 issue 所述的目标行为被真正修复。`PASS_TO_PASS` 在修复前后都应通过，对应「别为修 A 把 B 弄坏」。缺任何一类都会被刷：只有 F2P 会鼓励破坏性修复；只有 P2P 会鼓励空 patch 或改测试。评测器要输出每个测试的状态转移：F→P、P→P、P→F、F→F、以及「测试消失」。出现 P→F 或测试消失，即使 F2P 全过也不能标 resolved。一个语义正确但覆盖不全的 patch 仍可能漏 edge case，所以人工接受率要单独报，不能被 F2P 代替。

## 评测器必须冻结与记录

冻结：base SHA、评测用 test commit、测试命令、超时、容器 digest。记录：应用 patch 前后测试文件与 fixture 的 hash、每个测试的状态转移、patch 触及的路径、是否改了 `tests/`、`tox.ini`、CI workflow。评测器应拒绝修改测试、断言、fixture、快照和 CI 配置；对允许修改的生产路径做 allowlist。Hidden tests 不进 Agent 可见工作区，跑在独立阶段。再加 mutation：故意破坏正确断言或删除一个 F2P，看 Agent 是否靠「删测试 / 改 `assert` 为 `pass`」过关。日志里要能回答「这个绿是修了行为，还是测试被改了」。

## 失败模式与分报

常见投机：删除失败用例；把 `assert` 改成 `pass`；按 issue 文本硬编码返回值；关闭类型检查；扩大 mock 让测试不再碰真实逻辑；改系统时间或时区让 flaky 变绿。报告拆开五列：目标测试通过率、回归通过率、测试完整性（测试文件未被改）、patch 范围是否越权、人工抽检接受率。只报「tests passed」会把奖励对准投机。resolved 的定义是 F2P 通过 ∧ P2P 通过 ∧ 测试完整性通过 ∧ 路径 allowlist 通过；缺一项就是 failed 或 invalid。被问「怎么防刷分」，按这个顺序答：测文件 hash → 路径 allowlist → hidden tests → mutation → 人工抽检。前三项是自动门禁，后两项抓语义投机。这五步写进 evaluator。

评测报告把 resolved 写成布尔不够：要附状态转移表、测试 hash 是否变化、越权路径列表。评审时抽 10 条「全绿」样本做人审，专门找删断言和硬编码。没有抽检的自动分，默认当成可刷。

绿测试只是合同的一项；测试文件没被动、路径没越权、hidden 也过，才叫 resolved。这句话要对应到日志字段。

## 追问

- **hidden test 和 P2P 重复吗？** 不重复。P2P 防回归已知行为；hidden 防 Agent 对着可见断言过拟合。
- **允许改测试的仓库怎么办？** 把测试变更单独送审，不计入自动 resolved；或只允许新增、禁止删除 / 弱化断言。
- **正确 patch 也可能 F2P 不全？** 可以。issue 描述的行为比可见测试更宽，所以人工接受率与 hidden 覆盖要单独报。
- **编译绿了能不能提前结束？** 不能。编译只证明能构建，不证明目标行为或回归合同成立。
