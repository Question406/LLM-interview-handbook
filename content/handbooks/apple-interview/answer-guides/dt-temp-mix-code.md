---
id: dt-temp-mix-code
kind: coding
situation: 来源体量不同，直接按条数抽会失衡。
task: 按域预算做可复现 sampling。
approach: 域间配额、域内温度，明确不足与重复上限。
result: 检查空域、配额偏差及 low-resource 重复次数。
---

## 可以这样回答

来源体量不同，直接按条数抽会失衡。

sampling 分两层：先按能力需求给各分组分配 token 预算，再在组内用 $p_i\propto n_i^{\alpha}$ 平衡来源，$\alpha=1$ 是按体积抽，趋近 0 时更均匀。low-resource 数据重复太多会出现 overfitting，所以要配合课程和 English regression data。实际数据不足或某组为空时必须报告。

测试时，我会检查空域、配额偏差及 low-resource 重复次数。
