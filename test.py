from block import *
import os
import random

transactions = []

for i in range(3):
    num_inputs = random.randint(1, 5)
    transaction_inputs = []
    for i in range(num_inputs):
        ti = TransactionInput(os.urandom(32).hex(), 0, os.urandom(64).hex())
        transaction_inputs.append(ti)

    num_outputs = random.randint(1, 5)
    transaction_outputs = []
    for i in range(num_outputs):
        pybits = int.from_bytes(os.urandom(4), 'little')
        to = TransactionOutput(pybits, os.urandom(32).hex())
        transaction_outputs.append(to)

    t =  Transaction(transaction_inputs, transaction_outputs)
    transactions.append(t)

b = Block(os.urandom(32).hex(), transactions)

