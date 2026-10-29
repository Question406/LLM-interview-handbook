---
id: drustz-a15ca2ae37d386b728
section: collections
order: 23
level: A
title: Google DeepMind 题库（爬取全量） · System Design
quick: 作者文档章节 · Google DeepMind 题库（爬取全量） · System Design
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
## System Design

### Google/DeepMind · System Design 题库（20 题，经典分布式系统）
*hard · 频率: onsite 高频 — Google 频率：Design Job Scheduler 9、Design News Feed 9、Design Typeahead 8、Design Youtube 8、Design Distributed Rate Limiter 7、Design Instagram 7、Design TinyURL 7 · 2025-12 至 2026-04*

Google SD 全 20 题（Onsite，正文需登录；practice URL .../google/system-design/{id}/practice）：Design Payment System(Hard)、Design Slack-like Chat System(Hard)、Design News Feed(Medium, id 69ca9b37ff3ebde766ced8eb)、Design TinyURL(Easy)、Design Metrics System(Medium, 69cc94b2ff3ebde766cee3f2)、Design Youtube(Hard)、Design Distributed Rate Limiter(Hard, 69cd9871ff3ebde766cee7fe)、Design Dropbox(Hard, 69cdf6feff3ebde766ceea74)、Design Job Scheduler(Medium)、Design Notification System(Medium, 69cfaa8f4f38b199f9e49615)、Design Facebook Messenger(Medium)、Design A Top K Popular Items System(Medium, 69d2ef0707421ca06eb8e53b)、Design Typeahead Suggestion(Medium, 69d55ecf60ca00f1f2f5f100)、Design Spotify(Medium)、Design S3-like Object Storage System(Medium, 69d84a1bc4c1bc791ee2309f)、Design Quota Service(Medium)、Design Key-value Store(Hard, 69dc51e8e4441834b3f7376f)、Design Instagram(Hard, 69e1b8b295e80ae213e5d4a2)、Design Google News(Medium)、Design A VM Bandwidth Rate Limiter(Hard, 6a074964906c2652b8dd4616)。多为跨公司通用经典题（非 Google 独有）。

**解法**: （我的推断）Google 侧重规模化与一致性：Rate Limiter（令牌桶/滑窗、分布式计数）、Key-Value Store（一致性哈希、复制、quorum、LSM）、Top-K（count-min sketch + heap）、Typeahead（Trie + 前缀聚合缓存）。对 RE 岗建议至少熟练其中 5-6 道 Hard。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/google/system-design&gt;)

### techinterview.org 2026：SWE track 轮次（含 ML serving domain depth）
*hard · 频率: 聚合指南 + 1 条 Blind 佐证 · 2026*

SWE 4-5 轮：2 场 coding（medium-hard；数组/字符串/图/树/DP，unaided）+ 1 场 system design 60min（端到端设计可扩展服务：需求澄清、API、存储选型）+ 1 场 domain depth（按团队考 ML serving / API 设计 / infra：latency、batching、deployment）+ behavioral。2026 政策：技术轮普遍禁止或严格限制 AI 工具，仅个别 applied 岗例外。佐证（Blind 2025-12 xhrkeb8z）：L4 SWE 称 system design 题“very weird and ambiguous”。

来源: &lt;[来源链接](https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/gdm.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/gdm.md)。作者整理资料；许可和第三方来源范围见阅读指南。
