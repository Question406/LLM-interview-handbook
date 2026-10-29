---
id: dt-pre-mid-post
kind: project
situation: 知识覆盖和行为格式属于不同缺口。
task: 决定数据应投哪个训练阶段。
approach: 按能力来源、预算和遗忘风险做阶段对照。
result: 目标与 regression tasks 证据支持，不靠阶段名称判断。
---

## 可以这样回答

我会先判断这个问题是不会，还是会但没有按需要表现出来。比如一种语言的基本理解和知识都很弱，少量聊天示范通常补不了整个 base model 覆盖。

这类问题我会比较 pre-training 或 continued pre-training 的数据干预。如果基础能力已经有了，主要是工具协议、回复格式或拒答方式不对，就更接近 post-training。领域材料和 long context 覆盖，也要看当前 base model 和 training recipe，不能只靠阶段名字分类。

我会先用小规模对照看目标能力、旧能力和成本，再决定投入哪一段。不会把所有缺口都默认变成再加一批 SFT。
