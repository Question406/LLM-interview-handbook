---
id: cu-reproducible-benchmark-run
section: computer-use
order: 2
level: S
title: 云服务、网页和 GUI 都会变化：怎样发布一条可复现、可比较的 Computer-use benchmark run？
quick: "冻结整套版本包：VM 或容器、账号与预置数据、任务资料、外部服务 mock、Harness、随机种子、动作和时间预算，模型版本只是其中一项。每次保存执行轨迹和环境版本，多次重跑后报方差，frozen 分和 live 分分开报。"
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

一条能比较的 run，要冻住的是整套版本包：环境、fixture、mock、harness、预算，模型版本只是其中一项；然后多次重跑报方差，frozen 和 live 分开报。GUI 评测复现不了，多半怪不到模型头上，是页面改版、登录态、DPI、时钟、后台通知和真实 SaaS 在漂。

比如有一道任务是「整理今天的邮件」。不冻时钟，明天跑的就是另一批邮件；DPI 换了，同一个坐标会点到别的位置；登录态过期，任务卡在验证码上。只冻模型版本就发 leaderboard，这样的数字没法比。一个「提升两个点」，没有重跑方差和环境 digest，也算不上结果。

## 版本包里要有什么

一条 run 要标出：task ID 与任务版本、初始 VM / 容器 image digest、账号 fixture 与种子数据、浏览器与 OS 版本、外部 API 是 mock 还是 live、harness 与 oracle 版本、模型 snapshot、prompt/ tool 字段和类型规范（schema）hash、sampling seed、动作步数与实际耗时预算。分辨率、设备像素比（DPR）、语言 locale、时区也要写进合同，不然相同坐标也可能指向不同的位置。

真实云服务只放在 live 轨，frozen 轨一律用 snapshot 或 mock，评测时不许打没有版本化的生产站点。登录态用预置 cookie 或本地账号，别每次都走验证码。能冻时钟的任务就冻上。

## 记什么、怎么报

每次执行保存 observation、action、tool result、屏幕 / DOM checkpoint、oracle 逐条结果，以及失败原因（`timeout` / `oracle_fail` / `env_crash` / `auth_expired`）。artifact 和环境 digest 绑在一起存，缺 checkpoint 的 run 不进正式对比。环境崩溃和模型失败分两列记，否则 harness 一抖，模型分数就跟着抖。

有随机性的环境至少要多次重跑，报均值、方差、超时率，单次的百分点说明不了什么。提交结果时附上环境 digest、重跑次数、超时率、env_crash 率，缺这四项，百分点就没有对照物。比较两个模型必须用同一个任务版本包，换过 mock 或 DPI 的数字不能直接相减。

Live benchmark 也有价值，它反映新鲜度和站点漂移，只是不能和冻结环境的分数加成一个总分。我会分别报 frozen reproducible score 和 live robustness score，放在两张表里，免得读者把漂移当成退化。能发表的是带版本包和方差的 frozen 分，live 分用来看 benchmark 是不是过时了，别拿它刷榜。发布页面把 frozen 包的下载地址和环境 digest 放在分数旁边，缺版本包的分数没法用来做可复现的比较。网页会变，正因为这样才要分 frozen 和 live，这不能当放弃复现的理由。

评测里容易刷出来的做法有：对着会变的网站一直调到绿再截图发论文、不报超时、把环境崩溃算成模型失败或者反过来全甩给环境、只跑一次。

## 追问

**为什么要 mock 外部服务？**
不 mock 的话，同一个任务的 oracle 要依赖第三方账本，没法复现，也拦不住真实扣款。

**固定 seed 对 GUI 够吗？**
不够。动画、焦点、通知还是会抖，所以要多 seed 重跑并报方差。

**和 SWE 的 run contract 差在哪？**
代码任务主要冻 commit；计算机使用还要冻像素环境、输入法、locale 和第三方 mock。
