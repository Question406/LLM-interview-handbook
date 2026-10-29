---
id: dt-swe-success-noise
kind: concept
situation: 终局补丁正确仍可能包含差的工具行为。
task: 决定成功 trajectories 哪些部分值得学。
approach: 剔除改测试和无效循环，审核恢复片段。
result: 新任务行为改善，筛选比例由当前数据决定。
---

## 可以这样回答

终局补丁正确仍可能包含差的工具行为。

不能。hidden tests 通过只说明最终补丁对，过程里仍可能有改测试、重复执行但没有推进任务和反复失败的 tool calls，整段进 SFT 会把这些一起教给模型。先丢掉改过测试文件的 trajectories，再按过程质量筛片段，loss 只算助手生成的编辑和推理。SWE-Prime 筛出的约 10% 子集胜过全部已解决 trajectories，这个比例是论文 ablation study 结果，换了数据要重新定。
