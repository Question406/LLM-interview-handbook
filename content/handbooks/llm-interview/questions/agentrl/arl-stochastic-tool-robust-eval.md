---
id: arl-stochastic-tool-robust-eval
section: agentrl
order: 195
level: A
title: 工具输出随机或偶发失败时，Agent 评测如何稳健？
quick: "分两套集：固定种子、mock 工具层的回放集测确定性逻辑，随机压力集对每题多跑几次估计成功分布。报告均值、分位数和 flaky 率，发布门看 P10，单次 采样轨迹（rollout） 不能定胜负。"
tags:
  - Evaluation
  - Robustness
  - Stochasticity
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
---

我会拆成两套集：固定种子、mock 工具层的确定性回放集，用来测决策逻辑；允许随机的压力集，每题跑多次，估计成功率的分布。报告均值、P10 / P50、超时率和 flaky 率，单次 采样轨迹（rollout） 不能定胜负。

举个例子：这次搜索刚好把关键文档排在第一，测试也刚好没 flaky，就宣布模型赢了两个点。单次碰巧变绿，告诉不了你限流那天 P10 会不会翻车。工具链上的随机来源很多，检索排序、限流、验证码、非确定性的编译和测试、页面动画都算。SWE-bench 一类任务已经说明，环境隔离和测试稳定性决定了数字能不能比，flaky 测试不隔离，就会变成模型分数；GUI、网页和计算机使用还要冻 fixture，分 frozen 与 live，见 `cu-reproducible-benchmark-run`。所以评测协议的任务，是把「策略脆弱」和「环境噪声」分开。

Frozen replay 固定 seed、mock 工具层、观测结果（observation） 用录像式回放，测的是决策逻辑和 字段和类型规范（schema） 遵守情况，方差应该接近 $0$；数字一抖，先查 harness，别急着调模型。Stochastic stress 对每题跑多次，允许真实或受控的随机。flaky 率是同一策略在同一题上既有成功又有失败的比例：

$$
\mathrm{flaky}(i)=\mathbf{1}\big[\hat p_i\gt 0\big]\cdot\mathbf{1}\big[\hat p_i \lt 1\big]
$$

压力集里还要用 mock 注入受控故障，空结果、超时、`429`、写操作部分成功，测恢复能力，别只看 happy path。发布门禁用 P10 成功率，均值会被少数幸运的 run 拉高，单次的百分点也别写进发布说明。发布说明里同时给均值、P10、flaky 率、超时率，缺了 P10 就当稳健评测没做完。

归因按两套集的结果来分。同一个 frozen seed 下必失败，是策略或契约的问题，先查 schema、权限、计划，加 rollout 次数没用；只在随机集上失败，才谈得上缺重试和查状态，见 `arl-retry`。比较两个模型要同 $n$、同一份故障注入清单、同预算，一方多试三次不算赢。每次失败的错误码也记成直方图，才看得出是偶发 `429`，还是策略根本不会退避。

训练侧可以把随机失败写进观察，奖励有效的重试（查终态、换查询、退避），盲目重复同一个非幂等写不给分。评测和训练的随机源都要版本化，否则「变强了」可能只是今天搜索首页换了。

## 追问

**有了随机压力集，为什么还要 frozen replay？**
没有它，分不清是模型退步了还是环境周一改版了。随机压力集再强，也替代不了一条可复现的逻辑回归，这就是 `cu-reproducible-benchmark-run` 里 frozen / live 分轨的用意。

**每题跑 n 次够不够？**
看 flaky 率。flaky 高的题要更大的 $n$ 才能谈两个点的差异，先报 CI 再比均值。经验上 flaky 率 $\gt 0.2$ 的题，不应该进「单次定胜负」的发布门。

**环境崩溃能算模型失败吗？**
不能。`env_crash` 和 `oracle_fail` 要分列，否则 harness 一抖分数就跟着抖。崩溃率上升时先修环境，再谈策略。

**训练要不要按同样的分布注入故障？**
要，但限制在安全动作子集里。评测注入的故障类型要有一份公开清单，免得只对已知噪声过拟合。注入清单和 schema 一样要版本化，旧分数不能和新注入包的分数直接相减。
