---
id: dt-traj-quality
kind: design
situation: 最终成功 trajectories 也可能包含坏过程。
task: 决定哪些片段适合监督。
approach: 按证据、权限、恢复和无效动作审核。
result: 被学到的行为可迁移，失败片段不冒充正例。
---

## 可以这样回答

最终成功 trajectories 也可能包含坏过程。

用于 SFT 的 tool-use trajectories 要逐步过检查，每一步参数合法、结果真实、写操作确实完成，最后的回答和实际状态一致，并能在对应环境版本重放。工具返回内容是模型读取的输入，不算进损失。失败尝试可以做恢复示范或偏好负例。
