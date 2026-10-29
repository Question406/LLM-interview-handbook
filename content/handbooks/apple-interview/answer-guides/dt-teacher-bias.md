---
id: dt-teacher-bias
kind: design
situation: 最强 teacher 的输出可能不适合较小 student。
task: 选择 student 能学且覆盖真实任务的数据。
approach: 比较 teacher 风格、难度和验证后 learnability。
result: 同预算 student 收益决定选择，不只看 teacher 分数。
---

## 可以这样回答

最强 teacher 的输出可能不适合较小 student。

teacher 回答正确，不代表 student 能学会。还要查过程是否过长、是否用了 student 没有的工具，以及 student 自己 sampling 时能不能找到类似的正确解。太难的示范可以压缩、拆成子任务，或改用 student 自己生成且验证通过的回答。
