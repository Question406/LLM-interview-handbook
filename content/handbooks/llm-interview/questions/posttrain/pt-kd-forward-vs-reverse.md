---
id: pt-kd-forward-vs-reverse
section: posttrain
order: 223
level: A
title: 知识蒸馏默认用正向 KL，MiniLLM / OPD 为什么改成反向？
quick: >-
  标准 KD 在教师轨迹或全词表上最小化 $D_{\mathrm{KL}}(\pi_T\|\pi_S)$，学生必须覆盖教师所有峰，生成任务里容易把低概率尾巴学「糊」。反向
  $D_{\mathrm{KL}}(\pi_S\|\pi_T)$ 只罚学生瞎说，更适合自回归。OPD 再改成学生自己采样，并去掉 exposure bias。
tags:
  - KL
  - Distillation
  - OPD
  - MiniLLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: MiniLLM
    url: https://arxiv.org/abs/2306.08543
    type: primary
  - title: On-Policy Distillation
    url: https://thinkingmachines.ai/blog/on-policy-distillation/
    type: primary
  - title: 拼多多 - 大模型算法 秋招一面
    url: https://www.nowcoder.com/discuss/906953010406772736
    type: candidate-first-hand
---

分类 KD 用正向 KL / CE 很自然：标签分布要被学生盖住。生成式 LLM 的教师分布多峰且尾巴长，同一套正向目标会逼学生在教师几乎不说的 token 上也摊概率，回答变长、变飘。面试别答「反向更高级」。要先说生成任务怕的是 **covering 把质量摊糊**，再解释 MiniLLM 改方向、OPD 再改采样。拼多多 2026 秋招原话是「OPD 算法中的正向 KL / 反向 KL」，先答采样决定方向，再对照 SFT（正向）和 RLHF（反向）。标准 KD 在教师轨迹上做正向 covering，生成任务容易把低概率尾巴学糊；MiniLLM 改成反向 seeking，只罚学生瞎说；OPD 再改成学生采样，状态与部署一致。方向由谁吐 token 决定，不由「蒸馏」这个名称决定。

## 正向 KD：学生必须盖住教师的每一个峰

标准蒸馏最小化 $D_{\mathrm{KL}}(\pi_T\|\pi_S)$，期望在教师（或教师轨迹）上取。教师 $p$ 有、学生 $q$ 接近 0，正向 KL 爆炸，于是学生不敢漏峰——mode-covering，和 SFT 同一几何，见 `fund-kl-directions`。分类、短标签时这是优点：对的类不能漏。自回归词表上这是缺点：教师在每个位置都有长尾，正向会逼学生给大量低质量 token 留概率，生成时采样到这些尾巴，句子变长、变散、变「像教师的平均」而不是「像教师会选的那一句」。

Off-policy 实现还常在教师上下文里算 CE：下一 token 的监督来自教师 prefix。学生部署时却吃自己的 prefix（exposure bias）。训练分布和推理分布不一致，方向问题会被放大：covering 学到的糊分布，在学生自己滚出来的状态下更差。词表蒸馏还有一个计算问题：全词表正向 KL 要对教师分布的每个 token 都给质量，学生在低频 token 上浪费容量。实践里常做 top-k 词表截断，那其实已经在悄悄减少 covering 的负担——但截断的是教师峰的尾巴，方向仍是正向。生成任务真正想要的往往是「学生自己会说的句子里不要瞎说」，这不是截断能单独完成的，所以才改方向、改采样。

## MiniLLM：改成反向，宁可漏次优说法

MiniLLM 把目标改成 $\min D_{\mathrm{KL}}(\pi_S\|\pi_T)$。期望改到学生上：学生瞎说、跑到教师低密度区会被重罚；教师有、学生不去的次优说法 **不进期望**。这是 mode-seeking：锁住教师真正会用的峰，而不是把词表摊平。生成质量往往比「更像教师的全分布」更接近「像教师会写的句子」。

反向不是免费午餐。学生若过早锁死在一个笨拙的主峰上，就会漏掉教师里仍然有用的多样写法。温度、词表截断、是否在学生序列上算 KL，都会改变有效方向。GKD 一类工作在两种散度之间插值，知道即可；面试先把两端讲清：正向 covering、反向 seeking，生成蒸馏默认怕的是前者把尾巴学进来。MiniLLM 的论文动机写得很直白：把学生当成生成器而不是分类器，目标应对齐生成时的分布。现场若只能说「反向更适合 LLM」，要补上「适合」的是自回归采样，不是参数量。小学生、大数据时正向仍可能更好学覆盖；部署是开放生成、且已经能跟上教师主峰时，再强调 seeking。

## OPD：不仅改方向，还改谁来采样

反向 KL 仍可以在教师轨迹上算，那只是把公式左右换了，状态还是教师的。On-Policy Distillation 更进一步：**学生采样**，教师只对同一 prefix 给 $\log\pi_T$。逐步优势可写成 $\mathrm{adv}\approx\log\pi_T-\log\pi_S$。期望在 $\pi_S$ 下，仍然是反向 KL，但状态是学生自己会碰到的，exposure bias 被拿掉。

现场对照三句话就够：

- 标准 KD：教师采样（或教师文本）+ 正向 KL → covering，状态是教师的。
- MiniLLM：反向 KL → seeking，减轻糊尾巴；状态仍可能是 off-policy。
- OPD：学生采样 + 反向 KL → seeking，且 on-policy。

不要说「OPD 是一种 GRPO」。它用教师 log-prob 当稠密信号，优势估计器可以和 GRPO / PPO 正交，见 `pt-on-policy-distillation`。方向问题的答案永远是：看 token 从谁采样，再看 KL 左右哪边。把 OPD 答成「正向蒸馏的工程加速」，方向就反了。拼多多原问若只给「正向还是反向」，先答：OPD 期望在学生上，是反向；标准 KD 期望在教师上，是正向。然后再补一句：即使公式写成 CE，只要样本来自学生，有效方向仍偏 seeking。采样决定方向，名称不决定方向。这和 SFT（数据采样、正向）对 RLHF（策略采样、反向）是同一张表，见 `pt-sft-fwd-kl-vs-rlhf-rev-kl`。

面试收束：分类 KD 默认正向是因为漏类代价高；生成 KD 改反向是因为词表长尾 covering 会学糊；OPD 再把状态改成学生自己的，去掉 exposure bias。不要把三步并成一句「用反向更好」。GKD 插值、温度、词表截断都是在这条轴上滑动，先把两端讲清再谈中间。标准 KD 用正向 KL 逼学生覆盖教师所有峰，生成词表上会把长尾学糊；MiniLLM 改成反向，只罚学生瞎说，宁可漏次优说法。OPD 进一步让学生自己采样，教师只对同一前缀给对数概率，方向仍是反向，但去掉了教师上下文造成的 exposure bias。面试先答「谁采样」，再答「KL 左右哪边」，就能把拼多多原问和 SFT / RLHF 对照表接上。生成怕学糊所以改反向，分类怕漏类所以留正向。

## 追问

- **为什么分类用正向、生成改反向？** 分类标签峰少、漏类代价高；生成词表长尾，covering 会学糊。同一条 `fund-kl-directions` 几何，任务不同所以默认方向不同。把生成当整词表分类来蒸，就会把尾巴学进来。
- **反向是否一定更好？** 不一定。需要覆盖教师多样写法、或学生还远小于教师时，正向或插值可能更稳。MiniLLM / OPD 的点是生成部署更怕瞎说，不是反向在一切 KD 上占优。学生太弱时 seeking 可能锁死在错误主峰。
- **和 RLHF 的反向 KL 是同一个吗？** 几何相同、锚点不同。RLHF 锚的是 $\pi_{\mathrm{ref}}$ 与奖励；OPD 锚的是教师 $\pi_T$。不要把教师 KL 说成 reward hacking 护栏。
- **白板怎么写 OPD 目标？** 先写学生采样 $y\sim\pi_S$，再写 $\mathbb{E}[\log\pi_S-\log\pi_T]$ 或对应的 token 级 advantage，明确这是 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$。左右写反就变成又一次标准 KD。拼多多原问先答采样、再答方向。方向由采样决定，不由算法名称决定。
- **OPSD 算正向还是反向？** 前缀来自学生，但是 Zhao 论文默认全词表 $D_{\mathrm{KL}}(p_T\|p_S)$。不要和拼多多外部 OPD 题并成一句「蒸馏都是反向」。见 `pt-opsd`。
