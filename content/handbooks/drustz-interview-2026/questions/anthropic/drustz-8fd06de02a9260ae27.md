---
id: drustz-8fd06de02a9260ae27
section: anthropic
order: 1
level: A
title: Coding Q1 Image Processing
quick: locally-saved-topic-editorial · Coding Q1 Image Processing
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-image-processing
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Batch Image Processor

## Introduction

In this coding challenge, you will build a tool to edit many images at once. You are given a folder of images and a list of changes (in JSON format). Your job is to apply these changes to each image and save the results.

This test checks if you can:

- **Research quickly** - You can and should look up documentation.
- Read settings from JSON files.
- Read and write files efficiently.
- Make your code run faster using parallel processing.

### Interview Notes

- **Searching online is allowed.** The interviewer wants to see how you learn new APIs.
- You can use any resource (except AI answers).
- **Recommended Libraries:** **Pillow (PIL)** or **scikit-image**. It helps to know one of these before the interview.
- You will start with small images. Later, you must optimize the code to handle large images within a time limit.

## Files and Folders

You get four directories:

```text
project/
├── small_images/      # Small files to test your code
│   ├── image1.png
│   ├── image2.jpg
│   └── ...
├── large_images/      # Big files to check speed/performance
│   ├── photo1.png
│   ├── photo2.jpg
│   └── ...
├── transformations/   # JSON files that list the changes
│   ├── transform1.json
│   ├── transform2.json
│   └── ...
└── output/            # Where you save the finished images
```



You also get helper tools to list files and create output file names.

## How to Change the Images

Every JSON file in the `transformations/` folder lists changes to make in order. There are **six types** of changes:

### Simple Changes (No Settings)

| Type | Description |
| :--- | :--- |
| `grayscale` | Turn the image black and white |
| `flip_horizontal` | Mirror the image left-to-right |
| `flip_vertical` | Mirror the image top-to-bottom |

### Advanced Changes (With Settings)

| Type | Setting | Description |
| :--- | :--- | :--- |
| `scale` | `factor` (float) | Resize the image (e.g., 0.5 is half size) |
| `blur` | `radius` (int) | Blur the image by this amount |
| `rotate` | `angle` (float) | Rotate the image by degrees |

### Example JSON File

```json
{
  "transformations": [
    { "type": "grayscale" },
    { "type": "scale", "factor": 0.5 },
    { "type": "rotate", "angle": 90 }
  ]
}
```



This list tells the program to:

- Turn the image grayscale.
- Shrink it to 50% size.
- Rotate it 90 degrees.

## What You Need to Do

### Part 1: Make it Work

- **Pick a Library**: Choose a Python library that can do all six changes.

Pillow (PIL)
- scikit-image
- OpenCV
- **Write Functions**: Write code to handle each of the six change types.
- **Process the Images**:

Read every transformation JSON file.
- For each JSON file, go through every source image.
- Apply the changes in order.
- Save the final image to the output folder.
- **Test**: Make sure it works correctly using the `small_images/` folder.

### Part 2: Make it Fast

Once the code works, process the `large_images/` folder. You must finish within a **target time limit**.

Keep in mind:

- Editing images uses the CPU a lot.
- You can process different images at the same time (they don't depend on each other).
- You should use parallel strategies.

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



## Example Solution

**Note**: This is just one way to solve it. In the interview, use your own style and explain your steps.

### Picking the Right Tool

**Pillow (PIL)** is a great choice because:

- It is easy to use.
- It can do all the required changes built-in.
- It is very popular and well-documented.
**scikit-image** is also good if you like using NumPy.

### Pillow Cheat Sheet

Use these terms when searching the docs:

| Change | Pillow Command |
| :--- | :--- |
| Grayscale | `PIL.ImageOps.grayscale()` |
| Flip horizontal | `PIL.ImageOps.mirror()` |
| Flip vertical | `PIL.ImageOps.flip()` |
| Scale/Resize | `Image.resize(size, resample)` |
| Blur | `PIL.ImageFilter.GaussianBlur(radius)` |
| Rotate | `Image.rotate(angle, expand=True)` |

### Simple Solution Code

```python
from PIL import Image, ImageFilter, ImageOps
import json
import os
from pathlib import Path


def load_transformations(json_path: str) -> list:
    """Load transformation specifications from a JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data.get('transformations', [])


def apply_transformation(image: Image.Image, transform: dict) -> Image.Image:
    """Apply a single transformation to an image."""
    transform_type = transform['type']

    if transform_type == 'grayscale':
        # Convert to grayscale. We convert back to RGB because
        # some later steps might expect 3 color channels.
        return ImageOps.grayscale(image).convert('RGB')

    elif transform_type == 'flip_horizontal':
        return ImageOps.mirror(image)

    elif transform_type == 'flip_vertical':
        return ImageOps.flip(image)

    elif transform_type == 'scale':
        factor = transform['factor']
        new_size = (int(image.width * factor), int(image.height * factor))
        return image.resize(new_size, Image.Resampling.LANCZOS)

    elif transform_type == 'blur':
        radius = transform['radius']
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    elif transform_type == 'rotate':
        angle = transform['angle']
        return image.rotate(angle, expand=True)

    else:
        raise ValueError(f"Unknown transformation type: {transform_type}")


def apply_all_transformations(image: Image.Image, transformations: list) -> Image.Image:
    """Apply a sequence of transformations to an image."""
    result = image.copy()
    for transform in transformations:
        result = apply_transformation(result, transform)
    return result


def process_images(
    image_dir: str, transformation_dir: str, output_dir: str, get_output_path
) -> None:
    """Process all images with all transformation configurations."""

    # Get all image and transformation files.
    # Note: In a real interview, helper functions might give you these lists.
    image_files = [
        f
        for f in Path(image_dir).iterdir()
        if f.suffix.lower() in ('.png', '.jpg', '.jpeg')
    ]
    transform_files = list(Path(transformation_dir).glob('*.json'))

    for transform_file in transform_files:
        transformations = load_transformations(str(transform_file))

        for image_file in image_files:
            # Load image
            image = Image.open(str(image_file))

            # Apply transformations
            result = apply_all_transformations(image, transformations)

            # Save to output directory
            output_path = get_output_path(str(image_file), str(transform_file))
            result.save(output_path)

            # Close images to free memory
            image.close()
            result.close()
```



### Fast Solution Code (Parallel)

For big images, use `ProcessPoolExecutor`. Image editing is **CPU-bound** (it does a lot of math). You need multiprocessing to get around Python's GIL restrictions.

**Important**: On Windows, you must put the executor code inside `if __name__ == '__main__':`. This stops the code from starting infinite new processes.

```python
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageFilter, ImageOps
import json
from pathlib import Path
import os


# Note: This function must be at the module level (not inside another function)
# so Python can send it to other processes (pickling).
def apply_transformation(image: Image.Image, transform: dict) -> Image.Image:
    """Apply a single transformation to an image."""
    transform_type = transform['type']

    if transform_type == 'grayscale':
        return ImageOps.grayscale(image).convert('RGB')
    elif transform_type == 'flip_horizontal':
        return ImageOps.mirror(image)
    elif transform_type == 'flip_vertical':
        return ImageOps.flip(image)
    elif transform_type == 'scale':
        factor = transform['factor']
        new_size = (int(image.width * factor), int(image.height * factor))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    elif transform_type == 'blur':
        radius = transform['radius']
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    elif transform_type == 'rotate':
        angle = transform['angle']
        return image.rotate(angle, expand=True)
    else:
        raise ValueError(f"Unknown transformation type: {transform_type}")


def process_single_image(args: tuple) -> str:
    """Process a single image with a transformation configuration.

    This function runs in a separate process.
    """
    image_path, transform_path, output_path = args

    # Load transformation config
    with open(transform_path, 'r') as f:
        data = json.load(f)
    transformations = data.get('transformations', [])

    # Load and process image
    image = Image.open(image_path)
    result = image.copy()

    for transform in transformations:
        result = apply_transformation(result, transform)

    # Ensure output directory exists and save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(output_path)

    image.close()
    result.close()

    return output_path


def process_images_parallel(
    image_dir: str,
    transformation_dir: str,
    output_dir: str,
    get_output_path,
    max_workers: int = None,
) -> None:
    """Process all images in parallel using multiple processes."""

    # Collect all work items
    image_files = [
        f
        for f in Path(image_dir).iterdir()
        if f.suffix.lower() in ('.png', '.jpg', '.jpeg')
    ]
    transform_files = list(Path(transformation_dir).glob('*.json'))

    work_items = []
    for transform_file in transform_files:
        for image_file in image_files:
            output_path = get_output_path(str(image_file), str(transform_file))
            work_items.append((str(image_file), str(transform_file), output_path))

    # Process in parallel using multiple CPU cores
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single_image, work_items))

    print(f"Processed {len(results)} images")
```



## Interview Questions

The interviewer will likely ask how you made the code faster. Be ready to explain the difference between Threading and Multiprocessing.

### Why Multiprocessing?

**Question**: Why did you use `ProcessPoolExecutor` instead of `ThreadPoolExecutor`?

**Key Points to Discuss**:

| Feature | ProcessPoolExecutor | ThreadPoolExecutor |
| :--- | :--- | :--- |
| **Best For** | CPU Tasks (Math, Logic) | I/O Tasks (Waiting for data) |
| **GIL Impact** | Bypasses GIL (Fast) | Stuck by GIL (Slow for CPU) |
| **Memory** | Separate memory per process | Shared memory |
| **Overhead** | High (Slow to start) | Low (Fast to start) |

**Why use it here?**

- Image changes (blur, rotate) require heavy math. This is **CPU-intensive**.
- The Python **GIL (Global Interpreter Lock)** prevents threads from running Python code at the exact same time.
- Processes run in their own memory space. This lets them use all CPU cores at once.
**When is Threading better?**

- Downloading files, waiting for a database, or reading files from a slow drive (**I/O-bound**).
- When tasks spend most of their time waiting.
**The GIL Explained Simply:**

```text
Thread 1: [Work] [Wait] [Work] [Wait]
Thread 2:      [Wait] [Work]  [Wait] [Work]
                    ↑ Only one thread works at a time

Process 1: [Work] [Work] [Work]
Process 2: [Work] [Work] [Work]
                    ↑ Both work at the same time
```



**Advanced Answer:**

- This problem has both I/O (reading files) and CPU (editing images) work.
- If your hard drive is very slow, threading might work.
- However, image editing is usually heavier than reading the file. This makes the CPU the bottleneck, so Multiprocessing is the correct choice.

### Other Questions

**How do you handle huge images that don't fit in RAM?**

- Process the image in small chunks (tiles) instead of loading the whole thing.
**How do you make this code safe for production?**

- Check if the JSON is valid.
- Add error handling so one bad image doesn't crash the whole program.
- Add logging to track progress.
**How do you scale to millions of images?**

- One computer isn't enough. Use a message queue to send work to many different computers.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100010*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-image-processing)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
