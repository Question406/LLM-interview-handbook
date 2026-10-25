---
id: slime-sglang-multimodel
section: systems
order: 263
level: A
title: slime 怎么同时 serve 会更新的 actor 和冻住的 ref / reward？
quick: "在 `--sglang-config` 中给 actor、ref、reward 分别配置 model 和 `model_path`，actor 的 `update_weights` 为 `true`，冻结模型为 `false`。每个模型有独立 router，自定义 generate 按模型名分流，总 GPU 数包含所有模型。"
tags:
  - slime
  - SGLang
  - KL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
  - title: slime SGLang Config
    url: https://thudm.github.io/slime/advanced/sglang-config.html
    type: primary
---

用 `--sglang-config` 同时挂多个模型，让 actor 接收新权重，把 ref / reward 冻结，并按模型名路由请求。如果裁判也随 actor 热更新，KL / 过滤实际用到的就是新权重，$\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{ref}})$ 会接近 0，约束也就失效。

- 训练图 KL / ratio：Megatron `--ref-load`，和 actor 同一套并行，数值稳，见训练侧 logp。
- 采样期当 judge / 过滤 / 教师：SGLang 再挂一个冻住 replica，YAML `update_weights: false`，自己的 `model_path`。

只配置 `--ref-load` 还没有给 SGLang 声明冻结模型；采样期的模型要另配，并确认 `update_weights: true` 没有误用。OPD 教师也按 `source_name` 走多模型路由，不需要另开 estimator。

`--sglang-config` 里写多个 model：`actor` 设 `update_weights: true`，`ref` / reward 设 `false`。每个模型独立 router。`args.sglang_model_routers` 是 `{name: (ip, port)}`。自定义 generate 用 `get_model_url(args, "ref")` 分流，不要全部打到默认 actor router，否则「ref」在吃新权。

计算卡数时，`--rollout-num-gpus` = 所有 model 的 `num_gpus` 之和。漏加 reward 卡，表现为起不来或挤占 actor KV。和 PD 一样，总卡必须对得上 YAML。

veRL 常在 `actor_rollout_ref` 里同卡算 ref logp，不一定再起一套 serving。slime 把「推理期多模型」当成 serving topology，把「训练期 ref」留在 Megatron。面试讲清你要的是数值 KL 还是采样期裁判；两者可以同时存在，但更新开关必须相反。reward 模型若也挂在 SGLang，同样 `update_weights: false`，并给独立 `model_path`，避免和 actor 抢同一份 HF 目录。

## 追问

**冻住模型跟着 actor 更新会怎样？**
裁判和策略同一权，KL / 过滤失效，看起来 reward 很稳，其实没约束。
**只用 Megatron `--ref-load` 够不够？**
够算训练图 KL；不够做采样期 judge（要用 SGLang 生成或打分）。按职责拆。
**`--rollout-num-gpus` 怎么填？**
所有 model 的 `num_gpus` 相加，含冻住 replica。只填 actor 会让 ref engine 没卡。
**自定义 generate 忘了分流？**
默认打 actor router，日志里叫 ref，权是新的。先打印 `get_model_url`。
