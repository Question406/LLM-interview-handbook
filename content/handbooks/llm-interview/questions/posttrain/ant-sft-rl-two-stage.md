---
id: ant-sft-rl-two-stage
section: posttrain
order: 124
level: A
title: 蚂蚁：SFT 和 RL 两阶段各自解决什么？
quick: >-
  SFT 先把格式、领域知识和可解析输出克隆到基座上，降低后续探索的无效轨迹；RL 再用奖励优化期望回报，处理示范覆盖不到的权衡与错误抑制。跳过
  SFT 直接 RL 常得到乱格式和零有效组；只用 SFT 则难突破示范上限。
tags:
  - Ant Group
  - SFT
  - RL
  - Post-Training
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型llm算法日常实习面经
    url: https://www.nowcoder.com/feed/main/detail/c6aadaf60f9c431bbe0738e0c802dfd7
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型 LLM 算法日常实习
- 届别 / 流程：日常实习；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-31
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“SFT和RL两阶段的意义”**

这块容易直接答成「先拟合再拟合」，或者说「RL 就是继续做 SFT，只是换了损失」。方向从一开始就不同。SFT 最小化正向 $D_{\mathrm{KL}}(p_{\mathrm{data}}\|\pi)$，mode-covering，数据里出现过的写法都得给质量；RL 在当前策略上最大化奖励，并加反向 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$，mode-seeking，见 `fund-kl-directions`。跳过 SFT 直接组采样，有效组常为零，格式全错，奖励全相同；只用 SFT 则停在示范分布，示范里的坏峰压不掉，示范外的更好路径也找不到。蚂蚁金融场景还要把合规拒答同时写进两阶段，不能指望第二阶段自己长出来。

## SFT：把格式铺上，降低无效探索

目标是把基座变成「会做这道题的格式」：指令遵循、领域术语、工具 schema、可解析思维链和基本正确率。指标应看格式通过率、基础任务成功和 holdout 不崩，不是只看 CE loss 下降。没有这一步，GRPO 对同一题采 $n$ 条，几乎全是乱码或解析失败，组内 $\mathrm{std}(r)=0$，优势恒零，见 `sys-rl-group-n`。PPO 同样会拿到全是零的终局奖，GAE 没有可传的信号。SFT 的几何代价也要说：它不敢丢掉数据里出现过的峰，有害或啰嗦模式只要在示范里，就会被覆盖。清洗能减少坏峰，但不能把正向 KL 变成 seeking，只要坏峰还在经验分布里，MLE 就得给质量。

冷启动还可以穿插拒绝采样：用规则滤出合法轨迹再克隆。那仍是 SFT 族，不是 RL。门禁没过就切第二阶段，后面所有「算法选型」都在浪费 rollout。

## RL：在可执行奖励上探索与权衡

$$
\max_\pi\ \mathbb{E}_{y\sim\pi}[r(x,y)]-\beta D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}}).
$$

这一阶段的目标是探索示范外的更好路径，压制看似合理但业务失败的输出，并在安全、成本和正确率之间做权衡。没有可靠奖励（verifier、规则引擎或校准过的 RM），这一阶段不成立。切分门禁建议量化：格式稳定、verifier 精度可接受、同一 prompt 采样已经出现对错混合，再切 RL。GRPO 此时才有非零 $\hat A$；PPO 才有可学的 GAE。两阶段不能互相替代：SFT 没有「允许遗忘」这一项，RL 没有「从零学会 schema」这一项。资源不够时可以用 DPO 做离线偏好，它仍是反向 KL 换元，但探不到新工具路径，见 `ant-why-dpo-under-resource`。

## 追问

- **为什么不能只 RL？** 有效组为零，rollout 全是格式失败，GRPO 优势恒零，PPO 的 $r$ 也没有可学结构。
- **为什么不能只 SFT？** 正向 KL 突破不了示范上限，也压不住示范里的坏峰；业务权衡不在数据里就学不会。
- **DPO 算哪一段？** 离线偏好，数学上来自反向 KL 约束的闭式解；有 verifier 要探索时不够，只能当中间对齐。
- **切 RL 的量化门？** 格式通过率、同题对错混合比例、verifier 精度 / 逃逸率，而不是 CE 降了就切。
- **合规拒答放哪？** SFT 示范里必须有，RL 硬门里也必须有。只放第二阶段，第一阶段会先把错误格式学牢。
