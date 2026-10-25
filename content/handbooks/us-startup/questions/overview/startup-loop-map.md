---
id: startup-loop-map
section: overview
order: 1
level: B
title: 美国 startup：这批公开面经里反复出现的轮次
quick: >-
  这批美国 startup 面经的电面多是一道业务题拆成三四问，要能跑。Onsite 常加一段你没见过的代码（修 bug 或接 API），外加贴近他们产品的设计，再加项目深挖。有的轮允许用 AI（Rippling），有的明文禁止（Cursor 技术面、Perplexity 动手题、Stripe 集成轮），进面前要问清。
tags:
  - Startup
  - Process
  - SWE
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Stripe Software Engineer Interview Guide (2026)
    url: https://www.tryexponent.com/guides/stripe-software-engineer-interview
    type: secondary
  - title: Rippling Offer Received, AI Coding Experience
    url: https://leetcode.com/discuss/post/7649290
    type: candidate-first-hand
  - title: Inside Cursor's hiring strategy
    url: https://www.businessinsider.com/cursor-interview-process-no-ai-on-site-project-coding-tool-2025-6
    type: primary
  - title: Perplexity Hands-on Coding Interview
    url: https://interviewresources.perplexity.ai/hands-on-coding/
    type: primary
---

这张卡用来先看个大概：美国 startup 的 SWE 面试，电面多是一道业务题拆成几个 part、要能跑，Onsite 常有一轮在你没见过的代码上干活，设计题贴着他们自己的产品，行为面多半是项目深挖。每家的具体题看后面各章；AI 能不能用各家说法相反，进面前一定要问 recruiter。

## 题怎么来的

这一张没有某一家的原题。我把 2025–2026 还能对上帖子的美国 startup SWE 面经放在一起，发现它们的轮次安排挺像。公司还是私营、候选人也把它当 startup 面的，收在后面各章。已经上市的 Coinbase、Datadog、Snowflake、DoorDash 没放进来。

## 轮次

招聘官电话很短，会问为什么是这家。技术电面通常是一道题，题干很长，分成几个 part，过了测试再开下一个 part。数据结构就是 map、区间、字符串、图上的环。复杂度很少是得分点，写不完、写不干净才会挂。

Onsite 里至少有一轮不在白纸上写算法。Stripe 叫 Bug Bash 和 Integration，仓库不是你的，或者 API 文档要现查。Scale 把一段能调他们模型的代码给你，让你查为什么没有输出。Headway、Notion 的设计题围绕他们自己的产品限定范围，不让你画 Twitter。

行为面在 startup 里经常变成项目深挖。Harvey 的 hiring manager 会在一个项目上待满一小时，Anduril 会追「为什么是国防」。

## AI 能不能用

三家公开说法相反，进面前先问 recruiter，别自己猜。

- Rippling 允许。2026 年有拿到 offer 的人写，电面和 onsite coding 都可以用 ChatGPT、Cursor、Claude，代码仍要贴回 HackerRank 跑。面试官不建议把整题粘给模型。
- Cursor 部分禁止。CEO Michael Truell 在 YC 播客里说，第一轮技术面除了自动补全，不许用 AI。后面是到办公室做两天真实项目。
- Perplexity 的官方动手编码不许用 AI 写答案。可以查语言文档，也可以用搜索或 AI 问标准库怎么用，主要部分不能让它写。Stripe 集成轮同样写明不许用 AI coding assistant。

## 后训练

MLE 岗和 SWE 岗是两套。Scale 2026 年初有一篇博士挂经，第一面被写成 post-training 八股，题面本身帖子里没公开，见 `scale-posttrain-oral`。Snorkel 和 Fireworks 没有对得上的候选人原话，收的是他们自己发表的做法，也就是迭代式直接偏好优化（DPO），以及只给一个打分函数的强化微调。

## 这次没收成题的

这几家我查过，但公开文本对不上具体题面，所以没有单独开卡：Ramp（CodeSignal 加结对，汇总站列了账本、webhook、对账，没有一份能核对的候选人原帖）、Plaid、Brex、Glean、Linear、Vercel、Applied Intuition。Figma 2022 年已经并进 Adobe，也不放在 startup 里。

## 追问

**电面要不要先写最优解？**
先交一个能过当前 part 的版本。Stripe 运费、Rippling 骑手结算都是规则一层层往上加，推倒重写会超时。

**设计题要不要背 CAP？**
不用先背。Headway 的 Airbnb 题写明是 startup 规模，要的是模型和 API。Ramp 的汇总文章把重点放在幂等和对账，但那些具体题我没有收，因为来源对不上。
