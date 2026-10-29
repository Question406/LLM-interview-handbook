---
id: drustz-f6f0c69388c3260ded
section: openai
order: 119
level: A
title: Time-Aware Social Network Follow Graph with Recommendations
quick: >-
  original-structured-preparation-guide · Time-Aware Social Network Follow Graph
  with Recommendations
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
      https://www.1point3acres.com/interview/problems/d9afe2bc-6711-4a13-90d1-aafcee4cb705
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Time-Aware 关注图：在历史时刻生成推荐

> 内容定位：本地题库对“时间感知关注图”给出了较明确的版本日志与二分提示。以下题意与算法是重新组织的原创指南，不是会员页面的逐字题面或答案。

## 接口与历史语义

支持 `follow(u,v)`、`unfollow(u,v)`、`take_snapshot()->sid`、`is_following(u,v,sid)` 与 `recommend(u,k,sid)`。一个 snapshot 是只读时间点；推荐必须完全基于该时刻的图，而不能使用最新关系。

可令每次有效更新获得单调 `op_version`，`snapshots[sid]=op_version`。每条边保存 `history[(u,v)]=[(op_version,True/False), ...]`。查询 snapshot 时用 `bisect_right` 找 `<= snapshots[sid]` 的最后状态。重复 `follow` 已 active 的边、重复 `unfollow` 已 inactive 的边不写日志，避免无意义膨胀。

## Top-K 推荐

维护 `ever_out[u]` 记录 u 历史上关注过的所有人，但它只是候选索引，是否生效仍须对边日志二分。令 `F(u,t)` 为时刻 t 的直接关注集合：

1. 对 `v in F(u,t)`，遍历 `F(v,t)`；
2. 每出现候选 c 一次，`score[c]+=1`；
3. 排除 `c==u` 及 `c in F(u,t)`；
4. 按分数降序、用户 ID 升序取前 k。

```python
def recommend(u, k, sid):
    cutoff = snapshots[sid]
    direct = following_at(u, cutoff)
    score = Counter()
    for friend in direct:
        for cand in following_at(friend, cutoff):
            if cand != u and cand not in direct:
                score[cand] += 1
    return sorted(score, key=lambda x: (-score[x], x))[:k]
```



例如快照 7 时 A 关注 B/C，二者都关注 D，则 D 得 2 分。快照 8 前 B 取消 D，查询 sid=7 仍为 2，查询 sid=8 才为 1。这一对测试能直接抓出错误使用 live adjacency 的实现。

实现 `following_at` 时不要扫描全图：只扫描 `ever_out[u]` 中的目标，再逐边二分。若需要查询“谁关注我”，另建 `ever_in[v]`；它只在边第一次出现时更新，后续开关不重复加入。两个候选索引都不代表当前状态，因此绝不能跳过日志判断。

## 复杂度与扩展

单边状态查询 `O(log H_e)`；`following_at` 为 `O(D_ever log H)`；推荐时间与被访问的历史二跳边数成正比，候选很多时可用大小为 k 的最小堆，把最终选择从 `O(C log C)` 降到 `O(C log k)`。存储为 `O(U+E_ever+M)`，M 是有效状态变化数。

边界包括快照前从未存在的边、同一版本连续切换、删除后重新关注、k 大于候选数、self-follow 与确定性同分规则。若读多写少，可按热门 snapshot 缓存 `following_at`，但缓存键必须包含 sid；若需要删除旧历史，可在最老保留 snapshot 处做 checkpoint，再截断更早日志。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/d9afe2bc-6711-4a13-90d1-aafcee4cb705)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
