---
id: pt-kd-forward-vs-reverse
section: posttrain
order: 223
level: A
title: 知识蒸馏默认用正向 KL，MiniLLM / OPD 为什么改成反向？
quick: "标准 KD 在教师轨迹或全词表上最小化 $D_{\\mathrm{KL}}(\\pi_T\\|\\pi_S)$，学生得盖住教师所有的峰，生成任务里容易把低质量的长尾也学进来。MiniLLM 改成反向 $D_{\\mathrm{KL}}(\\pi_S\\|\\pi_T)$，只罚学生瞎说；OPD 再让学生自己采样，去掉 exposure bias。方向看 token 由谁采样，跟算法叫不叫蒸馏无关。"
tags:
  - KL
  - Distillation
  - OPD
  - MiniLLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
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
生成任务里，正向 KL 会逼学生给教师的整条长尾都分概率，有限的容量被摊薄，回答变长、变飘；所以 MiniLLM 改成反向 KL，只罚学生跑到教师不会去的地方。OPD 再进一步，连采样也换成学生自己来，状态和部署时一致。判断方向就看一件事：token 是谁吐的，期望在谁身上取。

拼多多 2026 秋招的原题是「OPD 算法中的正向 KL / 反向 KL」。我会先答采样决定方向，再拿 SFT（正向）和 RLHF（反向）对照一下，这样面试官马上知道我分得清。别答成「反向更高级」，要先讲生成任务为什么怕把容量分散到过多低质量输出上。

## 正向 KD：学生得盖住教师的每一个峰

标准蒸馏最小化 $D_{\mathrm{KL}}(\pi_T\|\pi_S)$，期望在教师或教师轨迹上取。教师 $p$ 有概率、学生 $q$ 接近 0 的地方，正向 KL 会爆，所以学生不敢漏峰。这就是 mode-covering，和 SFT 是同一个几何，见 `fund-kl-directions`。

分类、短标签的时候这是优点，对的类不能漏，所以分类 KD 用正向 KL / 交叉熵损失（CE）很自然。换到自回归词表上就成了缺点：教师在每个位置都有一条长尾，正向 KL 逼学生给大量低质量 token 留概率，生成时一采样就采到这些尾巴。比如教师在某个位置把大部分概率给了「因此」，剩下一点散在一大串奇怪的词上，学生为了不漏，也得给这一串词都留概率，结果句子越写越散，越来越像「教师的平均」，不像教师真会选的那一句。

off-policy 实现里还有一层问题。CE 常常是在教师的上下文里算的，下一个 token 的监督来自教师的 prefix，学生部署时用的却是自己生成的前缀，这就是 exposure bias。训练和推理分布不一致，会把方向问题放大：覆盖了大量模式后学到的分布，放到学生自己的上下文里表现可能更差。全词表正向 KL 还有计算上的负担，学生在低频 token 上浪费容量。实践里常做 top-k 词表截断，这其实已经悄悄减轻了 covering，但截掉的是教师峰的尾巴，方向还是正向。生成任务想要的是「学生自己会说的句子里别瞎说」，光靠截断做不到，所以才去改方向、改采样。

## MiniLLM：改成反向，宁可漏掉次优说法

MiniLLM 把目标改成 $\min D_{\mathrm{KL}}(\pi_S\|\pi_T)$，期望换到学生身上。学生瞎说、跑进教师的低密度区，会被重罚；教师有、学生没去的次优说法，根本不进期望。这是 mode-seeking，锁住教师会用的那几个峰，不去把词表摊平。论文的动机写得很直白：把学生当生成器看，目标就该对齐生成时的分布。所以生成质量更接近「像教师会写的句子」。

反向 KL 也有代价。学生如果过早锁在一个笨拙的主峰上，教师里那些有用的多样写法就漏掉了。温度、词表截断、KL 是不是在学生序列上算，都会改变有效方向。GKD 一类工作在两种散度之间插值，知道就行，面试先把两端讲清楚。如果现场只说得出「反向更适合 LLM」，要补一句：适合的是自回归采样，跟参数量无关。学生较小、数据较多时，正向照样可能更容易学到覆盖；部署是开放生成、学生已经跟得上教师主峰的时候，再强调 seeking。

## OPD：方向改了，采样的人也换了

反向 KL 也可以在教师轨迹上算，那只是把公式左右换了一下，状态还是教师的。On-Policy Distillation 更进一步：学生采样，教师只对同一个 prefix 给出 $\log\pi_T$，逐步优势可以写成 $\mathrm{adv}\approx\log\pi_T-\log\pi_S$。期望在 $\pi_S$ 下取，所以仍然是反向 KL，但状态是学生自己会碰到的，exposure bias 就没了。

三者放一起，一句话就能说完：标准 KD 是教师采样加正向 KL，covering，状态属于教师；MiniLLM 换成反向 KL，seeking，少学低质量长尾，但状态可能还是 off-policy；OPD 是学生采样加反向 KL，seeking 而且 on-policy。

OPD 别说成「一种 GRPO」。它用教师的 log-prob 当稠密信号，优势估计器可以另选 GRPO 或 PPO，两者是正交的，见 `pt-on-policy-distillation`。把 OPD 答成「正向蒸馏的工程加速」，方向就反了。即使公式写成 CE，只要样本来自学生，有效方向就偏 seeking。这和 SFT（数据采样、正向）对 RLHF（策略采样、反向）是同一张表，见 `pt-sft-fwd-kl-vs-rlhf-rev-kl`。

## 追问

**为什么分类用正向，生成改反向？**
分类标签峰少，漏一个类代价高；生成的词表有长尾，covering 会把模型学糊。几何是同一条 `fund-kl-directions`，任务不同，默认方向就不同。把生成当成整词表分类来蒸，就会把尾巴学进来。

**反向一定更好吗？**
不一定。需要覆盖教师多样写法，或者学生比教师小很多的时候，正向或者插值可能更稳。学生太弱时，seeking 可能锁死在一个错误的主峰上。MiniLLM 和 OPD 想说的是生成部署更怕瞎说，没说反向在所有 KD 上都占优。

**和 RLHF 里的反向 KL 是同一个吗？**
几何一样，锚点不同。RLHF 锚的是 $\pi_{\mathrm{ref}}$ 加奖励，OPD 锚的是教师 $\pi_T$。教师 KL 也别当成防止模型钻奖励漏洞的通用保证。

**白板上 OPD 目标怎么写？**
先写学生采样 $y\sim\pi_S$，再写 $\mathbb{E}[\log\pi_S-\log\pi_T]$ 或者对应的 token 级 advantage，标明这是 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$。左右写反，就又变回标准 KD 了。

**OPSD 算正向还是反向？**
前缀来自学生，但 Zhao 那篇论文默认用的是全词表 $D_{\mathrm{KL}}(p_T\|p_S)$，所以别和拼多多那道外部 OPD 题合成一句「蒸馏都是反向」，见 `pt-opsd`。
