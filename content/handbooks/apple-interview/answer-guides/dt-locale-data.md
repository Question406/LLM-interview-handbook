---
id: dt-locale-data
kind: design
situation: 翻译自然度和当地任务习惯会影响评价。
task: 识别真实 locale 缺口。
approach: 母语任务与本地协议优先，翻译只作补充。
result: 独立当地 human evaluation 与 capability slices 支持改进。
---

## 可以这样回答

翻译自然度和当地任务习惯会影响评价。

训练和评测用不同来源。训练可以用验证过的机翻和爬取 corpus 补覆盖，用母语者示范和 human evaluation 改善自然度；正式评测让母语者直接出题，翻译题不自然，测到的只是英语题的影子。过滤阈值按语言做 calibration，配额逐步提高，桶内做 temperature sampling；AFM 公开把 multilingual 比例从 8% 提到 30%，human evaluation 不用翻译题。
