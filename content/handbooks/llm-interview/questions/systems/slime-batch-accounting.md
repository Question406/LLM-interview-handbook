---
id: slime-batch-accounting
section: systems
order: 260
level: S
title: slime 的 rollout / global / micro batch 怎么对到 veRL 那套字段？
quick: "一轮轨迹数是 rollout batch size 乘每题采样数 $n$，对应 veRL 的 `train_batch_size` × `rollout.n`。`--global-batch-size` 按样本条数计，一步 on-policy 时等于这个乘积。"
tags:
  - slime
  - VeRL
  - Batch
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
  - title: 26秋招蚂蚁金服大模型算法一面
    url: https://www.nowcoder.com/feed/main/detail/e2585943c7874b3081b0878b646b6f01
    type: candidate-first-hand
---

蚂蚁那道 veRL 账本，用 slime CLI 重答。常见误区是：把 `--global-batch-size` 当成 输入提示（prompt） 数，或把 $n$ 和 batch 拧成同一个旋钮。官方写明 gbs 按 sample 计：一条 completion 才是 1。对不齐时，要么一步重复用同一批轨迹（off-policy 上升），要么 drop 掉组的一部分（GRPO 组统计坏掉）。面试我先在白板上写 $N_{\mathrm{traj}}=\mathrm{rbs}\times n$，再填 gbs 和 micro，不要从 Hydra 字段名倒推。需要同时说明四个量：每步几道题、每题几条、一次 optimizer 看见几条、每卡一次塞多少。缺一个，学习率、KL 和显存反推都会错。动态 batch 还会把 micro 作废，超长样本可能拆组，账本和长尾是同一类 bug。

## 字段怎么对

| 含义 | slime | veRL（常见 Hydra） |
| --- | --- | --- |
| 每步 prompt 数 | `--rollout-batch-size` | `data.train_batch_size` |
| 每 prompt 条数 | `--n-samples-per-prompt` | `actor_rollout_ref.rollout.n` |
| 一次 optimizer 的样本数 | `--global-batch-size` | `actor.ppo_mini_batch_size` / global |
| 一轮 采样轨迹（rollout） 训几步 | `--num-steps-per-rollout` | mini-batch 切分次数 |
| 每卡 micro | `--micro-batch-size` | `ppo_micro_batch_size_per_gpu` |

一轮轨迹数：

$$
N_{\mathrm{traj}} = \texttt{rollout\_batch\_size} \times \texttt{n\_samples\_per\_prompt}.
$$

一步严格 on-policy：把 `--global-batch-size` 设成这个乘积，`--num-steps-per-rollout 1`。`num_steps_per_rollout \gt 1` 就是同一批轨迹上多步更新，等价 PPO 的多 epoch，off-policy 程度上升，要盯 KL。开动态 batch 后 `--micro-batch-size` 被忽略，改由 token 预算切分，见 `slime-dynamic-bsz`、`sys-verl-dynamic-bsz`。

## 整除约束

`global_batch_size` 应整除 $N_{\mathrm{traj}}$。除不尽时实现会丢尾或补，GRPO 的组可能被切开：同一输入提示 的 $n$ 条必须进 同一次 优势估计。组被拆到两个 optimizer step，组均值就不是那 $n$ 条，优势定义坏了，见 `sys-rl-group-n`。面试先写

$$
\texttt{gbs} \mid (\texttt{rbs}\times n),\quad \texttt{gbs}=n\times k
$$

（$k$ 是每次更新覆盖的 prompt 数），再谈显存。micro 只影响每卡能塞多少 token / 多少条，不改变「一组有没有被拆」。veRL 的 `ppo_mini_batch_size` 有的配方写在 prompt 维、有的已经乘过 $n$，对字段时必须问一句「含不含 rollout.n」。含糊地对过去，学习率、KL 和「一步看到多少题」会对不上，复现 DAPO 数字就会差一截。`--num-steps-per-rollout` 大于 1 时，要像 PPO epoch 一样报：同一批轨迹更新几次、KL 涨多少就停。不要把它理解成「多走几步优化器所以收敛更快」，off-policy 程度在涨。动态 batch 按 token 数切 micro 时，一条超长 completion 可能独占一卡，组内其余短样本被分到别的 step，又是拆组。长尾和账本是同一类 bug。

## `--balance-data` 的坑

## 追问

- **gbs 小于乘积是什么意思？** 一轮 rollout 训多步，同一批轨迹被复用，等价 PPO 多 epoch。要配更小学习率或 TIS，盯 KL，并承认不是纯 on-policy。不要把它理解成「多更新几次所以收敛更快」。
- **gbs 大于乘积呢？** 通常不合法或会跨 rollout 拼 batch，freshness 更差。先问实现会不会直接报错。即便能跑，组可能被从两个 rollout_id 拼出来，GRPO 组均值就不是同一时刻的 $n$ 条。
- **和 veRL `ppo_mini_batch_size` 差在哪？** 名字不同，都是一次 `optimizer.step` 看见的样本条数。veRL 配方有的写在 prompt 维、有的已乘 $n$，对字段时必须问清「含不含 rollout.n」。含糊地对过去，学习率和「一步看见多少题」会对不上。
- **动态 batch 后还报 micro 干什么？** 开了就被忽略。改报每卡 token 预算和最长序列，否则按静态 micro 反推显存会对不上。超长一条可能独占一卡，组内短样本被切到别的 step，又是拆组。
- **`--balance-data` 什么时候可以开？** 非 group 算法、或你按 prompt 组做 packing 而不是按单条 FLOPs。GRPO 默认谨慎。蚂蚁面 损失（loss） 抖、组方差对不上，先查这一项和 gbs 整除。
- **`num_steps_per_rollout` 和异步是一回事吗？** 不是。前者是同一批轨迹多步更新；后者是 generate 与 train 重叠或跨步交组。两个都会引入 off-policy，但机制不同，不要用同一个词。
- **一步 on-policy 的充分条件是什么？** `--global-batch-size` 等于 `--rollout-batch-size` × `--n-samples-per-prompt`，且 `--num-steps-per-rollout 1`，并且没有把组拆到不同 DP。三条缺一，就不是「采完立刻用同一批更新一次」。
- **为什么 gbs 必须整除乘积？** 除不尽会丢尾或补样本，GRPO 的 $n$ 条可能跨两次 `optimizer.step`，组均值就不是那一组。整除是优势定义的约束，不是风格问题。
- **面试怎么报这道账本？** 先写 $N_{\mathrm{traj}}=\mathrm{rbs}\times n$，再声明 gbs 按 sample 计、一步 on-policy 时 gbs 等于乘积。四个量（题数、$n$、一次 step 条数、每卡 micro）缺一就会和 veRL Hydra 对不上。动态 batch 后改报 token 预算。`--balance-data` 可能拆组，GRPO 上默认谨慎。蚂蚁面若问 loss 抖，优先查计数单位和组有没有被切开，而不是先改学习率。gbs 不是 prompt 数，这是这道题最常见的坑。
