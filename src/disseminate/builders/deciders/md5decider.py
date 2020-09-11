"""
A decider that uses MD5 hashes.
"""
import diskcache

from .decider import Decider, Decision
from .utils_hash import hash_items


class Md5Decision(Decision):
    """A decision for the Md5Decider"""

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
        input_hash, output_hash = self.calculate_hash(inputs=inputs,
                                                      output=output)

        # Check the database hash (input_hash is the key, output_hash is the
        # value)
        key = input_hash
        cached_output_hash = db.get(key, None)

        # Reset the cached hash, if needed
        if reset:
            # Recalculate the hash
            input_hash, output_hash = self.calculate_hash(inputs=inputs,
                                                          output=output)
            db[input_hash] = output_hash
            return False
        else:
            return cached_output_hash != output_hash

    @staticmethod
    def calculate_hash(inputs, output):
        """Calculate the md5 hash for the inputs, output and args."""
        sorted_inputs = sorted(inputs, key=str)
        hash_input = hash_items(*sorted_inputs)
        hash_output = hash_items(output)

        return (hash_input, hash_output)


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
            self._db = diskcache.Cache(self.db_path)
        return self._db
