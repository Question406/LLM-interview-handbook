---
id: drustz-d9f7750e868cbfbebb
section: coding
order: 17
level: A
title: Claude Stock Tool-Use Agent
quick: 作者完整文档 · Claude Stock Tool-Use Agent
companies: []
tags:
  - DrustZ
  - 作者完整文档
  - 公司 Coding 与手写训练
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/practice/anthropic/agent_tool_use/README.md
    type: primary
---
# Claude Stock Tool-Use Agent

这是 `Agents Coding LLM Tool Use` 的最小可运行练习项目。完整题面写在
[`agent.py`](?book=drustz-interview-2026&section=coding&question=drustz-9f5991c31e3d8aaa26) 顶部；[`SYSTEM_DESIGN.md`](?book=drustz-interview-2026&section=coding&question=drustz-fecadc3afe29bd6387) 单独回答
“能适应新任务的 agentic AI system”设计题，避免把两道题混成同一题。

## 离线测试

```bash
cd /Users/mingrui/Documents/codes/interview/1acre3points
python3 -m unittest tests/test_claude_stock_agent.py -v
```



测试使用 fake Claude client 和 mock 股票工具，不需要 API key、Anthropic SDK 或网络。

## 调用真实 Claude API

```bash
python3 -m pip install anthropic
export ANTHROPIC_API_KEY='...'
export CLAUDE_MODEL='claude-sonnet-4-6' # 可换成账户可用的当前模型
python3 -m practice.anthropic.agent_tool_use.demo \
  'Compare the sample prices for AAPL and MSFT.'
```



Demo 的股票数字是明确标注的固定 mock 数据。面试中可把
`StaticStockPriceService` 换成真实行情 API adapter；agent loop 无需修改。

## 目录

```text
agent_tool_use/
├── agent.py          # 题面、tool schema、manual agent loop、错误与并行处理
├── demo.py           # 可选的真实 Claude API 入口
├── SYSTEM_DESIGN.md  # 独立的 adaptive-agent system design 答案
└── README.md
```

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/practice/anthropic/agent_tool_use/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/practice/anthropic/agent_tool_use/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
