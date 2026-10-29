---
id: dt-gui-agent-rl
kind: design
situation: GUI 状态受视觉布局、时序和工具影响。
task: 构建可对齐可 replay 的交互监督。
approach: 固定截图动作语义，状态检查独立于模型自报。
result: 新 UI 成功与权限、坐标和延迟错误都检查。
---

## 可以这样回答

GUI 状态受视觉布局、时序和工具影响。

差在观测、动作和奖励检查的对象。代码环境看 stdout、靠测试给奖励；GUI 任务是指令加初始桌面快照加状态 checker，模型读截图和无障碍树，点击、键入、滚动，奖励看文件、窗口、单元格这些最终状态。checker 要放在只读镜像里，和 agent 工作区隔离。
