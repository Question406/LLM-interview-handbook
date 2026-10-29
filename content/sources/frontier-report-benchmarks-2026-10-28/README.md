# Frontier reports 的 safety/security benchmarks · 2026-10-28

本轮以官方 tech reports / model cards / system cards 的实际采用证据为优先，新增 20 张 canonical cards：2 个索引、18 个专题，位于 llm-safety-security / report-benchmarks。题本由 60 扩到 80 张，章节由 11 扩到 12。

## 可维护记录

- reports.json：10 份抽查报告、官方链接、核对范围、下载 PDF 的 SHA-256。
- benchmarks.json：31 个条目；包含公开 benchmark、任务 variant、攻击方法、internal suites、capability controls 与研究补充，不称为 31 个独立固定安全测试集。
- cards.json：20 张新增题卡及其 benchmark IDs。

## 采用证据规则

实际评测、外部评测、改编版、方法组件、方法使用、该报告退役、仅讨论引用分别标注。报告标题含 safety、正文讨论一个 benchmark、在比较图中出现其他模型，都不能自动证明某个 provider 自己运行了完整公开测试。

对 Llama 4 与 Qwen3 的抽查未建立本表 named public safety benchmarks 的逐项采用证据，只保留为披露范围对照。这不证明公司没有内部评测或从未使用它们。

本批只作目的性取样，不计算全行业采用率。多个同一实验室的版本也不算独立实验室。P0/P1 是基于已核实使用及 agent-security 相关性的阅读优先级。

## 本轮重要发现

- Gray Swan ART / IPI 需要按历史版本、surface、k、safeguards 与 fallback 解释。
- Claude Opus 5.5 §3.3.4 明确说明 CyberGym 在该报告中因 saturation 退役；Grok 4.7 §6.1 仍有实际使用，不泛化成全领域弃用。
- Crescendo 与 GPT-Red 是方法，不伪装成固定数据集。
- MASK-Rectified、FORTRESS-RN、ProtocolQA Open-Ended 是需要保留的 variants。
- Cybench / CyberGym / CVE-Bench / ExploitBench / ExploitGym 测 cyber capability；拒绝、授权与 agent 的 containment 另行评估。
- Public academic baselines 仍有价值；HarmBench、XSTest、AgentDojo 等的研究热度与本次核实的报告采用关系分开。

## 核对方式

官方 HTML / 原论文 metadata 与相关 sections 检索；长 PDF 使用 pypdf 提取分页面文本，并通过 pypdfium2 渲染关键表格与图页。已 visual-review Claude Opus 5.5 PDF p.85（Gray Swan IPI）、Gemini 4 report PDF p.212 / printed p.211（IPI figure）、Grok 4.7 PDF p.23 / printed p.22（StrongREJECT / long-horizon jailbreak table）。

PDF page 为文件顺序，从 1 开始。Gemini / Grok 的 printed page 可能少一。本文不复制报告的大段文字或完整表格；原报告可通过各 card 链接访问。源文件下载仅用于核对，没有随代码提交大型 PDF。

本次创建 references 与研究题，不执行真实外部攻击、模型训练或未公开 evaluations。所有 proposed experiments 使用 prospective phrasing。

## 网站入口

http://127.0.0.1:3000/?book=llm-safety-security&section=report-benchmarks&question=report-benchmarks-map

采用证据索引：
http://127.0.0.1:3000/?book=llm-safety-security&section=report-benchmarks&question=report-benchmarks-evidence

## 完成检查

- 80 张 canonical cards、12 章节、79 个 distinct primary-source URLs；20 张新增 cards 渲染成功。
- 31 个条目的 question IDs、report IDs 与 locators 均有效；全书 internal links 已核对。
- `npm run content:build`：2616 rendered questions / 11 handbooks。
- Node suite：60/60 通过；`git diff --check` 通过。
- 本地 HTTP：80-card index、新章速查页与采用证据表均已成功读取。
