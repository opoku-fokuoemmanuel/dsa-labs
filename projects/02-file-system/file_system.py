class FileNode:
    def __init__(self):
        self.name = ""
        self.is_file = False
        self.firstChild = None
        self.nextSibling = None
        self.parent = None

    def setName(self, name):
        self.name = name

    def setAsFile(self):
        self.is_file = True


class FileSystem:
    def __init__(self):
        self.root = FileNode()
        self.root.setName("<root>")
        self.root.is_file = False
        self.root.parent = None
        self.cwd = self.root

    # --- Shared helpers ---

    def _resolve_start(self, path):
        """Return the starting node based on whether path is absolute or relative."""
        return self.root if path.startswith('/') else self.cwd

    def get_node(self, parent, name):
        """Navigate one step — directories only."""
        if name == ".":
            return parent
        if name == "..":
            return parent.parent if parent.parent else parent
        child = parent.firstChild
        while child:
            if child.name == name and not child.is_file:
                return child
            child = child.nextSibling
        raise ValueError(f"Directory not found: '{name}'")

    def _find_node(self, parent, name):
        """Find any child node (file or directory) by name."""
        child = parent.firstChild
        while child:
            if child.name == name:
                return child
            child = child.nextSibling
        return None

    def _has_child_dir(self, parent, name):
        """Check if a directory child with this name exists."""
        child = parent.firstChild
        while child:
            if child.name == name and not child.is_file:
                return True
            child = child.nextSibling
        return False

    def _has_any_child(self, parent, name):
        """Check if any child (file or dir) with this name exists."""
        return self._find_node(parent, name) is not None

    def _create_dir(self, parent, name):
        new_dir = FileNode()
        new_dir.setName(name)
        new_dir.is_file = False
        new_dir.parent = parent
        if not parent.firstChild:
            parent.firstChild = new_dir
        else:
            temp = parent.firstChild
            while temp.nextSibling:
                temp = temp.nextSibling
            temp.nextSibling = new_dir
        return new_dir

    def _create_file(self, parent, name):
        new_file = FileNode()
        new_file.setName(name)
        new_file.setAsFile()
        new_file.parent = parent
        if not parent.firstChild:
            parent.firstChild = new_file
        else:
            temp = parent.firstChild
            while temp.nextSibling:
                temp = temp.nextSibling
            temp.nextSibling = new_file
        return new_file

    # --- mkdir ---
    def mkdir(self, path):
        parts = [p for p in path.strip('/').split('/') if p]
        if not parts:
            return

        # FIX 1: respect absolute vs relative path
        current = self._resolve_start(path)

        for name in parts:
            existing = self._find_node(current, name)
            if existing:
                if existing.is_file:
                    # FIX 3: catch conflict where a file already occupies this name
                    raise ValueError(f"Cannot create directory '{name}': file exists")
                current = existing
            else:
                current = self._create_dir(current, name)

    # --- touch ---
    def touch(self, path):
        parts = [p for p in path.strip('/').split('/') if p]
        if not parts:
            return

        # FIX 1: respect absolute vs relative path
        current = self._resolve_start(path)

        for name in parts[:-1]:
            if self._has_child_dir(current, name):
                current = self.get_node(current, name)
            else:
                # check it's not blocked by a file with the same name
                existing = self._find_node(current, name)
                if existing and existing.is_file:
                    raise ValueError(f"Cannot create directory '{name}': file exists")
                current = self._create_dir(current, name)

        filename = parts[-1]
        existing = self._find_node(current, filename)
        if existing:
            if existing.is_file:
                return existing  # idempotent — file already exists, that's fine
            raise ValueError(f"Cannot create file '{filename}': directory exists")
        return self._create_file(current, filename)

    # --- cd ---
    def cd(self, path):
        parts = [p for p in path.strip('/').split('/') if p]
        if not parts:
            self.cwd = self.root if path == '/' else self.cwd
            return

        current = self._resolve_start(path)

        for name in parts:
            current = self.get_node(current, name)
        if current.is_file:
            raise ValueError(f"Not a directory: '{path}'")
        self.cwd = current

    # --- ls ---
    def ls(self, path=""):
        parts = [p for p in path.strip('/').split('/') if p]
        if not parts:
            current = self.cwd
        else:
            current = self._resolve_start(path)
            for name in parts:
                current = self.get_node(current, name)
        if current.is_file:
            raise ValueError("Not a directory")
        names = []
        child = current.firstChild
        while child:
            names.append(child.name)
            child = child.nextSibling
        return names

    # --- pwd ---
    def pwd(self):
        """Return the current working directory as a path string."""
        if self.cwd is self.root:
            return "/"
        parts = []
        node = self.cwd
        while node is not self.root:
            parts.append(node.name)
            node = node.parent
        return '/' + '/'.join(reversed(parts))


# === TESTS ===
if __name__ == "__main__":
    fs = FileSystem()

    print("=== File System Tests ===\n")

    # absolute mkdir
    fs.mkdir("/home/emmanuel/projects")
    assert fs.ls("/") == ["home"], f"Expected ['home'], got {fs.ls('/')}"
    print("✅  mkdir absolute path works")

    # absolute touch
    fs.touch("/home/emmanuel/projects/notes.txt")
    assert fs.ls("/home/emmanuel/projects") == ["notes.txt"]
    print("✅  touch absolute path works")

    # cd then relative ls
    fs.cd("/home/emmanuel")
    assert fs.ls() == ["projects"]
    print("✅  cd + relative ls works")

    # relative touch respects cwd
    fs.touch("docs/todo.txt")
    assert "docs" in fs.ls()
    print("✅  touch relative path respects cwd")

    # touch existing file is idempotent
    fs.touch("/home/emmanuel/projects/notes.txt")
    assert fs.ls("/home/emmanuel/projects") == ["notes.txt"]
    print("✅  touch on existing file is idempotent")

    # mkdir on existing file raises
    try:
        fs.mkdir("/home/emmanuel/projects/notes.txt")
        print("❌  mkdir on file should have raised")
    except ValueError:
        print("✅  mkdir on existing file raises correctly")

    # touch on existing dir raises
    try:
        fs.touch("/home/emmanuel/projects")
        print("❌  touch on directory should have raised")
    except ValueError:
        print("✅  touch on existing directory raises correctly")

    # pwd
    fs.cd("/home/emmanuel/projects")
    assert fs.pwd() == "/home/emmanuel/projects"
    print("✅  pwd works correctly")

    # cd to root
    fs.cd("/")
    assert fs.pwd() == "/"
    print("✅  cd to root works")

    # .. navigation
    fs.cd("/home/emmanuel/projects")
    fs.cd("..")
    assert fs.pwd() == "/home/emmanuel"
    print("✅  cd .. works")

    print("\nAll tests passed!")
