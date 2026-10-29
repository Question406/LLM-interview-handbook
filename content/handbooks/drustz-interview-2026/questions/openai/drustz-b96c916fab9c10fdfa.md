---
id: drustz-b96c916fab9c10fdfa
section: openai
order: 66
level: A
title: Machine Topology Reasoning (Topology / Dependency Graph)
quick: >-
  original-structured-preparation-guide · Machine Topology Reasoning (Topology /
  Dependency Graph)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/985c6952-0c9e-40e2-8d54-e2b1a7731c80
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Machine Topology Reasoning：机器拓扑推理

> 内容定位：当前 UUID 的公开标题可以确认；本地资料进一步佐证了“树形机器cluster、统计节点、重建拓扑”这一题族。下面是据此整理的原创准备题，不是会员原文，也不保证输出字符串格式与隐藏测试完全一致。

## 建议练习的题目

一个分布式cluster是一棵 rooted n-ary tree。每台机器只知道自己的 `id`、父节点和直接子节点，并且只能与相邻节点通信。客户端向根节点发起操作：

1. `count`：返回整个cluster的机器数；
2. `topology`：返回能表达父子关系的稳定字符串。

为了让答案可测试，可约定子节点按 ID 排序，叶节点表示为 `id`，非叶节点表示为 `id(child1,child2,...)`。

## 接口与例子

```text
receiveMessage(fromId, {requestId, operation, phase, payload})
sendAsyncMessage(toId, message)
```



例如 `0 -> {1,2}`、`1 -> {3}`，则 `count = 4`，一种拓扑输出是 `0(1(3),2)`。真实面试若给了别的编码规则，应以现场协议为准。

## 解法：向下广播，向上归并

根节点收到请求后把同一个 `requestId` 发给所有孩子。每个节点为该请求维护：尚未回复的孩子集合、当前计数或孩子的拓扑片段。叶节点可立即返回 `1` 或自己的 ID；内部节点收齐全部回复后计算：

```text
subtreeCount = 1 + sum(childCount)
subtreeTopology = id + "(" + join(sorted(childTopology)) + ")"
```



再把部分结果发给父节点，根节点最终输出答案。状态必须按 `requestId` 隔离，不能复用一个全局 counter，否则两个并发请求或迟到消息会互相污染。回复处理还应做到幂等：同一孩子的重复回复只接收一次。

## 复杂度

两个操作都会访问每个节点一次，消息数为 `O(n)`，节点状态总量 `O(n)`。计数只传常数大小 payload；拓扑最终 payload 为 `O(n)`。若在退化链上反复拼不可变字符串，可能产生 `O(n²)` 拷贝，可改传 token 列表/树节点，最后在根一次序列化。

## 边界与追问

- 单节点cluster应直接得到 `1` 和根 ID；
- 子节点回复乱序时，输出仍应确定；
- 重复、迟到、未知 `requestId` 的消息不能重复累计；
- 节点失败时要定义 timeout、重试以及“部分结果还是整体失败”；
- 若输入并不保证是一棵树，还需检测环、多个父节点和不可达节点。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/985c6952-0c9e-40e2-8d54-e2b1a7731c80)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
