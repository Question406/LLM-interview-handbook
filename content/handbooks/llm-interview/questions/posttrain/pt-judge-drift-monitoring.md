---
id: pt-judge-drift-monitoring
section: posttrain
order: 236
level: A
title: 用 LLM-as-judge 做持续评估时，如何监控 judge drift？
quick: >-
  Judge 的模型、prompt、温度、rubric 一变，分数的尺度就会漂。我会冻一份金标集定期重打分，看均值和排序 Kendall
  $\tau$，judge 配置进版本号、变更走 acceptance checks，这样时间序列上的涨跌才反映的是政策模型。这题管的是尺子换没换，静态偏差在
  `fund-judge`。
tags:
  - LLM-as-Judge
  - Evaluation
  - Monitoring
  - Drift
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: 'https://arxiv.org/abs/2306.05685'
    type: primary
---
我会把 judge 当成一台会漂的仪器来管：冻一份金标集，每次发版用同一套 judge 配置重打一遍，看分数和排序有没有动；judge 的配置本身进版本号，改了就走 acceptance checks。没有金标重打和排序 acceptance checks，judge 分数的时间趋势我是不会去解释的。

举个例子。周报上 arena-judge 胜率涨了 3%，看着像模型变强了。可金标重打一看，新旧 judge 在同一批 200 条上的一致率从 0.82 掉到了 0.70，新 judge 还普遍更偏爱长答案。这时候该先修裁判或者回滚提示，再去谈策略的收益。最常见的错就是只给政策模型做版本管理，不管裁判，然后把这 +3% 当成能力。

和 `fund-judge` 的分工是这样的：那题讲位置、冗长、self-preference 这类静态偏差；这题讲的是这些偏差，连同底座、提示、温度、rubric，会随时间变化，导致同一批回答的分数尺度整体平移，或者排序翻过来。judge 一换，时间序列就断了，分不清是策略变好了还是裁判变松了。

## 冻结金标，把裁判当会漂的仪器

换底座、改 system prompt、改温度、改 rubric，或者裁判自己被持续微调，都会让尺子漂。最低配的监控有四样。一是冻结一份金标对话集，每次发版用同一个 judge 配置重打，画均值、方差和排序的 Kendall $\tau$。二是新旧 judge 对同一批回答并行打分，报一致率和系统性偏移，比如是不是更偏长答案。三是用已知难度的锚题做 calibration 曲线。四是把 judge 配置（模型、提示、温度、rubric 哈希）写进版本号，变更走 acceptance checks。

金标集要覆盖短答和长答、security constraints、工具轨迹，不然你监控的只是「简单闲聊」上的那把尺子。人审抽检的比例跟着一致性走，一致性越低抽得越多。控制图看的是金标均值和 $\tau$ 的时间序列；业务 win-rate 里混着策略本身的变化，拿它当漂移检测器是测不准的。这和 `data-offline-online-metric-gap` 是同一个道理，代理指标的尺度变了，就不能拿它解释线上涨跌。Zheng 等的 MT-Bench 那篇已经把 judge 对提示和位置敏感写成了必须处理的工程问题，持续评估只是让这种敏感随着每次发版变成漂移。

## 涨跌要对齐到同一把尺子

政策模型和裁判如果是同一家族，self-preference 会跟着策略更新一起漂：新政策写得越来越像新 judge 喜欢的样子，win-rate 就虚高。这是 `fund-judge` 里的自偏好在时间维度上的版本，算不上能力提升。

多个异构 judge 做集成，能把方差平均掉，但也可能把系统性偏见藏起来，比如大家都偏爱长答案、都偏爱某个家族的文风，所以集成替代不了金标重打。position bias 这些静态问题怎么修见 `fund-judge`，这题要多保证一件事：修完偏差的配置要钉住，之后的时间序列才读得懂。

升级 judge 只有一个正当理由：人审一致性明确提高了，而且新旧并列 calibration 做完了。升级当时就开一条新的时间序列，别接在旧曲线后面假装连续。每周看 win-rate 之前，先问一句这周的 judge 配置哈希变了没有。

## 追问

**和 `fund-judge` 怎么分工？**
那题列偏差和缓解办法，这题管偏差和配置随时间漂不漂、尺子换没换。先把配置钉住，再谈偏差。

**Kendall $\tau$ 掉了，但均值没变呢？**
那就是排序已经乱了，不能再拿它做模型对比。均值不动只说明尺度没有整体平移，相对名次已经不可信了。

**多 judge 集成能掩盖漂移吗？**
能。成员如果共有 verbosity bias，集成也会一起漂，所以还是得对金标重打。

**人审比例怎么调？**
一致率或 $\tau$ 跌破 acceptance checks，就提高抽检比例，同时暂停自动排名；恢复以后再降下来。别等业务来投诉。

**能拿新 judge 回溯给历史回答打分吗？**
可以做对照，但要同时报旧配置的重打结果。只用新尺子回溯，历史曲线会出现假的跳变。
