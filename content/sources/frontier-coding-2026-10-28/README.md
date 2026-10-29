# Frontier coding 来源核对 · 2026-10-28

收录九张 coding cards，清单见 [cards.json](./cards.json)。网页总导航：[五家公司 Coding 新题](http://127.0.0.1:3000/?book=us-tech&section=overview&question=frontier-coding-guide-2026-10-28)。

## 证据范围

- Meta：两位 Reddit 候选人的自述；具体披露 convolution、node-count diameter、LC32。按来源支持到的题型收录。
- Humans&：DrustZ 第一手博客的美卡论坛同作者转贴，Humans& 小节确认 top-p 与实时 debug；缺陷代码、mask 和测试是手册练习约定。原博客链接保留，浏览工具打开失败后用公开转贴核对。
- OpenAI indexed sequence：Chill Interview 的 Reddit 转述及 Land the Lab 公开目录，属于二手来源；免费内容支持 add/get 与 cheap snapshots 方向，persistent treap 是手册选择。
- OpenAI tree counting：只采用 Screna 的 Questions Asked 区公开题目。页面的 AI Generated Hints 不用作候选人经历证据；重复投递、多 request 与具体 API 是手册约定。
- xAI autocomplete：AceOffer 公开目录/预览支持 offline local-data autocomplete 题型；登录后的完整题干与 follow-ups 未读取。Trie、ranking、nondecreasing score 与 prefix cache 是手册约定。
- Thinking Machines Lab：一亩三分地两帖仅支持存在 coding 轮；具体 coding 原题仍缺少公开题面。两张卡明确取材官方 batch-invariance 与 LoRA 文章，realInterview=false。排除菲律宾同名公司的题目；不将 SEO 站的推测当作候选人记录。

## 查重

xAI 的 KV/transactions、LRU、sorting、group testing、flatten/unflatten、Spaces、patchify、distributed matmul、speculative edits，及 OpenAI 的 credits、KV、SQL、NumPy、autograd 等已存在，导航复用原题，不重新计数。

## 来源

- [Meta 候选人自述：ML Research Scientist loop](https://www.reddit.com/r/leetcode/comments/1r37w7q/meta_ml_research_scientist_interview_experience/)
- [Meta 候选人自述：2D convolution](https://www.reddit.com/r/leetcode/comments/1reuwrd/meta_ai_coding_interview/)
- [Humans& 第一手记录：DrustZ 找工记（3）](https://www.uscardforum.com/t/topic/535363)
- [Thinking Machines Lab coding round 公开讨论，2026-08](https://www.1point3acres.com/home/thread/1185730)
- [Thinking Machines coding rounds 公开讨论，2026-10](https://www.1point3acres.com/interview/discussion/1191996)
- [Thinking Machines Lab：batch invariance 官方文章](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)
- [Thinking Machines Lab：LoRA 官方文章](https://thinkingmachines.ai/blog/lora/)
- [OpenAI indexed sequence：二手候选人记录](https://www.reddit.com/r/OfferEngineering/comments/1wzedra/openai_senior_software_engineer_interview_it_felt/)
- [OpenAI tree message counting：公开候选人记录](https://www.screna.ai/experience/aa1b5634-5b22-42a3-9077-5787f791e718)
- [xAI offline autocomplete：二手题型目录](https://aceoffer.app/interviews/xai_autocomplete_input_box)

验证命令：使用安装 NumPy/PyTorch 的 Python 运行 scripts/check-frontier-coding-new.py；九张题目直接从 canonical Markdown 执行。九份程序在 NumPy/PyTorch 环境全部通过；九道独立题面校验通过。构建生成 2,398 道网页题；58 项 Node 测试、615 道 coding cards 的测试说明检查、公司筛选与导航链接检查通过。
