"""
A decider that uses MD5 hashes.
"""
import dbm

from .decider import Decider, Decision
from ...paths import SourcePath
from ...utils.list import md5hash
from ...utils.string import hashtxt


class Md5Decision(Decision):
    """A decision for the Md5Decider"""

    _hash = None

    def build_needed(self, inputs, output, reset=False):
        build_needed = super().build_needed(inputs, output)

        if build_needed:
            # A build is needed if some of the files don't exist
            return True

        # At this stage, the files exist but we're not sure whether their
        # md5 hashes have changed. See if there's an existing (cached) hash
        db = self.parent_decider.db
        assert db is not None

        # Check to see there's an existing hash
        key = str(output)
        cached_hash = db.get(key, None)

        # Reset the cached hash, if needed
        if reset:
            # Recalculate the hash
            self._hash = None
            current_hash = self.calculate_hash(inputs=inputs, output=output)
            db[key] = current_hash
            return False
        else:
            return (cached_hash !=
                    self.calculate_hash(inputs=inputs, output=output))

    def calculate_hash(self, inputs, output):
        """Calculate the md5 hash for the inputs, output and args."""
        if self._hash is None:
            sorted_inputs = list(sorted([i for i in inputs
                                         if isinstance(i, str)]))
            input_files = list(sorted(p for p in inputs
                                      if isinstance(p, SourcePath)))
            sorted_inputs += [hashtxt(p.read_bytes(), truncate=None)
                              for p in input_files]
            output_file = hashtxt(output.read_bytes(), truncate=None)

            hash = md5hash([sorted_inputs, output_file])

            # Convert the hash to bytes, which will be stored in the database
            hash = bytes(hash, 'ascii')
            self._hash = hash
        return self._hash


class Md5Decider(Decider):
    """A decider that uses md5 hashes to compute whether a build is needed."""

    name = None
    decision_cls = Md5Decision

    _db = None

    def __init__(self, env, name=None):
        self.name = name
        super().__init__(env)

    def __del__(self):
        # Close the database if it's open
        if self._db is not None:
            self.db.close()

    @property
    def db_path(self):
        """The path for the database file"""
        name = self.name if self.name is not None else 'md5decider'
        return str(self.environment.cache_path / name)

    @property
    def db(self):
        if self._db is None:
            self._db = dbm.open(self.db_path, 'c')
        return self._db
