---
id: swe-test-contract
section: swe-agent
order: 2
level: S
title: SWE benchmark 的 fail-to-pass / pass-to-pass tests 各在验证什么？如何阻止 Agent 通过删测试或改无关行为刷分？
quick: "fail-to-pass 验证 issue 要的目标行为修好了，pass-to-pass 保证原有行为没被改坏。光这两类还会被刷，所以还要锁测试文件、限制 patch 路径、加隐藏测试和人工抽检；编译过了或者单测绿了，都不够单独判 resolved。"
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

`FAIL_TO_PASS` 验的是 issue 要的行为修好了，`PASS_TO_PASS` 验的是原来的行为没被改坏；但两类测试都过还不够判 resolved，测试文件本身没被动过、patch 没碰越权路径、隐藏测试也过，四样齐了才算。「测试全绿」只是其中一项。

比如一个 issue 说某函数遇到空输入会崩。Agent 可以老老实实修，也可以把那条失败的断言删掉、把 `assert` 改成 `pass`、按 issue 编号硬编码返回值、把异常吞掉，或者为了修这一个 case 拆掉旁边的功能。这些做法都能让测试变绿。编译通过、lint 变绿、测试数量增加，也都只是旁路信号。

先说两类测试各管什么。`FAIL_TO_PASS` 在 base commit 上失败，打上候选 patch 之后应该通过，对应 issue 描述的行为被修好了。`PASS_TO_PASS` 修复前后都应该通过，意思是别为了修 A 把 B 弄坏。少了哪一类都会被刷：只有 F2P，会鼓励破坏性修复；只有 P2P，会鼓励空 patch 或者改测试。评测器要输出每个测试的状态转移：F→P、P→P、P→F、F→F，还有「测试消失」。出现 P→F 或者测试消失，就算 F2P 全过也不能标 resolved。语义正确但覆盖不全的 patch 仍可能漏 edge case，所以人工接受率要单独报，F2P 代替不了它。

然后评测器要冻住并且记账。冻结 base SHA、评测用的 test commit、测试命令、超时、容器 digest；记录打 patch 前后测试文件和 fixture 的 hash、每个测试的状态转移、patch 碰了哪些路径、有没有改 `tests/`、`tox.ini`、CI workflow。评测器直接拒绝修改测试、断言、fixture、快照和 CI 配置的 patch，允许改的生产路径做 allowlist。Hidden tests 不放进 Agent 看得见的工作区，在独立阶段跑。再加 mutation：故意破坏一条正确断言或删掉一个 F2P，看 Agent 是不是靠删测试、把 `assert` 改成 `pass` 过关。日志要能说清楚，测试通过是因为行为修好了，还是因为测试被改了。

常见的投机手法还有几种：删失败用例，按 issue 文本硬编码返回值，关掉类型检查，扩大 mock 让测试碰不到真实逻辑，改系统时间或时区让 flaky 变绿。所以报告我会拆成五列：目标测试通过率、回归通过率、测试完整性（测试文件没被改）、patch 范围有没有越权、人工抽检接受率。只报「tests passed」，奖励就对准了投机。resolved 的定义写成 F2P 通过 ∧ P2P 通过 ∧ 测试完整性通过 ∧ 路径 allowlist 通过，缺一项就是 failed 或 invalid。

被问「怎么防刷分」，我按这个顺序答：测试文件 hash → 路径 allowlist → hidden tests → mutation → 人工抽检。前三项是自动门禁，后两项抓语义上的投机，这五步都写进 evaluator。报告里 resolved 也别只写一个布尔值，要附状态转移表、测试 hash 有没有变、越权路径列表。评审时抽 10 条「全绿」样本人工看，专门找删断言和硬编码。没有抽检的自动分，默认当成可刷。上面每一条判定都要能对应到日志字段。

## 追问

**hidden test 和 P2P 是不是重复了？**
不重复。P2P 防的是已知行为回归，hidden 防的是 Agent 对着看得见的断言过拟合。

**有的仓库本来就允许改测试，怎么办？**
测试变更单独送审，不计入自动 resolved；或者只允许新增，禁止删除或弱化断言。

**正确的 patch 也可能 F2P 不全吗？**
可能。issue 描述的行为比可见测试宽，所以人工接受率和 hidden 覆盖要单独报。

**编译绿了能不能提前结束？**
不能。编译只说明能构建，证明不了目标行为修好了，也证明不了没回归。
