---
id: drustz-5333161bbca92aad2b
section: mlsd
order: 209
level: A
title: 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 12. 配套代码
quick: 作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 12. 配套代码
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md
    type: primary
---
## 12. 配套代码

```bash
cd labs/swe_data
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V toyrepo.py                    # 造一个带真实 git 历史的玩具仓库（9 个 commit）
$V github.py                     # 仓库筛选打分 + issue 链接解析（离线；--live 需 token）
$V mine.py                       # 挖候选 + **真跑 pytest** 做三步 F2P/P2P 验证
$V synth.py                      # SWE-smith 式 AST 造 bug + 执行验证
$V curate.py                     # 去重 / 去污染 / 难度分层
$V -m pytest test_swe_data.py -q # 26 passed
```



只依赖 pytest，无网络、无 Docker、无 API key。**F2P/P2P 是真跑出来的，不是模拟的。**

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
