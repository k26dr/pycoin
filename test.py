from block import *
import os
import random

transactions = []

for i in range(3):
    num_inputs = random.randint(1, 5)
    num_outputs = random.randint(1, 5)
    transaction_inputs = []
    transcation_outputs = []
    for i in range(num_inputs):
        ti = TransactionInput(os.urandom(32).hex(), 0, os.urandom(64).hex())
        transaction_inputs.append(ti)

    for i in range(num_outputs - 1):
        to = TransactionOutput(
b = Block(os.urandom(32).hex(), transactions)

