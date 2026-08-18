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
updatedAt: 2026-08-17
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
---

线上漏斗至少分为：尝试是否完成、是否给出可应用 patch、CI/测试是否通过、工程师是否接受、是否在发布后回滚或引入回归。每层的 denominator 都不同，不能用一个“成功率”混在一起。

成本指标用每成功修复的 tokens、模型/工具美元、sandbox 时间和人工复核时间；体验指标用 time-to-first-useful-patch、time-to-resolution、P95 latency。按 bug/feature/refactor、安全等级、语言和 repo 规模切片，否则平均数会掩盖长尾。

高风险变更保持人工 review，并抽样审计“自动接受”的 patch。模型升级必须同时过离线 golden、shadow、canary 与 post-release regression gate。
