"use client";

export function ShortcutDialog({ onClose }: { onClose: () => void }) {
  return (
    <div className="shortcut-layer" role="presentation">
      <button className="shortcut-backdrop" type="button" onClick={onClose} aria-label="关闭快捷键说明" />
      <section className="shortcut-dialog" role="dialog" aria-modal="true" aria-labelledby="shortcut-title">
        <header>
          <div>
            <div className="eyebrow"><span /> 快捷键</div>
            <h2 id="shortcut-title">键盘操作</h2>
          </div>
          <button type="button" onClick={onClose} aria-label="关闭快捷键说明">×</button>
        </header>
        <dl>
          <div><dt><kbd>↑</kbd> <kbd>↓</kbd></dt><dd>上一题 / 下一题</dd></div>
          <div><dt><kbd>←</kbd> <kbd>→</kbd></dt><dd>上一个 / 下一个模块</dd></div>
          <div><dt><kbd>Enter</kbd></dt><dd>展开或折叠当前题</dd></div>
          <div><dt><kbd>Esc</kbd></dt><dd>关闭面板</dd></div>
        </dl>
      </section>
    </div>
  );
}

export function ContentGuide({ onOverview }: { onOverview: () => void }) {
  return (
    <section className="content-guide">
      <div className="guide-number">+N</div>
      <div>
        <div className="eyebrow"><span /> 内容层</div>
        <h2>新资料只需要进内容层。</h2>
      </div>
      <p>页面、搜索、筛选、复习进度都由通用组件负责。以后每新增一题，只需要放入一个独立 Markdown 文件；构建器会自动汇总、校验并生成资料库。手册会出现在地址栏的 book 参数里，链接可以精确分享到某一本、某一章、某一题。</p>
      <button type="button" onClick={onOverview}>回到首页 ↑</button>
    </section>
  );
}

export function EmptyState({ title, detail, action }: { title: string; detail: string; action?: { label: string; onClick: () => void } }) {
  return (
    <div className="empty-state">
      <b>{title}</b>
      <p>{detail}</p>
      {action && <button type="button" onClick={action.onClick}>{action.label}</button>}
    </div>
  );
}
