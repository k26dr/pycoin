from block import *
import os
import random

transactions = []
for i in range(75):
    transactions.append(Transaction(os.urandom(32).hex(), 
        os.urandom(32).hex(), random.randint(100,200)))

b = Block(os.urandom(32).hex(), transactions)

