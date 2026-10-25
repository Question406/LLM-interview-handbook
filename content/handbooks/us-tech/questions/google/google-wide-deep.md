---
id: google-wide-deep
section: google
order: 10
level: A
title: Google：Wide & Deep 记忆 vs 泛化，现在还怎么用这个直觉
quick: "Wide 用显式交叉的线性模型记住常见 ID 组合，Deep 用 embedding 和 MLP 给未见过的组合泛化。比如高频应用对可以直接记权重，新物品则需要依赖类别、文本等侧信息。这个记忆与泛化的分工也能迁移到 FM、DCN 和更大的推荐模型里。"
tags:
  - Google
  - Wide & Deep
  - Recsys
  - Features
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Wide & Deep Learning for Recommender Systems
    url: https://arxiv.org/abs/1606.07792
    type: primary
  - title: Deep & Cross Network for Ad Click Predictions
    url: https://arxiv.org/abs/1708.05123
    type: primary
---

Wide & Deep 给记忆和泛化各留了一条路径：显式交叉记常见组合，embedding 加 MLP 给新组合打分。比如用户装了 Netflix 后常点 Hulu，wide 可以记住这对应用；新应用没有这个历史，就需要 deep 从类别等共享信息推断。Google Play 的 2016 论文用这个组合做推荐，漏斗设计见 `google-youtube-rank`。

Wide：线性模型 $y=w^\top x+b$，输入里显式放交叉，比如 `AND(user_installed_app=netflix, impression_app=hulu)`。这类特征一旦在训练里出现过且权重大，就能 **记住** 高频共现。它几乎不把「没见过的交叉」推到一个合理分数上。

Deep：每个离散 ID 进 embedding，过 MLP。相似用户、相似物品在向量空间里靠近，所以 **没见过的组合** 还能打分。代价是高频规则可能被 MLP 抹平：明明「这个用户永远点这个游戏」是硬记忆，embedding 平均掉了。

联合训练，不是两阶段 stacking。输出

$$
P(y=1\mid x)=\sigma(w_{\mathrm{wide}}^\top \phi(x)+w_{\mathrm{deep}}^\top a^{(l_f)}+b)
$$

$\phi(x)$ 是交叉后的宽特征，$a^{(l_f)}$ 是深度网络最后一层。Wide 那条路用 FTRL 一类对稀疏特征友好的优化器；Deep 用 AdaGrad。两条路径的特征稀疏程度不同，所以采用了不同优化器。

Google Play 的结果说明：只用 wide，长尾组合缺少泛化；只用 deep 会在超高频、超稀疏的安装规则上欠记忆。两者一起，应用商店的安装率才上去。

生产线很少再训练一个「左边 LR、右边三层 MLP」的原版。但问题没消失：

**ID 要记忆。**
用户 ID、物品 ID、广告创意 ID 的头部组合，仍然是最强信号。交叉可以用 FM、Deep & Cross (DCN / DCN-v2)、掩码交叉，不必手写一百万条 `AND`。DCN 的显式交叉层就是在自动化 wide 那一侧。
**侧信息要泛化。**
类别、文本、图像、上下文进 embedding / Transformer。新物品没有点击，只能靠内容塔，这是 deep 的活。
**别让 MLP 独自扛记忆。**
把哈希交叉全丢进 256 维 embedding，头部规则会和长尾抢容量。该宽的地方保持高维稀疏（或大 embedding 表 + 频次分组统计），该深的地方用稠密。
**大模型不是自动的 wide。**
生成式推荐能泛化语义，对「这个 cookie 昨天刚买了 A」这种精确记忆仍然弱，除非你把 ID 检索 / 特征交叉接回去。「上 Gemini 就不用交叉了」站不住。

可以用出现频次说明这种区别：某交叉一天出现 $10^7$ 次，另一交叉出现 3 次。前者应该被记住，几乎是 lookup；后者必须靠共享 embedding 才有分。Wide & Deep 就是给这两类样本两条路。

把 wide 说成「浅层网络」、deep 说成「深层网络」，没提交叉和 embedding。把记忆说成过拟合、主张全丢掉 ID。反过来，只堆手工交叉、没有泛化路径，新广告冷启动会挂，见 `google-ads-auction`。

过拟合确实会发生：wide 交叉太多会记噪声。要用正则、频次截断、交叉只留高频候选。记忆是有意保留可复现的共现，不是把训练集背下来。

## 追问

**和 FM / DCN 什么关系？**
FM 用隐向量内积近似二阶交叉；DCN 用显式交叉层替代手工 $\phi(x)$。都是 wide 直觉的可扩展版。

**Embedding 很大算 wide 还是 deep？**
大 embedding 表本身是记忆；MLP 是泛化。表太大而 MLP 很弱，等于昂贵的 wide。

**为什么不两阶段先 LR 再 MLP？**
联合训练让两边的误差一起回传，deep 不会只拟合 LR 的残差盲区。论文明确反对纯 ensemble。

**多任务里每条任务都要 wide 吗？**
共享 deep、任务特定 wide / 偏置很常见。安装率和时长的头部规则不一样，硬共享会互相踩。

**Play 商店交叉举个例？**
论文是已安装应用 ∩ 当前曝光应用。这是记忆。把应用类别放进 MLP，是泛化到没见过的应用对。wide 侧是超高维稀疏，要用 FTRL / 频次过滤，不能和 dense MLP 共用一个 Adam 就完事。
