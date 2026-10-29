---
id: drustz-4b7815b05f1bcbdda8
section: forum-notes
order: 113
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 6: Deep Dive'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 6: Deep Dive'
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
