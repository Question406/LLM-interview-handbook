---
id: dt-reservoir-code
kind: coding
situation: 流式文档总量超过内存。
task: 在有限空间做带权无放回 sampling。
approach: 维护随机优先键的固定大小水库。
result: 统计频率符合权重，条数与 token 预算分开检查。
---

## 可以这样回答

流式文档总量超过内存。

用加权水库 sampling：每条文档生成随机键 $k_i = u_i^{1/w_i}$，流式保留键最大的 $k$ 条，权重可以取 token 数乘质量分。按域各维护一个水库，不用把全量装进内存。水库控制的是条数，要和 token 预算对上，超长文档要切块或限制权重；空域要报告。

测试还要满足这个条件：统计频率符合权重，条数与 token 预算分开检查。
