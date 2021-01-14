
def fnv1a(b):
    h = 2166136261
    for c in b:
        h = (h ^ c) * 16777619

    return h & 0xFFFFFFFF


class HashMap:
    """ Hash table using open addressing insertion technique """
    def __init__(self, initializer=None, *, chunksize=16, loadfactor=0.75, growfactor=2, maxsize=2**19):
        self.chunksize = chunksize
        self.loadfactor = loadfactor
        self.growfactor = growfactor
        self.maxsize = maxsize
        self.capacity = chunksize
        self.indices = [None] * chunksize
        # These are parallel arrays
        self.hashes = []
        self.keys = []
        self.values = []
        if initializer:
            self.insert_all(initializer)

    def insert(self, key, value, *, byhash=False):
        if isinstance(key, str):
            key = bytes(key, "ascii")

        if not byhash:
            hsh = fnv1a(key)
        else:
            hsh = key

        idx = hsh & (self.capacity - 1)
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

        idx = hsh & (self.capacity - 1)
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

        idx = hsh & (self.capacity - 1)
        removed = False
        while not removed:
            cidx = self.indices[idx]
            if cidx is None:
                # Not present
                return

            if self.hashes[cidx] == hsh:
                # Make a tombstone
                self.indices[idx] = False
                # In case we're removing the only one or the last
                # element, just pop the values
                if (cidx == 0 and self.count == 1) or cidx == self.count - 1:
                    self.hashes.pop()
                    self.values.pop()
                    self.keys.pop()
                    break

                # Otherwise, fill the gap
                lasthash = self.hashes[-1]
                lastidx = lasthash & (self.capacity - 1)
                # Resolve collisions once again
                while not removed:
                    lastcidx = self.indices[lastidx]
                    if self.hashes[lastcidx] == lasthash:
                        self.indices[lastidx] = cidx
                        self.hashes[cidx] = self.hashes.pop()
                        self.values[cidx] = self.values.pop()
                        self.keys[cidx] = self.keys.pop()
                        removed = True
                    else:
                        lastcidx += 1
                        if lastcidx == self.capacity:
                            lastcidx = 0
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

    def _allocate_next(self):
        if self.chunksize < self.maxsize:
            self.chunksize *= self.growfactor
            self.capacity = self.chunksize
        else:
            self.capacity *= self.growfactor

        mask = self.capacity - 1
        self.indices = [None] * self.capacity
        for cidx, h in enumerate(self.hashes):
            idx = h & mask

            while True:
                if self.indices[idx] is None:
                    self.indices[idx] = cidx
                    break

                idx += 1
                if idx == self.capacity:
                    idx = 0

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

        idx = hsh & (self.capacity - 1)
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

    def remove(self, value, *, byhash=False):
        if isinstance(key, str):
            key = bytes(key, "ascii")

        if not byhash:
            hsh = fnv1a(key)
        else:
            hsh = key

        idx = hsh & (self.capacity - 1)
        removed = False
        while not removed:
            cidx = self.indices[idx]
            if cidx is None:
                # Not present
                return

            if self.hashes[cidx] == hsh:
                # Make a tombstone
                self.indices[idx] = False
                # In case we're removing the first or the last
                # element, just pop the values
                if (cidx == 0 and self.count == 1) or cidx == self.count - 1:
                    self.hashes.pop()
                    self.values.pop()
                    break

                # Otherwise, fill the gap
                lasthash = self.hashes[-1]
                lastidx = lasthash & (self.capacity - 1)
                # Resolve collisions once again
                while not removed:
                    lastcidx = self.indices[lastidx]
                    if self.hashes[lastcidx] == lasthash:
                        self.indices[lastidx] = cidx
                        self.hashes[cidx] = self.hashes.pop()
                        self.values[cidx] = self.values.pop()
                        removed = True
                    else:
                        lastcidx += 1
                        if lastcidx == self.capacity:
                            lastcidx = 0
            else:
                idx += 1
                if idx == self.capacity:
                    idx = 0
