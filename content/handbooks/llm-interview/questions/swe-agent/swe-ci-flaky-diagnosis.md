---
id: swe-ci-flaky-diagnosis
section: swe-agent
order: 191
level: S
title: SWE Agent 如何区分真实 CI 失败与 flaky test，并给出诊断？
quick: 同 sha 重跑、隔离失败用例、比对非确定性信号（时间、并发、网络）。Flaky 入隔离舱，真实失败才驱动补丁循环。
tags:
  - CI
  - Flaky Tests
  - SWE Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: "Understanding Flaky Tests: The Developer's Perspective"
    url: https://arxiv.org/abs/1907.01466
    type: primary
---

Agent 若把偶发红当确定性信号，会引入错误补丁：删断言、加 sleep、扩大 mock，甚至改无关生产代码去「稳住」一个本与本次改动无关的测试。面试陷阱是「失败了就修，绿了就提交」。Flaky 文献反复强调：同一 SHA 上结果翻转，就不能当回归证据。SWE-bench 式合同里，`FAIL_TO_PASS` 必须可复现；把 flaky 当 F2P 会同时破坏 `swe-test-contract` 的目标行为定义。流程应是：失败签名聚类 $\to$ 同 SHA 重跑 $\to$ quarantine $\to$ 仅确定性失败进修复循环。工具输出要含可复现置信度，而不是只抛 traceback。

## 先判可复现，再谈补丁

同 SHA、同镜像、同命令至少重跑 $k$ 次（$k\ge 3$ 起步，高噪套件更大）。定义复现置信：$\hat{p}_{\mathrm{fail}} = k_{\mathrm{fail}}/k$。仅当 $\hat{p}_{\mathrm{fail}}=1$ 才当确定性失败；$\hat{p}_{\mathrm{fail}}=0$ 当环境毛刺；若 $0 \lt \hat{p}_{\mathrm{fail}} \lt 1$ 则标 flaky。判定不要用单次墙钟；并发打开与关闭要分成两列，否则你会把资源争用当成业务 bug。隔离失败用例，关掉并发，看是否仍翻。对照非确定性信号：未冻结时钟、睡眠竞争、网络实打、测试顺序依赖、未播种随机。签名按测试名 + 断言位点 + 错误类聚类，避免把同一 flake 的不同 stack 当成多个 bug。记录字段：SHA、重跑矩阵、并发开关、是否触网、签名、判定（`reproducible` / `flaky` / `env`）。

## Quarantine 与修复循环隔离

Flaky 入隔离舱：不阻塞本次 patch，不进入自动修复目标，但要开缺陷票并计健康指标。真实失败才允许改生产代码。禁止用「加 sleep / 重试到绿」当修复，除非产品明确接受并写进测试合同。评测器若在 base SHA 上该测试已经闪红，就不应把它标成由 Agent 引入的 P2P 回归。Agent 诊断报告应给出：为何判 flaky、重跑表、建议（隔离 / 冻时钟 / 去网），而不是直接出 diff。可被刷的点：失败一次就修；把 flaky 测删掉刷绿；用随机重试把 $\hat{p}$ 藏起来不报。

面试口径：绿红必须在同 SHA 上可复现，才配驱动补丁；flake 是测试债务，不是 issue。开发者视角的研究也指出，复现本身是最大成本——Agent 若跳过复现，只会放大这笔成本。现场能讲清 $k$ 次矩阵和 quarantine 边界，比讲「我们会看日志」更像做过 CI Agent。

与 `swe-test-contract` 对齐：F2P 的前提是 base 上稳定失败、patch 后稳定通过。闪烁的 F2P 不能标 resolved。周报把 flake 率与 resolved 分列，避免 Agent 靠跳过闪烁测试抬分。签名里要单独标时间、线程、网络三类根因，修复建议才能落到冻时钟、去并发或夹具化，而不是统一加 `sleep`。若隔离后 $\hat{p}_{\mathrm{fail}}$ 仍在中间带，保持 quarantine，不要为了让 Agent 有事做而去改生产逻辑。对「加长等待就绿」的补丁默认拒绝：它既不证明复现，也把套件变得更慢更脆。

## 追问

- **为什么同 SHA 重跑？** SHA 不变而结果变，失败就不由这次 diff 解释；再改代码是在拟合噪声。
- **和 `swe-test-contract`？** 那题定义 F2P / P2P 与防删测试；本题保证进入该合同的失败是确定性的。
- **$k=1$ 行不行？** 不行。单次红对 flaky 套件没有似然意义。
- **隔离舱会不会藏真 bug？** 会，所以要票、复现率和定期重试；不能把 quarantine 当永久删除。
