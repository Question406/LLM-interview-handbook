# Interview Atlas

一个内容驱动的面试资料库，包含 LLM、ML 基础、LeetCode、美国公司面经与 System Design，按“一题一个 Markdown 文件”维护。

Apple 备考可直接选择 **Apple 面试题本**，或打开 `/?book=apple-interview`。[全题目录与复习摘要](content/handbooks/apple-interview/README.md) 汇总已有 Apple／Data Team 资料，并将 cumsum、矩阵与 mask 单独成章。

## 已有功能

- 全文搜索与 S / A 级、真实面经、掌握状态筛选
- 随机抽题、全部展开 / 折叠、题目深链接
- 复习进度与深色主题保存在当前浏览器
- 桌面、平板和手机自适应
- 大章答案按模块懒加载，资料库扩展后不会持续拖慢首屏
- 开机只拉手册目录；点进一章再拉卡片公式，点开一题再拉该题答案

## 内容架构

```text
content/
├── handbooks/<slug>/  # _handbook.md、questions/ 与 drafts/
├── templates/         # 新题模板
├── generated/         # 构建产物（不提交）
└── registry.ts        # 读取自动生成的资料库
public/content/        # catalog / 分手册 index / 章卡片 / 单题答案（构建产物，不提交）
components/            # 通用的学习工作台 UI
scripts/               # 内容校验、编译与静态资源准备
```

新增题目时，只需复制 `content/templates/question.md`，写入自己的 `drafts/<agent-id>/`，通过审核后移至 `questions/<section>/`。索引、统计、搜索文本和懒加载答案包会自动生成，不需要登记或改前端。详细规则见 `content/README.md`。

## 本地使用

```bash
npm install
npm run dev
```

Node 26 下如果启动停在 `content:build`，可用以下兼容选项避免 Prettier 同步模块初始化卡住；构建和测试也可使用同一环境变量：

```bash
NODE_OPTIONS=--no-experimental-require-module npm run dev
```

验证成品：

```bash
npm test
```

System Design 手册可从资料库切换，或打开 `/?book=system-design`。36张题卡按答题方法、分布式基础、通用设计、ML、LLM与公司来源组织，参考讨论默认折叠。学习顺序和来源边界见 [手册说明](content/handbooks/system-design/README.md)。

## 本地 Python 编程练习

首次安装运行环境（Python 3.11–3.13，首次下载依赖和建立字体缓存需要等待）：

```bash
npm run practice:setup
npm run practice
```

打开 [本地练习页](http://127.0.0.1:3001/practice)。可以直接试 PyTorch 自动求导、pandas / scikit-learn / Matplotlib 和两数之和；也可以在手册题目卡片点击“编程练习”，载入题目描述、默认测例、起始代码和测试。草稿按手册和题号保存在当前浏览器，支持下载代码文件。

LeetCode 的 225 个题库条目对应 209 道不同题。`content/practice/leetcode-public-examples.json` 保存官方公开的 512 组输入输出、约束和来源链接；题意使用手册的中文整理，官方完整原文通过链接打开，不批量保存逐字题面或题解。测试适配器处理链表、树、原地修改、设计类和允许多种合法答案的题。它们是公开示例，不是平台隐藏测试。自定义题提供手册默认测试，并明确标注来源。

练习页的 Ground truth 区域默认折叠，展开后才显示只读参考实现和预期结果。可以独立运行参考实现验证默认测例，不会覆盖自己的代码或修改过的测试。旧草稿会保留；需要载入最新默认测试时，点击“恢复默认测例”。

编辑器支持缩进、高亮和 `Cmd/Ctrl + Enter` 运行测试。测试与标准输入可以编辑；报错可跳到对应行，简单相等断言显示预期值与实际值，Matplotlib 图片直接出现在结果区。每次运行使用新进程，默认 15 秒超时，可选 5 / 30 秒，也可以手动停止。循环中的测试遵循 Python 原本的断言语义；结果列表单独展示顶层断言，并在第一个失败处停止。

Tab、Shift-Tab 与 Python 自动缩进统一使用四个空格。面试模式的默认测试只覆盖合法输入及有效边界，不要求对 NaN、非法形状、超出参数约束等输入额外抛错；题目本身的状态冲突与有效 mask 行为仍保留。原有未修改的默认测例草稿会自动更新，用户代码与手动修改的测试不会被覆盖。

运行器预装 CPU PyTorch、JAX、NumPy、SciPy、pandas、scikit-learn、Matplotlib、Pillow、SymPy、sortedcontainers 与 pytest，版本见 `scripts/practice/requirements.txt` 和 `requirements.lock`。现有 JavaScript / React 题使用本机 Node.js 执行测试。Python 环境与字体缓存放在系统临时目录，不同步到 Dropbox；如果系统清理了该目录，重新运行 `practice:setup` 即可。可通过 `PRACTICE_PYTHON` 指定其他 Python 环境，通过 `PRACTICE_PORT` / `PRACTICE_RUNNER_PORT` 指定网页和运行器端口。

这是用于自己代码的本地原型：服务只监听回环地址，网页经同源代理调用运行器；执行子进程不继承服务认证信息，但不是面向陌生人代码的系统沙箱。运行器暂不支持 CUDA、Triton、分布式训练或交互式终端。自动提取的题目框架需要核对接口，多片段题目可能需要手动整理；只有已测试的题目和示例可视为已验证可运行。断点与单步调试尚未实现。

验证本地运行器：

```bash
npm run practice:test
```
