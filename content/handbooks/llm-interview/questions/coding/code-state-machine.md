---
id: code-state-machine
section: coding
order: 9
level: A
title: 设计 Tool-Call State Machine：哪些状态不能交给 LLM 自己“记”？
quick: >-
  建议显式 runtime 状态
  PARSE→VALIDATE→AUTHORIZE→EXECUTE→OBSERVE→RETRY/FAIL→RETURN，并持久化
  attempt、tool-call ID、权限、side-effect status。安全/幂等状态不应只存在自然语言 context 中。
tags:
  - Agent
  - State Machine
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>建议显式 runtime 状态 PARSE→VALIDATE→AUTHORIZE→EXECUTE→OBSERVE→RETRY/FAIL→RETURN，并持久化 attempt、tool-call ID、权限、side-effect status。安全/幂等状态不应只存在自然语言 context 中。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><pre><code data-lang="text">PARSE -&gt; VALIDATE -&gt; AUTHORIZE -&gt; EXECUTE -&gt; OBSERVE -&gt; RETURN
              |             |            |
            REPAIR        DENY       RETRY / UNKNOWN
                                      |
                                    STATUS_CHECK</code></pre><p>LLM 擅长语义决策，但 transaction state、permission、retry count、预算、唯一 call ID 必须由 harness 结构化维护。否则 context compression、模型 hallucination 或重启会丢掉关键安全信息。</p><p>每个 transition 都应产出 machine-readable event，便于 replay、audit、eval 和 checkpoint/restore。</p></div>
