---
id: dt-llama-edit-pref
kind: concept
situation: 两条中更好的回答也未必达到标准。
task: 获得更清晰且有质量底线的偏好。
approach: 编辑改善 chosen，区分强弱信号和 label noise。
result: 独立质量而非仅排序准确率支持选择。
---

## 可以这样回答

两条中更好的回答也未必达到标准。

两个做法都是为了让偏好信号更干净。chosen 只是两条里较好的那条、未必达标，所以 Llama 3 让 annotator 再改一遍，得到 edited > chosen > rejected；差距很小的对 label noise 大，reward model 只用清晰的 preference pairs，DPO 只留「明显更好」和「更好」两档。AFM 用 cohesion 优先选 human evaluation 一致的 prompt，也是在减少弱信号。
