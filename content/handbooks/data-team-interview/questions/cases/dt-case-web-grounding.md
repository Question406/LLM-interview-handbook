---
id: dt-case-web-grounding
section: cases
order: 5
level: S
title: "案例 4/4：网页里的数字是模型编的，怎么设计 hallucination penalty？"
quick: "让模型写每个数字时带上它在数据里的地址，再按地址回查，对不上就扣分，扣多少按错的类型定。只罚错的话模型会少写数字，所以另加一项覆盖率。最理想是数字直接由渲染器按地址填，当时工程上没做成。"
companies:
  - apple
tags:
  - Apple
  - Grounding
  - Hallucination
  - Reward
  - RL
  - Data Story
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Why Language Models Hallucinate (Kalai, Nachum, Vempala, Zhang)"
    url: https://arxiv.org/abs/2509.04664
    type: primary
  - title: "Enabling Large Language Models to Generate Text with Citations (ALCE)"
    url: https://arxiv.org/abs/2305.14627
    type: primary
  - title: "Learning to Reason for Factuality (Chen et al., Meta)"
    url: https://arxiv.org/abs/2508.05618
    type: primary
  - title: "Fine-Grained Human Feedback Gives Better Rewards for Language Model Training"
    url: https://arxiv.org/abs/2306.01693
    type: primary
  - title: "Anthropic: Introducing Citations on the API"
    url: https://www.anthropic.com/news/introducing-citations-api
    type: secondary
---

简单说，我们让模型写每个数字时带上它在数据里的地址，再按地址回查，对不上就扣分，扣多少看错在哪。这个方案是一步步改出来的。

问题本身很好理解。比如用户给一张季度销售表，让模型做个看板，页面上却出现「同比增长 34%」，可表里根本没有去年的数。〔填：你们当时这类页面大概占多少。〕原因有一大半在我们自己：前面为了让页面好看加了视觉奖励，统计卡片越多分越高，数据不够，模型就自己补。

最理想的做法是模型只写地址，数字交给渲染器去填，这样就编不出来了。可当时〔填：工程原因〕，没做成。于是退一步，让模型每写一个数字，旁边记一条 reference，指向渲染器数据里的位置。检查的时候按地址把值取出来，和页面上的数对一下就行。

扣分是按错的类型分开的。编出来的数、编出来的地址扣得最重，地址对了但数抄错也算重；数是对的、标签写错了，比如把 Q2 的值标成 Q3，扣得轻一些。数据里本来就没有的项，模型写「未提供」，不扣。后来又加了一项覆盖率，〔填：是不是因为看到模型开始少放数字〕，该展示的字段没展示也扣分。

这个检查我们在 rejection sampling、偏好对和 RL 奖励里都用上了，〔填：效果〕。回头看，如果工程上允许，我还是会先把渲染器直接填数这条路打通。现在这套是在输出之后补救，模型写错 reference 的情况还是要靠检查去抓。

## 追问

**reference 也是模型写的，它会不会连地址一起编？**
会。所以除了查地址存不存在，还要把页面上没带 reference 的数字单独抓出来，一律当可疑。只查带了 reference 的，模型很快就学会没把握的数不写引用。带引用生成的研究里这很常见，ALCE 测下来，当时最好的模型也有大约一半回答引用不完整。

**为什么要一个数一个数地扣，整页算对错不行吗？**
一页二十个数错了一个，整页给 0 分，模型不知道该改哪个。逐个扣学得快，Fine-Grained RLHF 在长回答上做过同样的比较，按句子给奖励比整段一个分数好。

**模型会不会全写「未提供」来躲扣分？**
会有这个倾向，覆盖率那项就是管这个的：数据里有的字段写「未提供」，照样扣。之所以不罚真的缺数据的情况，是想让「承认没有」比「编一个」划算。Kalai 他们那篇 Why Language Models Hallucinate 讲的就是，按对错打分时猜一个更划算，模型就学会了猜。Meta 用事实性分数做 RL 奖励时也碰到过模型越写越短，后来把细节程度也放进了奖励。

**合计、占比这种算出来的数怎么查？**
〔填：你们的做法，比如 reference 写成几个地址的表达式，检查时重算一遍。〕

**和视觉分放在一起，模型会不会拿好看换编造？**
会，所以视觉分要乘一个 grounding 系数，错得多了整页打折，好看的页面也赚不回来。

相关：`dt-grounding-data`、`dt-honest-fluent`、`dt-webgpt-cite`、`dt-agent-reward-spec`、`dt-pref-pair-code`
