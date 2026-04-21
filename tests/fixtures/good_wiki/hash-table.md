---
title: "Hash Table"
slug: "hash-table"
tags: ["data-structures", "computer-science", "hashing"]
summary: "A hash table maps keys to values using a hash function, providing O(1) average-case lookup, insert, and delete."
related: ["binary-search"]
updated: "2024-02-10"
---

# Hash Table

A hash table (also called a hash map) stores key-value pairs and uses a **hash function** to map keys to array indices, enabling near-constant-time operations.

## Hash Table Collision Resolution

Two main strategies handle index collisions:

- **Chaining:** each slot holds a linked list of entries that hash to the same index.
- **Open addressing:** on collision, probe to the next available slot (linear, quadratic, or double hashing).

## Hash Table Load Factor

The load factor $\alpha = n/m$ (items $n$ over slots $m$) controls performance:

- $\alpha < 0.75$ keeps average probe length near 1 for most implementations.
- When $\alpha$ exceeds the threshold, the table **resizes** (typically doubles) and rehashes all entries — $O(n)$ amortized over operations.

```python
# Python dict is a hash table; direct usage:
table: dict[str, int] = {}
table["key"] = 42
value = table.get("key", 0)
```
