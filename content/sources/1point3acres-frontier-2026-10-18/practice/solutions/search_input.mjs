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
