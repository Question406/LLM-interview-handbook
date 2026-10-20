# 一亩三分地 Frontier Lab：完整练习修订版

采集/修订日期：2026-10-18。通过用户Chrome正常读取；复查范围为本轮新增的全部167张题卡，不是仓库其他历史题卡。

本次纠正初版只给摘要的问题：**118张编程/实验题**加入明确题面、接口、约束、示例、完整参考实现、正确性解释、复杂度与可执行测试；**49张非编程题**加入具体场景与参考回答。xAI由24张增至30张，补6张并读取2篇原帖正文/作者补充。代码共85份（83 Python、2 JavaScript/React），相同算法的跨公司变体共用实现，每张题卡都嵌入完整代码。

## 练习和原题如何区分

原帖未披露的函数签名、数值规模、状态规则、测试和实现，均明确标作“手册重构版”或“练习约定”。只确认主题时不假装找回官方原题；Cohere删5、xAI N-gram/输入框三条仅标题线索，保留未核实标记。行为题使用假想示例，不冒称用户或候选人亲历。

`detail-read`为已读详情，`company-card-summary`为公司题卡摘要，`thread-read`/`thread-comment-read`为原帖或作者评论，`title-only`未核实完整题干。网站汇总仍是二手材料；已读取的两篇xAI原帖见curated.json。没有自动回帖解锁隐藏区，也没复制付费文章全文。

## 复习和验证

- 总导航：`content/handbooks/us-tech/questions/overview/p3a-frontier-source-map.md`。
- 每张题卡带`完整编程练习`或`场景参考答案`标签，保留稳定p3a题号。
- 参考程序：`practice/solutions/`，配套关系与测试哈希在`practice/manifest.json`。
- 统一验证：在仓库根执行`python3 scripts/check-frontier-practice.py`，测试结果在`practice/validation.json`。
- Python 3.11验证通过，依赖`practice/requirements.txt`中的NumPy和Pillow。JS使用Node 22与本仓库React依赖。代码验证不调用真实模型、真实账户或外部付费API。

## 来源档案

`curated.json`保存167张题意/路径/证据与练习映射，`source-index.json`/`.csv`保存385条具体来源（含重复变体与标题），`summary.json`保存统计。来源数与题卡数不能相加当独立真题数；本次不宣称穷尽论坛全部内容。

| 公司 | 题卡 | 具体来源条目 |
| --- | ---: | ---: |
| openai | 53 | 182 |
| anthropic | 35 | 79 |
| xai | 30 | 25 |
| microsoft | 16 | 仅相关题卡 |
| perplexity | 16 | 27 |
| mistral | 3 | 3 |
| cohere | 3 | 4 |
| google-deepmind | 2 | 2 |
| cursor | 2 | 10 |
| google | 3 | 14 |
| meta | 4 | 39 |

Google DeepMind独立目录两题来自Android岗，RS论文答辩在Google目录另有明确标记；Google/Meta通用题不推定为Gemini/Llama团队专属。Perplexity/Cursor按相关AI公司补充。现有历史题卡没有覆盖；新增卡的交叉链接用于对照不同契约。
