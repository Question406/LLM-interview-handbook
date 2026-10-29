---
id: dt-code-repo-vs-fn
kind: design
situation: 单函数正确不代表能修完整仓库。
task: 按能力需求分配代码数据。
approach: 函数题教局部逻辑，仓库题保留环境与 tool-use trajectories。
result: 分别测函数正确、跨文件修复及回归。
---

## 可以这样回答

单函数正确不代表能修完整仓库。

分成两个桶，分别 data mix、分别评测。函数级是短 prompt、单文件、单测；仓库级要读 issue、定位多个文件、在执行环境里跑 regression tests，混在一起训，模型会把写独立函数的做法搬到仓库任务上。仓库 trajectories 要保留检索和失败恢复的过程，只训最终补丁，模型学不会定位；SWE-Gym 这类可执行环境里的成功 trajectories 也要再筛，见 `dt-swe-success-noise`。
