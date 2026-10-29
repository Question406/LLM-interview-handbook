---
id: dt-pii-luhn-code
kind: coding
situation: 规则匹配可能把 ISBN 或示例号当敏感信息。
task: 找到候选并区分真命中与假阳性。
approach: 正则定位后做 Luhn 或格式校验，保留位置。
result: 有效卡号、无效校验和与代码样例分别测试。
---

## 可以这样回答

规则匹配可能把 ISBN 或示例号当敏感信息。

先用正则找可能的 personally identifiable information (PII)，再做校验：信用卡号用 Luhn，邮箱和电话查格式。命中后记下文本位置，隔离还是脱敏交给单独的规则决定。代码里的示例卡号 `4111-1111-1111-1111` 和 ISBN 会 false positive，要按领域设白名单，命中都记录下来再处理。

测试还要满足这个条件：有效卡号、无效校验和与代码样例分别测试。
