# Python >3.5 required
import pickle
import hashlib
import os

class Block:
    def __init__(self, previous_block_hash, transactions=[], difficulty=4):
        self.header = BlockHeader(previous_block_hash, difficulty)
        self.transactions = transactions
        self.merkle = MerkleTree(transactions)
    
    def mine(self):
        hash = '1' * self.difficulty
        target = '0' * self.difficulty
        while (hash[0:self.difficulty] != target):
            hash = self.hash(nonce=True)
        return hash

    def hash(self, nonce=False):
        if nonce:
            self.nonce = os.urandom(32)
        return hashlib.sha256(pickle.dumps(self)).hexdigest()

class BlockHeader:
    def __init__(self, previous_block_hash, difficulty):
        self.previous_block_hash = previous_block_hash
        self.difficulty = difficulty
        self.nonce = None
    
    def to_bytes(self):
        
        
class Transaction:
    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount

class MerkleTree:
    def __init__(self, transactions):
        self.layer_sizes = [len(transactions)]
        hashes = [hashlib.sha256(pickle.dumps(t)).digest() for t in transactions]
        self.hash_tree = [d.hex() for d in hashes]
        while len(hashes) > 1:
            parent_hashes = []
            for i in range(0, len(hashes), 2):
                try:
                    children = hashes[i] + hashes[i+1]
                except IndexError: # last group may have only one child
                    children = hashes[i] + hashes[i]
                parent_hashes.append(hashlib.sha256(children).digest())
            self.hash_tree += [d.hex() for d in parent_hashes]
            self.layer_sizes.append(len(parent_hashes))
            hashes = parent_hashes
    
    def root_hash(self):
        return self.hash_tree[-1]

    def get_hash(self, height, across):
        """
        get a node from the hash tree by height and across index
        height of a leaf node is 0
        across is the zero-indexed count from left to right of the node at a specified height
        """
        index = sum(self.layer_sizes[0:height]) + across
        return self.hash_tree[index]
