
def fnv1a(b):
    h = 2166136261
    for c in b:
        h = (h ^ c) * 16777619

    return h & 0xFFFFFFFF


class HashMap:

    """ Hash table using open addressing insertion technique """
    def __init__(self, initializer=None, *, chunksize=65535, loadfactor=0.75):
        self.chunksize = chunksize
        self.loadfactor = loadfactor
        self.capacity = 0
        self.indices = None
        # These are parallel arrays
        self.hashes = []
        self.keys = []
        self.values = []
        self._allocate_next(firstcall=True)
        if initializer:
            self.insert_all(initializer)

    def insert(self, key, value, *, byhash=False):
        if isinstance(key, str):
            key = bytes(key, "ascii")

        if not byhash:
            hsh = fnv1a(key)
        else:
            hsh = key

        idx = hsh % self.capacity
        inserted = False
        substituted = False
        while not inserted:
            cidx = self.indices[idx]
            # We can insert either if it's not present or if it's a tombstone
            if cidx is None or cidx is False:
                inserted = True
                self.indices[idx] = len(self.hashes)
                self.hashes.append(hsh)
                self.values.append(value)
                self.keys.append(key)
            else:
                if self.hashes[cidx] == hsh:
                    inserted = True
                    substituted = True
                    self.values[cidx] = value
                else:
                    idx += 1
                    if idx == self.capacity:
                        idx = 0

        if self.overloaded:
            self._allocate_next()

        return substituted

    def insert_all(self, it):
        if isinstance(it, dict):
            it = it.items()

        for key, value in it:
            self.insert(key, value)

    def get(self, key, *, byhash=False):
        if isinstance(key, str):
            key = bytes(key, "ascii")

        if not byhash:
            hsh = fnv1a(key)
        else:
            hsh = key

        idx = hsh % self.capacity
        while True:
            cidx = self.indices[idx]
            if cidx is None:
                # Not present
                return

            if self.hashes[cidx] == hsh:
                return self.values[cidx]

            idx += 1
            if idx == self.capacity:
                idx = 0

    def remove(self, key, *, byhash=False):
        if isinstance(key, str):
            key = bytes(key, "ascii")

        if not byhash:
            hsh = fnv1a(key)
        else:
            hsh = key

        idx = hsh % self.capacity
        while True:
            cidx = self.indices[idx]
            if cidx is None:
                # Not present
                return

            if self.hashes[cidx] == hsh:
                # Make a tombstone
                self.indices[idx] = False
                self.hashes.pop(cidx)
                self.values.pop(cidx)
                self.keys.pop(cidx)

                break
            else:
                idx += 1
                if idx == self.capacity:
                    idx = 0

    @property
    def overloaded(self):
        return len(self.hashes) / self.capacity > self.loadfactor

    @property
    def currentload(self):
        return len(self.hashes) / self.capacity

    @property
    def count(self):
        return len(self.hashes)

    def _allocate_next(self, *, firstcall=False):
        self.capacity += self.chunksize
        self.indices = [None] * self.capacity

        if not firstcall:
            for cidx, h in enumerate(self.hashes):
                idx = h % self.capacity
                while True:
                    if self.indices[idx] is None:
                        self.indices[idx] = cidx
                        break

                    idx += 1
                    if idx == self.capacity:
                        idx = 0

        if self.chunksize < 2**20:
            self.chunksize *= 2

    def __contains__(self, key):
        return self.get(key) is not None


class HashSet(HashMap):

    def insert(self, value, *, byhash=False):
        if isinstance(value, str):
            value = bytes(value, "ascii")

        if not byhash:
            hsh = fnv1a(value)
        else:
            hsh = value

        idx = hsh % self.capacity
        inserted = False
        while not inserted:
            cidx = self.indices[idx]
            # We can insert either if it's not present or if it's a tombstone
            if cidx is None or cidx is False:
                inserted = True
                self.indices[idx] = len(self.hashes)
                self.hashes.append(hsh)
                self.values.append(value)
            else:
                if self.hashes[cidx] == hsh:
                    inserted = True
                    self.values[cidx] = value
                else:
                    idx += 1
                    if idx == self.capacity:
                        idx = 0

        if self.overloaded:
            self._allocate_next()

    def remove(self, value):
        if isinstance(value, str):
            value = bytes(value, "ascii")

        hsh = fnv1a(value)
        idx = hsh % self.capacity
        while True:
            cidx = self.indices[idx]
            if cidx is None:
                # Not present
                return

            if self.hashes[cidx] == hsh:
                # Make a tombstone
                self.indices[idx] = False
                self.hashes.pop(cidx)
                self.values.pop(cidx)
                break
            else:
                idx += 1
                if idx == self.capacity:
                    idx = 0
