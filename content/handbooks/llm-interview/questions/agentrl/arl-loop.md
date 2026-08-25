---
id: arl-loop
section: agentrl
order: 13
level: A
title: 怎么检测 Agent 死循环或无进展？
quick: >-
  同时看 repeated action、semantic repeat、state no-progress 与预算。只设 max turns
  能止损，但不能判断“已经没有进展”。
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

只设 `max_turns` 能止损，不能判断「已经没有进展」。ReAct 式 Thought / Action / Observation 很容易在同一查询上换措辞空转。这块容易直接答成把循环当成长度问题：截断只防止账单爆炸，不告诉你该换策略还是该停。检测要同时看动作重复、语义重复、环境无进展和预算。

## 四类信号，缺一就会漏

维护最近 $k$ 步的 action / state：

- **Exact repeat：** 对规范化后的 tool 调用做 hash（去掉空白、字段排序）。连续相同 `search(query=...)` 就是死循环。
- **Semantic repeat：** embedding 或 AST / schema 等价。`search("退货政策")` 与 `search("如何退货")` 字面不同，意图一样。
- **State no-progress：** 环境 delta。URL、DOM 哈希、测试结果、文件树、数据库行若 $\mathrm{delta}\approx 0$，动作再「像在干活」也无效。
- **Budget：** turns、tokens、tool 费用、wall-clock。超限必须停，哪怕模型还在写「再试一次」。

判定可以写成：action 高相似 **且** 状态几乎不变，才触发干预。只有动作相似但环境在变（分页浏览）不一定是环；只有状态不变但动作在探索新工具，可能是合法试错。Search / research 任务再加 novelty：连续多轮没有新证据 ID，视为无进展。这和 `arl-eval` 要报的 recovery / 空转比例是同一套字段。

## 触发后：换策略，不要原样重放

检测到环，默认不是再采样同一个 tool。分层响应：

1. **Strategy switch：** 换工具、换查询轴、改分解，见 `agent-when-to-replan`。
2. **Reflection / 结构化错误：** 把「相同调用已失败 / 状态未变」写成 observation，禁止模型假装没看见。
3. **Terminate 或升级：** 不可逆动作附近的环要立刻停；只读搜索可给一次改写机会。
4. **不要盲 retry：** 超时与环不同。超时先问幂等，见 `arl-retry`。环是「听到回音但仍回到同一状态」。

训练标签：把「同一失败调用再发三遍」标成负例；把「发现无进展后换工具或停」标成正 recovery。Reward 若惩罚步数但没惩罚空转，模型会改成「换同义查询刷步数」。评测应注入：工具恒返回同一错误、页面不随点击变化、检索结果集合不变。看 Agent 是重试到超时，还是切换 / 终止。

最后我会补一句：环 = 动作重复 + 状态不前进 + 预算。`max_turns` 只是保险丝。触发后换策略或停，不要原样重放。

## 追问

- **分页浏览算循环吗？** 动作相似但 URL / 结果集在变，一般不算。用 state delta 区分「换页」和「同一页连点」。
- **语义重复阈值怎么定？** 先用 schema 规范化 + 精确 hash，再对 query 文本做等价。阈值要在注入同义查询的 eval 上调，不要只靠 embedding 手感。
- **和 replan 的关系？** 环检测是触发器；replan 是响应。没有检测，replan 提示写了也不会被调用。
- **训练要不要奖「少步」？** 可以，但必须同时罚无进展。只奖短轨迹会鼓励过早停止；只罚长轨迹会鼓励同义空转。
