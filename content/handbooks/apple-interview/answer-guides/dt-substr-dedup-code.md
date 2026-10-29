---
id: dt-substr-dedup-code
kind: coding
situation: 整篇不重复也可能包含 leakage 片段。
task: 发现精确子串或评测重叠。
approach: 滚动哈希提速，命中后核对原文。
result: 覆盖 edge cases 和 hash collisions，避免哈希相同直接判真。
---

## 可以这样回答

整篇不重复也可能包含 leakage 片段。

把评测内容切成固定长度的字符或 token 窗口，用滚动哈希扫训练文档，命中后再比原文，排除哈希碰撞。它能发现整篇哈希漏掉的局部片段复制。窗口太短会 false rejection 常见代码，太长会漏掉变体，规范化按域选；训练内部的子串 deduplication 和评测隔离用不同的表和阈值。

测试时，我会覆盖 edge cases 和 hash collisions，避免哈希相同直接判真。
