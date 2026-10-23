---
id: dt-case-web-diagnose
section: cases
order: 2
level: S
title: "案例 1/4：agent 做网页设计很弱，怎么确定弱在哪？"
quick: "先把「不好看」拆开：能不能渲染、功能能不能用、设计好不好，分开打分，再去数失败样本落在哪一层。我们拆完发现页面大多能跑、功能也基本对，问题集中在设计都长一个样，说明模型缺的是设计上的取舍，所以下一步先试 skill。"
companies:
  - apple
tags:
  - Apple
  - Data Story
  - Evaluation
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "ArtifactsBench: Bridging the Visual-Interactive Gap in LLM Code Generation Evaluation"
    url: https://arxiv.org/abs/2507.04952
    type: primary
  - title: "WebGen-Bench: Evaluating LLMs on Generating Interactive and Functional Websites from Scratch"
    url: https://arxiv.org/abs/2505.03733
    type: primary
  - title: "Anthropic: Improving frontend design through Skills"
    url: https://claude.com/blog/improving-frontend-design-through-skills
    type: secondary
---

简单说，先把「模型做的网站不好看」拆成几层分开打分，再去数失败样本到底落在哪层。我们拆完发现，页面大多能渲染、功能也基本对，问题集中在设计上：不同的 prompt 做出来的页面长得差不多。〔填：各层失败的大致比例。〕

一开始大家的说法就是「不好看」，这句话没法指导造数据。渲染不出来，要补的是工程数据；按钮点了没反应，要补交互逻辑；长得千篇一律，才是设计的问题。三种情况要的数据完全不一样。所以我先搭了一套评测，渲染、功能、视觉各打各的分。功能那层可以写测试让 agent 去点，视觉那层没有标准答案，只能让 VLM 按一份 checklist 打分。

然后拿失败样本来分类。先人工看了〔填：多少〕条，边看边定类别，类别稳定了再让 VLM 批量打标，人再抽查。数下来最多的一类是设计趋同，比如 Inter 字体、白底紫色渐变、几乎没有动效。〔填：换成你们实际看到的典型样子。〕

这个结论决定了下一步。模型会写 CSS，缺的是设计上的判断，那就先试最便宜的办法：写一份设计规则放进上下文，看能修好多少。我当时写的假设是「加了规则，视觉分明显涨，功能分不动」。要是视觉分不动，就说明光靠 prompt 不够，得去造数据。

〔填：回头看你会改什么，比如 judge 和人评的一致率应该更早测。〕

## 追问

**为什么不直接让人打分？**
人评适合最后把关，太慢，没法每天迭代。日常用自动打分，定期拿人评去校准 VLM judge。

**VLM judge 靠得住吗？**
先测它和人工 pairwise 的一致率，一致率低的维度不拿来做决定。另外只截首屏会漏掉交互之后的状态，要按时间多截几张，ArtifactsBench 就是截三张图，再按每题一份 checklist 打分。

**功能测试怎么写？**
可以照 WebGen-Bench 的做法：每个功能点写一条测试，让 UI agent 去点页面，判 YES、PARTIAL 或 NO。他们测下来，DeepSeek-R1 驱动的 Bolt.diy 也只有 27.8%。

**「设计趋同」这个判断有依据吗？**
Anthropic 讲 frontend skill 的博客描述过一模一样的现象，叫 distributional convergence：没有引导的时候，模型会落到训练数据里最安全、最常见的设计上。

**评测和训练数据怎么隔开？**
评测 prompt 单独冻结，训练 prompt 另外生成，再对评测集做 n-gram 和语义去重，见 `dt-contam-hold`。

相关：`dt-case-web-skill`、`dt-benchmark-gap`、`dt-inspect-corpus`、`dt-judge-bias`、`dt-data-story`
