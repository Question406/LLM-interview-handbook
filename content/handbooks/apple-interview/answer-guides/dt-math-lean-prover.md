---
id: "dt-math-lean-prover"
kind: "design"
situation: "自然语言论证不容易自动判定。"
task: "判断形式化验证可覆盖哪些任务。"
approach: "将命题和证明分开验证，检查形式化忠实度。"
result: "证明通过且命题对应原题，不外推到全部数学。"
---

## 可以这样回答

自然语言论证不容易自动判定。

能，但只覆盖形式化证明。Lean 的 kernel 逐步检查证明，通过编译和证明检查才算正例，比只看最终 boxed 答案可靠；DeepSeek-Prover 先用成功证明和子目标冷启动，再用 Lean 反馈做 RL。自然语言计算题仍要靠 TIR 等方法验证，两类数据和 grader 分开记录、分开评测。
