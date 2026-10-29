---
id: drustz-15f3b27ac0c93dd3bf
section: forum-notes
order: 202
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · 1. What We Need to Build
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · 1. What We Need to Build
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## 1. What We Need to Build

### Functional Requirements

- **File Management:** Users can create folders, and add, edit, or delete files.
- **Run Code:** Users can run commands and see the output (stdout/stderr) instantly.
- **Stop Processes:** Users can stop a program that is running.
- **Install Packages:** Users can install libraries (like `npm install`) and they stay there while the session is active.
- **Sharing:** Users can share their workspace so others can view or edit it.
*Note on Sharing:* We will focus on simple access control. We will not cover real-time collaborative typing (like Google Docs) in this guide.

*Note on Persistence:* When a user installs a package, it stays until they close the tab/session. Saving the whole operating system state forever is hard and usually a paid feature.

### System Requirements (Non-Functional)

| Requirement | Target | Reason |
| :--- | :--- | :--- |
| **Startup Speed** | < 5 seconds | Users hate waiting for the environment to load. |
| **Output Speed** | < 100ms | Typing in the terminal needs to feel instant. |
| **Reliability** | 99.9% | Important for paying customers. |
| **Scale** | 100K users at once | Must handle popular traffic. |
| **Security** | Strong Isolation | One user must never access another user's data. |

*Interview Tip:* Ask the interviewer: "Do we support jobs that run for hours, or just short coding sessions?" For this design, we assume interactive coding with a 12-hour limit.

### Capacity Estimation

**Assumptions:**

- 100,000 concurrent users.
- Each user gets: 2 vCPU, 4GB RAM.
**Compute Needed:**

- 100,000 users × 2 vCPUs = **200,000 vCPUs**.
- 100,000 users × 4GB RAM = **400TB RAM**.
- If one server has ~40GB RAM, we need about **10,000 servers**.
**Network Bandwidth (Terminal Text):**

- Assume 50% of users are running a command at the same time.
- 50,000 active processes × 1KB/second = **50MB/second**.
- A small **Kafka** cluster (3-5 brokers) can easily handle this.
**Conclusion:** The biggest cost is the servers (compute), not the storage or network. We must be smart about how we use the VMs to save money.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
