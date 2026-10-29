---
id: slime-dynamic-partial
section: systems
order: 258
level: S
title: slime 里 DAPO 动态 sampling 和 partial rollout 怎么配？半截轨迹算 on-policy 吗？
quick: >-
  先多 sampling，再按组过滤奖励零方差的组；凑够有效组后中止其余请求，用 `--partial-rollout`
  回收未完成轨迹。旧前缀由上一版权重生成，续写时要 mask 掉它，或用 TIS 修正。
tags:
  - slime
  - DAPO
  - Partial Rollout
  - VeRL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: slime 使用文档
    url: 'https://thudm.github.io/slime/zh/get_started/usage.html'
    type: primary
  - title: LMSYS slime 介绍
    url: 'https://www.lmsys.org/blog/2025-07-09-slime/'
    type: primary
---

slime 用多 sampling 和按组过滤来凑够有学习信号的组，再中止剩余请求，把未完成轨迹留到下一步续写。需要单独处理旧前缀，因为它来自上一版策略，不能把整条续写都当作 on-policy 数据。整组全对或全错时，$\mathrm{std}(r)=0$，GRPO 优势为 0，这就是 DAPO 动态 sampling 要过滤的组，见 `sys-rl-group-n`。

典型配置：`--over-sampling-batch-size 64 --rollout-batch-size 32 --n-samples-per-prompt 8`，`--dynamic-sampling-filter-path` 指向 `check_reward_nonzero_std` 一类函数，按组 奖励分数（reward） 标准差丢掉零方差组。多采这些 prompt，是为了过滤后仍能凑够 `--rollout-batch-size` 个有效组。

同一 prompt 的 $n$ 条 response 要一起留或一起丢。单独丢掉低分回答属于 rejection；动态 sampling 检查整组有没有可学信号，温度和 nucleus 则控制组内多样性。两方面都不足时，增加 $n$ 也未必救得了全错组。over-sampling 会增加逐 token 生成（decode）的成本：采完 64 组后丢掉一半，这部分时间已经花掉，所以要测过滤后的有效组占比。filter 还必须跨 rank 稳定，随机差异会让各 rank 保留的组数不同，可能造成分布式 hang。官方 `check_reward_nonzero_std` 是最小实现；生产中也能按难度、长度和格式过滤，但要说明因此改变了数据分布。

有效组凑够后，通过 `/abort_request` 中止未完成请求。没有开 `--partial-rollout` 时，已生成的 token 会被丢弃；打开后，未完成的 `Sample` 写回 Data Buffer，下次从断点续写。`--buffer-filter-path` 默认用 FIFO，也就是 `pop_first`。

续写时，前半段来自上一版 $\theta$，本步新权重只生成后缀。若把整条当 on-policy 做 ratio，前半段的 $\pi_{\mathrm{old}}$ 已经对不上当前 $\pi_\theta$，这是 stale prefix。因此可以这样处理：

打开 `--mask-offpolicy-in-partial-rollout` 时，把已有 `response_length` 对应的 mask 置 0，只训练本步新生成的 token。也可以打开 `--use-tis`，对旧 token 做截断 importance sampling；直接取 $\rho=1$ 会忽略这段偏移。

两个开关都关掉，就会把 stale prefix 当成 on-policy 数据，KL 和 clip 会产生不易察觉的偏差。验收时看 zero-std 组比例、partial 复用率和被 mask 的 token 占比。未完成的题通常最长、最难，FIFO 优先取出它们后，下一步可能仍被同一批长尾拖住，需要用 `--buffer-filter-path` 或长度惩罚调整。mask 的代价是付过 decode 成本的旧 token 不进入损失（loss）；TIS 可以保留这些 token 并降权，但方差更大，clip 也更重要。abort → recycle → mask/TIS 的每一步都要计入这笔成本。

veRL 社区用 DAPO recipe + fully async 的 staleness 阈值丢过旧轨迹。slime 把 abort / recycle / mask 做成一等开关，和 Data Buffer 绑在一起。字节那道「GRPO 长尾」题也可以沿着多采滤零方差 → abort 回收半截 → 旧 token mask 或 TIS 解释。partial sampling 轨迹（rollout）提高利用率的同时，也增加了 off-policy 偏移。

## 追问

**半截算不算 on-policy？**
不算。前半段是上一版 $\theta$ 生成的。必须 `--mask-offpolicy-in-partial-rollout` 把已有 `response_length` 置 0，或 `--use-tis` 做截断 IS。两边都关等于把 stale prefix 当新 token。TIS 和 CISPO 不是同一个 clip，见 `pt-tis-async`。
**over-sampling 是不是越大越好？**
滤完要能凑满 `--rollout-batch-size`；再大只是多烧 decode。盯有效组比例和 zero-std 下降，不是盯 over-sample 倍数。filter 还要跨 rank 稳定，否则又成分叉。
**FIFO Buffer 会不会让最难的题永远排前面？**
默认 `pop_first` 偏公平；没写完的往往是最长最难的题，下一步会被同一批长尾拖住。可用 `--buffer-filter-path` 换策略，但要声明 freshness 变了。
**和 fully-async 一起开吗？**
可以，但 stale 来源变成两条：partial 的旧 prefix，以及跨 rollout 的旧整条。TIS / freshness 要一起配，见 `slime-async-train`。不要只开一个开关就报已经处理 off-policy。
**动态 sampling 是不是调温度？**
不是。温度管组内多样性；动态 sampling 管这组有没有可学信号（$\mathrm{std}(r)\neq 0$）。两条轴都缺时，加 $n$ 也救不了全错组。
**abort 掉的算力怎么算？**
没开 partial 就是白烧；开了是以增加 off-policy 偏移为代价提高利用率。mask 掉的 token 付了 decode 却不进 loss，账要算清楚，不能只报「throughput 涨了」。
**filter 带随机会怎样？**
不同 rank 丢掉不同组，轨迹数不一致，下一步 collective 可能 hang。filter 必须纯函数、跨 rank 稳定，见 `sys-distributed-hang`。
**只开动态 sampling 不开 partial 可以吗？**
可以，零方差组会少，但够数之后仍在飞的长请求被扔掉。长尾实际耗时降不下来。字节那道题通常三步都要，见 `byte-grpo-rollout-tail-gpu`。
**半截续写前要检查什么？**
`policy_version` 是否已变、mask 是否盖住旧 `response_length`、Buffer 弹出策略会不会把最长题堆在下一步。三件事没对齐，partial 就是把 stale 写进 on-policy loss。
