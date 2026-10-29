---
id: drustz-d4aea4680f984d866c
section: openai
order: 79
level: A
title: Distributed Topology Reconstruction via Async Messages
quick: >-
  original-structured-preparation-guide · Distributed Topology Reconstruction
  via Async Messages
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
      https://www.1point3acres.com/interview/problems/c4588a6c-a66e-4391-9b23-a16a365ae88e
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Distributed Topology Reconstruction via Async Messages

> 内容定位：公开标题明确指向“通过异步消息重建拓扑”；本地资料有高度相关的 rooted-tree 消息聚合题，但没有拿到当前会员页的逐字接口。以下把重点放在可复用的异步状态机上。

## 准备题面

每个 `Node` 只知道 `parentId` 和 `childIds`。消息可能以任意顺序到达，但假定最终可达；根节点收到 `TOPOLOGY_REQUEST` 后，需要仅通过父子消息得到整棵树的拓扑。不同请求可能同时存在，网络也可能重复投递消息。

推荐使用结构化信封，而不是把字段用 `-` 拼成字符串：

```text
Request  { requestId, kind: "topology" }
Reply    { requestId, fromId, subtree }
```



字符串分隔协议遇到 ID 或 payload 自带分隔符时很脆弱，JSON、typed object 或 length-prefix 编码更稳妥。

## 状态设计

每个节点维护 `pending[requestId]`：

```text
expectedChildren: set<NodeId>
replies: map<NodeId, Subtree>
parentForRequest: NodeId | CLIENT
completed: bool
```



第一次收到 request 时创建状态并向孩子广播；没有孩子就立刻返回叶节点。收到 reply 时先验证发送者属于 `expectedChildren`，再按 child ID 写入 map。只有 map 覆盖全部孩子时才组装本节点的 subtree 并向上回复。完成后可保留一个短期去重记录，随后按 TTL 清理状态。

## 小例子

树 `A -> {B,C}`、`B -> {D}`。即使回复顺序是 `C、D、B`，A 也应得到稳定结果，例如：

```text
A(B(D),C)
```



关键不是到达顺序，而是用 `fromId` 定位孩子，并在序列化前排序。若面试要求保留原 `childIds` 顺序，则应按照该列表输出，不能擅自排序。

## 正确性思路

对树高归纳：叶节点返回的拓扑显然正确；假设每个孩子都返回正确子树，父节点收齐后把这些子树接到自己下面，得到的正是以自己为根的完整子树。根节点应用同一规则，最终得到整棵树。

## 复杂度与边界

遍历和消息数均为 `O(n)`，最终表示占 `O(n)` 空间；朴素字符串逐层复制在链状树上可到 `O(n²)`。需要覆盖空孩子、单节点、重复 reply、请求重放、消息乱序、节点超时、多个并发 `requestId`、环形错误配置和超深树。若允许节点加入/离开，还必须给拓扑加 epoch：一次请求只读取同一版本的邻接关系。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/c4588a6c-a66e-4391-9b23-a16a365ae88e)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
