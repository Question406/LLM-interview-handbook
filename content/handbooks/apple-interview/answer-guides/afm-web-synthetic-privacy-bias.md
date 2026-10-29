---
{
  "id": "afm-web-synthetic-privacy-bias",
  "kind": "concept",
  "situation": "团队准备共享 synthetic records，认为不是原始数据就天然安全。",
  "task": "分开验证 privacy、representation 和真实训练 utility。",
  "approach": "追踪源数据权限，测试 memorization 与任务分布，必要时采用明确的 privacy mechanism。",
  "result": "有证据支持限定用途的共享，并且 minority tasks 的质量没有被掩盖。"
}
---

## 可以这样回答

我不会因为数据由模型生成，就默认可以共享。Generator 可能记住源记录，尤其是很少见的内容；如果源数据本来有使用限制，synthetic 这个名字也不会自动取消限制。

我会先明确共享对象和允许用途，检查生成链路有没有接触个人数据。然后做 exact match、近重复和针对稀有记录的人工审核，也可以在合适的 threat model 下做 membership inference 测试。但这些都只是发现风险的证据，没有检出不代表已经证明安全。

Bias 是另一件事。Generator 可能更容易生成主流语言或常见任务，过滤器又会把困难样本删掉，最后 synthetic set 看起来很干净，却失去了我们最想补的 long-tail。我会按语言、任务和群体检查 coverage，并在独立真实数据上验证收益。

如果需求需要严格的 privacy guarantee，我会考虑具有明确 budget 的 differential privacy 方案和相应 utility tradeoff。最终交付时分别报告 privacy 检查、representation 和 utility，不用某一项通过替代其他两项。
