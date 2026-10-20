---
id: tencent-qwen-vs-deepseek
section: arch
order: 201
level: A
title: 腾讯混元一面：Qwen 和 DeepSeek 差在哪，什么时候你会换底座？
quick: "比较时要分别看架构、数据和后训练。Qwen 系常用 GQA，包含稠密和常规 MoE 模型；DeepSeek 用 MLA 压缩 KV，并使用细粒度专家和共享专家。长上下文任务要比较缓存成本，中文指令和工具调用要比较后训练效果，再用同一套评测决定是否换底座。"
tags:
  - Tencent
  - Hunyuan
  - Qwen
  - DeepSeek
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496
    type: candidate-first-hand
---

## 真题记录

- 公司：腾讯 · 混元
- 岗位：大模型日常实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“Qwen 和 DeepSeek 有什么区别？你会怎么选底座？”**

常见误区是：只背参数量或复读博客「DeepSeek 更强」。比较时只讲能解释清楚的差异：注意力、MoE、后训练。换底座用同一套评测集，不要用社交媒体结论替实验。同面 MoE 题见 `tencent-moe-vs-dense`；MLA 原理见 `arch-mla`。

## 架构：GQA vs MLA，常规 MoE vs 细粒度 + 共享专家

- 注意力：Qwen 系常用 GQA，减少 KV 头数，实现较简单，也兼容标准 RoPE。DeepSeek-V2/V3 用 MLA：把 K/V 压缩成低维潜在表示，单独处理 RoPE；推理时通过矩阵吸收，避免还原完整 K/V。长上下文、大 batch 的逐 token 生成（decode）会更明显地受到缓存带宽影响；短上下文小模型上 GQA 往往够用。
- MoE：DeepSeek 细粒度专家 + 共享专家 + 负载均衡（aux / 无 aux 变体，见 `arch-moe-noaux`）。Qwen-MoE 更接近常规 top-$k$。选型时问：有没有共享专家兜底、专家粒度、训推路由是否一致。
- 其它：词表与 tokenizer、MTP / 推测解码、是否开源推理栈（vLLM 对 MLA/GQA 的成熟度）也会左右「能不能上线」，但一面先把注意力和 MoE 两条讲完。

不要把「总参数 671B」和「激活 37B」混报；DeepSeek 的卖点是激活小、容量大，见 `minimax-param-breakdown`。

## 后训练与何时换底座

- DeepSeek-R1 / 推理向：规则奖励、两阶段（监督微调（SFT） 冷启动 → 强化学习（RL））把长思维链训得很重。要长 CoT、竞赛数学、省 KV 时优先试。
- Qwen 指令版：中文对齐、工具调用、开箱模板往往更省事。要稳定 function call、中文产品、多模态 Qwen-VL 生态时优先试。
- 数据与许可：商用和蒸馏条款、是否允许继续训练，可能在比较排行榜分数之前就限制可选范围。

换底座时，用同一组输入提示比较指令跟随、工具调用、长上下文和安全表现；测量 decode 延迟与 KV 缓存开销；再检查自己的后训练主要依赖 SFT，还是基于可验证奖励的强化学习（RLVR）。R1 风格底座接短指令 SFT 可能把格式弄坏；Qwen 接纯推理 RL 可能不如从 R1 冷启动。最终对照实验，不要靠「听说换了就涨」。

## 追问

- **MLA 是不是一定更好？** 更好的是 cache；实现与 kernel 成熟度、短序列开销是代价。小模型短上下文 GQA 更简单。
- **共享专家是什么？** 每个 token 都会经过的专家，用来学习公共能力，减少对路由结果的依赖。常规 top-$k$ 没有这层兜底。
- **什么时候不换？** 现有底座在你们评测上已够、工具协议已对齐、换底座要重做全部后训练。换的成本是数据与配方，不是下载权重。
- **和混元自研底座怎么比？** 还需要考虑内部数据和推理栈的差异；开源底座用来对齐公开结果，不是替代内部基线。
- **后训练差能否用 SFT 抹平？** 部分可以（格式、中文），推理深度和 cache 结构抹不平。该换架构时换，该补数据时补。
