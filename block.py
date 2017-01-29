# Python >3.5 required
import pickle
import hashlib
import os
import time
import struct
from ecdsa import SigningKey, SECP256k1

def double_sha256(message):
    return hashlib.sha256(hashlib.sha256(message).digest())

class Block:
    def __init__(self, previous_block_hash, transactions=[], difficulty=4):
        self.transactions = transactions
        self.merkle_tree = MerkleTree(transactions)
        self.header = BlockHeader(previous_block_hash, difficulty, self.merkle_tree.root_hash())
    
    def mine(self):
        hash = '1' * self.header.difficulty
        target = '0' * self.header.difficulty
        while (hash[0:self.header.difficulty] != target):
            hash = self.header.hash(nonce=True).hexdigest()
        return hash

    def struct(self):
        transactions_struct = b''.join([t.struct() for t in self.transactions])
        return self.header.struct() + transactions_struct


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
        return double_sha256(self.struct())


class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    def struct(self):
        num_inputs = len(self.inputs)
        num_outputs = len(self.outputs)
        input_struct = [i.struct() for i in self.inputs]
        output_struct = [o.struct() for o in self.outputs]
        return struct.pack('HH', num_inputs, num_outputs) + inputs_struct + output_struct

    def hash(self):
        return double_sha256(self.struct())

class TransactionInput:
    def __init__(self, input_tx, input_tx_index, checksig):
        self.previous_tx = previous_tx
        self.previous_tx_index = previous_tx_index
        self.checksig = checksig

    def struct(self):
        format = "32sH64s"
        return struct.pack("32sH64s", self.previous_tx, self.previous_tx_index, self.checksig)

class TransactionOutput:
    def __init__(self, value, to_address):
        self.value = value
        self.to_address = to_address

class MerkleTree:
    def __init__(self, transactions):
        self.layer_sizes = [len(transactions)]
        hashes = [t.hash().digest() for t in transactions]
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
