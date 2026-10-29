---
id: drustz-09b2d06fad9116d7d7
section: openai
order: 110
level: A
title: Machine Count and Network Topology Message Delivery (implement receiveMessage)
quick: >-
  original-structured-preparation-guide · Machine Count and Network Topology
  Message Delivery (implement receiveMessage)
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
      https://www.1point3acres.com/interview/problems/756863af-79c3-43e8-977b-398f2a20fe61
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Machine Count and Network Topology：实现 receiveMessage

> 内容定位：公开标题点名 `receiveMessage`，本地也保存了 count/topology 的相关代码。这里把旧代码容易出错的“全局可变字段”改造成按请求隔离的事件驱动实现；它是准备指南，不是会员正文复刻。

## 需求模型

每台机器运行一个 `Node`，只允许调用 `sendAsyncMessage(target, envelope)`；框架在消息到达时调用 `receiveMessage(fromId, envelope)`。需要支持 `COUNT` 和 `TOPOLOGY`，并允许回复乱序或重复。建议 envelope 至少有：

```text
requestId, operation, phase(REQUEST|RESPONSE), payload
```



根节点由特殊的 `CLIENT` 触发；内部节点不能查询 `cluster.nodes` 来偷看全局答案。

## 统一状态机

两类操作可以共享聚合框架，只替换三个函数：叶子初值、合并 child response、完成时编码。

```text
on REQUEST:
  若 requestId 已存在，重发已缓存结果或忽略
  建立 state(waiting=children, replies={})
  若为 leaf：complete(baseValue)
  否则给每个 child 发 REQUEST

on RESPONSE:
  校验 requestId / operation / fromId
  若该 child 已回复则忽略
  记录 payload；收齐后 complete(aggregate(replies))
```



`COUNT` 的完成值是 `1 + sum(replies)`；`TOPOLOGY` 的完成值是当前 ID 加按约定顺序排列的孩子子树。完成后向父节点发送 RESPONSE；若当前节点是根，则回调客户端。

## 例子

对于 `r -> [a,b]`、`a -> [c]`：

- count 逐级返回 `c=1, a=2, b=1, r=4`；
- topology 可返回 `r(a(c),b)`。

若 `b` 先回、`a` 后回，计数不变；拓扑也应借助 child ID 或原 child list 恢复稳定次序，而不是直接使用到达顺序。

## 工程改进

每个 state 增加 deadline；超时后可以整体失败，或回传“缺失节点”列表，但语义必须先约定。至少一次投递下，用 `(requestId, fromId, phase)` 去重。重试同一个请求时不得重新累计；若缓存已完成结果，可以直接重发。动态拓扑需要携带 `epoch`，拒绝混合不同 epoch 的回复。

## 复杂度与边界

每次操作消息数和工作量都是 `O(n)`；count payload 为 `O(1)`，topology payload 总结果 `O(n)`。每个未完成请求在全网占 `O(n)` 状态，因此要限制并发并及时回收。测试单节点、多个并发请求、空孩子、重复/迟到消息、非法 child、节点失败、树很深、ID 含标点以及 topology 字符串转义。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/756863af-79c3-43e8-977b-398f2a20fe61)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
