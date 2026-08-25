---
id: cu-reproducible-benchmark-run
section: computer-use
order: 2
level: S
title: 云服务、网页和 GUI 都会变化：怎样发布一条可复现、可比较的 Computer-use benchmark run？
quick: 版本化的不只是模型。我会锁定 VM / 容器、账号和 fixture、任务资产、外部服务 mock、harness、模型快照、seed、动作和时间预算；保存 trace 和环境版本，多次重跑再报方差。
tags:
  - Benchmark
  - Reproducibility
  - Computer-use
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: OSWorld-V2
    url: https://github.com/xlang-ai/OSWorld-V2
    type: primary
---

GUI 评测不可复现，多半不是模型，而是页面改版、登录态、DPI、时钟、后台通知和真实 SaaS 漂移。只冻模型版本就发 leaderboard，数字没法比。我会讲整条 run 的版本包：环境、fixture、mock、harness、预算，以及 frozen 和 live 分报。一个「提升两个点」如果没有重跑方差和环境 digest，不能当结果。

## 必须冻结的清单

一条 run 标出：task ID 与任务版本、初始 VM / 容器 image digest、账号 fixture 与种子数据、浏览器与 OS 版本、外部 API 是 mock 还是 live、harness 与 oracle 版本、模型 snapshot、prompt / tool schema hash、sampling seed、动作步数与墙钟预算。分辨率、DPR、语言 locale、时区也要进合同，否则同一坐标协议都会漂。真实云服务只属于 live 轨；frozen 轨必须用 snapshot 或 mock，禁止评测时打未版本化的生产站点。登录态用预置 cookie / 本地账号，不要每次走验证码。时钟可冻的任务要冻，否则「今天的邮件」无法复现。

## 记什么、怎么报方差

每次执行保存 observation、action、tool result、屏幕 / DOM checkpoint、oracle 逐条结果、失败原因（`timeout` / `oracle_fail` / `env_crash` / `auth_expired`）。有随机性的环境至少多次重跑，报告均值、方差、超时率，而不是单次百分点。动画、焦点、通知仍会抖，seed 不够，所以要多 seed。artifact 与环境 digest 绑定存放，缺 checkpoint 的 run 不能进正式对比。环境崩溃与模型失败必须分列，否则 harness 一抖，模型分数就跟着抖。

## Frozen 与 live 不要混

Live benchmark 反映新鲜性与站点漂移，有价值，但不能和冻结分加总成一个 headline。分别报 frozen reproducible score 与 live robustness score。评测上能刷的是：对着会变的网站调到绿再截图发论文、不报超时、把环境崩溃算模型失败或反过来全甩给环境、只跑一次。发布数字时附上重跑次数、失败归因表和环境 digest。可发表的是带版本包和方差的 frozen 分；live 分用来看是否过时，不是用来刷榜。提交结果时附环境 digest、重跑次数、超时率、env_crash 率。缺这四项，百分点没有对照物。现场被追问「网页变了怎么办」时，答案是分轨，而不是每周重标一次当同一条曲线。比较两个模型必须用同一任务版本包；换过 mock 或 DPI 的数字不能直接减。

发布页面把 frozen 包的下载地址和环境 digest 放在分数旁边。没有包就没有分数。Live 轨用不同的表，避免读者把漂移当退化。比较模型时复制同一包，而不是各自准备网站账号。

我会讲版本包：镜像、fixture、mock、DPI、预算、方差。网页会变不是放弃复现的理由，而是必须分 frozen / live。没有 digest 的分数不要对外讲。

## 追问

- **为什么 mock 外部服务？** 否则同一任务的 oracle 依赖第三方账本，无法复现，也无法禁止真实扣款。
- **seed 对 GUI 足够吗？** 不够。动画、焦点、通知仍会抖，所以要多 seed 重跑并报方差。
- **和 SWE run contract 的差别？** 代码任务主冻 commit；计算机使用还要冻像素环境、输入法、locale 和第三方 mock。
