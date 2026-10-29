---
id: swe-production-success
section: swe-agent
order: 6
level: A
title: 如何把离线 resolve rate 转为可靠的线上 Coding Agent quality / cost 指标？
quick: >-
  把线上指标拆成一个漏斗，分开看 attempt 跑完、patch 可应用、测试通过、人工接受、窗口内不回滚，再加 time-to-resolution
  和每成功任务的成本，并按 repo 难度、任务类型、retry budget 切片。离线 resolve rate 只当 release
  criteria，代替不了人工接受和上线后的长期质量。
tags:
  - SWE Agent
  - Production Metrics
  - Quality
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: SWE-bench
    url: 'https://arxiv.org/abs/2310.06770'
    type: primary
---

## 可以这样回答

举个例子：Agent 交了一个 PR，CI 全绿，工程师把一半逻辑重写了才合进去，两周后又因为回归被回滚。如果按「测试绿了」算，这是一次成功；按漏斗看，它卡在了人工接受和回滚这两层。

至少拆五层，每层分母不同，不能共用一个成功率：attempt 有没有跑完（没超时、harness 没崩）；有没有产出可应用的 patch；CI / 目标测试有没有通过；工程师有没有接受（合入或明确 approve）；发布后窗口内有没有回滚或引入回归。「CI 绿」不等于「人接受」，「人接受」也不等于「长期质量」。

## 技术备查

离线 resolve rate 只能当 release criteria，线上要换成一个分层漏斗：attempt 跑没跑完、patch 能不能应用、测试过没过、工程师接不接受、合进去以后回不回滚，每层分母不同，再配上时延和每成功修复的成本。离线优化的是「冻结测试变绿」，线上要的是工程师愿意合、合了不回滚、成本还能接受。用一个「成功率」概括整个流程，是最常见的汇报坑。面试官想听的是各层的分母、怎么切片、release criteria 是什么，SWE-bench 的数字直接拿来当 SLO 是不够的。

举个例子：Agent 交了一个 PR，CI 全绿，工程师把一半逻辑重写了才合进去，两周后又因为回归被回滚。如果按「测试绿了」算，这是一次成功；按漏斗看，它卡在了人工接受和回滚这两层。

## 线上漏斗

至少拆五层，每层分母不同，不能共用一个成功率：attempt 有没有跑完（没超时、harness 没崩）；有没有产出可应用的 patch；CI / 目标测试有没有通过；工程师有没有接受（合入或明确 approve）；发布后窗口内有没有回滚或引入回归。「CI 绿」不等于「人接受」，「人接受」也不等于「长期质量」。

自动合入的 patch 要单独计「自动接受率」，并且强制抽样审计。像上面那种人工大改后才合入的 PR，Agent 的贡献要按 diff 比例下调，或者打上「需人工重写」的标记，不能整单算成 Agent 成功。日志字段至少要有：任务类型、repo、retry 次数、谁点了接受、回滚工单 ID。

## 成本、时延和切片

成本按每次成功修复来算：tokens、模型和工具的美元开销、sandbox 机时、人工复核时间。成功的分母用「被接受且窗口内没回滚」，「测试曾经绿过」不算。「每次尝试很便宜」掩盖不了低接受率。成本告警要和接受率一起看，否则模型变贵或者变勤快，都会被看错。体验上看 time-to-first-useful-patch、time-to-resolution 和 P95 等待。

切片按 bug / feature / refactor、语言、repo 规模、安全等级、retry budget 来切。平均数会把长尾藏起来：小仓库把数字刷得很高，大单体和权限敏感的变更其实全靠 human intervention。派单策略也要进指标，只把简单 issue 交给 Agent，接受率会被 selection bias 抬高，所以要同时报覆盖率和难度切片，selection bias 单独披露。

冻结的离线集用来做 regression checks，线上用分层漏斗和任务切片，两套别合成一个总分。

## 发布流程，以及哪里会被刷

模型或 harness 升级要依次过：离线 golden（含 hidden test）、shadow（只建议不合入）、canary、发布后的回归窗口。高风险变更保持强制 review。离线决定能不能发；发了以后，质量看接受率和回归率，成本按成功修复计。模型升级只看离线涨点就上线，等于拿代理指标代替真实效用。

评测上能刷分的做法有：只把简单 issue 派给 Agent；无限 retry 把 CI 堆绿；人工大改后的 PR 仍记成 Agent 成功；忽略回滚；拿离线集的涨点代替线上漏斗。

周报模板固定下来：五层漏斗每层的人数和转化、切片、成本、P95、回滚工单。模型卡发布时离线 golden 和线上漏斗要一起贴，缺一个就不能宣称质量提升。面试时先画漏斗再报数字，要能说出你们的成功定义和分母，光复述 SWE-bench 不够。如果手里只有离线 resolve rate，就承认它只是 acceptance checks。线上 SLO 建议同时守住接受率、回滚率和每成功修复成本，只优化其中一个一定会偏。

## 追问

**成功修复的成本，分母是什么？**
「被接受且窗口内没有回滚」才算成功，「测试曾经绿过」不算。

**shadow 阶段看什么？**
看建议接受率、和人写 patch 的 diff 大小对比，以及 CI 通过但被人拒绝的原因分布。

**和测试合同怎么衔接？**
离线的 F2P / P2P 决定能不能发；这题管的是发了以后用哪套线上指标看守。

**自动合入能不能算成功？**
可以单列，但必须抽样审计，回滚了仍要从成功里扣掉，光看合入那一刻不够。
