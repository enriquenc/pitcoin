import hashlib

def merkle_root(ts):
    transactions = None
    if isinstance(ts, list):
        transactions = ts.copy()
    else:
        return(hashlib.sha256(ts.encode('utf-8')).hexdigest())
    
    for i in range(len(transactions)):
        transactions[i] = hashlib.sha256(transactions[i].encode('utf-8')).digest()
        
    while len(transactions) > 1:
        i = 0
        if len(transactions) % 2 != 0:
            transactions.append(transactions[-1])
            
        while i < (len(transactions) - 1):
            transactions[i] = hashlib.sha256(transactions[i] + transactions[i + 1]).digest()
            transactions.remove(transactions[i + 1])
            i = i + 1
            
    return (transactions[0]).hex()