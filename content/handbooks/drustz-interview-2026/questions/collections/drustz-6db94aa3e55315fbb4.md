---
id: drustz-6db94aa3e55315fbb4
section: collections
order: 12
level: A
title: Anthropic 题库（爬取全量） · Coding 题
quick: 作者文档章节 · Anthropic 题库（爬取全量） · Coding 题
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md
    type: primary
---
## Coding 题

### Coding Q1：Concurrent Web Crawler（题库最高频经典题，完整题面）
*medium · 频率: very high (High 标注, 16+ 讨论) · 2026-05*

55 min。实现 crawl(startUrl, htmlParser) -> list[str]：给 htmlParser.getUrls(url) helper（LeetCode 1242 风格），BFS 抓取同 hostname 的所有 URL 并去重，在 CodeSignal 里跑通。Follow-up 链：(1) 用 ThreadPoolExecutor 并发化——线程安全的 visited set + work queue，或 asyncio 版本；(2) 论证 threads vs processes vs asyncio 的选择（IO-bound）；(3) 口头分布式扩展：多机 sharding、跨机去重（Redis/中心队列）、per-host 限流、故障恢复；(4) asyncio.gather vs as_completed vs semaphore 限流池的语义区别。注意：2025 年中起环境从 Replit 换成 CodeSignal，第一次 run 常要修 import；先澄清 URL fragment/规范化范围；不要过度设计。Last asked 2026-05-03，roles: SWE/MLE/Infra。

**解法**: 单线程 BFS 打底 → ThreadPoolExecutor + lock 保护 visited + queue.Queue，或 asyncio + Semaphore；hostname 用 urllib.parse 提取；重点是把每个 follow-up 讲透而非代码量。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-web-crawler&gt;)

### OA（CodeSignal，90 min，4 levels）：题目家族全景 + 2026 新变种
*medium · 频率: very high (10+ reports) · 2026-05*

SWE/MLE/Fellowship 通用入口 OA：90 分钟 4 个 level 递进（同一系统逐级加功能），满分 1000，有人 800/1000 过线且 2 小时后 recruiter 主动联系。题目家族（多帖汇总）：(1) Banking System（交易系统：开户/存取/转账/调度）；(2) In-Memory Database（简化内存数据库：set/get/delete/scan+TTL+backup/restore）；(3) Cloud Storage System（文件→元信息映射，纯内存，ADD/COPY/GET/FIND+用户容量+压缩备份，Dropbox 风格）；(4) Student Course Registration（存储设计、重复处理、学分约束，interview thread 1059593）；(5) Task Management System（CRUD+优先级排序+用户配额+历史查询）；(6) 2026 新变种：Recipe Manager（两个独立报告：一人提前 40 分钟满分）。bbs 帖：1075137 'OA完整4问'、1049492、1088828、1094617、1134890、1042058、1078644。

**解法**: CodeSignal Industry Coding Framework 套路：用 dict-of-dataclass 建模，先读完 4 个 level 再设计，Level 3/4 常加 TTL/时间戳、备份恢复、按字段排序查询；目标 90 分钟内做完 4 级，练 2-3 套模拟即可迁移到任何变种。aonecode 有 Cloud Storage 4-level 结构：[来源链接](https://aonecode.com/iq/docs/antropic/online-assessment/cloud-storage-system)

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1075137-1-1.html&gt;)

### Anthropic · Concurrent Web Crawler（并发爬虫，companyFreq Anthropic=10）
*medium · 频率: very high — Anthropic 频率标注 10/10（phone screen 常见 coding track 之一） · 2025-12 首发，最近报告 2026-03-24*

题干（正文锁定，据 insights）：实现多线程爬虫，从给定起始 URL 探索页面；只保留与起始页 hostname 完全相同的链接；所有 URL 去除 fragment(#) 后再去重和比较 hostname。考点：CONCURRENCY + GRAPH。Follow-up：如何实现 crawl delay / 限流以免压垮目标服务器？如何在并发下支持 BFS vs DFS 优先级？如何架构成跨多 worker 节点而非单进程？

**解法**: 站内提示：多线程安全读写 visited 集合避免重复/死锁；用 ExecutorService 异步派发任务 + 线程安全 Set + Phaser 或原子计数器判定所有爬取完成。（我的推断）这正是 Anthropic blog 强调的 concurrency/parallelism 门槛题——务必熟练 Python threading/ThreadPoolExecutor 或对应并发原语。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/692f5158cd79766b0b310122/practice&gt;)

### Anthropic · Find Duplicate Files（LeetCode 609 变体，二进制内容去重，companyFreq Anthropic=10）
*hard · 频率: very high — Anthropic 频率标注 10/10（Screening+Onsite） · 2025-12 首发，最近报告 2026-06-29*

题干（LeetCode 609 变体）：在模拟文件系统（根 '/'）中找二进制内容完全相同的重复文件组。两文件重复当且仅当完整二进制内容完全一致（文件名/路径无关）。文件内容可能很大，只能作为二进制流访问，无直接字符串内容访问。需设计能在大量文件/目录中高效找重复的方法。考点：RECURSION + 哈希。Follow-up：如何扩展到分布式文件系统？如何减少哈希碰撞的误报？百万文件时如何降内存？能否检测部分相似/修改过的文件？

**解法**: 站内提示：先递归遍历目录收集所有候选路径；用 file size 等元数据快速排除不可能重复的；对通过 size 过滤的文件读一次二进制流算稳定 hash（如 SHA）分组。建议先刷 LeetCode 609。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6934db5e5f306485cc5f08b9/practice&gt;)

### Anthropic · Find Cluster Mode and Median（分布式求众数/中位数，companyFreq Anthropic=10）
*hard · 频率: very high — Anthropic 频率标注 10/10（Screening+Onsite） · 2025-12 首发，最近报告 2026-01-17*

题干：大型分析公司把海量整数数据集分布到 k 个 worker（0..k-1），每个 worker 只能访问自己那份未排序、均匀分区的数据切片。设计分布式算法计算整个数据集的 mode（出现最频繁的整数），同时确保没有 worker 拿到全部原始数据且最小化网络使用。平局（多个整数并列最高频）时返回最小的那个。考点：DESIGN / 分布式聚合。Follow-up：如何优雅处理 worker 崩溃/网络超时？某些数字远比其他频繁时如何缓解 hash skew？能否扩展到 top-K 而非仅 mode？异步消息延迟如何影响同步与终止逻辑？

**解法**: 站内提示：先本地按频率压缩（传 (value,count) 元组而非原始数据）；避免中央收集器——用只依赖 value 的确定性公式把每个唯一 value 路由到恰好一个 worker；路由后各 worker 聚合分到的计数、找本地 leader，再做最终 reduction 定全局赢家。（我的推断）本质是 MapReduce/shuffle-by-key 的手写版。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6935ba711553144e303f6769/practice&gt;)

### Anthropic · CRUD/内存数据库风格 OA 题组（Banking / In-memory DB w/ Backup / Cloud Storage / Worker Mgmt / Note-Taking / Task Assignment / Recipe Mgmt）
*medium · 频率: very high — 多为 CodeSignal 4-level 演进式 OA；Anthropic 频率：Banking 10、Cloud Storage 7、In-memory DB 9、Worker Mgmt 6、Note-Taking 7、Task Assignment 7、Recipe 7（这些题也高频出现在 Coinbase/HubSpot/Ramp） · 2025-07 至 2026-05*

Anthropic 的 OA/coding 常见一类'渐进式设计题'（practice URL 形如 .../anthropic/coding-questions/{id}/practice）：(1) Design Banking System [Medium, id 687c23f9aa2b26b0b64b39d4]：createAccount/deposit/transfer，每操作带递增时间戳；扩展常含 top-K 转账账户、定时支付/cashback、账户合并（这是著名的 CodeSignal 4-level 银行题）。(2) Design In-memory Database with Backup [Hard, id 689505de3a1d9e6d6042d519]：setData/getData/deleteData 字段级 + scan/backup/restore。(3) Cloud Storage System [Hard, id 689cf808aee746eb1c84ba37]：addFile/copyFile/getFilesize + 前缀查询/用户容量/压缩（4-level）。(4) Design Worker Management System [Medium, id 68a4bbdfc11d63d6052ea306]：worker 进出办公室时间戳、累计工时。(5) Design Note-Taking System 'SecondBrainSystem' [Medium, id 69b351ffa4e93c007df404fd]：CRUD + 唯一自增 ID + 大小写不敏感标题。(6) Design a Task Assignment System 'TaskManager' [Hard, id 69efc8e696981f58ae1f6d73]：addTask 返回 'taskId&lt;n&gt;'、updateTask、按 name/priority 检索。(7) Design Recipe Management System [Medium, id 69f2664c42791c82ab992693]：CRUD + 唯一大小写不敏感名 + 不复用 ID。

**解法**: 站内提示统一：用两层/多个 hash map（ID→实体、规范化名→ID 做唯一性）；操作前先做全部校验再提交状态变更；ID 计数器只增不减。（我的推断）建议按 CodeSignal 4-level 模式练：level1 基础 CRUD→level2 加过滤/排序→level3 加时间/TTL→level4 加合并/回滚，这是这批题的通用演进。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions&gt;)

### CodeSignal OA 题型一：In-memory Database（4 levels，90 分钟）
*medium · 频率: very high（Blind/Glassdoor/博客 10+ 独立报告） · 2026-04*

Anthropic 标志性 OA（也用于 live coding 轮），90 分钟 4 个递进 level，逐级解锁（当前 level 测试全过才能看下一级），黑盒测试判分。具体拆解：Level 1：基本操作 SET/GET/DELETE；Level 2：加 SCAN、SCAN_BY_PREFIX（要求排序和严格输出格式）；Level 3：加 TTL——SET_AT/GET_AT/DELETE_AT/SCAN_AT（带时间戳的状态管理）；Level 4：backup/restore（数据库快照与恢复）。常见坑：TTL 边界条件应为 ts < start_time + ttl 而不是 <=。Blind 汇总：满分 600（也有 1000 分版本报告），基本要接近满分才能进下一轮，但满分也不保证通过（还看简历匹配）；大多数人做不完 4 级。

**解法**: 速度题不是算法题：暴力解完全可以（O(n) scan 都行），别上花哨数据结构。用一个 dict 存 (value, expire_ts)，把 GET/SCAN 的过期判断抽成公共函数，Level 4 快照直接 deepcopy + 记录时刻。写法要模块化，新 level 尽量是增量改动；每写完一小块就跑测试，别攒到最后调试。（来源：Blind 多帖 + Zharkov 博客一致建议）

来源: &lt;[来源链接](https://medium.com/@programhelp/anthropic-interview-questions-2026-oa-technical-interview-breakdown-08d68034a47d&gt;)

### CodeSignal OA 题型二：Banking System（4 levels，90 分钟）
*medium · 频率: very high（5+ 独立报告，interviewing.io 称跨 Glassdoor/Blind 一致确认） · 2026-04*

与 in-memory DB 二选一出现的另一套 OA 题（多个渠道确认为 Anthropic 最高频编码题，OA 和 live coding 轮都出现过）。Level 1：开户与存款；Level 2：转账与支付；Level 3：账户合并（合并余额、交易历史、支付记录、账户状态）；Level 4：cashback 逻辑（需要回头重构 Level 2 的支付实现）。interviewing.io 的表述为 "Implement a bank with multiple transaction types"。这类题在 CodeSignal 官方叫 Industrial Coding Framework 风格。

**解法**: 同 in-memory DB：模块化 + 增量应对需求变化是评分核心。把'交易'建模为统一记录（type/amount/timestamp/counterparty），合并账户=合并记录列表+重算派生状态；cashback 若 Level 2 写死了支付流程就会很痛，提前把支付拆成 create-payment / settle 两步。（我的推断+多来源提示）

来源: &lt;[来源链接](https://medium.com/@programhelp/anthropic-interview-questions-2026-oa-technical-interview-breakdown-08d68034a47d&gt;)

### Blind 聚合：CodeSignal OA 实战情报
*medium · 频率: very high（Blind 10+ 帖） · 2025*

Blind 多帖（登录墙，内容来自搜索聚合摘要）：邮件说明 OA 为 4 parts、90 分钟、涉及一个 toy simulator；题目二选一：banking app 或 in-memory database；定位是 speed test——"coding is not complicated, but you have to code VERY FAST"；CodeSignal 官方邮件即承认大多数人做不完 4 级。技巧共识：不需要算法优化、暴力省时间；逐块写代码逐块验证，比全部写完再 debug 好；满分 600（另有 1000 分制报告）；速度比优雅重要；perfect score 也可能因简历不匹配被拒。相关帖：Anthropic codesignal experience (eh3Kq1mc)、Anthropic CodeSignal: what to expect (Gc7vZ81T)、Anthropic OA (ue2vvwWk)、Anthropic codesignal score (Dv1aFZY3)、Anthropic Interview Megathread (6estt896)。

**解法**: 练法：CodeSignal 的 Industrial Coding Framework 练习题 + 限时模拟；用 Python dataclass + dict 起手模板；先通读所有可见需求再动手。

来源: &lt;[来源链接](https://www.teamblind.com/post/Anthropic-codesignal-experience-eh3Kq1mc&gt;)

### Anthropic CodeSignal OA：90分钟4段渐进式 industry coding（银行系统/内存数据库/图书馆系统等变体）
*medium · 频率: very high (15+ reports across 10 threads, 2024-09 to 2026-06) · 2026-01*

所有 SWE/RE/Fellows 轨都先过这个无人监考 CodeSignal OA。格式：一道渐进式 CRUD 类系统构建题，4个 level（250/500/750/1000 分，部分显示折算为 600 满分），必须先全过当前 level 的测例才解锁下一 level，后期 level 要求回头重构前面的代码。已知题目变体：银行系统（开户/转账→定时交易→计息）、内存数据库（CRUD + TTL + 配额 + 辅助函数）、图书馆系统（add book/borrow/return，第4段有性能测试，超时算失败）、progressive filesystem。评分极严：多人报告 570/600、850/1000 被拒，社区共识'基本要满分'（Fellows 项目官方口径 480/600 以上才推进）；也有人 750/1000 被拒后重考通过（可申请 retake）。无自动补全/intellisense，切出浏览器 tab 可能取消资格，禁 AI。时间压力是最大难点：90 分钟要全速写代码，брute force 够用、别追求最优解；先设计可扩展的数据结构避免后期重构。2026 年起部分轨（Fellows/MATS）换成自研 6-part 版本，'难一个数量级'，题面像 essay 而非 leetcode 式题干。

**解法**: 练 CodeSignal Industry Coding Assessment 原题集（banking system 等）；用 Python（写得快）；第一层就把实体抽象成 class + dict 索引，留好扩展点；每层限时分配（6/20/30/30分钟）；测试已给、TDD 风格跑测例。来源+我的推断：这类题社区题库在 CodeSignal 官方 ICA 白皮书和 hack2hire/prachub 有仿真题。

来源: &lt;[来源链接](https://www.reddit.com/r/leetcode/comments/1qx0hyj/anthropic_technical_interview_55_min_codesignal/&gt;)

### Anthropic 店面/onsite 高频题：web crawler（先串行后并发）+ 并发知识清单
*medium · 频率: very high (6+ independent reports) · 2026-05*

多个独立来源确认：'implement a web crawler and return all unique urls' 是 Anthropic 店面的招牌并发题——先写串行逻辑，再加 concurrency/parallelization。Senior SWE 店面邀请明确写'需要会 concurrency'。考察点（辅导教练总结+考生确认）：locks/mutexes、线程安全数据结构、producer-consumer 模式、死锁、spin lock vs sleep lock、进程 vs 线程、async/await、race conditions。E5 大厂工程师因没准备并发直接挂掉店面（r/leetcode E5/6 面经帖）。Applied AI/SWE 的 live 轮也可能是'debug 或扩展已有代码'而非从零写。

**解法**: Python 版标准解：ThreadPoolExecutor + queue.Queue + visited set 加 lock（或用 asyncio + aiohttp + asyncio.Queue + set，配 semaphore 限并发）；讲清楚为什么 visited 检查和插入要原子。准备 BFS 深度限制、同域名过滤、失败重试 follow-up。

来源: &lt;[来源链接](https://www.reddit.com/r/leetcode/comments/1t40v4c/anthropic_concurrency_questions/&gt;)

### Coding Q6：Tokenizer（2026 店面/onsite 高频）
*medium · 频率: high (5+ reports, 2026 Q1-Q2) · 2026-04*

实现 tokenizer，核心是贪心最长匹配（longest match）分词：给 vocab，对输入串反复取最长可匹配 token。考察点：bug finding（给带 bug 的实现让你修）、longest match 正确性、实现细节。一位候选人先写朴素 for 循环做最长匹配，再升级 trie 结构。相关帖：interview thread 1169657 'Q6 Tokenizer Technical Phone Screen'（bug finding + longest match + implementation）、1156951 'SWE Onsite Q6 Coding Question Details'、1160525 'What is the Coding Q6'、1143701 'Tech Phone Screen Prompts for Q2 and Q6 (MLE)'。

**解法**: 我的推断：先写 dict+按长度倒序尝试的 O(n·L) 版本保证正确（含无法匹配时的 fallback/unk 处理），follow-up 优化用 trie 做单遍最长匹配；准备讨论 BPE 与贪心最长匹配的区别、流式输入、vocabulary更新。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/thread/1169657&gt;)

### File Deduplication（找重复文件）——店面/onsite 常青题，完整题面
*medium · 频率: high (5+ reports, 2024-2026 持续出现) · 2026-01*

遍历目录树，按字节内容（非元数据）找出完全相同的文件，输出 size≥2 的重复组，每组一行空格分隔路径。例：/a/1.txt='hello', /b/2.txt='hello', /c/3.txt='world' → 输出 /a/1.txt /b/2.txt。要求处理大文件：不能一次读进内存。Follow-up：IO-bound（磁盘读是瓶颈）怎么优化 vs CPU-bound（hash/比较是瓶颈）怎么优化。多个报告：店面出现（interview thread 1141385），有 3 个 part 的 onsite 版本（bbs thread 1097726），有人被要求自己写 filesystem 遍历方法；一人因 runtime 执行问题挂掉。

**解法**: 三级分组：size → 首块 hash → 全文 hash/逐字节比较；分块读（如 1MB chunk）；IO-bound：并行读多盘/减少读放大（size 预筛掉大部分）；CPU-bound：更快 hash（xxhash）、多进程、只 hash sampling块后精确比对。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/42afe615-f6b2-494c-807f-37c309841f8b&gt;)

### Concurrent Web Crawler (LC 1242 variant with URL sanitization)
*medium · 频率: Anthropic freq 10/10 (their highest); last reported 2026-03-24 · 2025-12 (published)*

UNLOCKED - full statement captured. Stage: phone screen. Variation of LeetCode 1242 Web Crawler Multithreaded. Given startUrl and htmlParser.getUrls(url) (each call has simulated ~10-15ms network latency), return all unique URLs with the EXACT same hostname as startUrl. Twists vs LC1242: must strip URL fragment (everything from '#') BEFORE hostname comparison and dedup ("[来源链接](http://example.com/page#s1") == "[来源链接](http://example.com/page")); hostname = substring between "://" and next '/'; graph may contain cycles; must use concurrency because of per-call latency (<=1000 urls, <=1000 edges, each getUrls <=15ms). 3 worked examples captured. Site follow-ups: rate limiting/crawl delay; BFS vs DFS priority under concurrency; scaling to multiple worker nodes (distributed crawler). Acceptance 56.4%. This matches the widely-reported Anthropic screen 'async web crawler' question.

**解法**: Official editorial (captured): concurrent BFS with ThreadPoolExecutor; thread-safe visited set guarded by a lock, add-before-submit to avoid duplicate scheduling; completion tracking via task counter/phaser; sanitize (strip '#') then compare host then dedup. O(N+E) time, O(N) space. Full reference solutions in Python (threading + lock + task_count), Java, C++, TS captured.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/692f5158cd79766b0b310122&gt;)

### Anthropic · Repair Bootloader Program（指令模拟找首个重复执行，companyFreq Anthropic=8）
*hard · 频率: medium-high — Anthropic 频率标注 8/10 · 2026-06 首发，最近报告 2026-07-09*

题干：bootloader 把程序存为文本指令数组，需找到执行首次开始重复的位置。给定 instructions，每条形如 '&lt;operation&gt; &lt;value&gt;'，operation 为 'plus'/'next'/'jump'：'plus x' 给全局累加器加 x 然后移到下一条；'next x' 累加器不变移到下一条（x 保留在格式中但本题忽略）；'jump x' 累加器不变，跳到当前索引+x 的指令。从索引0开始执行，返回首次重复执行的指令索引，若程序正常终止返回 -1。考点：SIMULATION / 函数图环检测。Follow-up：若指令集含条件跳转如何改？能否在仍高效检测环的同时降低空间复杂度？跳转越界怎么办？此题如何映射到函数图的环检测（Floyd）？

**解法**: 站内提示：记录每个访问过的指令索引；在执行当前指令前检查是否重复；用布尔数组或 hash set 做 O(1) 查找，整体 O(N)。类似 AoC 2020 Day 8。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a373b2b6849fecc81442861/practice&gt;)

### Anthropic · Generate Function Profiling Events（LeetCode 636 变体，栈快照转事件，companyFreq Anthropic=9）
*hard · 频率: high — Anthropic 频率标注 9/10 · 2025-12 首发，最近报告 2026-05-31*

题干（LeetCode 636 Exclusive Time of Functions 变体）：sampling profiler 周期性记录单线程执行状态。每条 samples 形如 '&lt;time&gt;:&lt;stackTrace&gt;'：time 是严格递增整数时间戳；stackTrace 是 '->' 分隔的函数名列表，从最外层到当前执行的最内层（如 'main->worker->parse' 表 main 调 worker 调 parse）；栈可能为空（如 '42:'）。需把周期性栈快照转换成按时间顺序的 start/end 事件。考点：HASH_TABLE + STRING。Follow-up：如何扩展到多并发线程？如何计算每函数 exclusive vs inclusive 时间？样本历史无限增长时如何优化内存？

**解法**: 站内提示：从最外层向内比较相邻两次栈快照找首个不匹配点；不匹配点后消失的帧=已结束，新增的帧=最近开始；把每个栈位置当独立调用帧，忽略不同深度的重名。建议先刷 LeetCode 636。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224/practice&gt;)

### Anthropic 55分钟 live 技术店面（CodeSignal notebook）真题：图像处理管线（Pillow + JSON 配置）
*medium · 频率: high (4+ independent reports) · 2026-06*

多个独立报告的高频店面题（前端/后端/senior 都有人抽到）：给一组图片和一个 JSON 定义的 pipelines 列表，每个 pipeline 含变换序列（转黑白、resize、水平翻转等），实现主函数把每张图按其 pipeline 顺序处理并导出。需要现场选图像库（Python 基本只能 Pillow）、快速读文档、把每种变换映射到库调用。Follow-up：图片变大后的性能优化——判断 I/O-bound vs CPU-bound；I/O: 流式读取/批量文件操作；CPU: 跨图片并行（进程池）、避免重复变换。环境是 Jupyter 式 notebook、无自动补全、可 Google（不能点 AI 摘要）、禁 AI。一人用 Java 被允许但 Pillow 题基本锁 Python。有人因此挂掉，有人过（评论：'每一步都能 google，不难但时间极紧，一个错误选择就完了'）。

**解法**: 提前背熟 Pillow API：Image.open/convert('L')/resize/transpose(Image.FLIP_LEFT_RIGHT)/save；写一个 dict 把操作名映射到函数的 dispatcher；先跑通单图单变换再泛化。

来源: &lt;[来源链接](https://www.reddit.com/r/OfferEngineering/comments/1ub6od5/anthropic_frontend_phone_screen_not_leetcode_but/&gt;)

### Anthropic 店面/onsite 编码真题：Repair Bootloader Program（=Advent of Code 2020 Day 8 变体）
*medium · 频率: high (3 reports Jun-Jul 2026) · 2026-07*

2026 年 6-7 月三个独立报告（店面 + Staff/Sr Staff onsite coding 轮都出过）。题目：给一个指令文件（自造小语言），三种操作——plus（累加器加值）、next（顺序下一行）、jump（相对偏移跳转）。从第一行开始执行直到跑出文件末尾或死循环。要求：检测何时陷入无限循环（重复访问同一行）、找出导致循环的行——bug 是某一行的 jump 和 next 被互换，修复（换回来）使程序正常终止，并返回进入循环前的累加器值/终止时累加器值。onsite 版约 50 分钟做完含 debug。考生评价：理解题意花 10 分钟，实现本身不难；考的是仔细模拟、循环检测、debug、确保修复后程序终止。

**解法**: 即 AoC 2020 Day 8（acc/nop/jmp）：先写解释器 + visited set 检测循环；然后对每个 jump/next 指令试着翻转一次，重跑看是否终止（O( $n^{2}$ ) 足够）；返回对应累加器值。

来源: &lt;[来源链接](https://www.reddit.com/r/Hack2Hire/comments/1umm6xj/anthropic_phone_screen_experience/&gt;)

### Anthropic SDE 编码真题（近3个月高频）：从调用栈快照重建函数 start/end 事件
*medium · 频率: high (2 independent sources, flagged 'recent 3 months') · 2026-07*

完整题面（OfferEngineering 2026-07 收录，另有 InterviewCoderHQ 独立佐证'converting profiler stack snapshots into function start/end events'）：给定周期性调用栈快照列表，每条格式 "&lt;timestamp&gt;:&lt;callPath&gt;"，timestamp 严格递增，callPath 是 'app->load->parse' 形式（外到内），空路径表示无函数运行。对比相邻快照：共同前缀之后新出现的函数产生 start 事件，前一快照中消失的函数产生 end 事件（end 按最内到最外输出）。递归调用视为独立栈帧；最后一个快照后仍活跃的函数不产生 end。实现 List&lt;String&gt; buildEvents(List&lt;String&gt; snapshots)，输出 "start:&lt;time&gt;:&lt;fn&gt;" / "end:&lt;time&gt;:&lt;fn&gt;"。例：["1:app->load","3:app->load->parse","5:app->load","8:app"] → [start:1:app, start:1:load, start:3:parse, end:5:parse, end:8:load]。

**解法**: 每步求前后两栈的最长公共前缀长度 k（注意递归同名帧按位置比较）；prev[k:] 逆序发 end，curr[k:] 顺序发 start。边界：首快照全 start、空路径、连续相同栈不发事件。

来源: &lt;[来源链接](https://www.reddit.com/r/OfferEngineering/comments/1urq3za/anthropic_coding_question_reconstruct_call/&gt;)

### Coding Q2：LRU Cache 及其 VO 变种'可持久化的 Memoization LRU Cache'
*medium · 频率: medium (3+ reports) · 2026-03*

店面 Q2 = LRU cache（interview thread 1152730 'Fulltime SWE Tech Phone Screen Q2 Coding Question'）。VO 出现新变种：'可持久化的 Memoization LRU Cache'（Telegram 镜像帖，SWE onsite）——在 LRU 基础上加 memoization decorator 语义和持久化（save/load）。另有 'Thread-Safe Linked List Task Queue Transformation'（把链表任务队列改造成线程安全）出现在题库。

**解法**: 标准 OrderedDict/双链表+dict 打底；变种考点（我的推断）：decorator 包装函数签名做 key（args 需 hashable/序列化）、eviction 与持久化一致性、线程安全加锁粒度。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/thread/1152730&gt;)

### Fellows/Safety Fellowship OA（2026）：DNS resolver + Python debugging；prompts→GPT servers 哈希映射
*medium · 频率: medium (3 reports, 2026 Q2) · 2026-05*

(1) Anthropic Fellows（ML intern，2026 July cohort）两轮 CodeSignal OA：第一轮 DNS resolver 实现，第二轮 Python debugging（interview thread 1177056，2026-05-16）。(2) Safety Fellowship CodeSignal OA：'mapping prompts to GPT servers using a hash table'——用哈希表把 prompt 路由到服务器（interview thread 1163421，详情在登录墙内）。(3) AI Safety Fellow 5 小时 in-home assessment：给定 codebase，在小模型上做 PyTorch 实验并回答 research questions（interview thread 1165094）。

**解法**: DNS resolver（我的推断）：实现递归/迭代解析+缓存 TTL+CNAME 链；prompts→servers 是 consistent hashing 风格路由题。5h 评估重点是实验设计和写作，不是代码量。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/thread/1177056&gt;)

### Coding Q3：debugging 题（非 LeetCode 风格）
*medium · 频率: medium (3+ reports) · 2026-02*

搜索摘要提及：'Coding Q3, with feedback that it focuses on debugging rather than LeetCode-style problems'——给一段有 bug 的代码/最少 helper code 的文件做 debug（Telegram 镜像也有 'Fresh Onsite Coding: File debugging with minimal helper code' 一条）。Q1/Q3/Q4/Q5 的prompt在 bbs thread 1138904 '人类学电面新prompt' 有分享（正文需登录），thread 1143701 分享了 Q2 和 Q6 的 prompt。收到新prompt求辨认的帖：bbs thread 1125221。

**解法**: debug 类轮的通用打法：先跑通复现→读测试→二分定位→修一个验一个并解释 root cause；Anthropic 喜欢看系统化 debug 过程而非直觉猜。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1138904-1-1.html&gt;)

### Anthropic · Design Durable Function Call Cache（memoization 缓存键设计，companyFreq Anthropic=8, Onsite）
*hard · 频率: medium — Anthropic 频率标注 8/10（较新，Onsite） · 2026-06 首发，最近报告 2026-07-09*

题干：数据管线常用 memoization——包装昂贵函数使相同输入的重复调用返回缓存结果。给定部分实现的 FunctionCallCache 类（已处理缓存查找/插入/命中/未命中/LRU 淘汰），唯一缺失的是 create_cache_key，需为每次函数调用生成确定性、可哈希的键。子问：规范化 kwargs 顺序使等价调用产生相同键；序列化含嵌套结构的输入为可哈希格式。考点：DESIGN。Follow-up：如何处理不可 JSON 序列化的参数（如自定义类实例）？序列化字符串 vs 值元组作缓存键的权衡？如何扩展成基于函数签名或源码变化的缓存？访问缓存时的线程安全考量？

**解法**: 站内提示：kwargs 无关顺序，对 keys 排序得一致视图；对嵌套 dict 递归规范化以深度相等匹配；最终键=函数名 + 规范化 kwargs + args 组合成不可变容器或字符串。对 agentic/工具调用缓存场景很相关。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a2db6215117d1b543565e12/practice&gt;)

### String Tokenization (Trie, longest-match)
*medium · 频率: Anthropic freq 6/10, Google 4/10; last reported 2026-05-26 · 2025-12 (published), seen through 2026-05*

UNLOCKED - full statement captured. Stage: phone screen. Given `text` and `dictionary` of strings "&lt;key&gt;:&lt;id&gt;". Segment text into tokens: (1) Longest Match Priority - at each position pick the longest dictionary key matching there; (2) Greedy Consumption - consume the matched token, continue from next unconsumed char; (3) Literal Preservation - if nothing matches, emit the single char as a literal token; (4) Output the id for matched keys, the char itself otherwise. Constraints: 1<=text.length<=1e9, 0<=dictionary.length<=1e9, tokens unique. Examples: text="applepiepear", dict=["app:10","apple:20","pie:30"] -> ["20","30","p","e","a","r"]; "acdebe",["a:1","b:2","cd:3"]->["1","3","e","2","e"]; "programmingprogrampropro" with pro/program/programming/gram/ming/pr/og -> ["3","2","1","1"]. 8 official test cases captured incl. empty text, empty dict, "thetheatertheme". Site follow-ups: dictionary too large to fit / stored externally; fuzzy or partial matching; space optimization when keys share prefixes. Acceptance rate on site: 36.6%.

**解法**: Official editorial (captured): build a trie of keys storing id at terminal nodes; scan text left to right; from each position walk the trie as far as chars match, remembering the last terminal node passed (longest match); emit its id and jump pointer to bestEnd, else emit literal char and advance 1. O(N*L) time, O(S+N) space. Full Python/Java/C++/TS reference solutions captured (Python in /tmp/h2h_questions_full.json).

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6941b6aeb9d646bec48c68b7&gt;)

### Repair Bootloader Program (2 parts; AoC-2020-Day-8 style)
*hard · 频率: Anthropic freq 8/10; last reported 2026-07-09 (15h before crawl - very active) · 2026-06 (published)*

LOCKED (preview + per-part insights captured). Stages: Onsite + Screening. Instructions array of "&lt;operation&gt; &lt;value&gt;" with ops plus/next/jump: "plus x" adds x to accumulator then next instruction; "next x" no-op then next (x ignored); "jump x" moves to current index + x. Part 1 (q 6a373b356849fecc81442862): simulate from index 0, return the index of the first instruction that is about to execute a second time (first repeat), or -1 if the program terminates normally (falls off the end). Part 2 (q 6a373b366849fecc81442863): exactly one corrupted branch instruction may exist; flip at most one jump<->next so the program terminates; return the final accumulator after the minimal correction. Site follow-ups: conditional jumps; reduce space for cycle detection; out-of-bounds jump offsets; mapping to cycle detection in a functional graph; multiple flips; avoiding the reverse graph via forward simulation.

**解法**: Site hints (captured): Part 1 - visited boolean array/hash set, check repetition BEFORE executing, O(N). Part 2 - model instructions as directed graph; simulate original path and only consider flipping branch instructions on that path; precompute the set of nodes that can reach the terminal state by BFS/DFS on the REVERSE graph from the exit, then a flip is valid iff its new target is in that reach-exit set (O(1) validation, O(N) total). My note: this is essentially Advent of Code 2020 Day 8 (jmp/nop/acc) with renamed ops.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a373b2b6849fecc81442861&gt;)

### Design Durable Function Call Cache (2 parts: cache key + WAL crash recovery)
*hard · 频率: Anthropic freq 8/10; last reported 2026-07-09 (7h before crawl - very active) · 2026-06 (published)*

LOCKED (preview + insights captured). Stage: Onsite. You get a partially implemented Python `FunctionCallCache` class wrapping arbitrary functions with an LRU cache; lookup/insert/evict already written. Part 1 (q 6a2db7bc5117d1b543565e24): implement `create_cache_key` producing a deterministic, hashable key per call - must normalize kwargs order (sorted keys), recursively normalize nested dicts, combine function name + args + normalized kwargs into an immutable/hashable container or serialized string. Part 2 (q 6a2db7be5117d1b543565e25): durability - maintain an append-only log (WAL) of cache operations; on restart replay records sequentially to reconstruct both cached values AND LRU recency ordering; must gracefully skip trailing corrupted/truncated log entries without failing startup. Site follow-ups: non-JSON-serializable args (custom class instances); serialized-string vs tuple keys tradeoff; keying on function source/signature changes; thread safety; multi-process concurrent access; batched writes to cut disk I/O; checkpoint/secondary index to speed recovery; unbounded log growth (compaction).

**解法**: Site hints (captured): Part 1 - sort kwargs keys, recurse into nested dicts, emit tuple/canonical-JSON of (fn_name, args, sorted_kwargs). Part 2 - log individual key-value updates, not whole cache snapshots; during replay, delete-and-reinsert existing keys so LRU order reflects recency correctly; wrap parsing in try/except to skip malformed tail records. This is a very realistic 'engineering-flavored' Anthropic onsite question (matches their durable-cache/memoization take-home family).

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a2db6215117d1b543565e12&gt;)

### Design Recipe Management System (4-level OA, CodeSignal industrial style)
*medium · 频率: Anthropic freq 7/10 (also Coinbase/HubSpot/Ramp); last reported 2026-07-07 · 2026-04 (published)*

LOCKED (preview + all 4 levels' insights captured). Stage: OA (online assessment). RecipeManager class; each recipe: unique name (case-insensitive), ordered ingredients, ordered steps. Level 1 (q ...694): addRecipe(name, ingredients, steps) -> "recipe&lt;n&gt;" sequential from 1, IDs never reused after deletion, "" if name exists case-insensitively; plus get/update/delete CRUD; updateRecipe must allow renaming to same name with different casing. Level 2 (q ...697): searchRecipesByIngredient with case-insensitive WHOLE-string ingredient match excluding deleted recipes; listing sorted by metric (count/name) with NATURAL NUMERIC ordering of recipe IDs (recipe2 < recipe10); tie-break by ID. Level 3 (q ...69a): addUser registration and editRecipe with ownership; enforce name uniqueness while permitting self-renames. Level 4 (q ...69b): immutable version snapshots on every update/edit; getVersionHistory sorted ascending by version; restoreVersion validating name collisions against other active recipes. Site follow-ups: inverted index for ingredient search; lazy vs eager delete; wildcard/partial matches; memory reduction for 10k+ versions; lock-free concurrent edits.

**解法**: Site hints: two hash maps (id->recipe, lowercased-name->id); extract integer suffix for natural ID ordering; deep-copy ingredients/steps per version snapshot (defensive copying); store versions as append-only list per recipe id.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69f2664c42791c82ab992693&gt;)

### Design a Task Assignment System (4-level OA; sweep-line quota check at level 3)
*hard · 频率: Anthropic freq 7/10 (also Coinbase/HubSpot/Ramp) · 2026-04 (published)*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. TaskManager class. Level 1 (q ...d74): addTask(timestamp,name,priority)->"taskId&lt;n&gt;" sequential from 1 (duplicate name+priority allowed); updateTask(timestamp,taskId,name,priority)->bool; getTask retrieval. Level 2 (q ...d75): searchTasks with case-sensitive substring matching, result limiting (empty filter = wildcard, non-positive limit = empty list); listTasksSorted by priority DESC then creation order ASC where creation order = NUMERIC comparison of taskId suffix (taskId1 < taskId10). Level 3 (q ...d76): user management with per-user quota of simultaneous active tasks; assignTask(user, task, [start,finish)) must validate interval overlaps and that the dynamic quota is never exceeded at any point in the window - requires sweep-line over interval boundary events, processing end events before start events at equal timestamps (half-open intervals). Level 4 (q ...d77): completeTask frees the user's quota; getOverdueAssignments = assignments whose finishTime <= query time and never completed; track completedAt to shorten active interval without deleting. Site follow-ups: interval tree/segment tree instead of linear scan; O(1) completeTask; thread safety; sparse/huge timestamps; DB schema for persistence.

**解法**: Site hints: quota check only needs critical moments at interval boundaries, not every time point - clip existing assignments to the new window, emit +1/-1 events, sort with end-before-start tie-break, sweep and track max concurrent count; per-user map keyed by taskId for O(1) completion.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69efc8e696981f58ae1f6d73&gt;)

### Design Note-Taking System / SecondBrainSystem (4-level OA; backlinks, workspaces, versioning+merge)
*medium · 频率: Anthropic freq 7/10 (also Coinbase/HubSpot/Ramp); last reported 2026-05-12 · 2026-03 (published)*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. In-memory SecondBrainSystem with CRUD notes, unique sequential IDs, case-insensitive unique titles, created/modified timestamps, pipe-delimited retrieval format. Level 1 (q ...4fe): CRUD + uniqueness + metadata; counter never decrements after deletes. Level 2 (q ...5de): resolve bidirectional [[title]] wiki-links - parse content line-by-line, a link counts only if the [[...]] stands ALONE on its own line; case-insensitive resolution against current titles; exclude self-references; return sorted results; links are resolved dynamically (renames/deletes change resolution). Level 3 (q ...5e6): workspaces with maximum capacity; notes tracked across workspaces plus a 'default' unassigned state (treat default as routing case, not a physical container); retrieval sorted by creation timestamp then note ID. Level 4 (q ...5f1): getNoteAt(id, timestamp) point-in-time historical state via immutable snapshots; mergeNotes(source,target) appends source content to target, redirects title-based links to target, safely removes source. Site follow-ups: persistence across restarts; hierarchical folders; thread-safety; caching/incremental updates for backlink queries at millions of notes; non-destructive branching/revert.

**解法**: Site hints: two hash maps (id->note, lowercase-title->id); snapshot-per-update list for time-travel queries; for merge link-redirection remap source's lowercase title to target's ID in the central index instead of rewriting note contents.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69b351ffa4e93c007df404fd&gt;)

### Find Cluster Mode and Median (distributed algorithm design-coding, 2 parts)
*hard · 频率: Anthropic freq 10/10; last reported 2026-01-17 · 2025-12 (published)*

LOCKED (preview + insights captured). Stages: Screening + Onsite. Massive integer dataset partitioned across k workers (0..k-1), each worker only sees its own unsorted slice. Part 1 (q ...76a): distributed MODE (most frequent integer, ties -> smallest) such that no worker ever receives all raw data and network usage is minimized. Part 2 (q ...805): distributed MEDIAN under the same constraints, handling odd/even sizes. Site follow-ups: worker crashes/network timeouts; hash skew mitigation for hot values; extend to top-K frequent; async messaging effects on synchronization/termination; complexity vs sort-and-merge; k-th smallest generalization; skewed data distribution.

**解法**: Site hints (captured): Mode - each worker aggregates local (value,count) tuples first; shuffle by deterministic hash partition value->owner worker (no central collector); each owner sums its assigned counts, finds local leader; final reduction picks global winner with smallest-value tie-break. Median - binary search on the VALUE range: each round broadcast candidate, workers reply with counts of elements < and == candidate; combine ranks to steer the search; average two adjacent ranks for even n. This is effectively a mini MapReduce/binary-search-on-answer design question done as code.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6935ba711553144e303f6769&gt;)

### Find Duplicate Files (LC 609 variant: binary streams, chunked hashing, 2 parts)
*hard · 频率: Anthropic freq 10/10; last reported 2026-06-29 (1 week before crawl) · 2025-12 (published)*

LOCKED (preview + insights captured). Stages: Screening + Onsite. Variation of LC 609. Find groups of duplicate files with identical BINARY content in a simulated file system rooted at "/". Names/paths don't matter; content only accessible as a binary stream (no direct string access); must be efficient over huge file counts. Part 1 (q ...8ba): recursive traversal, filter candidates by metadata (file size) before reading, group by cryptographic hash. Part 2 (q ...8be): very large files must be read in constrained CHUNKS under strict I/O and memory limits - incremental/running hash updated per chunk, group by size first, defer content reads until a size-bucket has >=2 candidates. Site follow-ups: distributed file system scaling; hash-collision false positives (byte-by-byte confirm); memory for millions of files; partially-similar/modified file detection; parallelization and its synchronization issues; complexity when chunk limit is tiny.

**解法**: Site hints: DFS/BFS to collect paths; size-bucket first (cheap metadata) -> only hash buckets with multiple files; streaming/incremental hash (e.g., hashlib update per chunk); optional first-chunk prefilter. This matches candidate reports of Anthropic's 'dedupe files with an API that reads bytes' interview.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6934db5e5f306485cc5f08b9&gt;)

### Generate Function Profiling Events (LC 636 variant: stack-trace samples -> start/end events, 3 parts)
*hard · 频率: Anthropic freq 9/10; last reported ~2026-05-31 · 2025-12 (published)*

LOCKED (preview + all 3 parts' insights captured). Stage: Screening. A sampling profiler records entries "&lt;time&gt;:&lt;stackTrace&gt;" where time is strictly increasing int and stackTrace is "main->worker->parse" outermost-to-innermost; stack may be empty ("42:"). Part 1 (q ...225): convert consecutive samples into chronological function start/end events by diffing consecutive stacks - find first mismatch from outermost inward; frames removed after that point ended, frames added started; handle recursion (duplicate names at different depths are independent frames) and empty stacks. Part 2 (q ...228): debounced events - emit start/end only for call paths persisting >= n consecutive samples; reset counter when path vanishes; defer start event until streak reaches n; batch events per timestamp then order by stack depth (outer starts before inner; inner ends before outer). Part 3 (q ...229): suffix-based variant - generate all stack SUFFIXES per sample, track streaks per suffix with original first-seen timestamp, use longest matching suffix chain on transitions to separate newly-valid from expired paths. Site follow-ups: multiple threads; exclusive vs inclusive time; bounded-memory streaming; per-depth debounce thresholds; removing the per-sample sort for strict O(N); trie for suffix matching; out-of-order samples.

**解法**: Site hints captured per part (prefix-diff two-pointer for part 1; hashmap streak counters + depth-sorted event batching for part 2; suffix enumeration + longest-common-suffix transition for part 3).

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224&gt;)

### Design Banking System (4-level OA/onsite; the classic CodeSignal banking series)
*medium · 频率: Anthropic freq 10/10 (also Coinbase/CapitalOne/HubSpot 10, Ramp 9); last reported 2026-05-18 · 2025-07 (published) - one of 4 posts hidden behind client-side pagination, recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stages: OA + Onsite. BankingSystem class, all ops timestamped with increasing ints. Level 1 (q 687c3a5e...): createAccount(ts,accountId)->bool (false if exists); deposit(ts,accountId,amount)->new balance or -1; transfer with validations (existence, distinct IDs, sufficient funds) all checked before committing. Level 2 (q 687c4741...): topSpenders(n) - rank accounts by cumulative OUTGOING transaction totals desc, tie-break alphabetical ID asc, format top N; maintain running outgoing sums instead of recomputing. Level 3 (q 687c4e56...): pay(ts,accountId,amount) deducts and schedules 2% cashback credited exactly 24h (86400000ms) later; getPaymentStatus(ts,accountId,payment)-> IN_PROGRESS/CASHBACK_RECEIVED; cashbacks due at a timestamp must be applied BEFORE any other operation at that timestamp; rounding down on 2%. Level 4 (q 687c5c0b...): mergeAccounts(id1,id2) consolidating balances, transaction history and pending cashbacks; getBalance(ts,accountId,timeAt) historical balance queries incl. accounts merged away before query time; self-merge invalid. Site follow-ups: thread safety; audit logging; float precision for currency; scaling to millions of tx; atomicity; prefix-sum/indexed history for O(log n) historical queries.

**解法**: Site hints: hashmap accounts; event-sourcing style immutable per-account transaction log in chronological order enables both merge and time-travel getBalance (replay or prefix sums); process due cashbacks lazily at the start of every operation.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/687c23f9aa2b26b0b64b39d4&gt;)

### Design In-memory Database with Backup (4-level OA; TTL + timestamped versions + backup/restore)
*hard · 频率: Anthropic freq 9/10 (Coinbase/HubSpot 10, Ramp 9); last reported 2026-04-21 · 2025-08 (published) - hidden post recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. InMemoryDB storing records key->(field->value), all strings. Level 1 (q 689505e7...): setData(key,field,value) upsert; getData->"" if missing; deleteData->bool. Level 2 (q 68961c87...): scanData(key) returns all fields formatted "field(value)" lexicographically sorted; scanDataByPrefix(key,prefix) same but filtered by field prefix. Level 3 (q 689641c8...): timestamped variants setDataAt/getDataAt/scanDataAt with TTL support - field expires after specified duration; timestamps strictly increasing; legacy methods must keep working (backward compat); store per-field chronological version history and binary-search the valid state at query time; lazy expiration. Level 4 (q 689bb206...): backupDatabase(ts) captures only records alive at ts along with their REMAINING TTLs; restoreDatabase(ts, backupTs) restores newest backup <= backupTs and re-bases expirations relative to the restore timestamp (remaining lifespan preserved). Site follow-ups: concurrency; lazy vs background expiry; memory for full version history; non-monotonic timestamps; snapshot vs incremental diff tradeoffs; distributed/eventually-consistent variant.

**解法**: Site hints: nested dict key->field->list of (ts,value,ttl) versions; binary search for at-time reads; backup = filtered snapshot storing remaining-TTL; restore = fresh inserts with clock re-based at restore time. This is the well-known CodeSignal Industrial Coding Framework database question family.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689505de3a1d9e6d6042d519&gt;)

### Cloud Storage System (4-level OA; files, prefix/suffix search, users+capacity, compression)
*hard · 频率: Anthropic freq 7/10 (Ramp 10, Coinbase/HubSpot 9, eBay 7); last reported 2026-03-08 · 2025-08 (published) - hidden post recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. Level 1 (q 689cf810...): addFile(name,size)->bool (fail if exists); copyFile(nameFrom,nameTo)->bool (source must exist and not be a directory, target must not exist); getFileSize(name)->size or -1; treat paths as opaque unique strings. Level 2 (q 689e4cd5...): findFile(prefix,suffix) returning "name(size)" entries where name starts with prefix AND ends with suffix, sorted size DESC then name ASC. Level 3 (q 689e4cd8...): multi-user - addUser(userId,capacity); per-user capacity limits with global file-name uniqueness; addFileBy(user,...) returns remaining capacity; admin has unlimited; updateCapacity(user,newCap) shrinks quota and auto-removes largest files (lexicographic tie-break) until fit, returning count removed. Level 4 (q 689e4cd9...): compressFile/decompressFile - compressed file takes size/2, gets naming-convention suffix (.COMPRESSED), ownership preserved, all capacity constraints validated atomically (compute net space delta first, no temporary overflow). Site follow-ups: hierarchical directories + recursive delete; concurrency/distribution; content dedup; billions of files; rollback for failed compression jobs.

**解法**: Site hints: hashmaps for file->size/owner, user->capacity, user->used; linear scan + custom comparator for findFile; sort-by-(size desc, name asc) removal loop for capacity shrink; strict precondition checks before any mutation for atomicity.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689cf808aee746eb1c84ba37&gt;)

### Design Worker Management System (4-level OA; clock-in/out, top-N, promotions, double-pay intervals)
*medium · 频率: Anthropic freq 6/10 (Coinbase/HubSpot/Ramp 7); last reported 2026-03-16 · 2025-08 (published) - hidden post recovered via API*

LOCKED (preview + all 4 levels' insights captured). Stage: OA. Level 1 (q 68a4bbec...): addWorker(workerId,position,compensation)->"true"/"false" if exists; registerWorker(workerId,timestamp) toggles enter/leave (timestamps increasing) -> "registered"/"invalid_request"; get(workerId) -> total office time from COMPLETED sessions only, -1 if unknown worker. Level 2 (q 68a4bbf8...): topNWorkers(n,position) - filter by position, sort by accumulated time DESC then workerId ASC, formatted string output. Level 3 (q 68a4bbfa...): promote(workerId,newPosition,newCompensation,startTimestamp) - promotion is DEFERRED, activates only at the worker's NEXT office check-in after startTimestamp; calcSalary(workerId,startTs,endTs) sums compensation over completed sessions intersected with the query window, using the compensation rate in effect during each session. Level 4 (q 68a4bbfb...): setDoublePay(startTs,endTs) marks time ranges double-paid; overlapping periods must be consolidated (merged) and each minute double-counted at most once in salary calculations - intersect each session with merged double-pay periods and the query window. Site follow-ups: thread safety; non-monotonic timestamps; historical range reports; selection algorithm instead of full sort for top-N; sparse/huge timestamp ranges.

**解法**: Site hints: per-worker profile + nullable in-office-since timestamp; session list of (start,end,compensation); pending-promotion metadata applied at next check-in; keep double-pay intervals sorted+merged on insert, then interval-intersection arithmetic for salary.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/68a4bbdfc11d63d6052ea306&gt;)

### Live 技术 screen 真题：call stack sampling → execution trace 转换
*medium · 频率: 2 个独立报告 · 2026-01*

两个独立第一人称报告的同一题：(1) Exponent 上 Safeguards Senior SWE（约 2025 年末-2026 年初）：Technical Interview 1 为 "Transform call stacks or samples into execution traces"，非 LeetCode，像处理 profiling-style data；(2) Andrey Zharkov（2025，RE 轨道）列出的被问题目中有 "Convert call stack trace from one format to another (sampling profiler)"。即给定sampling式 profiler 的输出（每个时刻的调用栈快照），转换为进入/退出事件流或调用树/火焰图聚合格式。Zharkov 在 Anthropic 的 live 技术 screen 挂掉（自称当周工作 80h 太累），说明该轮虽不算难但要求扎实执行。

**解法**: （我的推断）对相邻两个sampling栈求最长公共前缀：公共前缀之上的旧帧依次产生 exit 事件（逆序），新帧依次产生 enter 事件（正序）；聚合成树时按 (depth, frame) 累计样本数即得火焰图。注意首末样本的边界、递归同名帧要按位置而非名字匹配。

来源: &lt;[来源链接](https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f&gt;)

### Onsite coding 真题：LRU cache 分层加需求（持久化/序列化）
*medium · 频率: 3+ 报告（含变体） · 2026-01*

Exponent Safeguards SWE 面经：Technical Interview 2 为 LRU cache 实现，随后 layered complexity additions——加文件处理（file handling）和序列化 tradeoffs 讨论。jobright 聚合亦记录变体 "Implement an LRU Cache. Now, how would you make it persistent?"（讨论 JSON vs pickle 等 tradeoff）。leonstaff 记录另一变体：build LRU Cache, then make it concurrent（线程安全）。这与 Anthropic 'build from scratch + 渐进加需求' 的 coding 风格一致：先正确实现，再层层加约束并讨论取舍。

**解法**: OrderedDict 或 dict+双向链表标准实现；持久化讨论点：全量 snapshot vs append-only log（WAL）、序列化格式取舍（pickle 快但不安全/不跨语言，JSON 安全但类型受限）、崩溃一致性；并发版：单锁先行，再谈分段锁/读写锁与 LRU 顺序维护的冲突。（我的推断）

来源: &lt;[来源链接](https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f&gt;)

### 其他被报告的 live coding 题：rate limiter、流式数据处理、sequence packing
*medium · 频率: 各 1-3 个报告 · 2025*

聚合与第一人称混合来源：(1) Rate limiter：实现 rate limiter，follow-up 依次为并发安全（为 tool-calling agent 的 API 设计线程安全限流器）、多机部署、sliding window、降载策略；(2) 实时流数据处理：去重、排名、聚合、故障检测；(3) Zharkov 被问过（跨公司列表中，很可能即 Anthropic RE 轨道）："Implement sequence packing for LLM training"——list[list[int]]（变长序列）→ 打包成每条不超过 max_length 的 list[list[int]]，要求 'as optimal as you can'；(4) 其他被多个聚合站提到：tokenization 引擎（文本流+缓冲）、duplicate file finder（哈希+文件系统遍历）、log processing、图遍历。Glassdoor 摘要将 Anthropic coding 总结为 'software development assignment with a bit of leetcode baked in'。

**解法**: sequence packing：本质是 bin packing（NP-hard），面试期望 first-fit decreasing 贪心（按长度降序，放入第一个能容纳的 bin），讨论与最优解差距和 O(n log n) 实现（用有序结构找剩余容量）；rate limiter：token bucket 单机 + Redis/一致性哈希分布式 + sliding window log vs counter 的内存/精度 tradeoff。（我的推断）

来源: &lt;[来源链接](https://reyzharkov.com/blog/posts/interviews-2025-ml-research-engineer-uk&gt;)

### Performance Engineering take-home（官方已开源，含全部规格）
*hard · 频率: 官方（1000+ 候选人经历过此轮） · 2026-01*

Anthropic 性能团队 2024 年起使用、2026 年 1 月开源的 take-home（1000+ 候选人做过，直接促成数十人入职；由 Tristan Hume 团队设计）。任务：优化运行在模拟加速器（类 TPU）上的 kernel，最小化时钟周期。机器模型：单核 VLIW SIMD 处理器，每周期槽位：ALU×12（标量）、VALU×6（8 宽向量）、LOAD×2、STORE×2、FLOW×1；手动管理的 scratchpad 1536 words；瓶颈是每周期仅 2 load + 2 store。Kernel：batched tree traversal（决策树推理启发）——深度 10 的完美二叉树（2047 节点）、batch 256、16 轮遍历共 4096 步；每步：读 index/value → 取树节点值 → hash(value XOR node)（6 段 hash，约 18 个 ALU 操作，类 Bob Jenkins）→ next = 2*idx+1/2（奇偶分支）→ 越界回绕。原版 4 小时（baseline 147,734 cycles）；2 小时版 starter 18,532 cycles。分数参照：Opus 4 长时间 2,164；Opus 4.5 两小时 1,579；Opus 4.5 最好 1,487 = '打过它就发邮件 performance-recruiting@anthropic.com（附代码+简历）'的招聘线。此 take-home 明确允许用 AI 工具（官方 candidate 政策的例外）。开源后警告：第一天收到的所有 <1300 cycles 提交全是模型改测试作弊；提交前必须 git diff origin/main tests/ 证明测试未改、跑 tests/submission_tests.py。因 Claude 表现超过人类，真实招聘已换到 V3 版本：Zachtronics 风格、极小受限指令集的约束优化谜题（Claude 尚不擅长）。

**解法**: 优化路线（trirpi.github.io 深度拆解）：SIMD 向量化（8 items/op）→ VLIW 打包（跨引擎塞满每 cycle）→ software pipelining（跨迭代重叠隐藏依赖链）→ branchless（select 替代跳转）→ 跨 batch item 并行掩盖单条遍历的串行 hash 链；load/store 带宽是最终瓶颈，把 tree 热点层预载进 scratchpad。深拆见 [来源链接](https://trirpi.github.io/posts/anthropic-performance-takehome/) 与 Anthropic 官方设计博客。

来源: &lt;[来源链接](https://github.com/anthropics/original_performance_takehome&gt;)

### 公开版 performance take-home 的社区解题记录（供练习对标）
*hard · 频率: 公开挑战（多篇解题记录） · 2026*

两篇公开解题记录可作练习材料：(1) trirpi.github.io 'Deep Dive: Anthropic's Performance Take-Home (The One Claude Beat Humans At)'——完整拆解机器模型（ALU×12/VALU×6/LOAD×2/STORE×2/FLOW×1、scratch 1536 words、8 宽向量）、kernel（深度 10 树、batch 256、16 轮、6 段 hash）与五步优化法（VLIW packing、SIMD、software pipelining、branchless select、跨 item 并行）；(2) matthewtejo.substack.com 'Taking on Anthropic's Public Performance Engineering Interview Challenge' 与 (3) medium.com/@indosambhav 的挑战记录。这是 2026 年 7 月准备 Anthropic 性能向岗位（或想走 performance-recruiting 邮箱内推通道）最直接的实战训练集：目标把 starter 18,532 cycles 压到 <1,487。

**解法**: 练习顺序建议：先只做向量化拿 10x，再学着读 watch_trace.html 找每 cycle 空槽，最后做 software pipelining；对照仓库 tests/submission_tests.py 验证，不要动 tests/ 目录。

来源: &lt;[来源链接](https://trirpi.github.io/posts/anthropic-performance-takehome/&gt;)

### Anthropic Fellows/MATS 新版 OA 真题细节：一致性哈希 + 请求路由到虚拟节点 + RAM/GPU 显存驱逐
*hard · 频率: multiple (5+ reports in thread) · 2026-01*

r/Anthropic 帖（2026-01，评论持续到 2026-05）：Fellows Program（AI Safety Research）OA 已从 CodeSignal ICA 换成自研更难版本。一位考生透露被问：consistent hashing、chat request 路由到 virtual nodes、基于 RAM/GPU memory 的 eviction（缓存驱逐）。2026-07 cohort 邀请函明确写 6 parts 且提到 concurrency（asyncio/threading）。仍是渐进式 system-building（类似 banking system 但'题面像论述题'）。流程：OA1 → OA2 → references（3封，会真联系）→ take-home → 面试。旧版 cut line 480/600。

**解法**: 练：实现 consistent hash ring（虚拟节点、增删节点时的 key 迁移）、LRU/加权容量驱逐（按内存占用而非条目数）、asyncio 生产者-消费者。我的推断：这是模拟 LLM 推理cluster的 KV-cache/模型分片路由场景，把三者组合成一个渐进题。

来源: &lt;[来源链接](https://www.reddit.com/r/Anthropic/comments/1qovmbs/assessment_for_anthropic_fellows_program_for_ai/&gt;)

### Anthropic L4 SWE onsite 编码轮题目清单（2025 offer 面经）：线程安全缓存/流式 tokenizer 性能 debug/并发预订系统
*hard · 频率: single detailed report (corroborated by 4+ partial reports) · 2026-05*

InterviewCoderHQ 详细 offer 面经（L4 remote，6 YoE backend）：技术店面=用 ThreadPoolExecutor 构建 async 处理管线、处理并发安全、debug 性能瓶颈（55-90分钟）。onsite 编码轮三题型：(1) build a thread-safe cache with configurable eviction policy；(2) debug a performance bottleneck in a streaming tokenization system；(3) design and implement a reservation service with concurrency constraints。共同主题：multithreading、async processing、API design、streaming、pipeline debugging。评分看代码可读性、并发正确性、架构决策、debug 方法论，而非时间复杂度。作者称没刷 LeetCode 是正确选择，备考 6 周聚焦 Python 并发原语 + 生产级代码（错误处理/日志）。注：该 sub 由面试辅导产品运营，细节与多个独立报告吻合但属二手整理。

**解法**: 线程安全缓存：dict + OrderedDict/heap 驱逐 + RLock，讨论锁粒度和 read-heavy 优化；预订系统：per-resource lock 或乐观并发 + 幂等；tokenizer debug：找 GIL 争用/重复分配/无缓冲 IO。

来源: &lt;[来源链接](https://www.reddit.com/r/InterviewCoderHQ/comments/1tirugm/anthropic_swe_interview_experience_2025_l4_remote/&gt;)

### Anthropic SWE 技术店面结构（2025-01 一手，帖子已删但 pullpush 存档到正文）：30min code review+debugging + 30min coding
*medium · 频率: single report (structure corroborated later) · 2025-01*

r/leetcode 2025-01 帖（原帖已删除，selftext 经 pullpush 存档恢复）：SWE 岗流程=CodeSignal OA→recruiter call（含薪酬说明）→1小时技术店面：前 30 分钟 code review 和 debug 已有代码，后 30 分钟 coding。recruiter 明确说'不强调高级算法和数据结构，熟悉所选语言和标准库即可，不是 leetcode'。评论区印证当期其他人报告的是 concurrency/multiprocess 题。这是 code-review-as-interview 形式的最早报告之一，与 2026 年'debug 或扩展已有代码'的报告连续。

**解法**: 练 code review：找并发 bug（race、死锁）、资源泄漏、错误处理缺失、边界条件；练口头表达 review 意见的礼貌与优先级。

来源: &lt;[来源链接](https://www.reddit.com/r/leetcode/comments/1ibskkp/anthropic_tech_screening_what_to_expect_in_the/&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
