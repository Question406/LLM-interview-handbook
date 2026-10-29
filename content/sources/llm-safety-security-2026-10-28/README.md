# LLM / Agentic Safety & Security · research snapshot

- 检索截止：2026-10-28。
- Canonical book：content/handbooks/llm-safety-security。
- 60 cards：58 topical research questions + 2 guides；11 sections；51 primary references。
- sources.json 保存原始论文/作者官方研究/协议文档的链接、年份、证据类型、适用范围和核对日期。
- cards.json 连接每张题卡与 source IDs，便于 traceability、维护和查漏。

## 检索与阅读方法

主题包含 agent prompt injection、2026 dynamic/long-horizon benchmarks、memory poisoning、tool metadata / MCP、skills permissions、computer use、multimodal observations、information-flow defenses、AI control、CoT monitoring、privacy 与 secure coding evaluation。通过 web 搜索发现材料，再采用 arXiv、ACL/PMLR/会议原文、作者官方材料和 MCP 官方文档作为依据。

AgentDojo / ASB / InjecAgent / AgentHarm / SafeArena 等经典资料用于基础。2026 sources 包含 AgentDyn、AgentLAB、Skill-Inject、SkillGuard、Role Confusion、OS-BLIND、OSGuard、IH-Challenge、Constitutional Classifiers++、MonitorBench、eTAMP、benchmark-validity audit、Summer 2026 misalignment case studies，以及 2026-10 的 StegoMemory / Ignored, Not Refused。

CaMeL 与 Design Patterns 读取了 HTML full text 的结构与相关 sections；其余资料主要核对原始 abstract/metadata、官方项目说明与必要的 primary paper excerpts。索引不声称已经复现全部 artifacts。真正执行复现前，应进一步 pin source commit、dataset revision、scorers、model versions 和 attack budgets。

## 编辑与证据规则

1. 所有 cards 标 realInterview=false，为公开 research 整理的讨论题。
2. Professional terms 使用英文，中文解释选择、因果与具体例子。
3. 每张卡的完整答案前有 Situation / Task / Approach / Result callout。
4. 文献论点、适用范围与手册提出的实验分开；“我会”是 prospective phrasing，不编造用户经历或实验结果。
5. 最新 preprints 显式标注；simulations 与真实 incidents 区分；无条件安全或行业定论不从单篇论文推断。
6. 不复制论文的攻击 payload / 代码；实验使用 synthetic data、mock tools 和隔离环境。
7. Primary references 中的 protocol docs 作为工程规范依据，不冒充研究结论。
8. 统计公式和 proposed baselines 属于手册分析；独立性、预算、utility 与 scorer assumptions 同时说明。

## 阅读入口

http://127.0.0.1:3000/?book=llm-safety-security&section=guide&question=sec-research-map

全部 references 和 benchmark comparison：
http://127.0.0.1:3000/?book=llm-safety-security&section=guide&question=sec-reading-and-benchmark-index

## 完成检查

- 60 个 canonical IDs 与生成目录一致；51 个 primary references；所有内部 question links 均可解析。
- 每卡包含题面、四项 callout、自然口述、实验方案、追问和来源；guide 默认展开，研究题参考答案默认折叠。
- `npm run content:build`：2596 rendered questions / 11 handbooks。
- 现有 Node suite：60/60 通过；数学公式已用 KaTeX 渲染。
- Existing coding guidance checker：635 coding cards / 392 displayed simple examples，覆盖未回退。
- 本地 HTTP：catalog、新题本 index 与 research map 均已成功读取；60 cards / 51 sources 与 canonical source 相符。
- 本次只创建研究题本与文献索引，未声称执行了所提议的模型训练、攻击或 defense experiments。
