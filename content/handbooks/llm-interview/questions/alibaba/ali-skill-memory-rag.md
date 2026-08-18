---
id: ali-skill-memory-rag
section: alibaba
order: 21
level: S
title: 淘天面经：Skill、Memory、RAG 分别解决什么核心问题？
quick: Skill 解决“这类任务怎么做”的程序化经验复用；Memory 解决跨会话状态与个性化；RAG 解决外部知识证据注入。三者别混成一个向量库。
tags:
  - Alibaba
  - Skill
  - Memory
  - RAG
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Skill 解决“这类任务怎么做”的程序化经验复用；Memory 解决跨会话状态与个性化；RAG 解决外部知识证据注入。三者别混成一个向量库。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>组件</th><th>核心问题</th><th>典型实现</th></tr></thead><tbody>
<tr><td>Skill</td><td>How to do this class of tasks?</td><td>流程+模板+脚本+工具使用规范，按需加载</td></tr>
<tr><td>Memory</td><td>What should persist across turns/sessions?</td><td>短上下文、摘要、画像、向量事件</td></tr>
<tr><td>RAG</td><td>What evidence do I need now?</td><td>检索知识库/文档并引用</td></tr>
</tbody></table></div>
<p>淘天追问重点是边界：把操作手册塞进 RAG ≠ 有 Skill；把所有历史塞进窗口 ≠ 有 Memory 治理。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a></div>
