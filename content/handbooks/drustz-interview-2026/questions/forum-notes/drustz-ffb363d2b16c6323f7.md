---
id: drustz-ffb363d2b16c6323f7
section: forum-notes
order: 48
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Solution: JavaScript Implementation'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Solution: JavaScript Implementation'
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
## Solution: JavaScript Implementation

Below is a full JavaScript solution. It handles tasks concurrently and cleans up URLs to prevent duplicates.

### ThreadPool Class

```javascript
class ThreadPool {
  constructor(maxConcurrency) {
    this.maxConcurrency = maxConcurrency;
    this.queue = [];
    this.runningTasks = 0;
    this.waitForFinishPromise = null;
    this.waitForFinishResolve = null;
  }

  // Add a task to the queue and start processing
  execute(task) {
    return new Promise((resolve, reject) => {
      this.queue.push({
        task,
        resolve,
        reject,
      });
      this._processQueue();
    });
  }

  _processQueue() {
    // Stop if we reached the max number of running tasks
    if (this.runningTasks >= this.maxConcurrency) {
      return;
    }

    // If queue is empty, check if all work is fully done
    if (this.queue.length === 0) {
      if (this.runningTasks === 0) {
        this.waitForFinishResolve && this.waitForFinishResolve();
        this.waitForFinishPromise = null;
        this.waitForFinishResolve = null;
      }
      return;
    }

    // Run the next task from the queue
    const { task, resolve, reject } = this.queue.shift();
    this.runningTasks++;
    Promise.resolve()
      .then(task)
      .then(resolve, reject)
      .finally(() => {
        this.runningTasks--;
        this._processQueue();
      });
  }

  // Returns a promise that finishes when all tasks are done
  waitForFinish() {
    if (this.runningTasks === 0 && this.queue.length === 0) {
      return Promise.resolve();
    }

    if (!this.waitForFinishPromise) {
      this.waitForFinishPromise = new Promise((resolve) => {
        this.waitForFinishResolve = resolve;
      });
    }
    return this.waitForFinishPromise;
  }
}
```



### URL Helper Function

```javascript
function getProcessedUrlObject(url) {
  const newUrl = new URL(url);
  // Remove the hash (#) part so http://example.com/page#1
  // and http://example.com/page#2 are seen as the same URL
  newUrl.hash = "";
  return newUrl;
}
```



### Main Crawler Logic

```javascript
async function crawl(startUrl, htmlParser, maxConcurrency = 10) {
  const processedStartUrlObject = getProcessedUrlObject(startUrl);
  const startHostName = processedStartUrlObject.hostname;

  const result = [processedStartUrlObject.toString()];
  const visited = new Set([processedStartUrlObject.toString()]);
  const pool = new ThreadPool(maxConcurrency);

  const crawlUrl = async (url) => {
    try {
      const nextUrls = await htmlParser.getUrls(url);
      for (const nextUrl of nextUrls) {
        const nextUrlProcessedObject = getProcessedUrlObject(nextUrl);
        const nextUrlProcessedString = nextUrlProcessedObject.toString();

        // Only crawl if hostname matches and we haven't visited it yet
        if (
          nextUrlProcessedObject.hostname === startHostName &&
          !visited.has(nextUrlProcessedString)
        ) {
          visited.add(nextUrlProcessedString);
          result.push(nextUrlProcessedString);
          // Add to the pool (fire and forget)
          pool
            .execute(() => crawlUrl(nextUrl))
            .catch((err) => {
              console.error(`Error crawling ${nextUrl}:`, err);
            });
        }
      }
    } catch (error) {
      console.error(`Error fetching URLs from ${url}:`, error);
    }
  };

  // Start crawling from the first URL
  await pool.execute(() => crawlUrl(startUrl));
  // Wait for everything to finish
  await pool.waitForFinish();

  return result;
}
```



### How to Run the Code

```javascript
// Example with a fake HtmlParser
class HtmlParser {
  constructor(urls) {
    this.urls = urls;
  }

  async getUrls(url) {
    // Fake a network delay
    await new Promise((resolve) => setTimeout(resolve, Math.random() * 15));
    return this.urls[url] || [];
  }
}

const urls = {
  "http://news.yahoo.com": [
    "http://news.yahoo.com/news/topics/",
    "http://news.yahoo.com/news",
  ],
  "http://news.yahoo.com/news/topics/": [
    "http://news.yahoo.com/news",
    "http://news.yahoo.com/news/sports",
  ],
  "http://news.yahoo.com/news": ["http://news.google.com"],
  "http://news.yahoo.com/news/sports": [],
};

const parser = new HtmlParser(urls);
const result = await crawl("http://news.yahoo.com", parser, 2);
console.log("Crawled URLs:", result);
// Output should be yahoo.com URLs only (no google.com)
```



### Why We Built It This Way

- **ThreadPool**: We made a custom queue. This lets us limit how many downloads run at once so we don't overwhelm the system.
- **URL Normalization**: We remove the `#` part of URLs. This ensures we don't treat the same page as two different links.
- **Thread Safety**: We use a `Set` to track visited pages. Because JavaScript is single-threaded (event loop), we don't have race conditions here.
- **Error Handling**: If one link fails, we log the error, but the crawler keeps going.
- **Concurrency Control**: We limit the number of parallel requests to be polite to the server.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
