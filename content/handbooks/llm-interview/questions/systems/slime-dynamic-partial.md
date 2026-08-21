---
id: slime-dynamic-partial
section: systems
order: 258
level: S
title: slime 里 DAPO 动态采样和 partial rollout 怎么配？半截轨迹算 on-policy 吗？
quick: >-
  `--over-sampling-batch-size` 大于 `--rollout-batch-size`，用
  `--dynamic-sampling-filter-path` 丢掉全对/全错组（官方例子
  `check_reward_nonzero_std`）。多采出来的未完成请求走 `/abort_request`，开
  `--partial-rollout` 把半成品塞回 Buffer。半截是旧权生成的，要 `--mask-offpolicy-in-partial-rollout`
  或 `--use-tis`，不能当新的 on-policy token。
tags:
  - slime
  - DAPO
  - Partial Rollout
  - VeRL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
  - title: LMSYS slime 介绍
    url: https://www.lmsys.org/blog/2025-07-09-slime/
    type: primary
---

陷阱是把动态采样说成「把 temperature 调高一点」。DAPO 要解决的是 **零信息组**：整组全对或全错，$\mathrm{std}(r)=0$，GRPO 优势为 0，见 `sys-rl-group-n`。slime 的做法是多采、按组过滤、把还在跑的请求 abort，再决定半截轨迹怎么用。半截 **不是** 新的 on-policy token。温度管的是组内多样性，动态采样管的是这组有没有可学信号，两条轴不要拧在一个开关上。面试按三步答：filter 保证有效组、abort 避免长尾白烧、mask/TIS 处理旧 prefix。只说「我们开了 DAPO」而不提半截是否 on-policy，下一问会把数学拆穿。验收看零方差比例、partial 复用、mask 掉的 token，不看 flag 是否打开。

## 多采再滤

典型配置：`--over-sampling-batch-size 64 --rollout-batch-size 32 --n-samples-per-prompt 8`，`--dynamic-sampling-filter-path` 指向 `check_reward_nonzero_std` 一类函数，按组 reward 标准差丢掉零方差组。多出来的 prompt 是为了在滤完之后仍凑够 `--rollout-batch-size` 个有效组，不是为了把 batch 虚报大。

过滤发生在组级：同一 prompt 的 $n$ 条要一起留或一起丢。不要把「某条分数低」当动态采样，那是另一套 rejection。温度、nucleus 管的是组内多样性；动态采样管的是 **这组有没有可学信号**。两者都缺时，加 $n$ 也救不了全错组。over-sampling 的代价是多烧 decode：64 采完再丢一半，墙钟已经付了。所以要盯「滤完后的有效组 / 名义 over-sample」，而不是把 over-sample 倍数开到很大装好看。filter 函数必须稳定、无随机性差异跨 rank，否则又变成分布式 hang 的分叉源。官方 `check_reward_nonzero_std` 是最小实现，生产上还可以按难度、长度、格式分再滤，但要声明你改了数据分布。

## 半截轨迹：abort 与回收

够数之后，还在飞的请求走 `/abort_request`。不开 `--partial-rollout`，这些 token 直接扔掉，decode 算力白烧。打开后，未完成 `Sample` 写回 Data Buffer，下次从断点续写；`--buffer-filter-path` 默认 FIFO（`pop_first`）。

续写前半段来自 **上一版** $\theta$。本步新权只生成了后缀。若把整条当 on-policy 做 ratio，前半段的 $\pi_{\mathrm{old}}$ 已经对不上当前 $\pi_\theta$，这是 stale prefix。两条合法处理：

- `--mask-offpolicy-in-partial-rollout`：已有 `response_length` 的 mask 置 0，只训本步新生成的 token。
- `--use-tis`：对旧 token 做截断重要性采样，而不是假装 $\rho=1$。

两边都关 = 把 stale prefix 当 on-policy，KL 和 clip 会 silently 偏。验收看 zero-std 组比例、partial 复用率、mask 掉的 token 占比，不看「开了 dynamic sampling」。半截续写还有长度尾部问题：上次没写完的往往是最长、最难的题，FIFO 把它们优先弹出，下一步会被同一批长尾拖住。这和「动态采样提高有效组」是相反的压力，要用 `--buffer-filter-path` 或长度惩罚对冲，不能只开 partial 就以为长尾消失了。mask 掉的 token 不进 loss，等于你付了 decode 却不训它们——这是用算力换利用率，账要算清楚。TIS 则把旧 token 留在 loss 里但降权，方差更大，clip 更要紧。面试把 abort、recycle、mask/TIS 说成三步，比说「我们开了 DAPO」像做过。

## 和 veRL 怎么对

veRL 社区用 DAPO recipe + fully async 的 staleness 阈值丢过旧轨迹。slime 把 abort / recycle / mask 做成一等开关，和 Data Buffer 绑在一起。字节「GRPO 长尾」用这三步答：多采滤零方差 → abort 回收半截 → 旧 token mask 或 TIS。不要把 partial rollout 说成「免费加速」：它换的是利用率，买的是 off-policy 债。

## 三步怎么验收

字节长尾题用 slime 答：多采滤零方差 → abort 回收半截 → 旧 token mask 或 TIS。验收不要看开关是否打开，看零方差组比例是否下降、partial 复用率、mask 掉的 token 占比、以及 holdout 有没有因为 stale prefix 变差。FIFO Buffer 会把没写完的长题优先送回来，长尾可能更尖，要用 filter 或长度惩罚对冲。over-sample 倍数开太大只是多烧 decode，滤完凑满 `--rollout-batch-size` 即可。两边 mask 和 TIS 都关，等于把上一版权的 prefix 当 on-policy，clip 和 KL 会 silently 偏——这比「没开动态采样」更危险，因为看起来在训、数学已经错了。和 veRL DAPO recipe 对答时，强调 slime 把 abort / recycle / mask 做成一等 flag，而不是藏在 trainer 循环里。半截轨迹不是免费加速，是用 off-policy 债换利用率。

半截轨迹是旧权生成的 prefix，不能当新的 on-policy token，这是这题和「开了 DAPO」之间的差。mask 把已有长度置 0，TIS 把旧 token 留在 loss 里但降权；两边都关是 silent 的数学错误。FIFO 会把最长最难的半截优先送回，长尾可能更尖。over-sample 只为滤完仍凑满 batch，再大是白烧 decode。面试按 filter → abort → mask/TIS 三步答，并报零方差比例和 mask 占比，而不是报开关名字。

## 追问

- **半截算不算 on-policy？** 不算。前半段是上一版 $\theta$ 生成的。必须 `--mask-offpolicy-in-partial-rollout` 把已有 `response_length` 置 0，或 `--use-tis` 做截断 IS。两边都关等于把 stale prefix 当新 token。
- **over-sampling 是不是越大越好？** 滤完要能凑满 `--rollout-batch-size`；再大只是多烧 decode。盯有效组比例和 zero-std 下降，不是盯 over-sample 倍数。filter 还要跨 rank 稳定，否则又成分叉。
- **FIFO Buffer 会不会让最难的题永远排前面？** 默认 `pop_first` 偏公平；没写完的往往是最长最难的题，下一步会被同一批长尾拖住。可用 `--buffer-filter-path` 换策略，但要声明 freshness 变了。
- **和 fully-async 一起开吗？** 可以，但 stale 来源变成两条：partial 的旧 prefix，以及跨 rollout 的旧整条。TIS / freshness 要一起配，见 `slime-async-train`。不要只开一个开关就报已经处理 off-policy。
- **动态采样是不是调温度？** 不是。温度管组内多样性；动态采样管这组有没有可学信号（$\mathrm{std}(r)\neq 0$）。两条轴都缺时，加 $n$ 也救不了全错组。
- **abort 掉的算力怎么算？** 没开 partial 就是白烧；开了是用 off-policy 债换利用率。mask 掉的 token 付了 decode 却不进 loss，账要算清楚，不能只报「吞吐涨了」。
- **filter 带随机会怎样？** 不同 rank 丢掉不同组，轨迹数不一致，下一步 collective 可能 hang。filter 必须纯函数、跨 rank 稳定，见 `sys-distributed-hang`。
- **只开动态采样不开 partial 可以吗？** 可以，零方差组会少，但够数之后仍在飞的长请求被扔掉。长尾墙钟降不下来。字节那道题通常三步都要，见 `byte-grpo-rollout-tail-gpu`。
- **半截续写前要检查什么？** `policy_version` 是否已变、mask 是否盖住旧 `response_length`、Buffer 弹出策略会不会把最长题堆在下一步。三件事没对齐，partial 就是把 stale 写进 on-policy loss。动态采样不是调温度；半截不是新的 on-policy token。两边 mask 和 TIS 都关是 silent 数学错误。
