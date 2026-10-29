---
id: dt-url-canon-code
kind: coding
situation: URL 变体可能绕过重复与撤回规则。
task: 统一身份并正确处理拒绝条件。
approach: 规范化时保留语义参数，精确检查政策。
result: 别名、查询参数及拒收优先级按契约测试。
---

## 可以这样回答

URL 变体可能绕过重复与撤回规则。

URL 先统一规范化，再拿去做 deduplication、许可拒绝表和评测匹配：scheme 和 host 转小写，去掉默认端口和 fragment，只删跟踪类 query，保留分页参数。host 后缀匹配要检查 domain matching rules。原 URL 和规范化后的 URL 都要记录，robots 和 opt-out 由上游另做检查。

测试还要满足这个条件：别名、查询参数及拒收优先级按契约测试。
