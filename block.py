# Python >3.5 required
import pickle
import hashlib
import os
import time
import struct
import pdb
from ecdsa import SigningKey, SECP256k1

def double_sha256(message):
    return hashlib.sha256(hashlib.sha256(message).digest())

class PycoinError(Exception):
    pass

class Block:
    def __init__(self, previous_block_hash, transactions=[]):
        self.transactions = transactions
        self.merkle_tree = MerkleTree(transactions)
        self.header = BlockHeader(previous_block_hash, self.merkle_tree.root_hash())
    
    def mine(self):
        hash = '1' * 64
        while (hash > self.header.difficulty):
            hash = self.header.hash(nonce=True).hexdigest()
        return hash

    def struct(self):
        transactions_struct = b''.join([t.struct() for t in self.transactions])
        return self.header.struct() + transactions_struct


class BlockHeader:
    def __init__(self, previous_block_hash, merkle_root_hash):
        self.version = 1
        self.previous_block_hash = previous_block_hash
        self.difficulty = '0'*4 + 'f'*60
        self.timestamp = int(time.time())
        self.merkle_root_hash = merkle_root_hash
        self.nonce = '0' * 16
    
    def struct(self):
        return struct.pack('I32s32sI32s4s', self.version, bytes.fromhex(self.previous_block_hash), 
            bytes.fromhex(self.merkle_root_hash), self.timestamp, bytes.fromhex(self.difficulty), bytes.fromhex(self.nonce))
        
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
        input_struct = b''.join([i.struct() for i in self.inputs])
        output_struct = b''.join([o.struct() for o in self.outputs])
        return struct.pack('HH', num_inputs, num_outputs) + input_struct + output_struct

    def hash(self):
        return double_sha256(self.struct())

class TransactionInput:
    def __init__(self, input_tx, input_tx_index, checksig):
        self.input_tx = input_tx
        self.input_tx_index = input_tx_index
        self.checksig = checksig

    # 98 bytes
    def struct(self):
        return struct.pack("32sH64s", bytes.fromhex(self.input_tx), self.input_tx_index, bytes.fromhex(self.checksig))

class TransactionOutput:
    def __init__(self, pybits, to_address):
        self.pybits = pybits
        self.to_address = to_address

    # 40 bytes
    def struct(self):
        return struct.pack('Q32s', self.pybits, bytes.fromhex(self.to_address))

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
