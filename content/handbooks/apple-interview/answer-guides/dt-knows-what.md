---
id: dt-knows-what
kind: concept
situation: 强行回答未知事实容易制造 hallucination。
task: 学会在缺乏证据时表达不确定。
approach: 先探测已知知识，再构造承认不知道与检索示范。
result: 不该答时少编造，已知任务不一律拒绝。
---

## 可以这样回答

强行回答未知事实容易制造 hallucination。

先探测模型已经会什么，再教它对不会的题承认不知道。拿事实题反复问，模型多次给出具体但错误的回答，就配上承认不知道的示范；用 SFT 硬灌新知识更容易引发 hallucination，新事件交给搜索。探测题从许可的 pre-training 材料里生成。
