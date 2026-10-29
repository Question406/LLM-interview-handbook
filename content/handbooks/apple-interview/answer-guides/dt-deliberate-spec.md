---
id: dt-deliberate-spec
kind: concept
situation: 看着政策答对不等于学会适用规则。
task: 把安全规则变成可迁移行为。
approach: 生成可查示范，再按公开方法区分训练可见信息。
result: 越狱与 over-refusal 都评，条款版本明确。
---

## 可以这样回答

看着政策答对不等于学会适用规则。

为了让模型学会自己回忆该用哪条规则。生成安全示范时让模型看着政策、在推理里引用条款，SFT 时把政策正文拿掉，模型只能靠回忆；RL 的 scorer 仍看着政策来核对。验证同时看越狱抵抗和 over-refusal，并记下条款版本。
