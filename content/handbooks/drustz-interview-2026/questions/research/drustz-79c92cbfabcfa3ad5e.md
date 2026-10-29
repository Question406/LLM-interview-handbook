---
id: drustz-79c92cbfabcfa3ad5e
section: research
order: 113
level: A
title: cd/pwd 路径解析题 2026-07 仍在考（Blind 新帖，四 part 递进：normalize→绝对路径→~→symlink）
quick: >-
  supplemental-research-note · cd/pwd 路径解析题 2026-07 仍在考（Blind 新帖，四 part
  递进：normalize→绝对路径→~→symlink）
companies:
  - openai
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.teamblind.com/post/openai-interview-question-implement-a-cd-command-fuw1arri
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Blind 帖（约 2026-07-04，'OpenAI interview question - Implement a CD command'）：实现 cd(current_dir, destination) -> normalization绝对路径，四个递进 part，每 part 加一个参数。Part 1：处理 ..、.、重复斜杠 foo//bar、尾斜杠、越过根目录停在 /。例：cd('/usr/local','../A/B/')→'/usr/A/B'；cd('/','..')→'/'；cd('/a/b/c','../../x/./y//')→'/a/x/y'。Part 2-4：绝对路径 destination、~（home）展开、symlink 解析（含环检测；更长/更具体的 symlink 路径优先匹配）。评论（Meta 工程师）：'stack 题起手'，且'这题用了很多年，最早在 Twitter 见过'。Hello Interview 也收录 symlink 版（cycle detection 是难点）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.teamblind.com/post/openai-interview-question-implement-a-cd-command-fuw1arri)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
