---
id: arl-stochastic-tool-robust-eval
section: agentrl
order: 195
level: A
title: 工具输出随机或偶发失败时，Agent 评测如何稳健？
quick: 固定种子的回放集测确定性逻辑；另设随机压力集估计成功分布。报告均值、分位数与 flaky 率，禁止单次 rollout 定胜负。
tags:
  - Evaluation
  - Robustness
  - Stochasticity
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
---

陷阱是一次 rollout 定胜负：这次搜索排到了关键文档、这次测试没 flaky，就宣布模型赢了两个点。工具链上的随机来自检索排序、限流、验证码、非确定性编译与测试、页面动画。SWE-bench 一类任务已经说明：环境隔离和测试稳定性决定数字能不能比；计算机使用还要冻 fixture，见 `cu-reproducible-benchmark-run`。评测协议必须把「策略脆弱」和「环境噪声」拆开。单次碰巧变绿，其实并不能告诉你 P10 会不会在限流的那一天翻车。

## 两套集：确定性回放 + 随机压力

**Frozen replay：** 固定 seed、mock 工具层、录像式 observation。测的是决策逻辑和 schema 遵守，方差应接近 $0$。数字抖动首先查 harness，而不是调模型。**Stochastic stress：** 对每题多次试运行，允许真实或受控随机。报告均值、P10 / P50、超时率、flaky 率（同一策略同一题既有成功也有失败的比例）。禁止把单次百分点写进发布说明。

用 mock 注入受控故障（空结果、超时、`429`、部分写成功）测恢复，而不是只看 happy path。区分：同一 seed 下必失败 → 策略/契约问题；仅随机集上失败 → 缺重试与查状态，见 `arl-retry`。发布门禁用 P10 成功率，不只看均值——均值会被少量幸运 run 拉高。

$$
\mathrm{flaky}(i)=\mathbf{1}\big[\hat p_i\gt 0\big]\cdot\mathbf{1}\big[\hat p_i \lt 1\big]
$$

训练侧把随机失败写进观察，奖励有效重试（查终态、换查询、退避），不奖励盲目重复同一非幂等写。评测与训练的随机源要版本化，否则「变强了」其实是今天搜索首页换了。

## 归因：策略脆弱还是环境噪声

同一 frozen seed 必失败，先查 schema、权限、计划，而不是加 rollout 次数。仅 stress 集失败，才谈重试与鲁棒。比较两个模型必须同 $n$、同故障注入清单、同预算；一方多试三次不算赢。SWE-bench 要把测试隔离在干净环境，否则 flaky 测试会变成模型分数。GUI / 网页还要分 frozen 与 live，见 `cu-reproducible-benchmark-run`。发布说明同时给均值、P10、flaky 率、超时率；缺 P10 就当没做完稳健评测。随机工具还要记录每次失败的错误码直方图，才能看出是偶发 `429` 还是策略根本不会退避。

面试收口：确定性集看逻辑，随机集看分布；报分位数和 flaky，不报单次。P10 过门，均值才能拿来讲故事。

## 追问

- **为什么还要 frozen replay？** 没有它，你分不清是模型退步还是环境周一改版。对齐 `cu-reproducible-benchmark-run` 的 frozen / live 分轨。随机压力集再强，也替代不了一条可复现的逻辑回归。
- **n 次够不够？** 看 flaky 率。高 flaky 需要更大 $n$ 才谈两个点的差异；先报 CI，再比均值。经验上 flaky 率 $\gt 0.2$ 的题不应进入「单次定胜负」的发布门。
- **把环境崩溃算模型失败可以吗？** 不可以。`env_crash` 与 `oracle_fail` 分列，否则 harness 一抖分数跟着抖。崩溃率上升时先修环境，再谈策略。
- **训练要不要同分布注入故障？** 要，但闸在安全动作子集。评测注入的故障类型应有一份公开清单，避免只对已知噪声过拟合。注入清单版本化，和 schema 一样，旧分数不能和新注入包直接减。
