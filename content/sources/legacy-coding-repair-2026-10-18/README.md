# 旧 Coding 题卡原位补全

本次修复20张原有题卡，保留ID、复习进度与背景记录，将完整练习放在原卡正文最前面；不是新增20道独立面试题。

覆盖 xAI、OpenAI、Anthropic、Apple、Meta。新增完整实现包括带版本冲突验证的事务KV、双层原子限流、手写双向链表并发LRU、MHA/GQA及RoPE/KV cache、k-means、entropy与softmax-L1梯度。其余题卡内联既有重构练习，详见manifest.json中的来源。

练习接口和测试为手册约定；论坛未披露的完整代码不作为原帖事实。保留原卡来源，不将其他公司的相似练习作为该公司原题证据。

验证：`python3 scripts/check-legacy-coding.py`，从原卡前两段代码抽取并执行，确保页面展示内容自身可运行。
