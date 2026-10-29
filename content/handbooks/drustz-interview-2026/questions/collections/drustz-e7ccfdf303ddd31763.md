---
id: drustz-e7ccfdf303ddd31763
section: collections
order: 19
level: A
title: Google DeepMind 题库（爬取全量） · 流程与情报
quick: 作者文档章节 · Google DeepMind 题库（爬取全量） · 流程与情报
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/gdm.md
    type: primary
---
## 流程与情报

### GDM RS Intern 完整 4 轮流程（2022 Summer）：HR screening 起步，senior RS 主动挖人+referral
*medium · 频率: high（intern technical 轮 3 帖同格式：819210/813950/942891） · 2021-11*

《Deepmind 2022 Summer Research Scientist Internship 面经》2021-11-13。原文首段："AI 第三年博士，突然被Deepmind一位senior research scientist 联系要不要来summer intern，然后网申加上他给的referral，就进入了Deepmind 4 轮面试：1、HR screening……"（第 2-4 轮正文积分墙隐藏）。结合同期帖子可拼出 intern 轨全貌：1) HR screening；2) technical interview（813950：1 小时，一位 scientist 全程口头问基础数学概念——linear algebra、statistics 主要是 probability、ML，最后跟一个代码阅读；942891 同款：简单数学题+code comprehension+基本 ML 问题）；3) research/team 面；4) team match/final。Glassdoor 交叉数据：GDM intern 全程平均 120 天，极慢。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-819210-1-1.html&gt;)

### Official GDM interview process: 4 stages, 4-10 weeks, competency-based, no AI in live interviews
*unknown · 频率: official source · 2025*

From DeepMind's official candidate PDF: stages are Initial interviews → Skills interviews → Final interviews → Decision and offer. Candidates sign an NDA (Ironclad) before interviewing. Interviews are virtual (Google Meet), competency-based; DeepMind explicitly recommends STAR (Situation/Task/Action/Result) answers and 'clearly defined criteria' scoring for fairness. Timeline 4-10 weeks depending on role. AI policy: 'You're free to use AI to help you prepare... but unless told otherwise, please don't use any AI tools during live interviews, or during interview tasks.' Interviewing in parallel with Google is allowed but must be disclosed. Internships run through Google recruiting, not GDM. Tips emphasized: think out loud, admit uncertainty ('curiosity and intellectual honesty'), use data to demonstrate impact, prepare questions.

来源: &lt;[来源链接](https://storage.googleapis.com/deepmind-media/DeepMind.com/Assets/Docs/interviewing-at-google-deepmind.pdf&gt;)

### Research Engineer loop structure (IGotAnOffer guide): recruiter → gated coding screens → ML rounds → final round
*hard · 频率: aggregated from many reports · 2025*

Recruiter screen is conversational; recruiter decides whether you fit the research-focused or applied side, sometimes adds a hiring-manager interview probing ML+engineering background. Skills round = 2-3 calls: two coding rounds (algorithmic, in a real coding environment) plus a set of ML rounds testing depth/breadth of ML knowledge including the math and application to design problems. The two parts are gated — you must clear coding before ML, sometimes with a ~2 week wait. Key difference vs Google: 'DeepMind expects your code to actually run by the end of the round' (CoderPad-like environment). Final round = (1) team lead interview: background, ML experimentation/modeling experience, open-ended ML problems; (2) senior team lead interview: explicit team-fit assessment; (3) People & Culture partner: motivation/culture ('why do you want to join DeepMind'). Anything on your resume can come up; be ready to defend design decisions and discuss conflict with coworkers. ML rounds are consistently described as the toughest part of the process.

来源: &lt;[来源链接](https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview&gt;)

### Blind: full RE loop report (Amazon MLE, L5) — 2 coding screens, 2 ML screens, virtual onsite, rejected at team fit
*hard · 频率: single detailed report; structure corroborated by IGotAnOffer and Reddit · 2023*

6-7 weeks total. Round 1: two coding screens with Google-style questions from Google's internal bank. First screen: one LC-medium coded + LC medium/hard follow-up (explanation only) + LC easy + LC easy/medium (explanation only). Second screen: an LC-hard not found on LeetCode requiring knowing a polynomial-time solution. 'You have to run the code and it's expected that by the end you have a solution which runs in CoderPad.' Round 2 (only after clearing coding): two ML screens. First probed depth of ML knowledge — probability, Bayes-theorem questions ('a number of balls style question on Bayes theorem'), plus design problems; emphasis on mathematical intuition (e.g., not just that L1 gives sparse features but WHY, in terms of gradients acting on weights). Second ML screen: 'hardest ML round I ever gave' — design-style question where interviewer kept adding constraints; discussed 7-8 different techniques with 7-8 constraints layered onto each solution. Round 3: virtual onsite = two non-technical interviews with team leads on background and ML experimentation experience + one People&Culture behavioral. Outcome: rejected with feedback 'didn't have enough experience in ML experimentation and modeling.'

来源: &lt;[来源链接](https://www.teamblind.com/post/deepmind-research-engineer-interview-process-wp1gjgyb&gt;)

### techinterview.org 2026: RS track round-by-round (paper discussion, research problem framing, ML coding, math/theory, behavioral)
*hard · 频率: prep-site synthesis (unverified but consistent with candidate reports) · 2026*

Research Scientist loop per this 2026 process guide: (1) Paper discussion, 60 min — present a recent paper of yours (or one you know deeply if unpublished); interviewer probes methodology, motivation, weaknesses, extensions; 'interviewers will push hard on assumptions'; candidates often do 2-3 paper discussions with interviewers from different subdomains. (2) Research problem framing, 60 min — open-ended problem; propose experiments, metrics, theoretical analysis, and what would falsify the approach; tests scoping under ambiguity. (3) ML coding, 60 min — implement a piece of ML pipeline by hand: custom loss, attention mechanism, sampling routine, or small training loop; 'almost always unaided.' (4) Math and theory, 60 min — probability, linear algebra, optimization, gradient flow, Bayesian inference, convergence, information theory. (5) Behavioral, 45 min — mission alignment, collaboration, past disagreements with collaborators. Overall funnel: recruiter screen → HM screen → 1-2 phone screens → 5-7 round loop → hiring committee (written packet, decision-makers are not your interviewers) → team match/offer. 8-12 weeks for research roles. PhD 'effectively yes' for RS.

来源: &lt;[来源链接](https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/&gt;)

### 2026 AI-tool policy in technical rounds: prohibited/heavily limited — unaided reasoning is filtered for
*unknown · 频率: multiple sources · 2026*

Multiple 2026 sources agree DeepMind is 'AI-prohibited or heavily limited in all technical rounds'; research roles explicitly filter on unaided foundational reasoning — implement algorithms and ML primitives without AI assistance. Official DeepMind PDF confirms: no AI tools during live interviews or interview tasks unless told otherwise. Positioning vs peers: more conservative than Anthropic (which grades AI-collaboration in some rounds), more uniform than OpenAI. Exceptions possible for applied roles — verify with recruiter.

来源: &lt;[来源链接](https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/&gt;)

### Blind 2023-06: the math/stats 'quiz' still exists but format loosened from 2-hour exam
*medium · 频率: multiple corroborating comments · 2023-06*

Ex-Googler (PhD, 3 YOE) preparing for RE asked whether DeepMind still asks 'math/stats knowledge questions such as definitions from the textbooks.' Answers: one commenter initially said the quiz was discontinued, then edited: 'incorrect, they still do'; another confirmed 'I am interviewing in couple of weeks and first interview is about that'; a third noted the format has evolved — 'some math/stats questions are asked, [but] it does seem different from previous years, when they had a 2h exam-like format.' IGotAnOffer corroborates: candidates call the ML fundamentals round 'the quiz'; it used to be a rigid set of textbook questions but has loosened in recent years; recruiters flag maths/stats coverage in advance. Historical variant (Blind): 'DeepMind for Google Research' vs 'DeepMind for Google' applications differed, the former involving a 2-hour quiz with ML and coding components.

来源: &lt;[来源链接](https://www.teamblind.com/post/interviews-for-research-engineer-at-deepmind-kd1tfu6b&gt;)

### Aleksa Gordić (hired 2021, Medium): 6-stage RE loop incl. 2 back-to-back quiz interviews covering math/stats/CS/ML + OS
*hard · 频率: single detailed report (pre-2024 but structurally consistent with current loop) · 2022-07*

Historical but detailed first-person account of getting RE (Core team) offer: stages = (1) recruiter chat (Core vs Applied fit); (2) quiz round: TWO back-to-back interviews on fundamentals across maths (linear algebra, probability, calculus), stats (hypothesis testing, distributions, inference), CS (algorithms/data structures, sorting/searching, formal big-O, operating systems: deadlocks, threads, virtual memory), ML (RL fundamentals: MDP/agent-environment-reward, classical ML, core DL); (3) coding interview (classic big-tech style); (4) team lead interview (resume deep-dives, open-ended ML problems, behavioral); (5) senior team lead interview (team fit, ML systems design); (6) People & Culture ('What do you like about DeepMind?', 'Why DeepMind and not some other company?', 'Tell me about your favorite project'). Prep resources he used: Cracking the Coding Interview, CLRS DP chapter, Mathematics for Machine Learning book, jbstatistics + StatQuest, GeeksForGeeks. Advises researching each interviewer's papers/profiles beforehand.

来源: &lt;[来源链接](https://gordicaleksa.medium.com/how-i-got-a-job-at-deepmind-as-a-research-engineer-without-a-machine-learning-degree-1a45f2a781de&gt;)

### Entry bar and RS-vs-RE routing (2026 Reddit + Blind): RS effectively needs PhD + strong pubs; RE flexible; recruiters are the main channel
*unknown · 频率: multiple corroborating reports · 2026-01*

r/MachineLearning 2026-01 thread (Amazon Applied Scientist II, no PhD, asking RE vs RS): top comment — 'You're not getting an RS interview unless you've published heavily... Apply for RE. Try and connect with a recruiter first. All my interviews with DeepMind came from recruiters and having a relationship with them.' GDM staff commenter: no hard publication rule — 'I would take a candidate that only wrote one paper if that paper was revolutionary'; being at another respected lab or doing relevant applied ML work counts; 'I was doing applied ML engineering before joining GDM'; once inside, RE→RS is fluid given research taste. Another academic: 'My PhD students graduate with 3+ tier-1 papers and ~100 cites and aren't getting RS interviews' — bar is high and noisy. Blind (2023): 'For research scientist they hire only PhDs but for research engineer they go for masters too.' 2026-05 Reddit RE candidate got the interview via cold LinkedIn application with an ACL first-author paper + senior GenAI SWE experience; used Claude to rewrite CV with JD keywords.

来源: &lt;[来源链接](https://old.reddit.com/r/MachineLearning/comments/1q2wiub/d_google_deepmind_research_engineerscientist/&gt;)

### Glassdoor overall stats and stage pattern (2024-2026): recruiter → 2 coding + 1 ML fundamentals → ML design + lead researcher
*medium · 频率: aggregate of ~18 RE + 13 RS reports · 2026*

Glassdoor aggregate for GDM Research Engineer: stages reported as '1) Recruiter call, 2) 2 Coding Interviews + 1 ML Fundamentals interview, 3) ML Design + an interview with the Lead Researcher.' Coding = two DS&A problems per virtual interview, standard LeetCode medium/hard; unlike standard Google interviews, code must RUN in a CoderPad-like environment with a working solution by end of round. Candidates also 'describe research papers and answer coding questions plus technical and theoretical questions in deep learning relevant to the role.' RE: difficulty 3.3/5, 61% positive, 46 days avg (18 reports). RS: difficulty 3.2/5, 49 days avg. Both Glassdoor interview pages are bot-blocked; data recovered via search snippets.

来源: &lt;[来源链接](https://www.glassdoor.com/Interview/Google-DeepMind-Interview-Questions-E1596815.htm&gt;)

### Interviewing.io: no DeepMind guide exists (only OpenAI/Anthropic company pages)
*unknown · 频率: n/a · 2026-07*

Checked interviewing.io for a DeepMind guide as requested: the site has dedicated company pages for Anthropic (interviewing.io/anthropic-interview-questions) and OpenAI (interviewing.io/openai-interview-questions) but no DeepMind-specific interview page as of 2026-07. Their generic AI-era interviewing posts don't cover GDM's loop. Use IGotAnOffer/techinterview.org/Glassdoor instead for GDM.

来源: &lt;[来源链接](https://interviewing.io/blog&gt;)

### GDM Research Engineer 挂经（2025-09，唯一确认的 2025 年 RE 全流程面经帖）
*unknown · 频率: single report · 2025-09*

帖子标题《Deepmind Research Engineer面经（挂经）》，发于 2025-09-23，海外面经版。正文在登录+积分墙后，无 Wayback 快照，无法恢复具体轮次内容。可确认：岗位 Research Engineer，结果为挂。这是 1p3a 上 2024-2026 期间唯一一篇 GDM RE 正式面经帖。结合 1p3a interview 聚合页（/interview/company/deepmind）显示的条目：有一条 2025 年 7-9 月的 Machine Learning 面试记录和一条 2023 年 10-12 月伦敦 Research Scientist 面试记录。若需正文，需要 1p3a 账号且积分达标。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1147017-1-1.html&gt;)

### GDM RE 伦敦 2022 改版流程：两大轮，第一大轮 = math / ML / CS+coding 三个一小时（GDM vs Google 区别的核心证据）
*medium · 频率: 流程结构被 3+ 帖交叉印证（918169/837817/825115） · 2022-08*

《deepmind伦敦 RE面试》2022-08-09。原文首段："recruiter联系就面了一下 之前不太了解RE的面试流程 不知道是整体都改了 还是RE和RS不同。目前RE是两大轮面试 第一大轮是三个一个小时的面试 分别是math, ML, cs+coding……"（后文积分墙隐藏）。即 RE 流程：第一大轮 3×1h 独立场（数学、机器学习、计算机科学+编码），过了再进第二大轮（结合其他帖为 ML design / Hiring Manager+BQ / team match）。这与 Google 普通 SWE 的 4-5 轮纯 LC + Googleyness 完全不同：GDM 由自己的 recruiter 驱动、按 RE/RS 分轨、显式考数学统计与 ML 理论。

**解法**: 我的推断：math 场以概率+线性代数口头快问快答为主（见 813950/825115 帖佐证），ML 场考基础概念深挖，CS+coding 场为 LC medium 级现场写码+复杂度分析。按三场分开准备。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-918169-1-1.html&gt;)

### GDM ML Research Engineer 正式面试三轮结构：coding / ML / Hiring Manager+BQ（终轮面经）
*medium · 频率: 单帖，但三轮结构与 825115 完全一致 · 2022-01*

《DeepMind ML research eng终轮面经》2022-01-11。原文首段："DeepMind ML research engineer，正式面试有三轮，一轮coding，一轮ML，第三轮Hiring manager + BQ。前两轮之前有发过面经。第三轮12/2, 12/3。"（终轮具体问题在积分墙后）。与 918169 相互印证：recruiter 聊天 → coding 轮 → ML 轮 → HM+BQ 终轮。时间线：11 月面前两轮，12 月初终轮。

**解法**: 我的推断：HM 轮一半以上时间会深挖简历里某个具体 model/项目的技术细节（825115 楼主终轮实录佐证），BQ 为标准冲突/失败/协作题。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-837817-1-1.html&gt;)

### GDM Research Scientist 终轮格式：research talk + 与每位 teammate 各聊 30 分钟（含与大佬面试求教帖）
*hard · 频率: 2 reports（942817 + 875411 流程互补） · 2022-11*

《DeepMind Research Scientist 最后一轮 求教如果跟citation 15w+的大佬面试》2022-11-05。原文首段："LZ是ML PhD……阴差阳错的面到了deepmind的最后一轮。最后一轮出了要做research talk，还要跟公司的teammate每个人都聊半个小时的那个环节"，且其中一位面试官是 citation 15w+ 的大佬。印证 RS 轨终轮 = job talk（研究报告）+ 逐个团队成员 1:1。结合 875411：RS 流程入口为 LinkedIn 看到职位→官网投递→2 周后 recruiter email→先与 team manager 面谈（岗位为 DeepMind London，与研究方向高度匹配）。

**解法**: 我的推断：research talk 按 job talk 标准准备 45-60 min 报告+被打断问细节；对大佬面试官不必迎合其领域，重点讲清自己工作的 motivation、与 DM 研究方向的连接、未来 1-2 年 research agenda。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-942817-1-1.html&gt;)

### GDM RE 面试 timeline 实录（进行时长帖，3 页）：1 月海投→3 月 HR 联系→可自选推迟 1 个月，招聘周期极长
*unknown · 频率: single report（长帖多人跟更） · 2022-04*

《Google DeepMind Research Engineer 面试 （进行时）》2022-04-02 开帖，持续更新至 2023-10（3 页、回复量大）。原文首段："一月初海投的以为没有什么戏，3月HR联系我，和HR聊了一下，问我什么时候面试，我说能不能1个月之后，HR说完全没问题，招聘周期长……"（后续各轮 update 在积分墙后）。要点：GDM 海投有响应但周期以月计；HR 允许候选人大幅自定面试时间（备考窗口可谈）；与 Glassdoor 数据一致（RE 平均 46 天从面到 offer，全岗位平均 40-41 天，intern 120 天）。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-878129-3-1.html&gt;)

### GDM RS 伦敦电面（两个组同时面）：HR screening 内容 + 跨组共享轮次机制
*unknown · 频率: 2 reports (682678, 579309) · 2020-10*

《deepmind伦敦电面》2020-10-29。原文首段："面了伦敦两个组的research scientist 一个是朋友内推的 一个是自己海投 面试内容两个组有共同的部分 就都一起面的。HR screening基本上就是问你想做啥 介绍一下面试流程……"（后续隐藏）。要点：可同时进两个组的 RS 流程，技术轮跨组共享结果；HR screening 主要问研究意向并讲解流程。另《DeepMind DMG research scientist Intern》(thread-579309, 2019-12) 印证：第一轮 HR 聊天的目的是"HR想给你找合适的组来面你"，即先 team match 后技术面。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-682678-1-1.html&gt;)

### GDM 薪酬数据点（1p3a 晒工资版）：2022 L4 RE offer 谈到 4 年均 400k/首两年 520k；2024-2025 另有 Refresh 与 RE 包裹帖
*unknown · 频率: 4 data points · 2022-08 / 2024-03 / 2025-01*

三个薪酬帖：(1)《DeepMind L4 报一波》thread-906852，2022-08："上面报的是initial offer，后来DeepMind加到了4年平均400k，第一年第二年520k"（美元/年，含股票；初始包数字隐藏）；(2)《Google Deepmind Refresh》thread-1051085，2024-03（数字隐藏）；(3)《Google Deepmind Research Engineer包裹》thread-1105016，约 2025 初（数字隐藏）。另《Deepmind Research Scientist London包裹》thread-662595，2020-08：伦敦 RS 包裹无 sign-on，为谈过一轮后的数字（具体隐藏）。用于谈包参考：GDM offer 有较大谈判空间（906852 案例 initial→400k avg）。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-906852-1-1.html&gt;)

### 组织背景：2023 年 Google Brain 与 DeepMind 合并为 GDM，招聘/面试流程与 Google 普通 SWE 仍分离
*unknown · 频率: unknown · 2023-04*

《🐶家合并了research和deepmind》thread-989608，2023-04："新的pa还叫deepmind，但是不是other bet"——合并后 GDM 成为 Google 内的 PA（product area）而非 Alphabet other bet。对面试的含义（多帖综合）：GDM 仍有独立 recruiter、独立面试轨（RE：coding+ML+math quiz+ML design+HM；RS：manager chat+technical quiz+research talk+team 1:1s），不走 Google SWE 的统一 HC/packet 流程；但 coding 轮题风与 Google 题库趋同（1116355 帖策略佐证）。另有《[公司评价] Google的经历》thread-1114328（2023 年入职 GDM 者吐槽代码质量）可作团队体验参考。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-989608-1-1.html&gt;)

### 1p3a GDM 面经索引（deepmind 标签页全量清单，截至 2026-01 共 29 帖）
*unknown · 频率: 29 threads total · 2019-2026*

deepmind 标签页（tag/deepmind-3761-1.html，2026-01-16 时 29 主题/344 回复）经 Wayback 恢复的全部面试相关帖：2025: 1147017(RE挂经), 1116355(DS求米), 1105016(RE包裹)；2024: 1051085(Refresh)；2022-2023: 989608(合并讨论), 942891(RS intern tech), 942817(RS终轮), 938855(ML design), 938777(SWE intern), 918169(伦敦RE流程), 906852(L4包), 878129(RE进行时), 875411(RS technical), 865383(research lab做eng体验讨论), 837817(RE终轮)；2021: 825115(RE二轮ML), 824784(research SDE职责讨论), 819265(RE电面), 819210(RS intern 4轮), 813950(RS intern quiz)；2019-2020: 695950(RS intern), 689380(research tech店面), 682678(伦敦RS电面), 662595(RS London包), 637871(London电面), 628812(英国实习/applied scientist), 579309(DMG RS intern), 578953(RE一面), 540650(RE quiz), 482242(intern一二轮), 475151(面经), 467663(SDE intern挂经), 455587/432949/444088/426795(2018-19老帖)。另有淘帖合集 collection/229692。所有正文均需登录+积分。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/tag/deepmind-3761-1.html&gt;)

### Google DeepMind RS/RE interview process summary (Sundeep Teki company guides; details paywalled)
*unknown · 频率: single source (commercial guide) · 2026*

Visible summary: 5-8 rounds through Google's hiring-committee structure; technical assessment spans 'maths, statistics, ML, coding, and system design' with emphasis on 'first-principles mathematical fluency' and 'JAX-native implementation'; cultural signals: intellectual curiosity, scientific rigour, 'Googleyness & Leadership'; comp cited &#36;336-406K + GOOG equity. Contrast drawn: OpenAI = 3-6 rounds incl. research discussion round where 'OpenAI sends you a paper to analyze', practical coding (LRU caches, rate limiters) not pure LeetCode, 'AGI focus / intense & scrappy' culture signal; Anthropic = CodeSignal 4-level assessment with 520+/600 passing threshold, 4-6 rounds incl. explicit safety round, focus on 'practical coding, LLM system design, Constitutional AI fundamentals', 'do the simple thing that works' culture. Full guides are paid (Stripe links); only these summaries are free.

来源: &lt;[来源链接](https://www.sundeepteki.org/company-guides.html&gt;)

### GDM Research Engineer 完整面试流程（2026 版，IGotAnOffer 聚合指南）
*hard · 频率: 聚合指南（基于 Glassdoor+Blind 多条报告） · 2026-06*

全程 6-7 周（含 hiring committee 可更长）。流程：简历筛（~90% 淘汰）→ 30min recruiter call（判定你适合 Applied 还是 Core 方向，有行为面成分）→ 可能加 HM 面 → Skills 轮 2-3 场：2 轮 coding + 一组 ML 轮（fundamentals + design）；coding 与 ML 轮是 gated 的——必须先过 coding 才安排 ML，中间可能等两周 → 终面：Team Lead 面（简历任何内容+开放式 ML 问题）+ Senior Team Lead 面（更明确考察团队匹配）+ People & Culture 行为面 → 每轮面试官填standardization反馈表（Strong no hire→Strong hire），打包送第三方 hiring committee → 4 种结果：录用 / 先 team match / 加面 1-2 轮 / 拒。Coding 轮特点：LC medium-hard，题目多出自 Google 内部题库，CoderPad 环境，要求代码最终真正跑通（与普通 Google 面不同）；每题约 20 分钟；建议刷 LeetCode Google-tag 最新 top 50；明确限制/禁止 AI 编程助手。级别（L3/L4/L5）全程不告知，过 loop 后才定。ML 轮被普遍称为整个流程最难部分。

来源: &lt;[来源链接](https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview&gt;)

### 【重要情报】2025 起 RE 岗 recruiter 确认取消 maths/stats quiz，保留 ML/AI quiz + coding
*unknown · 频率: 2 条独立报告（2023、2025） · 2025-03*

Blind 2025-03-01（Meta 员工，10 天后面 GDM RE）：“Recruiter confirmed that there is no maths / stats quiz anymore”，评估组件为 ML/AI quiz 和 coding 轮。佐证：Blind 2023-06 帖（kd1tfu6b，ex-Googler PhD）评论区称“仍会问一些 math/stats 问题，但与前几年 2 小时考试式格式不同”——即 quiz 逐年软化：2 小时笔试 → 对话式快问快答 → （2025 部分岗位）并入 ML/AI 轮。备考含义：数学不再单独设轮，但会揉进 ML fundamentals 轮里问直觉与推导。

来源: &lt;[来源链接](https://www.teamblind.com/post/deepmind-re-interviews-z8txzan3&gt;)

### Research Scientist 2025 实报 loop：ML 面 + coding(1M+1H) + paper presentation + senior scientist chat
*hard · 频率: multiple reports (2025) · 2025-05*

Glassdoor RS 页 2025-05 报告（原页 403，经搜索摘要还原）：4 轮——1) ML Interview；2) Coding interview（LC 风格，1 道 medium + 1 道 hard）；3) Paper presentation（自选一篇论文做 ~1 小时展示）；4) 与 senior scientist 对话。全程 1.5-2 个月。另一条 RS 报告：总计 7-9 轮（视候选人而定），每轮 1-3 名 scientist，考 leetcode 式题、AI fundamentals、Transformers、Finetuning、以及 Gemini/DeepSeek 等大模型的训练方法。RS 整体难度评分 3.2/5，平均 45-49 天，54% 正面体验。

**解法**: 对候选人（post-training 背景）：ML 面重点准备“从 pretraining 到 SFT 到 RLHF/RLAIF 的完整训练流程”并能对比 Gemini/DeepSeek(-R1/V3) 的技术路线（MoE、MLA、GRPO、distillation）。

来源: &lt;[来源链接](https://www.glassdoor.com/Interview/Google-DeepMind-Research-Scientist-Interview-Questions-EI_IE1596815.0,15_KO16,34.htm&gt;)

### techinterview.org 2026：Research Scientist track 五类轮次拆解
*hard · 频率: 聚合指南 · 2026*

1) Paper Discussion 60min：讲自己近期论文，面试官“会狠戳假设、弱点与扩展”，跨领域可能有多场；2) Research Problem Framing 60min：开放问题的实验设计、指标选取、理论分析提案；3) ML Coding 60min：实现自定义 loss、attention 机制、sampling例程或训练循环，几乎总是 unaided（禁 AI）；4) Math & Theory 60min：概率/线代/优化，覆盖 gradient flow、Bayesian inference、收敛性证明、信息论；5) Behavioral 45min：使命认同、科研协作、过往分歧。整体时间线 6-10 周，研究岗 8-12 周。

**解法**: ML coding 备考：numpy/torch 手写 MHA（含 mask、shape 管理）、top-p/top-k sampling、完整 training loop（zero_grad/backward/step/eval）。

来源: &lt;[来源链接](https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/&gt;)

### RE 4 轮结构 + 各轮内容细节（Blind 2024-08，Snap 员工亲历）
*medium · 频率: single detailed report（与其他来源互洽） · 2024-08*

Amazon 候选人确认 RE loop：4 轮 = 2 coding + 1 ML system design + 1 ML fundamentals。Snap 员工（亲历者）细节：ML fundamentals 轮考“经典 ML（SVM、naive bayes、回归、树）+ 现代 ML（卷积、transformers、优化算法等）的基础问题”，数学很少；coding 轮一场是“typical leetcode (medium-hard)”，另一场考“software fundamentals：class design、multithreading、memory fundamentals 等”；并提醒“Don't sleep on the final hiring manager interview”。

**解法**: 第二场 coding 按 OOD+并发准备：设计类（LRU/限流器/线程安全队列）、GIL、进程 vs 线程、内存模型/引用计数。

来源: &lt;[来源链接](https://www.teamblind.com/post/deepmind-research-engineer-interview-help-keaohhu8&gt;)

### RE loop = coding + math + ML 三类技术面（Blind 2023-11，亲历者）
*unknown · 频率: single report · 2023-11*

3 篇论文+1.5 YOE 候选人（Amazon/GS/AllenAI 实习）：recruiter 主动接触；第二阶段包含“a coding interview, math interview and ML interview”三场；自评“75% okay”；全程未被告知级别（L3 vs L4），佐证 GDM 定级不透明。此帖为此前 0J58GiRf 短链无法打开的原帖，已用 slug URL 恢复。

来源: &lt;[来源链接](https://www.teamblind.com/post/research-engineer-interview-at-deepmind-0j58girf&gt;)

### Gordic Aleksa：DeepMind RE 全流程亲历 + 备考资源清单（Medium 长文）
*hard · 频率: 经典一手长文（社区广泛引用） · 2021-10*

2021 年被引荐入 GDM 的完整记录。流程：recruiter chat（判定 Applied vs Core）→ “the quiz”= 2 场 back-to-back 面试考 maths/stats/CS/ML 基础 → 1 场经典 SWE coding → Team Lead 面 → Senior Team Lead 面 → People & Culture 面。备考资源（quiz）：算法书 ~340 页（线性/非线性数据结构、排序、查找）、Mathematics for ML book（数学+经典 ML）、统计用 jbstatistics + StatQuest + Cambridge IB Statistics sheets 1-2；coding 用 CTCI 前 8 章。行为面真题：What do you like about DeepMind? / Why DeepMind and not some other company? / Tell me something about your favorite project；他还专门研读 AGI 相关论文以应对使命类问题。结局：挂在第 6 场 Senior Team Lead（反馈：显得对 research 比 engineering 更有热情，而岗位是 RE）→ 作为 technically strong 候选人被转到 Incubation/Applied 组重面，4 个 YES 拿 offer。教训：研究每位面试官的论文；RE 岗要强调工程热情。

来源: &lt;[来源链接](https://gordicaleksa.medium.com/how-i-got-a-job-at-deepmind-as-a-research-engineer-without-a-machine-learning-degree-1a45f2a781de&gt;)

### 官方文档《Interviewing at Google DeepMind》PDF
*unknown · 频率: 官方文档 · unknown*

官方 6 页候选人指引（storage.googleapis.com/deepmind-media 托管）：面试通过 careers portal 排期；轮次含技术评估+文化契合；备考建议：研读 deepmind.google、Gemini 等产品、目标团队项目；面试日测试设备、准备无干扰环境、box breathing 呼吸法减压；技术环节 think aloud、用数据支撑成就；推荐 Google Interview Warmup 工具、DeepMind podcast/blog。无具体题目，但可作为官方流程与期望的权威出处。已下载至 /tmp/gdm_official.pdf。

来源: &lt;[来源链接](https://storage.googleapis.com/deepmind-media/DeepMind.com/Assets/Docs/interviewing-at-google-deepmind.pdf&gt;)

### Data Scientist（Gemini/Quant Engineering）岗面试情报（Blind 2025-12 + 4dayweek）
*medium · 频率: 1 条 Blind 报告 + 1 份聚合指南 · 2025-12*

Blind 2025-12-31：GDM Data Scientist (Gemini) 岗（产品向，内部或称 Quant Engineering），TC &#36;250K，recruiter 提供信息极少；候选人推测考察：统计（A/B testing、因果推断）、ML（线性回归、随机森林）、coding（SQL+Python）、进阶 AI（agents、LLMs、多模态，可能以 case study 形式）；Google 员工评论称与 DSR（前 Quantitative Analyst）岗结构类似。4dayweek.io：GDM DS 流程 4-6 周 5 阶段（recruiter → 2+ 轮 coding 45-90min → 2+ 轮 ML 面 45-90min → HM 面 60-90min → culture fit 60-90min），难度 3.2/5；样题 15 条：特征选择方法、超参调优、推荐系统构建步骤、模型评估、L1 vs L2、梯度下降及变体、类别不平衡、时间序列分析步骤、缺失值处理、CNN 原理、bias-variance trade-off 等。

来源: &lt;[来源链接](https://www.teamblind.com/post/interview-tips-for-google-deepmind-data-scientist-x0xpjsi2&gt;)

### Glassdoor RE 页聚合数据与其余零散真题（distributed system / NN from scratch / research paper）
*hard · 频率: 聚合（多条 review） · 2024-2026*

Glassdoor（原页 403，搜索摘要还原）：RE 面试整体：先讲自己的 research papers，然后 coding + deep learning 理论技术问题；DSA 为 medium/hard LC 级，虚拟面试。零散真题：Implement a distributed system to process large-scale data efficiently；Design and implement a neural network from scratch in Python；Describe a research paper you implemented；ML fundamentals 覆盖 loss functions、classification vs regression、降维、regularization、CNN、RL、模型训练。RE 难度 3.3-3.4/5，平均 46 天，整体 66.3% 正面 / 难度 3.23（255 题 226 条 review，login 墙内）。另 QTN_8056849：“一上来就直接问 LC 式 coding 题”。

**解法**: NN from scratch：numpy 实现 2 层 MLP——forward、BCE/softmax-CE loss、手推 backward、SGD 循环，20 分钟内写完的版本要提前练熟。

来源: &lt;[来源链接](https://www.glassdoor.com/Interview/Google-DeepMind-Research-Engineer-Interview-Questions-EI_IE1596815.0,15_KO16,33.htm&gt;)

### Blind 零散 2025-2026 SWE/移动岗情报汇总（低信息量帖）
*unknown · 频率: 4 条低信息量报告 · 2025-10 ~ 2026-03*

1) SWE（Bloomberg 候选人，2025-10，notaegsj）：唯一实质评论“yeah, leetcode medium”。2) Mobile Engineer（Meta 候选人，2026-03，0wz2srt8）：Meta 员工评论“The bar is higher than the bar at Meta. Grind hard algorithms and mobile system design”。3) 2026-01 mj3zcuiy：确认 DeepMind 面试流程与 Google 分开。4) 2026-02 Waymo/DM loop（5mcv3okv）：ML infra 候选人称 DM 可走普通 Google 轮+后置 team match（无人证实）。这些帖无具体题目，但反映 2025-2026 SWE 侧 bar 与流程认知。

来源: &lt;[来源链接](https://www.teamblind.com/post/deepmind-swe-interview-experience-0wz2srt8&gt;)

### DeepMind Research Engineer 全流程挂经 (RE, PhD, 2025-09)
*hard · 频率: single report (2025 唯一确认的 RE 全流程挂经帖) · 2025-09*

岗位: Google DeepMind Research Engineer (RE). 楼主背景: 'NG很一般的PhD + 没啥强工业经验'（NG=new grad/应届），走完全流程后被拒（'铁挂经验'）。可确认的流程/轮次: (1) HR电面 —— 聊签证情况 / 毕业情况 / 对 DeepMind 的看法等 general 问题; (2) ML 电面/讨论 —— 英文摘要标注为 'ML discussion'（正文在188积分墙后，具体题未取到）; (3) Coding 电面/轮次 —— 楼主给出的经验教训: 'corner/edge cases 要能够做到对答如流; Coding 至少要 3-4 个月狂刷, 楼主只用了一周高强度来刷, 之前面试别家太顺利以至于掉以轻心, 只刷了些高频题' —— 暗示挂在 coding 准备不足。这是当前唯一确认的 2025 年 GDM RE 全流程一手挂经帖。正文核心内容被 1point3acres 188 积分隐藏，以上为可见摘要 (Startpage/英文翻译摘要旁路获取)。

**解法**: 复盘教训(楼主原话)：DeepMind RE 的 coding 门槛不低，需 3-4 个月系统刷题而非临时抱佛脚高频题；ML 轮要对基础八股/corner case 对答如流。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1147017-1-1.html&gt;)

### DeepMind ML 全流程面筋 + Offer (2025-09 面试, 时间线明确)
*unknown · 频率: single report · 2025-09*

岗位: DeepMind Machine Learning 全职 (英文翻译摘要: 'DeepMind machine learning interview process ... offer status for a full-time role'). 楼主吐槽 '许久没在地里看到 GDM 的 dp 了' 且 '按着地里五六年前的面筋准备的一点都没用上'。明确时间线: 9/15 HR call (介绍面试流程/介绍公司/各种介绍) → 9/23 SD (system design 轮) → 9/24 Coding (页面显示 'Coding non-...' 疑为 non-standard/non-leetcode，正文被 188 积分墙截断)。英文摘要提到内容覆盖 HR calls / coding / project discussions / offer。这是 2025 年 GDM 少见的带 offer 结果的全流程帖。具体 SD 与 coding 题干在积分墙后未取到。

**解法**: 推断(基于同期 GDM ML 帖 1141654/1141656/1141657 组合): SD 轮很可能是 ML system/ML design 类而非通用分布式系统; coding 轮为 non-standard leetcode（如实现 generator / 概率分布类）。建议按 2025 新帖而非 5-6 年前老面筋准备。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1155040-1-1.html&gt;)

### GDM RS Intern 技术电面结构 (research 也会八股, 2025-10)
*medium · 频率: single report · 2025-10*

岗位: Google DeepMind RS intern (gdm RS intern)。楼主提醒: '给其他面 research 家/组的 PhD 提个醒——说是聊 research, 有时候还是会八股'。电面时间分配被规划为: 25 分钟八股 (fundamentals) + 5 分钟讲我的 research + 20 分钟 AI system design 八股 (详细问)。英文摘要: 'technical phone interview including research discussion and AI system design questions'。这颠覆了 'RS intern 只聊 research' 的预期。

**解法**: 推断: '八股' 指 ML 基础快问快答 (loss/optimizer/正则/attention/transformer 等); 'AI system design 八股' 指 LLM/训练系统设计的结构化提问。备考不能只准备 research pitch，要把 ML 基础和 AI system design 当成主要考点。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1152313-1-1.html&gt;)

### GDM Student Researcher (SR) 项目/流程解密 (2025-11)
*unknown · 频率: single report · 2025-11*

岗位: Google DeepMind Student Researcher (俗称 gdm SR)。信息性帖子(非题目): 对 early PhD '还是很香的'; 现在也开放本科和硕士生岗位; 本质上是 '临时科研 agent', 和暑期实习不一样——一般没有固定实习期结构。英文摘要: 'Google GDM Student Researcher internship details, application tips, and interview insights for early PhD and other candidates in ML'。适合了解 SR 与正式 intern/RS 的区别及申请路径。正文细节在积分墙后。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1153821-1-1.html&gt;)

### DeepMind London Research Scientist 面筋 (2024-01)
*unknown · 频率: single report · 2024-01*

岗位: DeepMind London Research Scientist (RS)。楼主 2023 下半年网申 DeepMind 伦敦多个岗位, 约不到一个月获面试(自评因背景匹配)。英文摘要: 'firsthand account of DeepMind London Research Scientist interview rounds and preparation materials for ML positions'。这是 2024 年初的 RS 全流程帖(轮次结构与备考材料), 正文细节在积分墙后。可作为 RS 岗流程基线参考。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1041792-1-1.html&gt;)

### DeepMind London RE 两大轮流程 (2022, 历史基线)
*hard · 频率: 历史帖 (2022), 与其他老 RE 帖 878129/837817/825115 互为佐证 · 2022-08*

岗位: DeepMind London Research Engineer (RE)。楼主(recruiter 联系): 'RE 是两大轮面试。第一大轮是三个一个小时的面试, 分别是 math, ML, cs+coding'(第二大轮细节被截断)。指出 RE 与 RS 流程可能不同。这是较早(2022)但结构清晰的 RE 流程基线: 第一大轮 = 3×1hr (数学 / 机器学习 / CS+coding)。注意 2025 帖楼主反馈老面筋已不完全适用, 仅作对照。

**解法**: 对照 2025: math+ML+coding 的三合一大轮结构可能仍在, 但 2025 RE 挂经楼主强调 coding 难度上升、需长期刷题, 说明标准比 2022 更高。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-918169-1-1.html&gt;)

### DeepMind ML Research Engineer 终轮 (三轮结构, 2022, 历史基线)
*hard · 频率: 历史帖 (2022) · 2022-01*

岗位: DeepMind ML Research Engineer。楼主: '正式面试有三轮: 一轮 coding, 一轮 ML, 第三轮 Hiring manager + BQ'。前两轮(coding/ML)之前另发过面经; 第三轮时间 12/2、12/3。可确认 RE 三轮结构: Coding → ML → HM+BQ。2022 历史帖, 与 2025 帖对照可见流程主干延续(coding/ML/HM)。

**解法**: 备考三轮: coding(见需长期刷题的 2025 反馈), ML(基础八股+研究讨论), HM+BQ(动机/项目/协作/最自豪项目, 见 1141654)。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-837817-1-1.html&gt;)

### DeepMind Research Engineer/Scientist 入口难度（Reddit 补充数据点）：简历关极难、quant 向岗位考统计概率而非 leetcode
*unknown · 频率: 2 threads · 2026-03*

r/cscareerquestions + r/MachineLearning 双发帖（2026-03）：新毕业生（数学/物理，有 string theory 引用论文）问 DeepMind RE 多难进。关键评论：'即使 top5 PhD 毕业、无 referral，~10 人无一通过简历筛到 HM'；infra 岗比 research 岗好进；发帖人自己的 quant-research 面试经验是'没有 leetcode，主要是 stats 和 probability'；Anthropic Fellow OA 后即挂。r/csMajors AI research intern 帖（2026-05）补充：顶级 lab research intern 面'不考 leetcode，考 conceptual ML + 简历项目深挖'。（GDM 主体面经已由前次 gdm:english 爬取覆盖，此为增量。）

来源: &lt;[来源链接](https://www.reddit.com/r/cscareerquestions/comments/1ry1h4c/how_hard_is_it_to_get_research_engineer_role_at/&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/gdm.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/gdm.md)。作者整理资料；许可和第三方来源范围见阅读指南。
