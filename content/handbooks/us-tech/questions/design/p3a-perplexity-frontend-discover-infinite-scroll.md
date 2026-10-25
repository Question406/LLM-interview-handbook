---
id: p3a-perplexity-frontend-discover-infinite-scroll
section: design
order: 603
level: A
title: "Perplexity：Discover 前端：分页、无限滚动与布局"
quick: "把分页逻辑放在独立状态模型里，同一时刻复用一个在途请求，成功后再推进 cursor。按稳定 id 去重，并给 reset 加版本号，迟到的旧响应就不会覆盖新列表。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · frontend-discover-infinite-scroll"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/frontend-discover-infinite-scroll
    type: secondary
---

## 题目描述

实现可加载下一页的 Discover feed 状态模型及 React 列表，处理分页、去重、重试和请求失效等行为。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `fetchPage(cursor, { signal })`：返回 `{ items: [{ id, title }], nextCursor: string | null }`，第一页的 cursor 是 `''`，`nextCursor` 为 `null` 表示没有更多。
- `FeedModel(fetchPage)`：`next()` 加载下一页，同一时刻最多一个在途请求，重复调用返回同一个 Promise。结果按 id 去重，重复时保留最早出现的那条。失败时保留 cursor，以便重试同一页；`nextCursor` 为 `null` 后 `done` 为真，`next()` 不再发请求。
- `reset()` 让所有旧请求的响应失效，并恢复初始状态；`dispose()` 之后 `next()` 返回被拒绝的 Promise。
- 响应格式不对，或者 `nextCursor` 等于本次请求的 cursor（不会前进），都视为错误。
- `Discover({ fetchPage })`：渲染列表、错误提示和一个可用键盘操作的 Load more 按钮。按钮进入视口时通过 IntersectionObserver 自动加载；组件卸载时断开观察并取消请求。
- 最多 100 页，每页最多 100 条。纯状态模型和服务端渲染测试可以直接用 Node 执行，浏览器里的组件需要通过项目已有的打包器运行。

### 输入输出示例

```text
fetchPage("") -> {items: [{id:"a", title:"A"}, {id:"b", title:"B"}], nextCursor:"p2"}
fetchPage("p2") -> {items: [{id:"b", title:"B新版"}, {id:"c", title:"C"}], nextCursor:null}
连续两次 await model.next() 后：
items -> [{id:"a", title:"A"}, {id:"b", title:"B"}, {id:"c", title:"C"}]
done -> true；之后调用 next() 不再发起请求。
```

## 解题思路与参考答案

## 题目

用给定的数据和 fetch helper，实现一个类似 Discover 页面的无限滚动信息流（原题要求 TypeScript）：滚到底部自动加载下一页，加载中、失败和全部加载完都要有对应的状态。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原始面试代码；练习用 JavaScript 和 React 写成，环境是 Node 22 + React 19。

## 思路

我会把分页状态从组件里抽出来：模型管理首次加载、追加下一页、失败和全部加载完，UI 只订阅并渲染。这样状态变化能直接在 Node 里测试，页面也更容易处理重试和刷新。

比如 IntersectionObserver 连续触发，用户又点了按钮，两个调用应该复用同一个在途请求，避免同一页加载两次。请求成功再推进 cursor，失败则停在原位置，下一次仍然重试这一页。

列表用后端的稳定 id 做 key，并按 id 去重。加载过程中可能插入新内容，让下一页重复出现旧条目。刷新或切换数据源，也就是 `reset` 时，版本号加一；旧响应回来对不上版本，就丢弃，避免覆盖新状态。

页面还要保留键盘可操作的按钮、图片占位和固定的容器高度，减少内容加载后的跳动。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `fetchPage(cursor, { signal })`：返回 `{ items: [{ id, title }], nextCursor: string | null }`，第一页的 cursor 是 `''`，`nextCursor` 为 `null` 表示没有更多。
- `FeedModel(fetchPage)`：`next()` 加载下一页，同一时刻最多一个在途请求，重复调用返回同一个 Promise。结果按 id 去重，重复时保留最早出现的那条。失败时保留 cursor，以便重试同一页；`nextCursor` 为 `null` 后 `done` 为真，`next()` 不再发请求。
- `reset()` 让所有旧请求的响应失效，并恢复初始状态；`dispose()` 之后 `next()` 返回被拒绝的 Promise。
- 响应格式不对，或者 `nextCursor` 等于本次请求的 cursor（不会前进），都视为错误。
- `Discover({ fetchPage })`：渲染列表、错误提示和一个可用键盘操作的 Load more 按钮。按钮进入视口时通过 IntersectionObserver 自动加载；组件卸载时断开观察并取消请求。
- 最多 100 页，每页最多 100 条。纯状态模型和服务端渲染测试可以直接用 Node 执行，浏览器里的组件需要通过项目已有的打包器运行。

### 输入输出示例

```text
第一页 [a, b]，第二页 [b, c]          -> 列表 [a, b, c]
第二页第一次请求失败                   -> cursor 停在第二页，error 有内容
再次 next()                            -> 重新请求第二页，而不是跳到第三页
```

### 解题思路与正确性

`next()` 在同一个同步调用里把在途请求存进 `this.pending`，所以紧接着的第二次 `next()` 一定能看到它并直接复用，不会发出第二个请求。请求结束后（无论成功还是失败）才清空 `pending`。

cursor 只在成功分支里更新。失败时只写入错误信息，cursor 保持不变，下一次 `next()` 自然重试同一页。

`reset` 和 `dispose` 都会把版本号加一，并中止当前请求。旧请求回来时发现版本号对不上，既不写入数据，也不改 `loading`，不会把新状态覆盖掉。按 id 去重时，已有条目保持原来的内容和位置，新页面里重复的条目被跳过。

组件在 effect 里创建模型、在 cleanup 里销毁它，并断开 IntersectionObserver。React StrictMode 下 effect 会挂载两次，每次拿到的都是新模型，不会复用已经销毁的实例。

### 完整参考实现（JavaScript / React）

```javascript
import React, { useEffect, useRef, useState } from 'react';

const INITIAL_STATE = { items: [], cursor: '', done: false, loading: false, error: null };

function isValidPage(page) {
  const itemsOk = Array.isArray(page?.items)
    && page.items.every((item) => typeof item.id === 'string' && typeof item.title === 'string');
  const cursorOk = page?.nextCursor === null || typeof page?.nextCursor === 'string';
  return itemsOk && cursorOk;
}

// 与 UI 无关的分页状态机：同一时刻最多一个在途请求，成功后才推进 cursor。
export class FeedModel {
  constructor(fetchPage) {
    this.fetchPage = fetchPage;
    this.listeners = new Set();
    this.version = 0; // reset / dispose 时加一；旧请求回来发现版本不同就丢弃
    this.closed = false;
    this.pending = null; // 在途请求的 Promise，重复调用 next() 共享它
    this.controller = null;
    this.state = INITIAL_STATE;
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  publish(patch) {
    this.state = { ...this.state, ...patch };
    for (const listener of this.listeners) {
      listener(this.state);
    }
  }

  next() {
    if (this.closed) {
      return Promise.reject(new Error('FeedModel is disposed'));
    }
    if (this.state.done) {
      return Promise.resolve();
    }
    if (this.pending) {
      return this.pending;
    }
    // pending 在同一个同步调用里建立，紧接着的 next() 一定能看到它
    this.pending = this.loadPage(this.version, this.state.cursor);
    return this.pending;
  }

  async loadPage(version, cursor) {
    const controller = new AbortController();
    this.controller = controller;
    const isCurrent = () => !this.closed && version === this.version;
    this.publish({ loading: true, error: null });
    try {
      // 先让出一次微任务，保证 this.pending 已经赋值，再调用可能同步抛错的 fetchPage
      await Promise.resolve();
      const page = await this.fetchPage(cursor, { signal: controller.signal });
      if (!isValidPage(page)) {
        throw new TypeError('page must be { items: [{ id, title }], nextCursor: string | null }');
      }
      if (page.nextCursor === cursor) {
        throw new Error('cursor did not advance');
      }
      if (!isCurrent()) {
        return;
      }
      this.publish({
        items: appendUnique(this.state.items, page.items),
        cursor: page.nextCursor,
        done: page.nextCursor === null,
      });
    } catch (error) {
      // 失败时 cursor 不变，下一次 next() 会重试同一页
      if (isCurrent()) {
        const message = error.name === 'AbortError' ? null : String(error.message);
        this.publish({ error: message });
      }
    } finally {
      if (isCurrent()) {
        this.pending = null;
        this.publish({ loading: false });
      }
    }
  }

  reset() {
    this.version++;
    this.controller?.abort();
    this.pending = null;
    this.publish(INITIAL_STATE);
  }

  dispose() {
    this.closed = true;
    this.version++;
    this.controller?.abort();
    this.listeners.clear();
  }
}

// 按 id 去重追加：已出现过的 id 保留最早的那一条和它的位置
function appendUnique(existing, incoming) {
  const seen = new Set(existing.map((item) => item.id));
  const items = [...existing];
  for (const item of incoming) {
    if (!seen.has(item.id)) {
      seen.add(item.id);
      items.push(item);
    }
  }
  return items;
}

// 列表 + 「Load more」按钮。按钮进入视口时自动加载，也可以用键盘或鼠标点击。
export function Discover({ fetchPage }) {
  const buttonRef = useRef(null);
  const modelRef = useRef(null);
  const [state, setState] = useState(INITIAL_STATE);

  useEffect(() => {
    const model = new FeedModel(fetchPage);
    modelRef.current = model;
    const unsubscribe = model.subscribe(setState);
    model.next();

    let observer = null;
    if (typeof IntersectionObserver !== 'undefined') {
      observer = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          model.next();
        }
      });
      if (buttonRef.current) {
        observer.observe(buttonRef.current);
      }
    }

    // cleanup 同时断开观察、退订并取消请求，StrictMode 重复挂载也不会泄漏
    return () => {
      observer?.disconnect();
      unsubscribe();
      model.dispose();
      modelRef.current = null;
    };
  }, [fetchPage]);

  let label = 'Load more';
  if (state.done) {
    label = 'All loaded';
  } else if (state.loading) {
    label = 'Loading…';
  }
  const items = state.items.map((item) => React.createElement('li', { key: item.id }, item.title));

  return React.createElement(
    'main',
    null,
    React.createElement('ul', null, items),
    React.createElement('p', { 'aria-live': 'polite' }, state.error || ''),
    React.createElement(
      'button',
      {
        ref: buttonRef,
        onClick: () => modelRef.current?.next(),
        disabled: state.loading || state.done,
      },
      label,
    ),
  );
}
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.js`，运行 `node solution.js`。

例如，测试中的 `assert.equal(first, second);` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```javascript
import assert from 'node:assert/strict';
import { renderToString } from 'react-dom/server';

// 第一页 [a]；第二页第一次失败，重试后返回 [a(重复), b] 并结束
let calls = 0;
let failOnce = true;
const model = new FeedModel(async (cursor) => {
  calls++;
  if (cursor === '') {
    return { items: [{ id: 'a', title: 'A' }], nextCursor: '2' };
  }
  if (failOnce) {
    failOnce = false;
    throw new Error('retry');
  }
  return { items: [{ id: 'a', title: 'A2' }, { id: 'b', title: 'B' }], nextCursor: null };
});

// 同时调用两次 next() 共享同一个请求
const first = model.next();
const second = model.next();
assert.equal(first, second);
await first;
assert.equal(calls, 1);

// 失败时 cursor 停在第二页，并展示错误
await model.next();
assert.equal(model.state.cursor, '2');
assert.match(model.state.error, /retry/);

// 重试成功：按 id 去重，保留最早的 a
await model.next();
assert.deepEqual(model.state.items.map((item) => item.id), ['a', 'b']);
assert.equal(model.state.items[0].title, 'A');
assert.equal(model.state.done, true);

// 加载完后 next() 不再发请求；dispose 后 next() 被拒绝
await model.next();
assert.equal(calls, 3);
model.dispose();
await assert.rejects(model.next());

// reset 之后，旧请求迟到的响应被丢弃
let resolveStale;
const stale = new FeedModel(() => new Promise((resolve) => { resolveStale = resolve; }));
const stalePromise = stale.next();
await Promise.resolve();
stale.reset();
resolveStale({ items: [{ id: 'x', title: 'X' }], nextCursor: null });
await stalePromise;
assert.deepEqual(stale.state.items, []);
stale.dispose();

// cursor 没有前进视为错误，避免无限重复请求同一页
const stuck = new FeedModel(async () => ({ items: [], nextCursor: '' }));
await stuck.next();
assert.match(stuck.state.error, /did not advance/);

// 服务端渲染：首屏是空列表和可点击的 Load more 按钮
const html = renderToString(React.createElement(Discover, { fetchPage: async () => ({ items: [], nextCursor: null }) }));
assert.match(html, /<button[^>]*>Load more<\/button>/);
```

### 复杂度与追问

设已加载 N 条。每追加一页都会复制已有数组并重建去重用的 Set，单次是 O(N)，累计下来最坏 $O(N^2)$。这份参考实现在一万条以内没有问题。

- 追问「feed 很长怎么办」：用虚拟列表只渲染视口附近的条目，并且只保留最近若干页的数据。去重的 Set 可以常驻在模型里，不必每页重建，但 `reset` 时要一起清空。
- 追问「第一页没填满屏幕，自动加载停了」：IntersectionObserver 只在可见性变化时触发。按钮一直在视口里，它就不会再次触发。可以在每次加载完成后检查按钮是否仍然可见，可见就继续加载，直到填满屏幕或 `done`。
