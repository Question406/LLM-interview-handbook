---
id: ml101-wordpiece-implementation
section: data
order: 15
level: A
title: 给定词表，怎样实现 WordPiece 的最长匹配编码？与 BPE 有何区别？
quick: WordPiece 编码从词首开始，贪心选择词表中最长的可用片段，后续片段用 ## 前缀区分词内位置。参考练习中只要某一段无法匹配，就把整个词返回为 [UNK]。词表学习与编码是两个阶段；BPE 编码通常按训练得到的合并顺序合并，不能把任意最长词表匹配都称为 BPE。
companies: [google]
tags: [Machine Learning, Tokenization, Coding]
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: Google MLE L5 候选人面经：WordPiece 如何实现
    url: https://www.1point3acres.com/interview/thread/894226
    type: secondary
  - title: Hugging Face LLM Course, WordPiece tokenization
    url: https://huggingface.co/learn/llm-course/en/chapter6/6
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

给定已经训练好的字符串词表，实现单个词的 WordPiece 编码。只实现编码，不训练词表。

### 输入与接口

实现 `wordpiece_encode`(word,vocab,*,`max_chars`=100)。word 是已经预分词的一个字符串；vocab 是包含 "[UNK]" 的字符串集合或可迭代对象；`max_chars` 为正整数，以 Python 字符串字符数计。

### 输出与约束

返回 token 字符串列表。词首片段直接匹配词表，后续片段必须以前缀 ## 的形式匹配；每个位置选择能匹配的最长片段。空词返回 []；词长超过 `max_chars` 返回 ["[UNK]"]。

某一位置无法匹配时，整个词返回 ["[UNK]"]，不能保留之前的半截结果，也不回溯改选更短片段。输入大小写、Unicode 字符和标点均原样处理，不额外归一化或拆词。

### 示例

```text
vocab={"[UNK]","play","##ing","p","##lay"}
wordpiece_encode("playing",vocab) -> ["play","##ing"]
wordpiece_encode("playx",vocab) -> ["[UNK]"]
wordpiece_encode("abc",{"[UNK]","ab","a","##bc"}) -> ["[UNK]"]
wordpiece_encode("",vocab) -> []
```

## 解题思路与参考答案

给定词表后，可以从左到右做最长匹配。词首片段直接查词表，后续片段在前面加 `##` 再查；找到一个片段就向右移动，直到词被编码完。

原帖只问 WordPiece 如何实现，没有给编码接口或词表学习规则。下面是手册重构练习：输入一个已经过预分词的单词和字符串词表，不做大小写转换、Unicode 归一化或标点切分；使用 `##` 作为词内前缀；失败时整个词输出 `[UNK]`，空词返回空列表，超过长度上限也返回 `[UNK]`。这些都是为了可测试而明确的约定。

```python
def wordpiece_encode(word, vocab, *, max_chars=100):
    if not isinstance(word, str):
        raise ValueError("word must be a string")
    if type(max_chars) is not int or max_chars < 1:
        raise ValueError("max_chars must be positive")
    vocab = set(vocab)
    if "[UNK]" not in vocab:
        raise ValueError("vocab must include [UNK]")
    if not word:
        return []
    if len(word) > max_chars:
        return ["[UNK]"]
    pieces = []
    start = 0
    while start < len(word):
        end = len(word)
        matched = None
        while end > start:
            candidate = word[start:end]
            if start:
                candidate = "##" + candidate
            if candidate in vocab:
                matched = candidate
                break
            end -= 1
        if matched is None:
            return ["[UNK]"]
        pieces.append(matched)
        start = end
    return pieces
```

词表为 {"[UNK]","play","##ing","p","##lay"} 时，playing 编码为 ["play","##ing"]；词首先选 play。输入 playx 时，虽然 play 能匹配，剩下的 x 没有 `##x`，整个词返回 [UNK]，不能返回已经成功的半截结果。

这种贪心算法不回溯。词表为 {"[UNK]","ab","a","##bc"}，输入 abc，先选 ab，后面 c 无法匹配，所以输出 [UNK]；它不会退回去改用 a、##bc。是否能找到任意一种合法分段，和是否遵循最长匹配规则，是两个不同问题。

这段代码会在调用时把词表转成集合，先花 $O(V)$ 时间和空间。对长度为 m 的词，最多检查 $O(m^2)$ 个候选；Python 每次切片、拼接和哈希字符串还与长度相关，因此朴素最坏时间可达 $O(m^3)$，不能忽略字符串复制就声称是线性。Trie 等专门结构可以改善编码成本。

**WordPiece 的词表怎样学习？**
编码规则不等于词表学习规则。Hugging Face 课程给出基于相邻片段分数的教学重构，同时明确原始训练实现未开源，不能把教学公式说成 Google 所有实现的精确算法。面试时应先澄清要实现的是编码还是训练。

**BPE 有什么区别？**
BPE 的常见编码从初始符号出发，根据训练保留的 merge rank 反复合并；WordPiece 使用词表做最长匹配。完整 tokenizer 还包含归一化、预分词、特殊 token 和解码规则，本文只实现子词编码这一层。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

先测最长匹配与 continuation 前缀，再测某一段无法匹配时整词回退为 UNK。空字符串应返回空列表。

```python
vocab = {"[UNK]", "play", "##ing", "p", "##lay"}
assert wordpiece_encode("playing", vocab) == ["play", "##ing"]
assert wordpiece_encode("playx", vocab) == ["[UNK]"]
assert wordpiece_encode("", vocab) == []
assert wordpiece_encode("ing", {"[UNK]", "##ing"}) == ["[UNK]"]
print("simple tests passed")
```
