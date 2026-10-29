---
id: drustz-e3dfab09c0040edd6d
section: anthropic
order: 20
level: A
title: SD Q3 Model Distribution
quick: locally-saved-topic-editorial · SD Q3 Model Distribution
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
      https://www.1point3acres.com/interview/problems/company/anthropic/sd-q3-model-distribution
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Distributed Model Deployment System Design

## The Challenge

You need to design a system to download a **large ML model** (500GB) and send it to **all GPU workers** in a data center. The system must work quickly, handle limited internet speed, and keep working even if computers fail.

### The Rules & Limits

- **Model size**: 500GB (Very large file).
- **Number of workers**: 100 to 1000 computers with GPUs.
- **External bandwidth**: 10 Gbps (Speed to download from the internet/cloud).
- **Internal bandwidth**: 10 Gbps "full-duplex" per worker.

*Note:* "Full-duplex" means a worker can upload at 10 Gbps and download at 10 Gbps at the exact same time.
- **Goal**: Make the total time to deploy the model to EVERY worker as short as possible.
- **Reliability**: The system must not stop if a worker crashes.

### Follow-up Questions to Expect

- **Strategy**: Why is a pipeline better than a tree or doing it one by one? Show the math.
- **Bandwidth**: How do we use 100% of the network speed?
- **Chunking**: Why split the file into small pieces? How big should pieces be?
- **Failures**: What if a worker in the middle of the chain breaks?
- **Scaling**: Does it still work with 10,000 workers?

## Proposed Solution

**⚠️ Note**: This is a sample guide. Try to solve the problem yourself first. Use this to check your work.

## Step 1: Understanding the Requirements

First, we need to ask questions to understand exactly what we are building.

### Questions to Ask

**Features:**

- **Updates:** Do we send only new parts of the file? (Assume yes).
- **Versions:** Do we need to keep old versions?
- **Rollback:** Can we quickly switch back to an old model?
**Scope:**

- **Tasks:** Are we just moving files, or loading them into GPU memory too?
- **Locations:** Is this for one data center or many?
**Performance:**

- **Time Limit:** How fast must it be? (Target: ~8 minutes for 100 workers).
- **Frequency:** How often do we do this? (Daily).
- **Failures:** How often do workers break? (1-5% of the time).

### Summary of Needs

**1. Moving the Data**

- Download 500GB from cloud storage (S3/GCS).
- Send to 100-1000 workers.
- Split files into "chunks" (pieces) to send them faster.
**2. Managing the Process**

- A central "Coordinator" decides the order of workers.
- Track which worker has which chunk.
- Handle new workers joining or leaving.
**3. Handling Errors**

- Check if workers are alive using a "heartbeat".
- If a worker fails, route data around them.
- Retry if a file piece is corrupted.
**4. Data Safety**

- Use "Checksums" (SHA256) to make sure files are not broken.
- Verify the whole file at the end.
**5. Monitoring**

- Show a progress bar for the deployment.
- Track network speed and errors.

## Step 2: Doing the Math

We need to estimate how long different methods will take. This proves why our choice is best.

**Assumptions:**

- **Model:** 500GB.
- **Network:** 10 Gbps.
- **Chunk Size:** 1GB.

### Option 1: Sequential (One by One) - The Bad Way

Every worker downloads the file directly from the internet at the same time. The 10 Gbps internet connection is shared by everyone.

- **Speed per worker:** 10 Gbps / 100 workers = 0.1 Gbps.
- **Time:** 500GB / 0.1 Gbps = **~11 hours**.
**Result:** Too slow. The internet connection is the bottleneck.

### Option 2: Binary Tree - The Okay Way

Worker A downloads it. Worker A sends it to B and C. B sends to D and E, etc.
At every level, the parent splits its upload speed between two children.

- **Root download:** 400 seconds.
- **Each level after:** 800 seconds (because speed is split).
- **Total for 100 workers:** **~100 minutes**.
**Result:** Better, but splitting bandwidth slows it down.

### Option 3: Pipeline (Chain) - The Best Way

Worker 1 gets a small piece (Chunk 1). It immediately sends Chunk 1 to Worker 2, while downloading Chunk 2.
This creates a chain. All workers upload and download constantly.

- **Download Phase:** Time to pull 500GB into the first worker = 400 seconds.
- **Propagation Phase:** Time for the last chunk to hop from Worker 1 to Worker 100.

Time per hop: 0.8 seconds.
- 99 hops: ~80 seconds.
- **Total Time:** 400s + 80s = **~8 minutes**.
**Result:** This is the winner. It is very fast regardless of how many workers you add.

## Step 3: API Design

We define how the parts of the system talk to each other.

### Coordinator API

The central brain of the system.

```text
// Start a new deployment
interface DeploymentRequest {
  modelId: string;
  sourceUrl: string;       // Where the file lives (S3)
  targetWorkers: string[]; // List of worker IDs
}

// Check how it is going
createDeployment(request: DeploymentRequest): Promise<DeploymentResponse>
getDeploymentStatus(deploymentId: string): Promise<DeploymentStatus>
```



### Worker API

The computers receiving the model.

```text
// Tell Coordinator "I am here"
registerWorker(info: WorkerInfo): Promise<{ registered: boolean }>

// Tell Coordinator "I am still alive" (Heartbeat)
interface HeartbeatRequest {
  workerId: string;
  status: 'idle' | 'downloading' | 'complete' | 'failed';
  chunksReceived: number[]; // Which pieces do I have?
}

sendHeartbeat(request: HeartbeatRequest): Promise<{ continue: boolean }>

// Ask another worker for a file piece
requestChunk(request: ChunkRequest): Promise<ChunkResponse>
```



### Manifest File

This is the "map" of the file. It lists all the pieces (chunks).

```typescript
interface Manifest {
  modelId: string;
  totalSize: number;
  chunkSize: number;
  numChunks: number;
  // List of all pieces and their verification codes
  chunks: ChunkInfo[];
  globalChecksum: string; // Verification for the whole file
}
```



## Step 4: Data Structure Design

How we store information in the database.

**1. Manifest (The Map)**
Shared with all workers so they know what to download.

```go
type Manifest struct {
    ModelID        string
    NumChunks      int
    Chunks         []ChunkInfo
    GlobalChecksum string     // SHA256 hash
}
```



**2. Worker State (The Status)**
Stored in the Coordinator's memory (or Redis/etcd).

```go
type WorkerState struct {
    WorkerID           string
    Status             WorkerStatus
    ChunksReceived     []int      // List of chunk IDs owned
    DownstreamWorker   string     // Who do I send data to?
    UpstreamWorker     string     // Who do I get data from?
}
```



**Storage Choices:**

- **etcd:** Use this for the Coordinator state. It handles failures well.
- **Local Disk:** Workers save the file chunks here.

## Step 5: System Architecture

### The Diagram

Imagine a long line of people passing buckets of water.

- **External Storage (S3):** The water source.
- **Coordinator:** The person shouting directions.
- **Workers (W1, W2, ... W100):** The people passing buckets.
**Flow:**
`S3` --> `W1` --> `W2` --> `W3` ... --> `W100`

### How It Works (The Phases)

**Phase 1: Setup**
The Coordinator chops the file list into 500 pieces (1GB each). It tells the workers: "Get ready. W1 gives to W2, W2 gives to W3..."

**Phase 2: Seeding**
Worker 1 (W1) downloads "Chunk 0" from S3.
As soon as W1 has Chunk 0, it sends it to W2.
At the same time, W1 downloads Chunk 1 from S3.

**Phase 3: The Pipeline**
Everyone is busy.

- W1 is downloading from S3 and sending to W2.
- W2 is receiving from W1 and sending to W3.
- This happens for all 500 chunks.
**Phase 4: Finish**
Workers verify the files using checksums. They tell the Coordinator "Success".

## Step 6: Deep Dive

### 1. The Pipeline Logic

This code shows how workers do two things at once: receive and send.

```python
# Coordinator logic
def create_deployment(model_id, workers):
    # 1. Create file list and checksums
    manifest = generate_manifest(model_id)

    # 2. Arrange workers in a line (Topology)
    # Put workers in the same rack next to each other
    topology = assign_pipeline_topology(workers)
    # Result: [W1, W2, W3, ..., W100]

    # 3. Tell everyone what to do
    distribute_manifest(workers, manifest)
    start_download(topology[0])  # Start W1


# Worker Logic (Middle Worker)
def middle_worker():
    manifest = receive_manifest()

    # Run two threads at the same time

    # Thread 1: Receive Data
    Thread(target=receive_loop).start()

    # Thread 2: Send Data
    Thread(target=send_loop).start()


def receive_loop():
    for chunk_id in range(500):
        data = receive_from_upstream(chunk_id)
        if check_hash(data):
            save_to_disk(data)
        else:
            ask_for_retry(chunk_id)


def send_loop():
    for chunk_id in range(500):
        # Wait until I have the chunk
        while not have_chunk_on_disk(chunk_id):
            wait()

        data = read_from_disk(chunk_id)
        send_to_downstream(chunk_id, data)
```



### 2. Choosing Chunk Size

How big should the pieces be?

- **Too Small (10MB):** Too much asking/answering overhead. Slow.
- **Too Big (50GB):** The next worker waits too long to start. Pipeline stalls.
- **Just Right (1GB):** Takes about 0.8 seconds to transfer. Good balance.

### 3. Handling Failures

What happens if Worker 3 (W3) crashes?

**Before:** W1 → W2 → **W3** → W4 → W5

- **Detection:** The Coordinator notices W3 stopped sending "heartbeats".
- **Fix:** The Coordinator tells W2 to skip W3 and talk directly to W4.
- **Result:** W1 → W2 → W4 → W5.
- **Recovery:** W4 asks W2 for any pieces it missed.

### 4. Rack Awareness

Data moves faster between computers in the same rack (cabinet).

- **Bad Order:** Rack A -> Rack B -> Rack A -> Rack B. (Lots of jumping).
- **Good Order:** Rack A (all) -> Rack B (all). (Only one jump).
We sort the list of workers by their Rack ID to keep data local.

## Step 7: Fixing Bottlenecks

### 1. External Bandwidth

**Problem:** The download from S3 is only 10 Gbps.
**Solution:** Only the first worker (W1) downloads from S3. Everyone else gets data from W1 via the local network. This saves the internet connection.

### 2. Disk Speed

**Problem:** Writing 500GB quickly can be too fast for hard drives.
**Solution:** Use NVMe SSDs (very fast disks). Write data in parallel streams.

### 3. Coordinator Overload

**Problem:** If 10,000 workers send updates constantly, the Coordinator will crash.
**Solution:**

- Workers only send updates every 10 chunks (batching).
- Use multiple Coordinators (one leader, several backups).

### 4. Corruption

**Problem:** Bits get flipped during transfer. The file is broken.
**Solution:**

- Calculate the SHA256 Hash of every chunk.
- If the hash doesn't match, ask for that chunk again.

## Interview Tips

### What Matters Most

- **Do the Math:** You must compare the Sequential vs. Pipeline times. Prove why Pipeline is best.
- **Identify the Limit:** The 10 Gbps internet link is the main limit (bottleneck).
- **Handle Failures:** A system that crashes when one worker fails is a bad system. Explain how you fix it.
- **Network Topology:** Mention "Rack Awareness." It shows you understand real data centers.

### Common Mistakes

- Forgetting to calculate time.
- Not checking for data corruption (Checksums).
- Making the system too complicated (Keep it simple: a line of workers).
- Ignoring that cross-rack communication is slower.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100001*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q3-model-distribution)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
