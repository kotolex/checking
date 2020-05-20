class WriteWrapper:
    """
    Wrapper for mock_open, push all writes to list
    """

    def __init__(self, container: list):
        self.c = container
        self.opened = True

    def flush(self):
        if not self.opened:
            raise IOError('Attempt to write on closed wrapper!')

    def write(self, n):
        if not self.opened:
            raise IOError('Attempt to write on closed wrapper!')
        self.c.append(n)

    def writelines(self, __lines):
        for line in __lines:
            self.write(line)

    def close(self):
        self.opened = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
