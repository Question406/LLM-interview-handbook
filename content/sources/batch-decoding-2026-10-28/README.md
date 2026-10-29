# Batched decoding implementation · 2026-10-28

本批为手册原创，不冒充 Apple 原题。新增三张 coding cards：

- apple-batched-token-selection：逐行 greedy、temperature/top-k/top-p、multinomial、Gumbel。
- apple-batched-generation：static batch、left padding、独立 EOS、逻辑 positions、prefill 与 KV decode。
- apple-batched-beam-search：完整 B×K 搜索、parent backpointer、重复 parent、cache gather、finished carry、invalid slots、最终 length penalty。

每卡源码和断言都嵌入 canonical Markdown，可在练习页直接运行，无需下载模型。测试模型实现真实单层 causal attention；无语言能力或生产性能声明。保持原单序列题及单步题，用导航表说明覆盖范围。Speculative verification 原题仍是单请求 block；没有声称实现 continuous batching、grammar compiler 或任意框架 Cache 对接。

验证命令：使用已安装 PyTorch 的 Python 运行 `scripts/check-batched-decoding.py`，直接从三张 Markdown 抽取并执行代码。测试含可手算转移、20,000 行分布、RNG replay、top-p crossing、top-k 后 normalization、不同长度 prompt、独立 EOS、pad=EOS、零步数、逐 token cached logits 与 full-prefix reference、beam width=1/3、alpha=0/0.6、重复 parent、非法空位和 deterministic ties。

来源保留在每张卡：PyTorch multinomial/stable sort、Hugging Face cache explanation、GNMT length normalization。只以这些来源支持机制；接口和搜索约定由题面明确定义。

验证结果：PyTorch 2.14.1 / CPU 下三份 Markdown 中展示的完整程序全部通过。内容构建生成 2,388 道网页题，Apple 题本 340 道、Decoding 专题 11 道；58 项 Node 测试通过，606 道 coding cards 的简单测试说明检查通过，`git diff --check` 通过。
