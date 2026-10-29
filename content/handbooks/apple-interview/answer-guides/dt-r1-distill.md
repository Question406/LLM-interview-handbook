---
id: dt-r1-distill
kind: concept
situation: 长推理文本不自动适合作为 student 监督。
task: 理解 distillation 数据的验证与筛选。
approach: 保留正确可读 trajectories 并混合通用任务。
result: student 独立收益支持数据，条数不横比不同配方。
---

## 可以这样回答

长推理文本不自动适合作为 student 监督。

R1 在 RL 收敛后做 rejection sampling，只留正确且可读的 trajectories，再加通用任务一起做 SFT：约 600k 推理加约 200k 写作 / QA，共约 800k，不含 RL 前那几千条冷启动。small model 只做 SFT，是为了单独看这些 trajectories 能不能把能力传过去。网上爬来的长思考没经过这套验证和过滤，和这份数据是两回事。
