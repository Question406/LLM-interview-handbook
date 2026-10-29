---
id: dt-exact-dedup-code
kind: coding
situation: 海量指纹无法都放进内存。
task: 稳定识别完全重复的文档。
approach: 规范化后哈希，Bloom 只预筛，精确记录复核。
result: 检查 false positive 不误删，撤回使用可删除的精确表。
---

## 可以这样回答

海量指纹无法都放进内存。

先规范化正文再生成指纹，内存够时用 set 判断见没见过。十亿级时用 Bloom 先筛出「可能见过」的文档，再查落盘的精确记录复核，免得误删。exact deduplication 只管规范化后相同的内容，near-duplicates 另用 MinHash；opt-out 撤回要用精确墓碑表，因为 Bloom 不支持删除。

测试时，我会检查 false positive 不误删，撤回使用可删除的精确表。
