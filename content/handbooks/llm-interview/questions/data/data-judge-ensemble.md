---
id: data-judge-ensemble
section: data
order: 217
level: A
title: Judge Ensemble 怎样构权与校准？和单 Judge + 更好 prompt 如何取舍？
quick: "不同 judge 投票能降低单个模型的独立失误，权重和温度校准放在独立金标集上做。共同偏差，比如都偏好长回答或同一种文风，投票消不掉。所以先修 rubric 和顺序交换，再在同等调用成本下比较单 judge 多次判断、更明确的 rubric 和 ensemble，ensemble 赢了才上。"
tags:
  - LLM-as-Judge
  - Ensemble
  - Eval
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: https://arxiv.org/abs/2306.05685
    type: primary
---

Ensemble 降的是 judge 之间相互独立的噪声，共同的口味它降不了。所以我会先修 rubric 和位置交换，再在同等成本下拿单 judge 和 ensemble 比，ensemble 赢了才上，权重和校准都放在独立金标上做。「三个弱 judge 一平均就比一个强 judge 稳」，很多时候并不成立。

比如三个 judge 都来自同一个模型家族，都偏好长回答。把一条啰嗦但没多说什么的回答和一条简洁正确的回答放在一起，三票都投给长的，投票后方差看起来下降了，排名却更偏向长回答。Zheng et al. 已经把 LLM-as-Judge 的位置、篇幅、自我偏好列成必须处理的偏差（`fund-judge`），这些相关误差投票之后还在。面试官想听的是构权、校准和同等成本的对照，光说「我们用了四个模型」不够。

## 先处理相关误差

成对比较照样要交换回答的展示顺序，交换后判断频繁翻转的 judge 要降权或者剔除。pairwise ensemble 也一样，对调顺序后多数票结果还翻，说明判断受顺序影响。Ensemble 的分数可以写成

$$
s=\sum_j w_j s_j,\qquad \sum_j w_j=1,
$$

权重可以均匀平均、按金标集准确率加权，或者在一个小的 stacking 集上回归。金标要和训练 judge 的那批数据独立，不然就是在拟合标注噪声（`data-annotator-agreement`）。Stacking 权重如果在同一小份金标上又训又选模型，会过拟合那几十条标注里的偏好，金标要再切 train/eval，或者只用温度缩放这种低容量的校准。

输出用温度缩放 $\hat p=\sigma(s/T)$ 或者 isotonic，把分数校准到人类胜率上，没校准的 $s$ 不能当阈值门禁。人审校准集按任务分层，安全题和文风题别混成一个 $T$。Pointwise ensemble 方便做回归校准，但分数尺度可能会变。

## 同等成本下，先比单 judge 加更好的 prompt

很多场景下，「更强的单 judge + 结构化 rubric + 先抽证据再打分」比三四个弱 judge 好。我会先画出准确率随费用变化的曲线：ensemble 调用 $K$ 次，对照单 judge 自洽 $K$ 次，或者换一个 $K$ 倍贵的更强模型。曲线上 ensemble 不占优，就别为了「听起来像集成学习」去烧钱。同等美元下单 judge 自洽赢了，就不上弱模型投票。

输入提示（prompt）这边的最低配置是分维度 rubric、隐藏模型身份、长度匹配或长度惩罚、强制引用证据。这些没修好之前加 judge，只是把同一个偏差复制 $K$ 份。弱模型投票有时只是在平均同一种 verbosity，上线前用长度匹配的 pair 做一次对照再决定。ensemble 的 win-rate 也别直接当能力，judge 和选手同一家族时尤其如此。

## 什么时候必须上 ensemble

单 judge 在金标切片上不稳定，或者单一家族的 self-preference 很明显，这时加一个不同家族的 judge 才有边际收益。门禁级的评测我会用 ensemble 加人类抽检加可执行检查，关键的发布通道里至少要有一个可执行验证器（verifier）或人类锚点，别全是 LLM 互相打分。强化学习（RL）里用 judge 分数时，ensemble 也别当唯一的奖励来源，否则策略可能只学会迎合这些 judge 的共同偏好。

## 追问

**均匀平均够不够？**
起步可以。金标上明显更差的 judge 要降权；没有金标就别学复杂权重，免得过拟合。

**和更好的 prompt 怎么排期？**
先 rubric、swap、证据协议，再上 ensemble。prompt 能消掉的偏差，投票消不掉。

**相关偏差怎么检验？**
看 judge 两两之间的残差相关，以及匹配回答长度之后表现差距会不会消失。相关性高的时候，再加同类模型没有新信息。

**为什么一定要校准？**
没校准的分数没法设发布阈值，也没法和人类胜率比。温度缩放成本低，先做。

**和 `fund-judge` 怎么分？**
那题列偏差和缓解方法；这题回答多个 judge 怎么合成、什么时候不如一个更好的单 judge。偏差协议是 ensemble 的前置条件。
