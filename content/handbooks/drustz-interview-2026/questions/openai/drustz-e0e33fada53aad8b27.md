---
id: drustz-e0e33fada53aad8b27
section: openai
order: 2
level: A
title: Memory Allocator
quick: locally-saved-topic-editorial · Memory Allocator
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/company/openai/memory-allocator
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Memory Allocator

## Problem Statement

You need to build a system that manages a block of computer memory. Your tool should work like `malloc()` and `free()` in C. It handles asking for memory (allocation) and giving it back (deallocation).

Your `MemoryAllocator` must:

- Start with a set total amount of memory.
- Give out unbroken (contiguous) blocks of memory.
- Take back memory when it is no longer needed.
- Fix gaps in memory (fragmentation).
- Report errors if a request is invalid or if there is no space left.

## Core Requirements

You must write a `MemoryAllocator` class with these specific features:

### Initialization

```text
def __init__(self, total_capacity: int)
```



- **total_capacity**: The total size of the memory in bytes.
- The system starts with all memory marked as "free" (empty).

### Methods

#### 1. `allocate(size: int) -> int`

This asks for a block of memory.

- **Input**: `size` (How much memory you need).
- **Output**: The starting index (address) of the new block.
- **How it works**:

Look for the first empty spot that is big enough (First-fit strategy).
- Mark that spot as "taken".
- Return the starting address.
- **Errors**:

Raise an error if `size` is zero or negative.
- Raise an error if there isn't enough contiguous memory.

#### 2. `free(address: int, size: int) -> None`

This returns memory back to the system.

- **Input**:

`address`: The starting index of the block.
- `size`: How big the block is.
- **How it works**:

Mark this section of memory as "free".
- Check if the memory right next to it is also free. If yes, join them together to make one big empty spot.
- **Errors**:

Raise an error if the address is outside the memory limits.
- Raise an error if you try to free memory that wasn't allocated.
- Raise an error if the size is wrong.

## Part 1: Basic Approach

We will use a **Linked List** to track the empty (free) spots in memory.

### Data Structure

Use a "doubly-linked list". Each node in the list represents an empty gap in memory. Each node has:

- `start`: The starting address.
- `size`: How big the gap is.
- `next` / `prev`: Pointers to the neighbor nodes.
**Important**: Keep this list sorted by address (lowest address first). This makes it easy to merge gaps later.

### How to Allocate

- **Strategy**: First-fit.
- Walk through the list from the start.
- Stop at the first node that is big enough.
- **Case 1**: The node is the exact size needed. Remove it from the list.
- **Case 2**: The node is bigger than needed. Make the node smaller (update its start address and size).

### How to Free (Deallocate)

When memory is freed, check its neighbors to see if you can merge them. There are 4 cases:

- **No Merge**: The freed block has allocated memory on both sides. Just add a new node to the list.
- **Merge Left**: The block sits right after an existing empty node. Make the left node bigger.
- **Merge Right**: The block sits right before an existing empty node. Make the freed block bigger and remove the right node.
- **Merge Both**: The block fills a gap between two empty nodes. Combine all three into one large node.

### Usage Example

```python
# Start with 100 units of memory
allocator = MemoryAllocator(100)

# Ask for 20 units
addr1 = allocator.allocate(20)  # Returns 0
# Memory: [Allocated(0-19)] [Free(20-99)]

# Ask for 30 units
addr2 = allocator.allocate(30)  # Returns 20
# Memory: [Allocated(0-19)] [Allocated(20-49)] [Free(50-99)]

# Ask for 40 units
addr3 = allocator.allocate(40)  # Returns 50
# Memory: [Allocated(0-19)] [Allocated(20-49)] [Allocated(50-89)] [Free(90-99)]

# Free the middle block
allocator.free(20, 30)
# Memory: [Allocated(0-19)] [Free(20-49)] [Allocated(50-89)] [Free(90-99)]

# Ask for 25 units (it will use the gap we just made)
addr4 = allocator.allocate(25)  # Returns 20
# Memory: [Allocated(0-19)] [Allocated(20-44)] [Free(45-49)] [Allocated(50-89)] [Free(90-99)]

# Free the first block
allocator.free(0, 20)
# Memory: [Free(0-19)] [Allocated(20-44)] [Free(45-49)] [Allocated(50-89)] [Free(90-99)]

# Free the second block (this merges with gaps on BOTH sides)
allocator.free(20, 25)
# Memory: [Free(0-49)] [Allocated(50-89)] [Free(90-99)]
```



## Part 2: Complexity and Improvements

After coding the basic version, discuss these points:

### Time Complexity

- **Allocation**: **O(n)**. You might have to check every free block to find space.
- **Deallocation**: **O(n)**. You might have to search the list to find the right spot to insert or merge the freed block.

### Space Complexity

- **O(m)** where `m` is the number of free blocks.
- If memory is very chopped up (fragmented), this list can get long.

### Weaknesses

- **External Fragmentation**: Over time, you get many tiny empty gaps. You might have 100 bytes free total, but if they are in 10-byte chunks, you cannot allocate a 50-byte block.
- **Slow Search**: Scanning the list takes O(n) time.
- **No Moving**: You cannot move allocated data to close the gaps.

### How to Optimize

**To Fix Fragmentation:**

- **Segregated Free Lists**: Keep different lists for different sizes (e.g., one list for small blocks, one for large). This is faster and cleaner.
- **Best-Fit Strategy**: Don't just take the *first* block. Find the *smallest* block that fits. This saves large blocks for later but takes longer to search.
- **Buddy System**: Divide memory into powers of 2 (e.g., 2, 4, 8, 16). This makes merging very fast and easy.
**To Improve Speed:**

- **Balanced Binary Search Tree (BST)**: Organize free blocks in a tree. This makes searching and adding blocks take **O(log n)** time instead of O(n).
- **Bitmap**: If all blocks are the same size, use a bitmap. This allows **O(1)** allocation.
**To Improve Space:**

- **Implicit Free List**: Don't use a separate Python list. Write the block size and status directly inside the memory itself (in a header).
- **Boundary Tags**: Add a footer to every block. This lets you look backward in memory instantly (**O(1)**) to merge with the previous block.

## Interview Questions

Be ready to answer these follow-ups:

- How would you handle **alignment** (e.g., all addresses must be multiples of 8)?
- How do you stop a user from freeing memory that is currently in use?
- How would you implement `realloc()` (resizing a block while keeping the data)?
- How do you make this **Thread-Safe**?
- How is this different from real hardware memory management?

## Coding Tips

### Edge Cases

- User asks for size 0 or negative.
- User frees an address that doesn't exist.
- "Double-free": User tries to free the same block twice.
- Memory is full or too fragmented to fit the request.

### Testing Strategy

Write tests for:

- Normal add/remove steps.
- Using up all memory.
- Creating gaps and filling them.
- Merging scenarios (Left, Right, Both).
- Boundaries (Address 0 and the very end of memory).

## Code Solution

```python
class FreeBlock:
    def __init__(self, start: int, size: int):
        self.start = start
        self.size = size
        self.next = None
        self.prev = None


class MemoryAllocator:
    def __init__(self, total_capacity: int):
        if total_capacity <= 0:
            raise ValueError("Total capacity must be positive")

        self.capacity = total_capacity

        # Start with one big free block covering all memory
        self.free_list_head = FreeBlock(0, total_capacity)

        # NOTE: We use this dictionary to check for errors/debugging.
        # A true space-optimized version would store metadata inside the memory blocks.
        self.allocated = {}  # {address: size}

    def allocate(self, size: int) -> int:
        if size <= 0:
            raise ValueError("Allocation size must be positive")

        # First-fit strategy: Find first block that is big enough
        # The list is always sorted by address
        current = self.free_list_head
        while current:
            if current.size >= size:
                # We found a spot
                allocated_address = current.start

                if current.size == size:
                    # Perfect fit: Remove the whole block from free list
                    self._remove_free_block(current)
                else:
                    # Block is too big: Shrink it
                    current.start += size
                    current.size -= size

                # Record the allocation
                self.allocated[allocated_address] = size

                return allocated_address

            current = current.next

        # If we get here, no space was found
        raise MemoryError(
            f"Cannot allocate {size} units: insufficient contiguous memory"
        )

    def free(self, address: int, size: int) -> None:
        if address < 0 or address >= self.capacity:
            raise ValueError(f"Invalid address: {address}")

        if size <= 0:
            raise ValueError("Size must be positive")

        if address + size > self.capacity:
            raise ValueError(f"Free range exceeds memory bounds")

        # Check if this memory was actually allocated correctly
        if address not in self.allocated or self.allocated[address] != size:
            raise ValueError(
                f"Invalid free: no allocation at address {address} with size {size}"
            )

        # Stop tracking this as allocated
        del self.allocated[address]

        # Calculate where the block ends
        freed_end = address + size

        current = self.free_list_head
        prev_block = None

        # Find the correct spot in the list to keep it sorted by address
        while current and current.start < address:
            prev_block = current
            current = current.next

        # Check if we can merge with neighbors
        can_merge_with_prev = prev_block and (
            prev_block.start + prev_block.size == address
        )
        can_merge_with_next = current and (freed_end == current.start)

        if can_merge_with_prev and can_merge_with_next:
            # Merge with BOTH sides
            prev_block.size += size + current.size
            self._remove_free_block(current)
        elif can_merge_with_prev:
            # Merge with PREVIOUS only
            prev_block.size += size
        elif can_merge_with_next:
            # Merge with NEXT only
            current.start = address
            current.size += size
        else:
            # No merge - just add a new node to the list
            new_block = FreeBlock(address, size)
            self._insert_free_block_after(prev_block, new_block)

    def _remove_free_block(self, block: FreeBlock):
        """Helper: Remove a node from the linked list"""
        if block.prev:
            block.prev.next = block.next
        else:
            # We are removing the head
            self.free_list_head = block.next

        if block.next:
            block.next.prev = block.prev

    def _insert_free_block_after(self, prev_block: FreeBlock, new_block: FreeBlock):
        """Helper: Add a new node after 'prev_block'"""
        if prev_block is None:
            # Insert at the very front (Head)
            new_block.next = self.free_list_head
            if self.free_list_head:
                self.free_list_head.prev = new_block
            self.free_list_head = new_block
        else:
            new_block.next = prev_block.next
            new_block.prev = prev_block
            if prev_block.next:
                prev_block.next.prev = new_block
            prev_block.next = new_block

    def get_free_memory(self) -> int:
        """Helper: Count total free space"""
        total = 0
        current = self.free_list_head
        while current:
            total += current.size
            current = current.next
        return total

    def get_largest_free_block(self) -> int:
        """Helper: Find the biggest single gap"""
        max_size = 0
        current = self.free_list_head
        while current:
            max_size = max(max_size, current.size)
            current = current.next
        return max_size
```



## Similar Problems & Notes

- **Practice**: LeetCode 2502: Design Memory Allocator (A simpler version of this).
- **Concepts**: Operating Systems, Garbage Collection, Caching policies.
- **Note**: Real-world allocators (like `malloc`) are much more complex. They use many of the optimization strategies listed above combined together.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100050*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/memory-allocator)
- [相关来源](https://www.1point3acres.com/bbs/thread-1179374-1-1.html)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
