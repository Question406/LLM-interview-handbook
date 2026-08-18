# Interview Atlas

一个内容驱动的面试资料库。当前已将原来的单文件 LLM handbook 迁移为 140 道题、9 个模块的结构化站点。

## 已有功能

- 全文搜索与 S / A 级、真实面经、掌握状态筛选
- 随机抽题、全部展开 / 折叠、题目深链接
- 复习进度与深色主题保存在当前浏览器
- 桌面、平板和手机自适应
- 大章答案按模块懒加载，资料库扩展后不会持续拖慢首屏

## 内容架构

```text
content/
├── handbooks/          # 每本手册的元数据、章节和题目索引
├── registry.ts        # 资料库注册表
└── types.ts           # 统一内容 schema
public/content/       # 按模块分片的完整答案
components/           # 通用的学习工作台 UI
scripts/              # 老 HTML 导入器
```

新增资料时，复制 `content/handbooks/example.json`，填入内容，再在 `content/registry.ts` 登记即可。小手册可直接内联 `answerHtml`；大手册可通过 `answerPath` 按模块分片。详细说明见 `content/README.md`。

## 本地使用

```bash
npm install
npm run dev
```

重新从旧版单文件 HTML 生成内容：

```bash
npm run import:legacy -- ../llm_interview_handbook_v2.html
```

验证成品：

```bash
npm test
```
