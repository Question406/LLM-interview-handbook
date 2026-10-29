# Code block formatting · 2026-10-28

- 统一检查 2597 个代码块，748 个带代码的 source files；整理 482 个文件中的 731 个 blocks。
- Python 1748（719 changed）、JSON 8（7 changed）、JS 4（4 changed）、YAML 1（1 changed）、Bash 2（原已符合）、text 834（原样保留）。
- 所有 1748 个 Python blocks 格式化前后 AST 一致；4 个 JS blocks AST 一致；JSON/YAML 数据相等；纯文本布局与 Shell 示例保持。
- `content:format` 写回 canonical Markdown / legacy HTML snippets；`content:format:check` 检查 source idempotency。构建在 highlighting 前自动经过同一 formatter，不改 canonical source。
- Ruff WASM 0.17.3；Prettier 3.9.10；@prettier/sync 0.6.1；Shell plugin 0.20.2。无需独立 Python formatter，也不运行题目代码。
- Syntax errors in explicitly executable languages 阻止构建，指出 question / language；故意无效代码与伪代码用 text。
- 保护 inline code、代码字符串中的 HTML、实体、美元/反斜线、正文与公式；legacy numeric HTML entities 解码一次后格式化。

## 验证

- 新增 8 个 formatter regression tests；全部 Node tests 68/68 通过。
- 本地 practice runner integration tests 22/22 通过。
- 第一批 frontier additions 9/9、第二批 20/20、batch decoding 3/3 的题内 executable tests 全通过。
- Source formatter 第二次运行 0 changes；coding guidance coverage 保持 635 cards / 392 examples。
- npm run build（含 content build、server/client bundles）通过；targeted ESLint 与 git diff --check 通过。

文件级变化清单与统计见 summary.json。AST 与执行验证仅说明本次 formatting 没有改变已核对实现，不对原始题解正确性作额外声称。
