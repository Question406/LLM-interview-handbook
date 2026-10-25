---
id: swe-ci-flaky-diagnosis
section: swe-agent
order: 191
level: S
title: SWE Agent 如何区分真实 CI 失败与 flaky test，并给出诊断？
quick: "固定 SHA、环境和命令重跑 k 次，再单独跑失败用例，查时间、并发、网络这些不确定因素：每次都红才算真实失败，有红有绿就标 flaky。flaky 的测试先隔离、开票跟踪，只有能复现的真实失败才进自动补丁循环。"
tags:
  - CI
  - Flaky Tests
  - SWE Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: "Understanding Flaky Tests: The Developer's Perspective"
    url: https://arxiv.org/abs/1907.01466
    type: primary
---

先看能不能复现：同一个 SHA、同一个镜像、同一条命令重跑几次，每次都红才算真实失败，有红有绿就是 flaky，只有真实失败才进自动修复循环。Agent 要是把偶发的红当成确定性信号，就会打出错误补丁，比如删断言、加 sleep、扩大 mock，甚至去改跟这次改动毫无关系的生产代码，只为了「稳住」一个本来就不稳的测试。「失败了就修，绿了就提交」是最常见的错法。

举个例子：Agent 改了一个日志格式，CI 上一个订单超时测试红了。同一个 SHA 再跑三次，两次绿一次红，关掉并发后五次全绿。这个红跟这次 diff 没有关系，是资源争用，该做的是隔离并开票，去改订单代码就是在拟合噪声。

## 先判可复现，再谈补丁

同 SHA、同镜像、同命令至少重跑 $k$ 次，$k\ge 3$ 起步，噪声大的套件要更多。复现置信定义成 $\hat{p}_{\mathrm{fail}} = k_{\mathrm{fail}}/k$。只有 $\hat{p}_{\mathrm{fail}}=1$ 才当确定性失败；$\hat{p}_{\mathrm{fail}}=0$ 当环境毛刺；$0 \lt \hat{p}_{\mathrm{fail}} \lt 1$ 就标 flaky。Flaky 相关的研究反复强调，同一个 SHA 上结果会翻，这个失败就当不了回归证据。

判定时别看单次实际耗时。并发开和关要分成两列记，否则会把资源争用当成业务 bug。把失败用例单独拎出来跑，关掉并发，看还翻不翻。再对照这些非确定性来源：时钟没冻结、sleep 竞争、测试真的去打网络、测试顺序依赖、随机数没播种。签名按「测试名 + 断言位点 + 错误类」聚类，免得同一个 flake 的不同 stack 被当成好几个 bug。

每次诊断记下这些字段：SHA、重跑矩阵、并发开关、是否触网、签名、判定（`reproducible` / `flaky` / `env`）。签名里把时间、线程、网络三类根因单独标出来，修复建议才能落到冻时钟、去并发或夹具化上，别统一加 `sleep`。所以整个流程是：失败签名聚类 $\to$ 同 SHA 重跑 $\to$ quarantine $\to$ 只有确定性失败进修复循环。工具输出里要带上复现置信度，光抛一个 traceback 不够。

## Quarantine 和修复循环分开

flaky 测试先隔离：不阻塞这次 patch，也不进自动修复的目标，但要开缺陷票，并计进健康指标。真实失败才允许改生产代码。「加 sleep / 重试到绿」不算修复，除非产品明确接受、并写进了测试合同。对「加长等待就绿」的补丁默认拒绝，它证明不了复现，还会让套件更慢更脆。隔离之后如果 $\hat{p}_{\mathrm{fail}}$ 还在中间带，就保持 quarantine，别为了让 Agent 有事做去改生产逻辑。

Agent 的诊断报告要讲清楚为什么判 flaky、附上重跑表、给出建议（隔离 / 冻时钟 / 去网），别直接出 diff。flake 是测试债务，算不上 issue。开发者视角的那篇研究也指出，复现本身是最大的成本，Agent 跳过复现，只会把这笔成本放大。面试时讲清楚 $k$ 次重跑矩阵和 quarantine 的边界，别停在「我们会看日志」。

## 和测试合同、评测对齐

这题要和 `swe-test-contract` 对上。SWE-bench 式的合同里，`FAIL_TO_PASS` 必须可复现，F2P 的前提是 base 上稳定失败、patch 后稳定通过；把 flaky 当成 F2P，会把那张卡里目标行为的定义一起破坏掉。闪烁的 F2P 不能标 resolved。评测器如果在 base SHA 上这个测试就已经闪红，就不该把它算成 Agent 引入的 P2P 回归。

评测上能刷分的做法有这么几种：失败一次就修；把 flaky 测试删掉刷绿；用随机重试把 $\hat{p}$ 藏起来不报。所以周报要把 flake 率和 resolved 分开列，免得 Agent 靠跳过闪烁测试抬分。

## 追问

**为什么要在同一个 SHA 上重跑？**
SHA 没变、结果变了，这个失败就解释不到这次 diff 头上，再去改代码就是在拟合噪声。

**和 `swe-test-contract` 是什么关系？**
那题定义 F2P / P2P，并且防止删测试；这题保证进入那份合同的失败是确定性的。

**$k=1$ 行不行？**
不行。对 flaky 的套件来说，单次红在统计上说明不了什么。

**隔离会不会把真 bug 藏起来？**
会，所以要开票、记复现率、定期重试，quarantine 不能当成永久删除。
