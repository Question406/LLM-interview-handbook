---
id: code-beam-search
kind: coding
situation: 批量 beam 扩展要同时找父 prefix sum 新 token。
task: 从三维得分选出每批最优候选。
approach: 展平 beam 和 vocabulary 后 top-k，再整除和取模 backpointer。
result: 手算父 beam 索引，核对前缀与 cache 同步重排。
---

## 可以这样回答

批量 beam 扩展要同时找父 prefix sum 新 token。

每步把 $K$ 条 beam 的累计 logprob 加到 $[B,K,V]$ 的 log-softmax 上，展平成 $[B,KV]$ 取 top-$K$。下标整除 $V$ 得到父 beam，模 $V$ 得到新 token，再用父 beam 去 gather prefix sum KV cache。

测试时，我会手算父 beam 索引，核对前缀与 cache 同步重排。


本题只完成一次 batched beam step。包括多步生成、EOS、parent gather 与真实 KV cache 的完整版本见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-beam-search)。
