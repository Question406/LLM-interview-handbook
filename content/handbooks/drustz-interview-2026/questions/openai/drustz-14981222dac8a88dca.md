---
id: drustz-14981222dac8a88dca
section: openai
order: 14
level: A
title: Multi Tenant CI CD Workflow
quick: locally-saved-topic-editorial · Multi Tenant CI CD Workflow
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/company/openai/multi-tenant-ci-cd-workflow
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Multi-Tenant CI/CD Workflow System

## The Challenge

Design a CI/CD system that is scalable and can handle crashes. This system serves many different customers (multi-tenant). It must run workflows defined by users whenever they push code to Git.

The system needs to:

- Run the workflows.
- Schedule jobs.
- Show status updates in real-time.
- Ensure every job runs **exactly once**.
**Video Solution**: For a full explanation of the architecture, watch [this video solution](https://www.youtube.com/watch?v=y32PywFi7Ek).

## What Candidates Experienced

Here are stories from engineers who faced this specific interview question:

### Story 1: The "Exactly-Once" Focus

"The interviewer really focused on 'exactly-once execution.' They told me to treat every job as a single task. I did not need to make complex workflows at first. They also asked how I would handle multiple customers (multi-tenancy)."

"This interview is mostly about designing a job scheduler. I passed this round."

**Key Point**: The main test is ensuring a job runs one time only. Keep the workflow simple (linear).

### Story 2: Stateless Design with CDC

"The problem asks for a simple list of steps, not a complex graph (DAG). You need to start Step 2 only after Step 1 finishes.

My approach:

- Create a database entry for every step at the start. Mark them all 'PENDING'.
- Put only the **first** step into the worker queue.
- A worker runs the step and updates the database status to 'COMPLETED'.
- Use CDC (Change Data Capture) to notify the scheduler that the database changed.
- The scheduler sees the change, finds the next step, and puts it in the queue.
This makes the scheduler 'stateless.' You can add more schedulers easily."

**Key Strategy**:

- Create all steps in the DB first.
- Only queue the first step.
- Workers update the DB when done.
- The scheduler watches the DB (using CDC) to queue the next step.
- This keeps the scheduler **stateless**.

### Story 3: Using Kubernetes and Docker

"Design a job scheduler using technologies like Kubernetes (K8s) and Docker. Explain how you would fit these pieces together."

**Tech Focus**: You must mention Kubernetes and Docker.

### Story 4: Connecting the Front-End

"Design a workflow system triggered by a Git push. An internal API gives you the Repository ID. You must read the config file from the Git repo. Then, schedule the jobs listed in that file. Also, design a UI so users can see the progress."

**Extra Requirement**: You need a Front-End UI to show live progress.

### Story 5: Handling Crashes

"The main focus was: How do you make sure a job runs exactly once, even if parts of the system crash or fail?"

**Core Focus**: Fault tolerance (handling crashes) and "exactly-once" logic.

### Common Patterns

Many candidates saw these same requirements:

- **Multi-tenant**: Many users on one system.
- **Git Push**: This starts the process.
- **API Payload**: You get a Repository ID and Commit Hash.
- **YAML Config**: The steps are defined in a file in the repo.
- **Linear Jobs**: Step 1 -> Step 2 -> Step 3.
- **Real-time Views**: Users watch logs as they happen.
- **Exactly-Once**: The most important rule.
- **Stateless**: Necessary for scaling.

## How to Prepare

Use this guide to study. These are not exact answers, but the key topics you need to understand.

## System Needs

### Functional Requirements (What it does)

- **Triggering**

System gets an API call on a Git push.
- API sends Repository ID and Commit Hash.
- System reads a YAML file from the repo to know what to do.
- **Workflow Shape**

Workflows are a **straight line** of jobs (Linear).
- Job 2 cannot start until Job 1 finishes.
- Jobs run inside Docker containers on Kubernetes.
- **Running Jobs**

Use Docker containers for isolation.
- Run many workflows at the same time (parallel).
- Save (cache) Docker images so they load faster.
- **Monitoring**

Show logs and status to the user immediately.
- Show progress on a UI.

### Non-Functional Requirements (How it performs)

- **Exactly-Once Execution**: Critical. Jobs must run once. No more, no less.
- **Fault Tolerance**: If a worker crashes, the system must recover.
- **Scalability**: The system should handle more load by adding more servers (Horizontal Scaling).
- **Multi-Tenancy**: Keep data separate for different customers.

## Key Topics to Study

**Note**: If the interviewer says "keep workflows simple," listen to them. Do not build a complex graph (DAG) if they ask for a line.

### 1. Exactly-Once Execution

**This is the most important topic.** Be ready to answer:

- How do you stop a job from running twice if a worker crashes?
- How do you make sure a job isn't lost if a worker dies?
- What if two workers grab the same task from the queue?
**Key ideas:**

- **Atomic DB updates**: `UPDATE jobs SET status='IN_PROGRESS' WHERE status='PENDING'`
- **Idempotency**: Making sure repeating an action doesn't change the result.
- **Queue visibility**: Hiding a message while a worker is busy.

### 2. Starting the Next Job

**How do you trigger Job 2 after Job 1?**

**Option A: Change Data Capture (CDC)**

- The DB sends a signal when a job status changes.
- The scheduler hears this signal and queues the next job.
- Tools: PostgreSQL NOTIFY, DynamoDB Streams.
**Option B: Polling**

- The scheduler keeps asking the DB, "Is Job 1 done?"
- This is simpler but slower.
**Best approach from interviews**: Create all job rows as PENDING immediately. Only queue the first one. When it finishes, use the `step_index` to find the next one and queue it.

### 3. Stateless Architecture

**How do you keep servers "stateless"?**

- Do not store job info in the server's memory (RAM).
- Store everything in the Database.
- If a scheduler crashes, a new one can take over immediately because the data is in the DB.
- Workers just pull jobs, do the work, update the DB, and leave.
**Why?** It makes scaling easy. Just add more servers.

### 4. Handling Failures

**What if things break?**

- **Worker crashes**: The queue "visibility timeout" expires. The message reappears. Another worker picks it up.
- **Database down**: Wait and try again (Exponential Backoff).
- **Job takes too long**: Set a strict time limit (Timeout).
- **Docker fails**: Check the exit code. Decide if you should retry.
**Retries**:

- Try 3 times.
- Wait longer between each try.
- If it fails 3 times, move it to a "Dead Letter Queue" for inspection.

### 5. Multi-Tenancy (Many Users)

**How do you keep users separate?**

- **Quotas**: Limit how much CPU/RAM one user can use (Kubernetes Namespaces).
- **Security**: Don't let User A access User B's secrets.
- **Fairness**: Don't let one big user hog all the workers.

### 6. Docker Performance

**How do you make Docker start faster?**

- **Caching**: Kubernetes nodes keep images they have already downloaded.
- **Pre-warming**: Download common images before you need them.

### 7. Real-Time UI

**How does the user see live logs?**

- **WebSockets**: Keeps a connection open to send data back and forth.
- **Worker logic**: Worker writes logs to storage. System pushes these logs to the WebSocket.

## Interview Tips

### What the Interviewer Wants

- **Focus on Exactly-Once**

They will ask about this a lot.
- Explain how you handle crashes without running the job twice.
- Know the difference between "at-least-once" and "exactly-once".
- **Keep it Simple**

If they say "linear sequence," do not build a DAG.
- Solve the basic problem first.
- **Be Stateless**

State lives in the DB, not in memory.
- This is how you scale.
- **Database Design**

Know your tables (Workflows, Jobs).
- Know your indexes.
- Explain how you lock rows to prevent errors.

### Mistakes to Avoid

- **Using RAM for State**: Never say "I'll store the running jobs in a HashMap."
- **Ignoring Race Conditions**: What if two workers try to update the same row? (Use `WHERE status='PENDING'`).
- **Forgetting Timeouts**: If a worker dies silently, the job stays "IN_PROGRESS" forever unless you have a timeout.
- **Vague Answers**: Don't just say "I'll use a transaction." Write the SQL query logic on the board.
- **Ignoring Multi-Tenancy**: Remember you have many customers. You need to isolate them.

### Suggested Flow

**Start Simple, then Add Detail:**

- **Step 1**: Basic flow. Linear jobs. Single user. "Exactly-once" logic.
- **Step 2**: Add Fault Tolerance. What if it crashes? Add retries.
- **Step 3**: Scaling. Multi-tenancy. Docker caching.
- **Step 4**: UI. Live logs via WebSockets.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100046*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/multi-tenant-ci-cd-workflow)
- [相关来源](https://www.1point3acres.com/bbs/thread-1174549-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
