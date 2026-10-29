---
id: drustz-ad699422d8bc2b08ad
section: forum-notes
order: 132
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Function Signature
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Function Signature
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Function Signature

```python
def process_images(
    image_dir: str,
    transformation_dir: str,
    output_dir: str,
    get_output_path: Callable[[str, str], str],
) -> None:
    """
    Process all images with all transformation configurations.

    Args:
        image_dir: Path to directory containing source images
        transformation_dir: Path to directory containing transformation JSON files
        output_dir: Path to directory for saving processed images
        get_output_path: Utility function that generates output path
                        given (image_path, transform_json_path)
    """
    pass
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
