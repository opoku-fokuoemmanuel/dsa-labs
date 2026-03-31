
# 🗂️ In-Memory File System

A fully functional in-memory file system built from scratch in Python — no `os` module, no shortcuts. Real directory traversal, path resolution, and file management powered by a custom tree data structure.

```
mkdir /home/emmanuel/projects
touch /home/emmanuel/projects/notes.txt
cd /home/emmanuel
ls
# → ['projects']
pwd
# → /home/emmanuel
```

---

## Data Structure

The file system is a tree where every node is a `FileNode` — representing either a file or a directory. Instead of storing children in a list, it uses the **left-child right-sibling** representation:

```
FileNode
  ├── name
  ├── is_file
  ├── firstChild    →  points to first child node
  ├── nextSibling   →  points to next node at same level
  └── parent        →  points back up to parent
```

This is a classic technique for representing n-ary trees (trees where each node can have any number of children) using only two pointers per node — the same structure used in real OS implementations and compilers for parse trees.

A directory tree like this:

```
root/
├── home/
│   └── emmanuel/
│       └── notes.txt
└── etc/
```

Is stored internally like this:

```
root
 └─firstChild→ home ─nextSibling→ etc
                └─firstChild→ emmanuel
                               └─firstChild→ notes.txt
```

---

## Commands

| Command | Description |
|---------|-------------|
| `mkdir(path)` | Create directory (and all intermediate dirs) |
| `touch(path)` | Create a file, creating parent dirs as needed |
| `cd(path)` | Change current working directory |
| `ls(path)` | List contents of a directory |
| `pwd()` | Print current working directory path |

All commands support:
- **Absolute paths** starting with `/`
- **Relative paths** from current working directory
- `.` (current dir) and `..` (parent dir) navigation

---

## How it works

### Path Resolution
Every command calls `_resolve_start(path)` — returns `root` for absolute paths, `cwd` for relative ones. Then walks the tree node by node from there. `.` returns the current node, `..` returns `node.parent`.

### mkdir
Walks the path, creating missing intermediate directories along the way — same behaviour as `mkdir -p` in Unix. Raises an error if a file already occupies any name in the path.

### touch
Navigates to the parent directory (creating intermediate dirs as needed), then appends a file node at the end of the sibling chain. Idempotent — calling `touch` on an existing file does nothing.

### cd
Resolves the path and updates `self.cwd` — the pointer that tracks where you currently are in the tree.

### ls
Walks the `firstChild → nextSibling` chain of the target directory and collects all child names.

### pwd
Walks from `cwd` back up to root via `node.parent`, collecting names, then reverses them into a `/`-separated path string.

---

## Run it

```bash
git clone https://github.com/opoku-fokuoemmanuel/dsa-labs
cd dsa-labs/projects/02-file-system
python file_system.py
```

No dependencies — standard library only.

---

## DSA concepts used

| Concept | Where |
|---------|-------|
| N-ary Tree | Overall file system structure |
| Left-child right-sibling representation | `FileNode` pointer layout |
| Linked List traversal | Walking siblings with `nextSibling` |
| Tree traversal | Path resolution in `cd`, `ls`, `mkdir`, `pwd` |
| Pointer manipulation | Node insertion in `_create_dir`, `_create_file` |

---

## Planned improvements

- `rm` — delete files and directories
- `mv` / `cp` — move and copy nodes within the tree
- `tree` — pretty-print the full directory tree
- `find` — search for a file or directory by name
- File contents — let files actually store and retrieve text data

---

*Part of the [dsa-labs](https://github.com/opoku-fokuoemmanuel/dsa-labs) marathon.*
