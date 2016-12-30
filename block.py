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
        pass

            
