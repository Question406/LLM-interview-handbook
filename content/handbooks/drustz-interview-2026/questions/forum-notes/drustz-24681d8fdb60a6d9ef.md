---
id: drustz-24681d8fdb60a6d9ef
section: forum-notes
order: 205
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · 4. System Architecture
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · 4. System Architecture
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
## 4. System Architecture

### High-Level Diagram

```mermaid
flowchart TB
    subgraph Clients
        WEB[Web Browser]
    end

    subgraph Edge["Edge Layer"]
        LB[Load Balancer]
    end

    subgraph App["Application Layer"]
        API[API Servers]
        WSS[WebSocket Servers]
    end

    subgraph Orchestration["Manager Layer"]
        SM[Sandbox Manager]
        POOL[Warm Pool Controller]
        K8S[Kubernetes Cluster]
    end

    subgraph Streaming["Output Streaming"]
        KAFKA[Kafka]
    end

    subgraph Storage["Storage"]
        PG[(PostgreSQL - Data)]
        REDIS[(Redis - Cache)]
        S3[(S3 - Files)]
    end

    subgraph Compute["Sandboxes"]
        VM1[Sandbox Pod 1]
        VMN[Sandbox Pod N]
    end

    WEB -->|HTTPS| LB
    WEB -->|WSS| LB
    LB --> API
    LB --> WSS

    API --> SM
    API --> PG
    API --> S3

    SM --> POOL
    SM --> K8S
    POOL --> K8S

    K8S --> VM1
    K8S --> VMN

    VM1 --> KAFKA
    VMN --> KAFKA

    KAFKA --> WSS
    WSS --> REDIS
```



### Who Does What?

- **API Servers:** Handle login, file saving (to S3), and creating workspaces.
- **WebSocket Servers:** Send terminal text to the user. They listen to **Kafka**.
- **Sandbox Manager:** The "brain." It creates Sandboxes and assigns them to users.
- **Warm Pool Controller:** Keeps a list of "ready-to-go" Sandboxes so users don't have to wait.
- **Kubernetes:** Runs the actual Sandboxes (Pods).
- **Kafka:** A message bus that moves terminal output from the Sandbox to the WebSocket Server.

### Data Flow: Running a Command

- **User** clicks "Run".
- **API** tells **Sandbox Manager** to start the command.
- **Sandbox Manager** finds the correct **Sandbox (Pod)** and sends the command.
- **Sandbox** runs the code. Output (text) is sent to **Kafka**.
- **WebSocket Server** reads **Kafka** and sends text to the **User's** browser.

### Sandbox Design (The Pod)

Each Sandbox is a Kubernetes Pod with two containers:

- **Runtime Container:** Where the user's code runs (Python, Node, etc.). It has limited permissions.
- **Agent Container:** A helper program. It receives commands from our API and streams the output to Kafka.
**Security is key:**

- **Network Policy:** Block internet access (except for specific package managers like npm/pip).
- **Read-Only:** The root file system is read-only. We mount a separate volume for `/workspace` where the user writes code.

### Terminal Streaming (The Hard Part)

To make it feel real-time:

- **Agent** collects output from the user's code.
- It groups (batches) the text into small chunks (every 50ms).
- It sends the chunk to **Kafka**.
- **WebSocket Server** picks it up and sends it to the browser.
*Why batch?* Sending every single letter individually is too slow and expensive. 50ms is fast enough for humans but saves resources.

**Code Logic for Agent:**

```python
class OutputStreamer:
    def capture(self, data):
        self.buffer.append(data)

        # Send to Kafka if buffer is big OR 50ms has passed
        if self.should_flush():
            self.send_to_kafka(self.buffer)
            self.buffer = []
```



### Reconnecting

If a user refreshes the page, they shouldn't lose the terminal history.

- **Solution:** Store the last 1 hour of output in **Redis**.
- When a user reconnects, send the old data from Redis first, then switch to live Kafka streaming.

### Warm Pool Strategy (Speeding up Start Times)

Starting a new container takes 10-30 seconds. This is too slow.
**Solution:** Start them *before* the user needs them.

- **Warm Pool:** Keep 500 "blank" Python environments running.
- **Allocation:** When a user clicks "Start", grab one from the pool. It takes 1 second.
- **Refill:** The Pool Controller sees the pool is low and starts more.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
