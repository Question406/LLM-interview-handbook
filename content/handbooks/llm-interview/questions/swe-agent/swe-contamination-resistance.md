---
id: swe-contamination-resistance
section: swe-agent
order: 3
level: A
title: 为什么静态 SWE 集很容易发生训练污染，如何构建并报告一个 contamination-resistant 的持续 benchmark？
quick: >-
  静态 SWE 集的 issue、PR 和测试大多公开，模型可能直接记住了答案。持续 benchmark
  要用时间截断、近期或未见过的仓库、冻结提交和隐藏测试，声明训练 cutoff，并把 frozen leaderboard 和持续 live eval
  分开报。
tags:
  - SWE Agent
  - Contamination
  - Benchmark
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: SWE-bench Multimodal
    url: 'https://arxiv.org/abs/2505.23419'
    type: primary
---

静态 SWE 集容易被污染，是因为 GitHub issue、最终 PR、CI 测试，甚至讨论里给出的正确改法，大多是公开的，可能早就进了预训练或 SFT。所以要做一个抗污染的持续 benchmark，关键在评测协议：冻结哪些版本、cutoff 怎么声明、live 和 frozen 两套数字怎么分开报。面试时光说「我们跑了 SWE-bench」，说明不了有评测能力，用公开集上的高分去暗示线上修 bug 的能力也站不住。

举个例子：模型吐出来的 diff 和 gold patch 几乎一模一样，连变量名都对得上。这可能是它在仓库里诊断出来的，也可能只是背下了那个 PR。没有冻结版本和审计记录，两种情况根本分不开。

## 污染从哪些地方漏进来

公开任务至少有四条泄漏路径：issue 原文和标题；gold PR 的文件级 diff；`FAIL_TO_PASS` 的测试名和断言；第三方 blog、复现教程和合成 distillation 把同一批任务反复写进语料。

harness 也会泄漏。要是把测试文件、隐藏断言或者「应该改哪些文件」塞进 prompt，等于当场开卷。检索增强同样危险，评测时允许上网，模型就能把 gold PR 搜回来再「生成」一遍。时间截断只挡得住 cutoff 之后创建的 issue，那些 cutoff 前就已公开、后来才被收进 bench 的仓库它挡不住。所以污染要在训练、评测、harness 三边一起管，光洗语料不够。

## 评测协议要固定哪些版本

每个任务版本都要固定下来并写进报告：issue 的 `created_at`、repo 的 base SHA、评测用的 test commit、容器和依赖的 digest、harness 和 oracle 的版本。模型这边声明训练 cutoff，并记下评测当天是否允许联网检索、是否允许读测试目录。每次 attempt 至少还要记：task 版本、issue 创建时间、base SHA、test commit、harness digest、模型 cutoff、是否联网，以及生成的 patch 和 gold 的检索相似度。这些字段当时没记，污染审计事后补不回来。

持续的 live 集只收 cutoff 之后、来自没见过的组织或仓库的 issue。hidden test 不进公开镜像，失败 case 不能重新加入 SFT。Live 采集管道要和训练数据管道物理隔离，否则「持续评测」几周之内就会变成第二套训练集。

审计用字符串、AST、embedding 和 patch hunk 检索。命中了就标高风险，没命中也证明不了干净。去重粒度至少要到 hunk 和测试名，文件级 hash 会漏掉 fork 和 cherry-pick。

## 怎么报告，哪里会被刷

报告拆成三列，别加总成一个分：frozen leaderboard 的 resolve rate、cutoff 之后的 live rate、污染审计命中率（patch 近重复 / 测试名命中）。Live 更低通常更接近真实泛化，别把它解释成模型退化，也别用「我们后来又训了 live」把两列重新拉齐。持续 bench 的价值在趋势，单次的百分点没什么意义。

能被刷分的地方有：只报公开集；事后把 live 任务并进训练；评测时开检索去找 gold PR；harness 泄漏测试；拿同一个 issue 的镜像仓库冒充新题。面试官想听的是：你有 frozen 和 live 两套数字，审计方法写在报告里，失败日志有隔离通道。

发布清单至少附上：任务版本、cutoff、是否允许检索、审计方法、frozen / live 两列。缺了任何一项，这个数字只能当内部调试用，拿去做对外的能力声明不够格。

## 追问

**去重要做到什么粒度？**
文件级 hash 不够，要看 patch hunk 和测试名。同一个 issue 换到 fork 仓库里，仍然算污染。

**用私有的 hidden eval 就安全了吗？**
也不安全。人员、日志、失败 case 加入 training data，都会造成二次污染，需要独立的 ACL 和禁止用于训练的条款。

**和语料泄漏检测怎么区分？**
那题偏 n-gram 和检索重合；这题偏 SWE 任务合同，看的是冻结提交、时间窗、分开报告，以及 harness 有没有开卷。
