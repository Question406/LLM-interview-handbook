---
id: drustz-2dfe753b4530dbb20e
section: coding
order: 30
level: A
title: test bootloader repair
quick: 作者测试代码 · test bootloader repair
companies: []
tags:
  - DrustZ
  - 作者测试代码
  - 公司 Coding 与手写训练
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/tests/test_bootloader_repair.py
    type: primary
---
```python
import importlib.util
import unittest
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "practice"
    / "anthropic"
    / "bootloader_repair.py"
)
SPEC = importlib.util.spec_from_file_location("bootloader_repair", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
Solution = MODULE.Solution


class BootloaderTests(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()

    def test_classic_example(self):
        instructions = [
            "next +0",
            "plus +1",
            "jump +4",
            "plus +3",
            "jump -3",
            "plus -99",
            "plus +1",
            "jump -4",
            "plus +6",
        ]
        self.assertEqual(self.solution.firstRepeatedIndex(instructions), 1)
        self.assertEqual(self.solution.fixBootloader(instructions), 8)

    def test_public_format_example(self):
        instructions = [
            "plus +1",
            "next +2",
            "jump +3",
            "plus +3",
            "jump -1",
            "plus +2",
        ]
        self.assertEqual(self.solution.fixBootloader(instructions), 3)

    def test_next_value_is_used_only_after_swap(self):
        instructions = ["plus +5", "next +3", "jump -1", "jump +0"]
        self.assertEqual(self.solution.firstRepeatedIndex(instructions), 1)
        self.assertEqual(self.solution.fixBootloader(instructions), 5)

    def test_jump_zero(self):
        instructions = ["plus +1", "jump +0"]
        self.assertEqual(self.solution.firstRepeatedIndex(instructions), 1)
        self.assertEqual(self.solution.fixBootloader(instructions), 1)

    def test_out_of_bounds_is_not_success(self):
        instructions = ["plus +1", "jump +10", "plus +2"]
        self.assertEqual(self.solution.fixBootloader(instructions), 3)

    def test_large_input_is_iterative(self):
        n = 200_000
        instructions = ["plus +1"] * (n - 1) + ["jump +0"]
        self.assertEqual(self.solution.fixBootloader(instructions), n - 1)


if __name__ == "__main__":
    unittest.main()
```

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/tests/test_bootloader_repair.py](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/tests/test_bootloader_repair.py)。作者整理资料；许可和第三方来源范围见阅读指南。
