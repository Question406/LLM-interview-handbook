---
id: company-pdd
section: companies
order: 11
level: A
title: 拼多多：大模型算法岗应重点准备什么？
quick: "拼多多电商落地问得很重：监督微调（SFT）去模板化和 train/test 去重、Prompt 版本化回滚、可执行离线评测、Long Context 成本折中。算法侧会追 Pretrain vs SFT、PPO clip 后为什么还要 min、正向和反向 KL，手撕常见 top-k / BPE。"
tags:
  - PDD
  - 真题导航
  - "2026"
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多日常实习 大模型算法一面分享
    url: https://www.nowcoder.com/feed/main/detail/ba50ad3b3777443da540fcd9cfaf7377
    type: candidate-first-hand
  - title: 大模型算法二面-日常实习-拼多多
    url: https://www.nowcoder.com/feed/main/detail/a94c16e304bb40a188eeda38c5e973c8
    type: candidate-first-hand
  - title: 拼多多 - 大模型算法 秋招一面
    url: https://www.nowcoder.com/discuss/906953010406772736
    type: candidate-first-hand
---

拼多多面经里，业务题和公式题会在同一轮出现。前面刚讲完模板怎么灰度回滚，后面就可能让你在白板上写 PPO 的 clip + min。搜广推方向还会额外追推荐和用户侧目标，但基础后训练不能有明显空洞。

## 准备主线

1. 数据和评测要避免监督微调（SFT）模板化，用 lexical + semantic 去重防泄漏，离线集覆盖语言和类目。
2. 上线工程要做到 Prompt / 模板不可变 release、canary、按任务桶监控；训练不稳定要有一棵排查树。
3. 算法公式会问 Pretrain vs SFT、PPO 为什么 clip 之后仍取 min、正向 KL 和反向 KL 的优化含义。
4. 上下文成本要讲 Long Context 的常见路径，以及「能看长文本但不太贵」的折中。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- 拼多多：SFT 数据怎样避免模板化，并做 train / test 去重
- 拼多多：Prompt / 模板如何版本化、回滚并避免一次改动导致整体波动
- 拼多多：Pretrain 和 SFT 分别解决什么问题
- 拼多多：PPO clip 之后为什么仍然需要 min
- 拼多多：Long Context 如何做到能看长文本但不太贵
- 拼多多：如何做一套可执行的离线评测集，覆盖不同语言与类目
- 拼多多：多模态如何检查图文一致、不编造
- 拼多多：训练不稳定怎么排查
- 拼多多秋招：正向 KL 和反向 KL 有何区别（OPD：学生采样 → 反向 KL；OPSD 另拆一层）
- OPSD 和 OPD 差在哪？同一套权重怎么当自己的老师？
- Self-OPD 家族怎么分？u-OPSD、π-Distill、LOPD 各补哪块？
- SFT 在最小化哪种 KL？RLHF 又在最小化哪种？
- 对齐为什么用 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，而不是反过来？
- PPO 里的 Trust-Region KL 和 Drift KL 是同一个东西吗？
- 知识蒸馏默认用正向 KL，MiniLLM / OPD 为什么改成反向？
- 对齐为什么必须加 KL？系数太大或太小会怎样？
- Schulman 的 $k_1/k_2/k_3$ 各估什么？
- JS 散度和 KL 散度差在哪？为什么 GAN 早期爱提 JS？
- 自适应 KL controller 在做什么，比固定 $\beta$ 好在哪？
- KL 按 token 平均还是按整段序列加总？两种写法差在哪？
- Forward / Reverse KL 后训练八股要准备哪些题？
- [[pdd-context-overflow|拼多多：对话超过上下文后，滑动窗口、摘要和向量召回怎么选]]
- 拼多多：文档怎么切块，chunk 大小和重叠如何定
- 拼多多：为什么用 Token 而不是字符或单词
- 拼多多：上下文窗口越大越好吗
- 拼多多：为什么用多 Agent，改成单 Agent 会怎样
- 拼多多：检索返回很多相关内容时如何选最相关的
- 拼多多应用开发：手写 Attention 时要写出哪些形状和 Mask？
- 拼多多应用开发：如何手写交叉熵，数值上要防什么？
- 拼多多暑期实习：如何模拟 BPE，暴力实现之后还能怎么优化？
- 拼多多日常实习：对齐为什么需要偏好对或奖励信号？
- 拼多多：为什么常压缩前 70% 上下文？开头几轮需求不重要吗？
- 拼多多：OpenClaw 的记忆是什么？Spec-driven code agent 又在解决什么？
- 拼多多推理岗：FlashAttention V1–V3 差在哪，什么是 Dynamic Batching？
