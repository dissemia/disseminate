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

    db = None

    _hash = None

    def __init__(self, db, inputs, output, args):
        self.db = db
        super().__init__(inputs, output, args)

        # Calculate the hashes if the parent determined that the files exist
        if not self.build_needed:
            # Check to see there's an existing hash
            key = str(self.output)
            current_hash = db.get(key, None)
            self.build_needed = current_hash != self.hash

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and self.hash is not None:
            self.build_needed = False

            # Set the hash in the database
            self.db[str(self.output)] = self.hash

    @property
    def hash(self):
        """Calculate the md5 hash for the inputs, output and args."""
        if self._hash is None:
            sorted_inputs = list(sorted([i for i in self.inputs
                                         if isinstance(i, str)]))
            input_files = list(sorted(p for p in self.inputs
                                      if isinstance(p, SourcePath)))
            sorted_inputs += [hashtxt(p.read_text())
                              for p in input_files]
            output_file = hashtxt(self.output.read_text())

            hash = md5hash([sorted_inputs, output_file, self.args])

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

    @property
    def decision(self):
        def md5decision(db=self, *args, **kwargs):
            return Md5Decision(db=self.db, *args, **kwargs)
        return md5decision
