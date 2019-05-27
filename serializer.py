

class Serializer:
    
    @staticmethod
    def serialize(tx):
        return ('%04x' % tx.amount + ('0' * (34 - len(tx.sender))) + tx.sender + ('0' * (34 - len(tx.recipient))) + tx.recipient + tx.public_key + tx.signed_hash)
    
class Deserializer:
    @staticmethod
    def deserialize(serialized):
        d = {  "amount": int(serialized[:4], 16),
               "sender": serialized[4:38],
               "recipient": serialized[38:72].lstrip("0"),
               "public_key": serialized[72:202],
               "signed_hash": serialized[202:]
              }
        if d['sender'] != ('0' * 34):
            d['sender'] = d['sender'].lstrip('0')
        return d
    