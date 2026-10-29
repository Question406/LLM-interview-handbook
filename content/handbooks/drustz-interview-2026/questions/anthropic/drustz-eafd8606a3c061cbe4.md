---
id: drustz-eafd8606a3c061cbe4
section: anthropic
order: 31
level: A
title: SD Q2 Prompt Playground
quick: locally-saved-topic-editorial · SD Q2 Prompt Playground
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/sd-q2-prompt-playground
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Prompt Playground System Design

## The Design Problem

**Goal:** Design a "playground" tool for Prompt Engineering, similar to the OpenAI Playground or Anthropic Console. This is a **full-stack system design** question. You need to focus on product features, how the UI looks, how the code works, and how it scales.

### What is Prompt Engineering?

**Prompt engineering** means testing and changing input text (prompts) to get the best result from an AI model.

- **Not a Chatbot:** This is not like ChatGPT. There is no conversation history.
- **Independent Runs:** Every time you click "Run," the model starts fresh. It has no memory of the previous run.

### Example User Flow

- **Write:** A user types: "Write a recipe."
- **Refine:** They change it to: "You are a chef. Write a recipe for pasta."
- **Test:** They add examples of good recipes to help the model.
- **Repeat:** They keep changing the prompt until the result is perfect.
- **Save:** They save the best version to use later.

### Follow-up Questions

The interviewer might ask about these harder topics:

- **Scale:** How do we handle 10MB text files?
- **Versions:** How do we track changes if a user saves 1000 times?
- **Cost:** How do we stop users from spending too much money on the LLM API?
- **Search:** How do you search through huge text documents?

## Step 1: Defining the Requirements

First, ask questions to understand exactly what you need to build.

### Questions to Ask

**Features:**

- Can users create, edit, and save prompts?
- Do we need to save the history of changes (version control)?
- Does it support different models (like GPT-4, Claude)?
- Can users share prompts?
**Constraints:**

- **Max Size:** How big can a prompt be? (Answer: 10MB for editing).
- **Users:** How many people at once? (Answer: Thousands).
- **Speed:** Do we need real-time streaming? (Answer: Yes).

### Summary of Needs

**Functional Requirements (What it does):**

- **Editor:** A text box that handles huge text (10MB). Note: 10MB is about 2.5 million tokens, which is too big for most models to actually run, but we must store it.
- **Execution:** Send prompts to an API (like OpenAI) and stream the answer back.
- **History:** Auto-save versions so users can go back to old drafts.
- **Library:** Organize prompts with tags and search.
- **Sharing:** Create links to share prompts with others.
**Non-Functional Requirements (How it performs):**

- **Speed:** No lag when typing in a 10MB file.
- **Reliability:** Do not lose data if the browser crashes.
- **Scalability:** Support thousands of users editing at the same time.

## Step 2: Estimating Scale and Costs

Let's do some math to see how big the system needs to be.

### Assumptions

- **Users:** 1 million total users.
- **Daily Usage:** 10,000 users per day.
- **Prompt Size:** Most are small (1KB), but some are huge (10MB).
- **Read vs Write:** Users read/view prompts much more than they save them (80% read, 20% write).

### Calculations

**Traffic:**

- Reads: ~0.6 requests per second (very low).
- Writes: ~0.12 requests per second (very low).
- **Conclusion:** Traffic is low. We don't need complex database sharding yet.
**Storage:**

- Prompts: 1M users × 10 prompts × 1KB = 10GB.
- Versions: If we save every version, it gets big (300GB).
- **Conclusion:** Storage is cheap. We can use S3 for big files and a database for small ones.
**Costs:**

- **LLM API Cost:** This is the most expensive part.
- If we use high-end models (like Claude 3.5 Sonnet), it could cost &#36;450/day.
- **Strategy:** We must use **Caching** to save money. If a user runs the exact same prompt twice, show the saved result instead of paying the API again.

## Step 3: API Definition

We need clear rules for how the frontend (browser) talks to the backend (server).

### Main API Calls

```text
// Managing Prompts
createPrompt(userId: string, content: string, tags: string[]): Promise<Prompt>
updatePrompt(promptId: string, content: string): Promise<PromptVersion>
getPrompt(promptId: string): Promise<Prompt>

// Managing Versions (History)
getVersions(promptId: string): Promise<PromptVersion[]>
revertToVersion(promptId: string, versionNumber: number): Promise<PromptVersion>

// Running the Prompt
// Returns an ID to track the job
executePrompt(promptId: string, model: string, params: ModelParams): Promise<ExecutionId>

// Real-time Updates (WebSocket)
// The server sends these messages to the client:
{
  type: "TOKEN",      // A piece of the answer
  text: "..."
}
{
  type: "DONE",       // Finished
  cost: 0.05          // How much it cost
}
```



## Step 4: Database Schema Design

This is how we organize data in the database.

### The Data Model

We will use **PostgreSQL** because our data is structured and relationships are important.

**1. Prompts Table**

- `id`: Unique ID.
- `user_id`: Who owns it.
- `current_version`: The number of the latest version.
- `content_preview`: The first 500 characters (for fast searching).
- *Note: We do NOT store the full text here.*
**2. PromptVersions Table**

- `prompt_id`: Links to the prompt.
- `version_number`: e.g., Version 1, Version 2.
- `is_snapshot`: **True** if this is a full copy. **False** if it is just a list of changes (diff).
- `content`: The text (or a link to S3 if it is larger than 100KB).
**3. Executions Table**

- `id`: Unique job ID.
- `status`: Queued, Running, Success, or Failed.
- `cost_usd`: How much this run cost.
- `response_text`: The answer from the AI.

### Storage Strategy

- **Snapshots vs. Diffs:** To save space, we don't save the full text every time.

**Snapshot:** Save the full text every 10th version (v1, v10, v20).
- **Diff:** For versions in between (v2-v9), only save the *changes* from the previous version.

## Step 5: Architecture Overview

Here is how the different parts of the system connect.

### Component Diagram

- **Client (Browser):**

Uses **Monaco Editor** (like VS Code) to handle large text files smoothly.
- Uses **IndexedDB** to save drafts on your computer so you don't lose work if internet fails.
- **Load Balancer:**

Sends traffic to the API servers.
- **API Servers (Node.js):**

Handles requests.
- Checks if the user is allowed (Auth).
- Connects to WebSockets.
- **Redis (Cache):**

Stores recent prompts for speed.
- Counts requests to limit usage (Rate Limiting).
- **PostgreSQL (Database):**

Stores user data and small prompts.
- **S3 (File Storage):**

Stores huge prompts (over 100KB).
- **Bull Queue:**

A waiting list for jobs. If many people click "Run" at once, this puts them in line.
- **LLM API:**

External services like OpenAI or Anthropic.

### How Data Moves (The Flow)

**When a User Clicks "Run":**

- Browser sends a WebSocket message: "Run this prompt."
- Server checks: "Is the prompt too long for this model?"
- Server puts the job in the **Bull Queue**.
- A background worker picks up the job and calls the LLM API.
- As the API sends text back, the worker streams it to the Browser via WebSocket.
- When finished, the result is saved to the Database.

## Step 6: Deep Dive into Key Components

In an interview, focus on these hard problems.

### 1. Handling 10MB Prompts

**The Problem:** 10MB of text makes browsers slow. Also, AI models cannot read 10MB (context window limits).

- **Browser Fix:** Use **Monaco Editor** with "virtual scrolling." This only draws the text you can currently see on the screen, not the whole file.
- **Execution Fix:**

Calculate the number of tokens using a tokenizer library.
- **Validate:** If the prompt is 10MB (2.5M tokens) but the model only supports 200K tokens, **block the request**. Show an error: "Prompt too long."
- The 10MB limit is for *storage and editing*, not for running the AI.

### 2. Version Control (Snapshots + Diffs)

**The Problem:** If a user saves 1000 times, storing 10MB 1000 times is too expensive.
**The Solution:**

- **Version 1:** Save full text (Snapshot).
- **Version 2:** Save only the changes (Diff).
- ...
- **Version 10:** Save full text again (Snapshot).
- **Reconstruction:** To read Version 5, the system takes Snapshot 1 and adds the changes from V2, V3, V4, and V5.

### 3. Syncing Multiple Tabs

**The Problem:** A user has the same prompt open in two tabs.
**The Solution:**

- **Same Device:** Use `BroadcastChannel` API. If you type in Tab A, Tab B updates automatically.
- **Conflict:** If Tab A and Tab B try to save different things at the exact same time, use **Optimistic Locking**. The server checks the version number. If they don't match, ask the user which version to keep.

### 4. Search Strategy

**The Problem:** Searching the full text of huge prompts is slow and expensive.
**The Solution:**

- **Fast Search:** Store the first 500 characters in PostgreSQL. This is free and fast.
- **Deep Search:** Use **Elasticsearch** for the full text, but truncate prompts to 100KB to save money. Most important keywords are usually at the start.

## Step 7: Fixing Performance Issues

Identifying where the system might break.

- **Cost of LLM API:**

*Risk:* Users running the same prompt over and over cost us money.
- *Fix:* **Cache responses.** If the prompt + model + settings are identical, return the saved answer from the last run.
- **Latency (Slowness):**

*Risk:* Loading a 10MB prompt from S3 takes time.
- *Fix:* Use a CDN (Content Delivery Network) or cache active prompts in Redis.
- **Rate Limits:**

*Risk:* OpenAI blocks us because we send too many requests.
- *Fix:* Use the **Queue**. If we hit the limit, hold the jobs in the queue and retry them later.

## Additional Design Details

### API Design

We use **Cursor-based Pagination**.

- Instead of saying "Page 1, Page 2," we say "Give me 50 items starting after this specific ID."
- This is faster for databases and works better when data is constantly being added.

### UI Layout

- **Left:** Library/History sidebar.
- **Center:** The big Editor.
- **Right:** Configuration (Temperature, Model selection).
- **Bottom:** The output window (streaming text).

### Security

- **Prompt Injection:** Warn users if a shared prompt looks dangerous.
- **Data Privacy:** Allow users to delete their data fully (GDPR).
- **Access:** Use JWT tokens for login.

## Comparing Different Approaches

**Version Control:**

- *Option A (Save Everything):* Simple code, but storage costs are huge.
- *Option B (Snapshots + Diffs):* Complex code, but saves massive amounts of storage. **We chose B.**
**Streaming:**

- *Option A (WebSockets):* Fast, two-way communication. Harder to scale.
- *Option B (SSE - Server Sent Events):* Easier, but only one-way (Server to Client).
- *Decision:* **WebSockets** are better here because we need to send "Stop Generation" signals and other commands while streaming.

## Interview Advice

**How to use this guide:**

- Do **not** try to memorize every word.
- In a 45-minute interview, pick **2 or 3 deep topics** (like Version Control or Handling Large Files) and explain them well.
**Key Points to Remember:**

- **Not a Chatbot:** Emphasize that each run is standalone.
- **Storage vs. Execution:** 10MB is fine to store, but impossible to run on current models. You must explain this distinction.
- **Trade-offs:** Always say "We could do X or Y. I chose X because..." (e.g., "I chose Diffs to save storage, even though it makes reading slightly slower").

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100017*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q2-prompt-playground)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
