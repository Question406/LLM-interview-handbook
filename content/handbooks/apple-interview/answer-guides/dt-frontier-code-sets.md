---
id: "dt-frontier-code-sets"
kind: "design"
situation: "代码基准覆盖函数、仓库和终端操作。"
task: "按目标能力选择评测与训练任务。"
approach: "检查环境、测试和题目时间窗。"
result: "新题与真实执行支持收益，不混报子集和语言。"
---

## 可以这样回答

代码基准覆盖函数、仓库和终端操作。

这三套测的是不同的代码能力：SWE-bench 修真实 GitHub issue，新测试要从失败变成通过，旧测试还得过；Terminal-Bench 在终端里做完工程任务，运行框架对分数影响很大；LiveCodeBench 按比赛日期切新题，测算法编程、减少背题。三种分数不能合成一个比。
