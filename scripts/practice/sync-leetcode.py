"""Refresh factual public example data and constraints from official LeetCode.

Full descriptions and explanations are deliberately not stored in the project;
the practice page pairs handbook-authored descriptions with official links.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / "content/practice/leetcode-public-examples.json"
QUERY = "query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { questionId title content metaData } }"


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "div", "li", "pre", "br"):
            self.parts.append("\n")
        if tag == "sup":
            self.parts.append("^")

    def handle_endtag(self, tag):
        if tag in ("p", "div", "li", "pre"):
            self.parts.append("\n")

    def handle_data(self, text):
        self.parts.append(text)


def extract(slug, question):
    parser = Text()
    parser.feed(question["content"])
    text = "".join(parser.parts).replace("\xa0", " ")
    pattern = r"(?:Input|输入)\s*[:：]\s*(.*?)\s*(?:Output|输出)\s*[:：]\s*(.*?)(?=\s*(?:Explanation|解释|Example\s*\d|示例\s*\d|Constraints|提示|Follow.up|Note\s*:)|\Z)"
    examples = [{"input": match[1].strip(), "output": match[2].strip()} for match in re.finditer(pattern, text, re.S | re.I)]
    if not examples:
        for pre in re.findall(r"<pre[^>]*>(.*?)</pre>", question["content"], re.S):
            plain = unescape(re.sub(r"<[^>]+>", "", pre)).replace("\xa0", " ")
            match = re.search(r"Input\s*:?\s*(.*?)\s*Output\s*:?\s*(.*?)(?=\s*Explanation|\Z)", plain, re.S)
            if match:
                examples.append({"input": match[1].strip(), "output": match[2].strip()})
    if not examples:
        raise ValueError(f"No public input/output examples found: {slug}")
    constraints = []
    match = re.search(r"(?:Constraints|提示)\s*[:：](.*)", text, re.S)
    if match:
        constraints = [line.strip() for line in re.split(r"Follow.up|进阶", match[1], maxsplit=1, flags=re.I)[0].splitlines() if line.strip()]
    signature = json.loads(question["metaData"])
    signature = {key: value for key, value in signature.items() if key in ("name", "params", "return", "output", "classname", "constructor", "methods", "systemdesign", "manual")}
    return {"id": question["questionId"], "title": question["title"],
            "url": f"https://leetcode.com/problems/{slug}/description/", "examples": examples,
            "constraints": constraints, "signature": signature, "retrievedAt": date.today().isoformat(),
            "provenance": "leetcode-public-examples"}


def fetch(slug):
    payload = json.dumps({"query": QUERY, "variables": {"titleSlug": slug}})
    for attempt in range(3):
        response = subprocess.run(["curl", "--silent", "--show-error", "--fail", "--max-time", "30",
                                   "https://leetcode.com/graphql/", "-H", "Content-Type: application/json",
                                   "-H", f"Referer: https://leetcode.com/problems/{slug}/", "--data-binary", "@-"],
                                  input=payload, text=True, capture_output=True)
        try:
            return slug, extract(slug, json.loads(response.stdout)["data"]["question"])
        except (ValueError, KeyError, TypeError):
            time.sleep(attempt + 1)
    raise RuntimeError(f"Official data unavailable: {slug}; existing snapshot was not changed")


if __name__ == "__main__":
    slugs = {re.search(r"https://leetcode(?:\.com|\.cn)/problems/([^/\s]+)", path.read_text())[1]
             for path in (ROOT / "content/handbooks").glob("leetcode-*/questions/**/*.md")}
    with ThreadPoolExecutor(max_workers=4) as pool:
        questions = dict(pool.map(fetch, sorted(slugs)))
    DESTINATION.write_text(json.dumps({"schemaVersion": 1, "questions": questions}, ensure_ascii=False, indent=2) + "\n")
    print(f"Saved {len(questions)} official records / {sum(len(row['examples']) for row in questions.values())} public examples.")
