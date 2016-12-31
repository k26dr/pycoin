#!/usr/bin/python

import pickle
import hashlib
import os

class Block:
    def __init__(self, previous_block_hash, transactions=[], difficulty=4):
        self.previous_block_hash = previous_block_hash
        self.transactions = transactions
        self.nonce = None
        self.difficulty = difficulty
    
    def mine(self):
        hash = '1' * self.difficulty
        target = '0' * self.difficulty
        while (hash[0:self.difficulty] != target):
            hash = self.hash(nonce=True)

    def hash(self, nonce=False):
        if nonce:
            self.nonce = os.urandom(32)
        return hashlib.sha256(pickle.dumps(self)).hexdigest()

class Transaction:
    def __init__(self, from_address, to_address, amount):
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount

class MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        hashes = [hashlib.sha256(pickle.dumps(t)).digest() for t in transactions]
        while len(hashes) > 1:
            parent_hashes = []
            for i in range(0, len(hashes), 2):
                try:
                    children = hashes[i] + hashes[i+1]
                except IndexError: # last group may have only one child
                    children = hashes[i] + hashes[i]
                parent_hashes.append(hashlib.sha256(children).digest())
            hashes = parent_hashes
        self.root_hash = hashes[0].hex()

