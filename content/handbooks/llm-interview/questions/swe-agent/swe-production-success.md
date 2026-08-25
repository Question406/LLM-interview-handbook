---
id: swe-production-success
section: swe-agent
order: 6
level: A
title: 如何把离线 resolve rate 转为可靠的线上 Coding Agent quality / cost 指标？
quick: 分开看 attempt success、人工接受 patch、回滚/回归率、time-to-resolution 和每成功任务成本，并按 repo 难度、任务类型、retry budget 切片。离线测试通过不能替代人工接受和上线后的长期质量。
tags:
  - SWE Agent
  - Production Metrics
  - Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
---

离线 resolve rate 优化的是「冻结测试变绿」，线上要的是工程师愿意合、合了不回滚、成本可接受。用一个「成功率」把漏斗抹平，是最常见的汇报坑。面试官要听的是分层 denominator、切片方式和发布门禁，而不是把 SWE-bench 数字直接当 SLO。离线是必要门禁，不是线上质量的充分统计。

## 线上漏斗

至少拆五层，每层分母不同，禁止共用一个成功率：attempt 是否跑完（非超时 / 非 harness 崩溃）；是否产出可应用 patch；CI / 目标测试是否通过；工程师是否接受（合入或明确 approve）；发布后窗口内是否回滚或引入回归。自动合入的 patch 必须另计「自动接受率」，并强制抽样审计。不要把「CI 绿」等同于「人接受」，也不要把「人接受」等同于「长期质量」。人工大改后再合入的 PR，Agent 贡献要按 diff 比例或「需人工重写」标记下调，不能整单记成 Agent 成功。日志字段至少包括：任务类型、repo、retry 次数、谁点了接受、回滚工单 ID。

## 成本、时延与切片

成本用每成功修复的 tokens、模型 / 工具美元、sandbox 机时、人工复核时间；不要用「每次尝试很便宜」掩盖低接受率。成功的分母应是「被接受且窗口内无回滚」，而不是「测试曾绿过」。体验用 time-to-first-useful-patch、time-to-resolution、P95 等待。按 bug / feature / refactor、语言、repo 规模、安全等级、retry budget 切片。平均数会藏长尾：小仓库刷高、大单体和权限敏感变更全是人在兜底。冻结离线集用于回归门禁；线上用漏斗和切片，两者不要合成一个 headline。成本告警要跟接受率一起看，否则模型变贵或变勤快都会被误读。

## 发布与能刷的点

模型或 harness 升级必须过：离线 golden（含 hidden test）、shadow（只建议不合入）、canary、post-release 回归窗口。评测上能刷的是：只把简单 issue 派给 Agent；无限 retry 堆 CI 绿；把人工大改后的 PR 仍记成 Agent 成功；忽略回滚；用离线集涨点代替线上漏斗。高风险变更保持强制 review。Shadow 阶段看建议接受率、与人写 patch 的 diff 大小、CI 通过但人拒绝的原因分布。最后我会补一句：离线决定能不能发；线上质量以接受率和回归率为准，成本以成功修复计。把漏斗做成周报：每层人数、转化、切片、回滚工单。模型升级只看离线涨点就上线，是在用代理指标代替效用。现场要能说出你们的成功定义和分母，而不是复述 SWE-bench。派单策略也要进指标：若只把简单 issue 交给 Agent，接受率会被选择偏差抬高，应同时报覆盖率和难度切片。

周报模板固定五层漏斗加成本、P95、回滚。模型卡发布必须同时贴离线 golden 与线上漏斗，缺一则不能宣称质量提升。选择偏差（只派简单单）要单独披露，否则接受率不可信。

面试时先画漏斗再报数字。若只能报离线 resolve rate，就承认它只是门禁。线上 SLO 建议同时看守接受率、回滚率和每成功修复成本，三选一只优化一定会偏。

## 追问

- **成功修复的成本分母是什么？** 用「被接受且窗口内无回滚」当成功，而不是「测试曾绿过」。
- **shadow 看什么？** 建议接受率、与人写 patch 的 diff 大小、CI 通过但人拒绝的原因分布。
- **和测试合同怎么衔接？** 离线 F2P/P2P 决定能不能发；本题决定发了以后用哪套线上指标看守。
- **自动合入能不能当成功？** 可以单列，但必须抽样审计，且回滚仍从成功里扣，不能只看合入瞬间。
