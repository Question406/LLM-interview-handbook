---
id: dt-tool-turn-pref
kind: concept
situation: 整段胜负难判断哪次 tool calls 有问题。
task: 收集同上下文的逐跳监督。
approach: 相同 prefix 比较候选，工具返回不可随意修改。
result: 局部标签与真实执行一致，整段任务不退化。
---

## 可以这样回答

整段胜负难判断哪次 tool calls 有问题。

按每一跳标：在相同上下文中生成两条助手消息让人选择或编辑，把选中或编辑后的回答写回对话再继续。工具返回 annotator 不能修改，也不作为偏好候选，调用对错交给可执行检查。整段只标一个成败，reward model 会把运气算进调用质量，也定位不到哪一步出错。
