import hashlib
import numpy as np


class SimHash:
    def __init__(self, hash_size=64):
        self.hash_size = hash_size

    def _hash(self, token):
        """Hash a token into a fixed-size integer."""
        return int(hashlib.md5(token.encode()).hexdigest(), 16) & ((1 << self.hash_size) - 1)

    # CHATGBT CODE FOR A LIGHT-WEIGHT HASHER, LOW PRIORITY NGL
    # def _hash(self, token):
    #     """Hash a token into a fixed-size integer using Python's built-in hash."""
    #     return hash(token) & ((1 << self.hash_size) - 1)

    def compute(self, tokens):
        # EDGE CASE IF TEXT IS EMPTY
        # if not text:
        #     return 0  # Return 0 for empty input

        """Compute the SimHash fingerprint of the input text."""
        # Simple tokenization by whitespace
        vector = np.zeros(self.hash_size)

        for token in tokens:
            token_hash = self._hash(token)
            for i in range(self.hash_size):
                bit = (token_hash >> i) & 1
                vector[i] += 1 if bit else -1

        # Convert vector to final hash
        fingerprint = 0
        for i in range(self.hash_size):
            if vector[i] > 0:
                fingerprint |= (1 << i)

        return fingerprint

    def hamming_distance(self, hash1, hash2):
        """Compute the Hamming distance between two hash values."""
        return bin(hash1 ^ hash2).count('1')