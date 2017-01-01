# Python >3.5 required
import pickle
import hashlib
import os
import time
import struct

class Block:
    def __init__(self, previous_block_hash, transactions=[], difficulty=4):
        self.transactions = transactions
        self.merkle_tree = MerkleTree(transactions)
        self.header = BlockHeader(previous_block_hash, difficulty, self.merkle_tree.root_hash())
    
    def mine(self):
        hash = '1' * self.header.difficulty
        target = '0' * self.header.difficulty
        while (hash[0:self.header.difficulty] != target):
            hash = self.header.hash(nonce=True)
        return hash

    def struct(self):
        transactions_struct = b''.join([t.struct() for t in self.transactions])
        return self.header.struct() + transactions_struct

    def order_transactions(self):
        pass


class BlockHeader:
    def __init__(self, previous_block_hash, difficulty, merkle_root_hash):
        self.version = 1
        self.previous_block_hash = previous_block_hash
        self.difficulty = difficulty
        self.timestamp = int(time.time())
        self.merkle_root_hash = merkle_root_hash
        self.nonce = '0' * 16
    
    def struct(self):
        return struct.pack('I32s32sII4s', self.version, bytes.fromhex(self.previous_block_hash), 
            bytes.fromhex(self.merkle_root_hash), self.timestamp, self.difficulty, bytes.fromhex(self.nonce))
        
    def hash(self, nonce=False):
        if nonce:
            self.timestamp = int(time.time())
            self.nonce = os.urandom(4).hex()
        return hashlib.sha256(self.struct()).hexdigest()
        
        
class Transaction:
    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount

    def struct(self):
        return struct.pack('32s32sI', bytes.fromhex(self.from_address), bytes.fromhex(self.to_address), self.amount)

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
