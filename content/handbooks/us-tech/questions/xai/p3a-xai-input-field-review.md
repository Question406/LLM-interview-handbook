---
id: p3a-xai-input-field-review
section: xai
order: 750
level: S
title: "xAI：输入框 Code Review：异步搜索与过期响应"
quick: "搜索输入框的关键是每次输入都让旧请求失效：用版本号丢弃过期或乱序返回的响应，用 AbortController 取消不再需要的请求，空输入清空结果，组件卸载时清理计时器和订阅。"
companies:
  - xai
tags:
  - xAI
  - Coding
  - Frontier-2026-10
  - 完整编程练习
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: 1Point3Acres xAI source
    url: https://www.1point3acres.com/interview/problems/dcef89ff-9f57-4c98-bbcf-10692b3248af
    type: secondary
---

## 题目

给一段带异步搜索的输入框实现做 code review：用户边输入边搜索，结果列表跟着更新。要找出其中的竞态、资源泄漏和安全问题，并给出改好的版本。

> 来源：一亩三分地 xAI 题目目录里的一条「输入框实现审查」题（2026-10-18 读取），只有题目线索，原始代码没有披露，所以手册没有把它标成真实面经（`realInterview: false`）。下面的接口、实现和测试都是手册按这个方向编写的练习，不是原题代码。

## 思路

搜索输入框最常见的 bug 是乱序响应：先输入 `old` 再输入 `new`，如果 `old` 的请求更慢，它的结果会在 `new` 之后返回，把正确结果覆盖掉。review 时要逐项检查：

- 每次输入都要让之前所有请求失效。做法是维护一个递增的版本号，响应回来时版本不一致就丢弃。版本号要在输入时就加一，而不是等 debounce 结束、请求发出时才加，否则 debounce 期间的旧响应仍可能写进来；
- 用 `AbortController` 取消已经不需要的请求，节省带宽。但后端不一定理会 abort，所以它只是优化，正确性仍要靠版本号；
- 清空输入时要清空结果，之前请求的迟到响应也不能把结果填回来；
- 被主动取消的请求会抛 `AbortError`，这不是错误，不应该展示给用户；
- 组件卸载时要清掉计时器、取消请求、退订，之后不能再更新状态；
- 搜索结果按文本渲染，不要用 `dangerouslySetInnerHTML`，否则后端返回的内容可能被当成 HTML 执行。

这份练习把状态逻辑放进与 UI 无关的 `SearchModel`，React 组件只负责订阅和渲染，这样竞态可以直接在 Node 里测。

## 完整编程练习（手册重构版）

运行环境是 Node 22 + React 19。浏览器里使用组件需要经过项目现有的打包器；纯状态模型和服务端渲染的测试可以直接用 Node 执行。

### 题面、接口与约束

- `new SearchModel(searchFn, delay = 150)`：`searchFn(text, { signal })` 返回 `Promise<string[]>`；`delay` 是 debounce 毫秒数，为负抛 `RangeError`。
- `query(text)`：每次输入立即让旧请求失效，等待 `delay` 毫秒后发起搜索。只含空白的输入直接清空结果、不发请求。即使后端忽略 abort，旧响应也不能覆盖新输入的结果。
- 状态是 `{ query, items, loading, error }`，通过 `subscribe(listener)` 订阅，返回退订函数。搜索失败时 `error` 是错误信息；`AbortError` 不展示。
- `dispose()`：取消计时器和进行中的请求，清空订阅；之后再调用 `query` 抛错。
- `SearchBox({ searchFn, delay })`：受控输入框，卸载时清理订阅和模型，不使用 `dangerouslySetInnerHTML`。
- 最多 100 个请求交错进行，单次结果不超过 100 项。

### 输入输出示例

```text
query("old") -> query("new") -> new 返回 ["N"] -> old 返回 ["O"]
state.items   -> ["N"]          # old 的迟到响应被丢弃

query("later") -> query("") -> later 返回 ["bad"]
state.items   -> []             # 清空后迟到响应也不能填回来
```

### 解题思路与正确性

`query` 一开头就把 `version` 加一，并把这个值闭包进本次搜索；响应回来时只有 `version` 仍等于当前值才更新状态。因为任何后续输入（包括清空）都会让 `version` 变大，所以只有最后一次输入对应的响应能被采用，返回顺序再乱也不影响结果。`dispose` 同样把 `version` 加一并设置 `closed`，销毁后所有在途响应都会被丢弃。

`AbortController` 只用来减少浪费：被取消的请求如果抛出 `AbortError`，由于版本已经变了，同样不会写状态。React 把结果作为文本子节点渲染，会自动转义，外部内容不会被当成 HTML。

### 完整参考实现（JavaScript / React）

```javascript
import React, { useEffect, useRef, useState } from 'react';

const INITIAL_STATE = { query: '', items: [], loading: false, error: null };

function isStringList(value) {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}

// 与 UI 无关的搜索状态机：debounce、取消旧请求、丢弃过期响应。
export class SearchModel {
  constructor(searchFn, delay = 150) {
    if (delay < 0) {
      throw new RangeError(`delay must be non-negative, got ${delay}`);
    }
    this.searchFn = searchFn;
    this.delay = delay;
    this.version = 0; // 每次输入加一；响应回来时版本不一致就丢弃
    this.closed = false;
    this.timer = null;
    this.controller = null;
    this.state = INITIAL_STATE;
    this.listeners = new Set();
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

  query(text) {
    if (this.closed) {
      throw new Error('SearchModel is disposed');
    }
    // 在输入时就让旧请求失效，debounce 期间的旧响应也会被丢弃
    const version = ++this.version;
    clearTimeout(this.timer);
    this.controller?.abort();

    const hasQuery = text.trim() !== '';
    this.publish({ query: text, items: [], loading: hasQuery, error: null });
    if (!hasQuery) {
      return;
    }
    this.timer = setTimeout(() => this.runSearch(text, version), this.delay);
  }

  async runSearch(text, version) {
    const controller = new AbortController();
    this.controller = controller;
    const isCurrent = () => !this.closed && version === this.version;
    try {
      const items = await this.searchFn(text, { signal: controller.signal });
      if (!isStringList(items)) {
        throw new TypeError('search response must be an array of strings');
      }
      if (isCurrent()) {
        this.publish({ items, loading: false });
      }
    } catch (error) {
      if (isCurrent()) {
        // 被主动取消的请求不算错误
        const message = error.name === 'AbortError' ? null : String(error.message);
        this.publish({ loading: false, error: message });
      }
    }
  }

  dispose() {
    this.closed = true;
    this.version++;
    clearTimeout(this.timer);
    this.controller?.abort();
    this.listeners.clear();
  }
}

// 受控输入框。模型在 effect 里创建、在 cleanup 里销毁，StrictMode 重复挂载也不会复用已销毁的实例。
export function SearchBox({ searchFn, delay = 150 }) {
  const modelRef = useRef(null);
  const [state, setState] = useState(INITIAL_STATE);

  useEffect(() => {
    const model = new SearchModel(searchFn, delay);
    modelRef.current = model;
    setState(model.state);
    const unsubscribe = model.subscribe(setState);
    return () => {
      unsubscribe();
      model.dispose();
      modelRef.current = null;
    };
  }, [searchFn, delay]);

  const input = React.createElement('input', {
    value: state.query,
    onChange: (event) => modelRef.current?.query(event.target.value),
    'aria-label': 'Search',
  });
  const status = state.loading ? 'Loading…' : state.error || '';
  // 结果作为文本子节点渲染，React 会转义，不使用 dangerouslySetInnerHTML
  const items = state.items.map((text, index) => React.createElement('li', { key: index }, text));

  return React.createElement(
    'section',
    null,
    React.createElement('label', null, 'Search', input),
    React.createElement('div', { 'aria-live': 'polite' }, status),
    React.createElement('ul', null, items),
  );
}
```

### 可执行测试

```javascript
import assert from 'node:assert/strict';
import { renderToString } from 'react-dom/server';

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// 每个查询的 Promise 由测试手动 resolve，用来制造乱序返回
const pending = {};
const model = new SearchModel((query) => new Promise((resolve) => { pending[query] = resolve; }), 0);

// old 先发、new 后发；new 先返回，old 迟到，最终只能显示 new 的结果
model.query('old');
await wait(5);
model.query('new');
await wait(5);
pending.new(['N']);
await wait(0);
pending.old(['O']);
await wait(0);
assert.deepEqual(model.state.items, ['N']);

// 清空输入后，之前请求的迟到响应不能把结果填回来
model.query('later');
await wait(5);
model.query('');
pending.later(['bad']);
await wait(0);
assert.deepEqual(model.state.items, []);
assert.equal(model.state.loading, false);

// 搜索失败时展示错误信息
const failing = new SearchModel(async () => { throw new Error('boom'); }, 0);
failing.query('x');
await wait(5);
assert.equal(failing.state.error, 'boom');
assert.equal(failing.state.loading, false);

// 销毁后不能再查询；负的 delay 非法
model.dispose();
assert.throws(() => model.query('x'));
assert.throws(() => new SearchModel(async () => [], -1), RangeError);

// 服务端渲染出带 aria-label 的输入框
const html = renderToString(React.createElement(SearchBox, { searchFn: async () => [] }));
assert.match(html, /aria-label="Search"/);
```

### 复杂度与追问

设订阅者数为 L、结果项数为 K。每次输入是 O(L)（通知订阅者），每次响应是 O(L + K)；空间是 O(K) 加上至多一个在途请求的计时器和 controller。

- `searchFn` 必须保持引用稳定（用 `useCallback` 或定义在组件外）。它是 effect 的依赖，每次渲染都换一个新函数会导致模型被反复销毁和重建。
- 模型在 effect 里创建、在 cleanup 里销毁，所以 React StrictMode 下 setup/cleanup 被执行两次时，不会继续使用已经 dispose 的实例。
- 真实服务还应该限制查询长度、在服务端校验输入，并给请求设超时；超时可以用 `AbortSignal.timeout` 和用户触发的取消信号合并。
