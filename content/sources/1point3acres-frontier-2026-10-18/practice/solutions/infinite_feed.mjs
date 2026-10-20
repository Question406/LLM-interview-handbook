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
