---
id: dt-secret-scan-code
kind: coding
situation: 公开仓库也可能 leakage 可用密钥。
task: 定位敏感候选并控制 false positive。
approach: 模式与上下文、熵等信号结合，记录位置。
result: 检查示例值和真实格式，结果不直接外泄。
---

## 可以这样回答

公开仓库也可能 leakage 可用密钥。

用提供商前缀加字符串熵来找凭证，命中后整个文件隔离，高价值来源再人工核对。示例密钥可以白名单；只做脱敏的文件仍可能教会模型密钥格式，来源和安全检查都要做。检测覆盖不了所有提供商，teacher model 的合成输出也要扫。

测试时，我会检查示例值和真实格式，结果不直接外泄。
