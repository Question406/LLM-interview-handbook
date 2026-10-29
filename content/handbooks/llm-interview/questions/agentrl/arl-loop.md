---
id: arl-loop
section: agentrl
order: 13
level: A
title: 怎么检测 Agent 死循环或无进展？
quick: "同时看四类信号：动作是否原样重复、换了措辞是否还是同一意图、环境状态有没有进展、预算是否超限。只设最大轮数能止损，判断不了任务是否已经停滞；动作相似且状态不变才触发干预，触发后换策略或停止，不要原样重试。"
tags:
  - Failure Recovery
  - Loop Detection
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ReAct
    url: https://arxiv.org/abs/2210.03629
    type: primary
---

我会同时看四类信号：动作有没有原样重复、换了措辞是不是同一个意图、环境状态有没有进展、预算有没有超。只设 `max_turns` 能止损，但判断不了任务是不是已经停滞，截断只能限制费用，它不告诉你该换策略还是该停。

比如 Agent 先调 `search("退货政策")`，没找到想要的，又调 `search("如何退货")`，再换个说法查一次，返回的结果集合一模一样。字面上每次都不同，实际在原地打转。ReAct 式的 Thought / Action / Observation 很容易这样在同一个查询上换措辞空转。

## 四类信号，缺一类就会漏

做法是维护最近 $k$ 步的 action 和 state。精确重复（exact repeat）对规范化后的 tool 调用做 hash，去掉空白、字段排序，连续相同的 `search(query=...)` 就是死循环。语义重复（semantic repeat）用 embedding 或 AST / 字段和类型规范（schema）等价来判，上面那两个查询就属于这种。状态无进展看环境 delta，URL、DOM 哈希、测试结果、文件树、数据库行的 $\mathrm{delta}\approx 0$，动作再像在干活也没用。预算看 turns、tokens、tool 费用和 wall-clock，超了就要停，哪怕模型还在写「再试一次」。

判定时要组合起来：动作高度相似、状态又几乎不变，才触发干预。动作相似但环境在变，比如分页浏览，不一定是环；状态没变但动作在探索新工具，可能是合法的试错。搜索、调研类任务再加一个 novelty，连续几轮没有新的证据 ID，就算无进展。这和 `arl-eval` 要报的 recovery / 空转比例用的是同一套字段。

## 触发后换策略，别原样重放

检测到环，原样再 sampling 同一个 tool 没有用。可以换工具、换查询角度、改分解方式，见 `agent-when-to-replan`；把「相同调用已失败、状态没变」写成结构化的 observation 喂回去，别让模型假装没看见；靠近不可逆动作的环要立刻停或升级，只读搜索可以给一次改写机会。超时和环是两回事：超时先问幂等，见 `arl-retry`；环是听到了回音，但仍然回到同一个状态。

训练时，把「同一个失败调用再发三遍」标成负例，把「发现无进展后换工具或停下」标成正的 recovery。Reward 要是罚步数却不罚空转，模型会改成换同义查询刷步数。评测时注入几种情况：工具永远返回同一个错误、页面点了没变化、检索结果集合不变，看 Agent 是重试到超时，还是切换或终止。

## 追问

**分页浏览算循环吗？**
一般不算。动作相似，但 URL 和结果集在变，用 state delta 区分「换页」和「同一页连点」。

**语义重复的阈值怎么定？**
先用 schema 规范化加精确 hash，再对 query 文本做等价判断。阈值要在注入了同义查询的 eval 上调，别靠 embedding 手感。

**和 replan 是什么关系？**
环检测是触发器，replan 是响应。没有检测，replan 的提示写了也不会被调用。

**训练要不要奖励「少步」？**
可以，但要同时罚无进展。只奖短轨迹会鼓励过早停止，只罚长轨迹会鼓励同义空转。
