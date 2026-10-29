"""Collect the pinned DrustZ source into readable units and an auditable manifest.
Usage: python3 scripts/collect-drustz-materials.py /path/to/checkout /tmp/payload.json
No upstream code is executed. Third-party forum bodies are indexed, not copied.
"""

import collections
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import zipfile

root = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2])
commit = subprocess.check_output(
    ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
).strip()
expected = "04316c111d0e4b75ca2ab8de0e6b42379727946e"
if commit != expected:
    raise SystemExit(f"Expected pinned revision {expected}, got {commit}")
base = f"https://github.com/DrustZ/ai_interview_prep_2026/blob/{commit}/"
sections = dict(
    [
        ("guide", "阅读路线与来源"),
        ("openai", "OpenAI · 题库与复习指南"),
        ("anthropic", "Anthropic · 题库与复习指南"),
        ("research", "公司面试 · 补充研究笔记"),
        ("forum-notes", "面经整理与回答建议"),
        ("collections", "主题题库与复习资料"),
        ("deepml", "Deep-ML · ML Coding"),
        ("coding", "公司 Coding 与手写训练"),
        ("plans", "作者复习计划与报告"),
        ("sprint", "冲刺资料与公司笔记"),
        ("agent-core", "Agent · Core、Gaps 与 Benchmarks"),
        ("agent-questions", "Agent · Interview Questions & Solutions"),
        ("mlsd", "ML System Design · 全流程"),
        ("robotics", "Robotics · Data、Learning 与 System Design"),
        ("labs", "Labs · Code、Tests 与 Data"),
        ("references", "原始面经与资源索引"),
    ]
)
cards = []
record_map = {}
file_cards = collections.defaultdict(list)
seen = {}
duplicates = []


def mapped(p):
    return "online_resource/" + p.removeprefix("new/")


def fence(path):
    text = (root / path).read_text(errors="replace")
    lang = {
        ".py": "python",
        ".json": "json",
        ".jsonl": "text",
        ".js": "javascript",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".txt": "text",
    }.get(pathlib.Path(path).suffix, "text")
    marker = "`" * max(3, max((len(x) for x in re.findall(r"`+", text)), default=0) + 1)
    return f"{marker}{lang}\n{text.rstrip()}\n{marker}\n"


def url(p):
    from urllib.parse import quote

    return base + quote(p, safe="/")


def add(key, title, section, body, paths=(), kind="作者资料", extra=None):
    body = body.strip()
    if not body:
        return
    digest = hashlib.sha256(body.encode()).hexdigest()
    if digest in seen:
        target = seen[digest]
        record_map[key] = target["id"]
        target["paths"] = list(dict.fromkeys(target["paths"] + list(paths)))
        duplicates.append({"record": key, "question": target["id"]})
        for p in paths:
            file_cards[p].append(target["id"])
        return
    ident = "drustz-" + hashlib.sha256(key.encode()).hexdigest()[:18]
    card = dict(
        id=ident,
        key=key,
        title=title.strip() or key,
        section=section,
        body=body,
        paths=list(paths),
        kind=kind,
        extra=extra or {},
    )
    seen[digest] = card
    cards.append(card)
    record_map[key] = ident
    for p in paths:
        file_cards[p].append(ident)
    return card


local = json.loads((root / "1acre3points_crawl/data/local_materials.json").read_text())
raw = []
excluded = []
restored = 0
for x in local["materials"]:
    paths = [mapped(p) for p in x["sourceFiles"]]
    kind = x["kind"]
    body = x["content"]
    if paths and all(p.endswith(".md") for p in paths) and "Deep-ML" not in kind:
        continue  # Re-split current Markdown below; old line numbers refer to older edits.
    if kind == "一亩三分地本地原帖":
        raw.append(
            {
                "id": x["id"],
                "title": x["title"],
                "url": x.get("sourceUrl") or url(paths[0]),
                "paths": paths,
            }
        )
        continue
    if kind in ["原始数据", "旧版本地工具"]:
        excluded.append(
            {
                "record": x["id"],
                "paths": paths,
                "reason": "source data / viewer infrastructure",
            }
        )
        continue
    if "Deep-ML" in kind:
        chunks = []
        for p in paths:
            if not (root / p).is_file():
                continue
            chunks.append(
                "### "
                + pathlib.Path(p).name
                + "\n\n"
                + (
                    (root / p).read_text(errors="replace")
                    if p.endswith(".md")
                    else fence(p)
                )
            )
        body = "\n\n".join(chunks)
        section = "deepml"
    elif len(paths) == 1 and (root / paths[0]).is_file():
        p = paths[0]
        text = (root / p).read_text(errors="replace")
        if p.endswith(".md"):
            start = x.get("lineStart")
            end = x.get("lineEnd")
            body = (
                "\n".join(text.splitlines()[start - 1 : end]) if start and end else text
            )
        elif p.endswith(".py"):
            body = fence(p)
        if "截断" in x["content"]:
            restored += 1
        section = {
            "一亩三分地整理": "forum-notes",
            "题库汇编": "collections",
            "报告与计划": "plans",
            "冲刺资料": "sprint",
            "手写训练": "coding",
            "公司编程练习": "coding",
            "公司笔记": "sprint",
            "其他资料": "guide",
        }.get(kind, "collections")
    else:
        section = "collections"
    add(
        x["id"],
        x["title"],
        section,
        body,
        paths,
        kind,
        {
            "related": x.get("relatedQuestions", []),
            "lineStart": x.get("lineStart"),
            "lineEnd": x.get("lineEnd"),
        },
    )

for filename in ["questions.json", "supplemental.json"]:
    records = json.loads((root / "1acre3points_crawl/data" / filename).read_text())[
        "questions"
    ]
    for x in records:
        kind = x.get("contentKind", "supplemental-research-note")
        body = x.get("content") if filename == "questions.json" else x.get("detail")
        original = x.get("sourceUrl") or x.get("url")
        if "public-canonical" in kind:
            body = x.get("overview") or x.get("summary") or x["title"]
            body += "\n\n完整题面参阅原始来源；本卡保留作者的题目索引。"
        prefix = (
            "> DrustZ 整理的"
            + ("补充研究笔记" if filename == "supplemental.json" else "复习指南")
            + "。公司与轮次信息沿用作者的来源记录。\n\n"
        )
        suffix = "\n\n### 来源与内容类型\n\n- Content kind: `" + kind + "`\n"
        if original and original.startswith("http"):
            suffix += "- [原始来源](" + original + ")\n"
        sources = x.get("sourceUrls") or []
        for u in dict.fromkeys(sources):
            if isinstance(u, str) and u.startswith("http") and u != original:
                suffix += "- [相关来源](" + u + ")\n"
        add(
            x["id"],
            x["title"],
            x["company"] if filename == "questions.json" else "research",
            prefix + (body or x.get("summary") or x["title"]) + suffix,
            ["1acre3points_crawl/data/" + filename],
            kind,
            {"company": x.get("company"), "sourceUrl": original, "contentKind": kind},
        )

# Import current author Markdown, not stale line ranges in the historical index.
# Keep complete documents, splitting long files only at real top-level sections.
for top in [
    "online_resource",
    "agentic_prep",
    "ml_sys_prep",
    "1acre3points_crawl/practice",
]:
    for f in sorted((root / top).rglob("*.md")):
        p = f.relative_to(root).as_posix()
        if "/viewer/" in p or "/deepml-problems/" in p or "/raw/" in p:
            continue
        body = f.read_text(errors="replace")
        title = next(
            (
                re.sub(r"^#+\s*", "", l).strip()
                for l in body.splitlines()
                if re.match(r"^#\s", l)
            ),
            f.stem,
        )
        if "/labs/" in p or "/sample_code/" in p:
            section = "labs"
        elif "/bot_company/" in p:
            section = "robotics"
        elif top == "ml_sys_prep":
            section = "mlsd"
        elif top == "1acre3points_crawl/practice":
            section = "coding"
        elif top == "agentic_prep":
            section = "agent-questions" if "/05_questions/" in p else "agent-core"
        elif "1p3a" in p or "1point3" in p:
            section = "forum-notes"
        elif "00_reports" in p:
            section = "plans"
        elif "sprint" in p:
            section = "sprint"
        elif "handwrite" in p or "coding" in p:
            section = "coding"
        else:
            section = "collections"
        # Never split inside code fences.
        lines = body.splitlines(keepends=True)
        cuts = [0]
        offset = 0
        delimiter = None
        if len(body) > 14000:
            for line in lines:
                match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
                if match:
                    if (
                        delimiter
                        and match[1][0] == delimiter[0]
                        and len(match[1]) >= len(delimiter)
                    ):
                        delimiter = None
                    elif not delimiter:
                        delimiter = match[1]
                if not delimiter and re.match(r"^## ", line) and offset:
                    cuts.append(offset)
                offset += len(line)
        cuts.append(len(body))
        for n, (a, b) in enumerate(zip(cuts, cuts[1:])):
            chunk = body[a:b].strip()
            if not chunk:
                continue
            heading = next(
                (
                    re.sub(r"^#+\s*", "", l).strip()
                    for l in chunk.splitlines()
                    if re.match(r"^#+\s", l)
                ),
                title,
            )
            label = title if len(cuts) == 2 else title + " · " + heading
            if (
                "personal_bridge" in p
                or "stories" in p
                or "day_plan" in p
                or "study_plan" in p
            ):
                chunk = (
                    "> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。\n\n"
                    + chunk
                )
            add(
                "file:" + p + ":" + str(n),
                label,
                section,
                chunk,
                [p],
                "作者完整文档" if len(cuts) == 2 else "作者文档章节",
            )

# Attach local runnable modules and test/data files to the nearest documentation.
# Entire files remain available in the downloadable archive, including large data.
code_paths = []
for f in sorted(root.rglob("*")):
    if not f.is_file() or ".git" in f.parts:
        continue
    p = f.relative_to(root).as_posix()
    if f.suffix not in [".py", ".json", ".jsonl", ".ipynb", ".txt"] or "/viewer/" in p:
        continue
    if not (
        p.startswith("ml_sys_prep/")
        or p.startswith("online_resource/deepml-problems/")
        or p.startswith("online_resource/02_coding_practice/")
        or p.startswith("online_resource/new/")
    ):
        continue
    code_paths.append(p)
    if file_cards[p]:
        continue
    if p.startswith("ml_sys_prep/") and f.suffix == ".py":
        neighbors = [
            c
            for c in cards
            if any(
                pathlib.Path(q).parent == f.parent.relative_to(root) for q in c["paths"]
            )
        ]
        target = next(
            (c for c in neighbors if any(q.endswith("README.md") for q in c["paths"])),
            None,
        )
        if target:
            target["body"] += "\n\n## " + f.name + "\n\n" + fence(p)
            target["paths"].append(p)
            file_cards[p].append(target["id"])
        else:
            add(
                "file:" + p,
                f.stem.replace("_", " "),
                "labs",
                fence(p),
                [p],
                "作者源代码",
            )

# Additional runnable implementations and their separate test suites.
for folder in [
    "1acre3points_crawl/practice",
    "1acre3points_crawl/tests",
    "online_resource/drills",
]:
    for f in sorted((root / folder).rglob("*.py")):
        p = f.relative_to(root).as_posix()
        if p not in code_paths:
            code_paths.append(p)
        if file_cards[p] or f.name == "__init__.py":
            continue
        add(
            "file:" + p,
            f.stem.replace("_", " "),
            "coding",
            fence(p),
            [p],
            "作者测试代码" if "/tests/" in p else "作者源代码",
        )

# A complete file manifest distinguishes learning content from renderer/crawler code.
all_files = sorted(
    p
    for p in subprocess.check_output(
        ["git", "-C", str(root), "ls-files"], text=True
    ).splitlines()
    if (root / p).is_file()
)
code_paths = list(
    dict.fromkeys(
        code_paths + [p for p in all_files if p.endswith(".py") and file_cards[p]]
    )
)
archive = pathlib.Path("public/materials/drustz-interview-2026/code-and-tests.zip")
archive.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(
        set(code_paths + ["LICENSE", "online_resource/deepml-problems/LICENSE"])
    ):
        z.write(root / p, p)
    z.writestr(
        "IMPORT-NOTICE.txt",
        f"Source: https://github.com/DrustZ/ai_interview_prep_2026\nRevision: {commit}\nCopyright (c) 2026 Mingrui Zhang. MIT except separately licensed material.\nDeep-ML: Educational Use Only License, included at online_resource/deepml-problems/LICENSE.\nCode is preserved as reference; upstream labs are not all execution-verified by this import.\n",
    )
manifest = []
for p in all_files:
    if file_cards[p]:
        role = "reading-card"
    elif p in code_paths:
        role = "code-download"
    elif any(p in x["paths"] for x in raw):
        role = "original-post-reference"
    elif p.endswith((".md", ".py")) and not any(
        s in p for s in ["/viewer/", "/scripts/", "/.github/"]
    ):
        role = "source-reference"
    else:
        role = "infrastructure-or-data-reference"
    manifest.append(
        {
            "path": p,
            "sha256": hashlib.sha256((root / p).read_bytes()).hexdigest(),
            "bytes": (root / p).stat().st_size,
            "coverage": role,
            "questions": list(dict.fromkeys(file_cards[p])),
            "url": url(p),
        }
    )

# Raw forum reports are represented by titles and links rather than copied bodies.
for i in range(0, len(raw), 25):
    group = raw[i : i + 25]
    body = "原始帖子索引；阅读作者整理的笔记后，可以通过这些链接核对上下文。\n\n"
    for x in group:
        body += "- [" + x["title"].replace("]", "\\]") + "](" + x["url"] + ")\n"
    add(
        "raw-index:" + str(i),
        f"原始面经来源索引 · {i + 1}–{i + len(group)}",
        "references",
        body,
        [p for x in group for p in x["paths"]],
        "来源索引",
    )

# The original-guide Markdown is the backing source of 212 catalog cards.
original_guides = (root / "1acre3points_crawl/data/oj_original_guides.md").read_text()
for match in re.finditer(r"<!-- guide (.*?) -->", original_guides):
    original_id = json.loads(match[1])["id"]
    if original_id in record_map:
        file_cards["1acre3points_crawl/data/oj_original_guides.md"].append(
            record_map[original_id]
        )
extra_refs = [
    "1acre3points_crawl/README.md",
    "online_resource/raw/h2h_blog1_content.md",
    "online_resource/raw/h2h_blog2_content.md",
    "online_resource/raw/h2h_chatgpt_content.md",
]
add(
    "extra-source-index",
    "第三方文章与原仓库使用说明",
    "references",
    "第三方文章和原仓库使用说明保留原始来源入口。\n\n"
    + "\n".join("- [" + pathlib.Path(p).stem + "](" + url(p) + ")" for p in extra_refs),
    extra_refs,
    "来源索引",
)

# The guide is generated last so that its counts and chapter links are accurate.
counts = collections.Counter(c["section"] for c in cards)
guide = """这本书整理自 **DrustZ / Mingrui Zhang** 的公开仓库，按原作者的学习单元保留题目、分析、代码与参考资料。原仓库包含题库、复习笔记和计划；下列卡片数是阅读单元数，同一主题可以有多张卡。\n\n## 建议阅读顺序\n\n1. 近期面试先看 OpenAI / Anthropic 题库，以及公司 Coding 与手写训练。\n2. Agent 面试接着看 Core、Gaps、Benchmarks，再做 Interview Questions & Solutions。\n3. ML / Data 面试看 ML System Design、Robotics 和 Labs。\n4. Deep-ML 用来补 tensor、matrix、optimization 和经典 ML coding。\n\n## 全部章节\n\n"""
for sec, label in sections.items():
    first = next((c for c in cards if c["section"] == sec), None)
    if first:
        guide += f"- [{label}](?book=drustz-interview-2026&section={sec}&question={first['id']})：{counts[sec]} 张资料卡。\n"
guide += (
    """\n## Code、Tests 与 Data\n\n[下载源代码、tests 和练习数据](https://github.com/DrustZ/ai_interview_prep_2026/tree/"""
    + commit
    + """)。本网站书目页面另附本地 ZIP 下载链接，包含 starter / reference solutions / tests / data 及各自 license。引用的代码保留原作者实现；本次导入检查解析与渲染，未宣称所有算法和 labs 都已运行验证。\n\n## 如何理解材料来源\n\n- 公司题库包含作者整理与重建的 preparation guides；每张卡标明 content kind 和来源。\n- 个人项目经历、故事和日期安排属于 DrustZ，可参考结构，回答时应换成自己的经历。\n- 原始论坛帖子保留标题与链接；研究笔记和作者解读可在本书直接阅读。\n- 作者主体材料：MIT，Copyright (c) 2026 Mingrui Zhang。Deep-ML 使用单独的 Educational Use Only License，限教育用途，禁止商业使用和模型训练。\n\nPinned revision: `"""
    + commit
    + "`.\n"
)
add(
    "guide",
    "DrustZ Interview Book · 阅读路线、下载与来源",
    "guide",
    guide,
    ["README.md"],
    "阅读指南",
)
# Recompute manifest links after the source index and guide were added.
for row in manifest:
    row["questions"] = list(dict.fromkeys(file_cards[row["path"]]))
    if row["questions"] and row["coverage"] != "original-post-reference":
        row["coverage"] = "reading-card"
payload = {
    "commit": commit,
    "source": base,
    "sections": sections,
    "cards": cards,
    "manifest": manifest,
    "recordMap": record_map,
    "duplicates": duplicates,
    "excludedRecords": excluded,
    "rawReferences": raw,
    "restoredTruncatedUnits": restored,
    "archiveFiles": len(code_paths),
}
out.write_text(json.dumps(payload, ensure_ascii=False))
print(
    json.dumps(
        {
            "cards": len(cards),
            "files": len(manifest),
            "archiveFiles": len(code_paths),
            "restoredTruncatedUnits": restored,
            "sections": collections.Counter(c["section"] for c in cards),
        },
        ensure_ascii=False,
    )
)
