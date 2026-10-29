---
id: drustz-7c028d75c9ff7c1ab4
section: anthropic
order: 38
level: A
title: Longest-Match Tokenizer with Unknown Token Merging
quick: >-
  original-structured-preparation-guide · Longest-Match Tokenizer with Unknown
  Token Merging
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/48917c0b-2887-5f92-8547-15fedbc869aa
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Longest-Match Tokenizer：最长匹配并合并未知片段

## 题意

给定 `vocab: token_string -> token_id`，从左到右切分文本；在当前位置选择能匹配的**最长** token。若没有 token 从当前位置开始，就消费一个字符作为未知；连续未知字符最终只输出一个 `UNK`。

```python
def tokenize(text: str, vocab: dict[str, int]) -> list[int]: ...
```



例如 `vocab={"app":1,"apple":2,"UNK":-1}`：`"apple" -> [2]`，`"appbbbapple" -> [1,-1,2]`。这里必须追加 `vocab[s]`；旧 raw 草稿中的 `tokens.append(vocab)` 会把整个字典放进结果，是明确的笔误。

## 算法

预先求除保留键 `UNK` 外的最大 token 长度 `L`。位置 `i` 处从 `min(n, i+L)` 向 `i+1` 枚举终点，第一个存在于 vocab 的子串就是最长匹配：追加 `vocab[s]`，令 `i=end`，同时结束未知 run。若一个都没有，只有在上一输出不是 UNK 时才追加 `vocab["UNK"]`，然后 `i += 1`。

最长匹配不能写成“从短到长遇到第一个就提交”。例如vocabulary同时含 `app` 和 `apple`，短匹配会把 `apple` 错切成 `app + UNK + UNK`。也不能把实际文本 `"UNK"` 当特殊字符；`UNK` 是vocabulary里的保留 ID 名称，不参与普通匹配。

## 正确性

倒序枚举保证提交的是当前位置所有可用 token 中最长者；匹配后跳到其末尾，因此输出覆盖每个已知片段且不重叠。无匹配时至少前进一个字符，算法必然终止；用一个布尔状态或检查上一个 token，即可把相邻未知字符压成一个 UNK，遇到已知 token 后重新开始新的未知 run。

## 复杂度与边界

若 Python 切片复制长度计入成本，朴素实现最坏 `O(nL²)`；用 Trie 从每个起点向前走并记最后 terminal，可做到 `O(nL)`，额外空间为 Trie 大小。空文本返回空数组；缺少 `UNK` 应显式报错；还需确认 Unicode 是按 code point、grapheme 还是 UTF-8 byte 处理。UNK 合并会丢失未知字符数量和内容，因此 `detokenize(tokenize(text))` 一般不再可逆。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/48917c0b-2887-5f92-8547-15fedbc869aa)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
