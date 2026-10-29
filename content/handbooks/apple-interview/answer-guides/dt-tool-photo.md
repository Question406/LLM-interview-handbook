---
id: dt-tool-photo
kind: concept
situation: 用户上传只说明需要识别，不说明可训练。
task: 合法补足工具照片识别 long-tail。
approach: 许可目录、受控拍摄与验证合成为主。
result: 新 SKU 与拍摄条件泛化，来源用途可追溯。
---

## 可以这样回答

用户上传只说明需要识别，不说明可训练。

来自许可产品目录、厂商授权图、受控拍摄和验证过的 synthetic data。用户上传的识别图片只说明产品需要认它，没有明确的训练许可，就不能用作 base model 训练或固定评测。hard examples 从评测失败和许可 long-tail SKU 里挖，评测用按时间留出的新 SKU 和内部拍摄图。
