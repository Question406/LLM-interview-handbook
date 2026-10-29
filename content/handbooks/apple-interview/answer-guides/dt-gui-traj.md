---
id: dt-gui-traj
kind: concept
situation: 截图过期或动作错位会 contamination 监督。
task: 筛选可对齐可 replay 的 GUItrajectories。
approach: 核对动作前观察与状态，独立验证终局。
result: 新环境可复现成功，私人截图不默认训练。
---

## 可以这样回答

截图过期或动作错位会 contamination 监督。

只有能对上执行当时屏幕元素、能 replay 的动作才能进 SFT；依据过期截图的操作和犹豫点击要丢掉或 mask，任务成功与否由环境状态判。OSWorld 发现文本操作历史有帮助，堆历史截图没有同样的收益。trajectories 用研究集、合成界面或许可演示，用户真实屏幕涉及隐私。
