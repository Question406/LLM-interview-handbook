---
id: data-judge-ensemble
section: data
order: 217
level: A
title: Judge Ensemble 怎样构权与校准？和单 Judge + 更好 prompt 如何取舍？
quick: "让不同 judge 投票，可以降低单个模型失误的影响，再用独立金标集学习权重或做温度校准。但共同偏差，例如都偏好长回答或同一种文风，无法靠投票消除。应在同等调用成本下比较单 judge 的多次判断和更明确的 rubric，再决定是否使用 ensemble。"
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

常见误区是：「三个弱 judge 一平均就比一个强 judge 稳」，或以为 ensemble 能消掉 verbosity / 位置偏差。Zheng et al. 已经把 LLM-as-Judge 的位置、篇幅、自我偏好写成必须处理的偏差（`fund-judge`）。如果多个 judge 都偏好长回答或同家族文风，这些相关误差在投票后仍会保留。Ensemble 降的是独立噪声，不是共同口味。评委要听构权、校准和同等成本对照，别停在「我们用了四个模型」。

## 先承认相关误差，再谈投票

成对比较仍需交换回答的展示顺序；交换后判断频繁翻转的 judge，应降低权重或剔除。Ensemble 的分数可以写成

$$
s=\sum_j w_j s_j,\qquad \sum_j w_j=1,
$$

权重来源：均匀平均、按金标集准确率加权、或在小 stacking 集上回归。金标要独立于训练 judge 的那批，否则在拟合标注噪声（`data-annotator-agreement`）。输出用温度缩放 $\hat p=\sigma(s/T)$ 或 isotonic，把分数校准到人类胜率；未校准的 $s$ 不能当阈值门禁。关键发布通道还应含至少一个可执行验证器（verifier） 或人类锚点，避免全是 LLM 互相打分。

## 同等成本下，先比单 judge + 更好 输入提示（prompt）

很多场景「更强单 judge + 结构化 rubric + 先抽证据再打分」优于三四个弱 judge。成本上先画出准确率随费用变化的曲线：ensemble 的 $K$ 次调用，对照单 judge 的 $K$ 次自洽或 $K$ 倍更强模型。若曲线上 ensemble 不占优，就不要为了「听起来像集成学习」而烧钱。Prompt 侧最低配置：分维度 rubric、隐藏模型身份、长度匹配或长度惩罚、强制引用证据。这些修好之前，加 judge 只是把同一偏差复制 $K$ 份。

Pointwise ensemble 便于回归校准，但分数尺度可能变化；pairwise ensemble 要处理位置：对调展示顺序后，多数票结果仍翻转，说明判断受顺序影响。不要把 ensemble win-rate 直接当能力，尤其当 judge 与选手同家族时。

## 何时必须上 ensemble

单 judge 在金标切片上不稳定、或单一家族 self-preference 明显时，换一个不同家族的 judge 加入才有边际。门禁级评测：ensemble + 人类抽检 + 可执行检查。强化学习（RL）如果使用 judge 分数，ensemble 也不应作为唯一奖励来源，否则策略可能只学会迎合这些 judge 的共同偏好。Stacking 权重若在同一小金标上又训又选模型，会过拟合那几十条标注中的偏好；金标应再切 train/eval，或只用温度缩放这种低容量校准。人审校准集要按任务分层，安全题与文风题不要混成一个 $T$。弱模型投票有时只是在平均同一套 verbosity，看起来方差下降、排名却更偏长，应用长度匹配 pair 做一次对照再决定上线。先修 rubric 与 swap，再谈构权校准；同等美元下单 judge 自洽赢了，就不要上弱模型投票。

## 追问

- **均匀平均够不够？** 起步可以，但金标上明显更差的 judge 应降权。没有金标就不要学复杂权重，以免过拟合。
- **和更好 prompt 怎么排期？** 先 rubric、swap、证据协议，再 ensemble。Prompt 能消的偏差，投票消不掉。
- **相关偏差如何检验？** 看 judge 两两残差相关、以及匹配回答长度后，表现差距是否消失。高相关时加同类模型没有信息。
- **校准为什么必要？** 未校准分数不能设发布阈值，也不能和人类胜率对比。温度缩放成本低，先做。
- **和 `fund-judge` 怎么分？** 那题列偏差与缓解；本题回答「多个 judge 怎么合成、何时不如一个更好的单 judge」。偏差协议是 ensemble 的前置条件。
