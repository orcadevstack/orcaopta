import nacl.signing

class NodeIdentity:
    def __init__(self):
        self.signing_key = nacl.signing.SigningKey.generate()
        self.verify_key = self.signing_key.verify_key

    def sign(self, message: bytes):
        return self.signing_key.sign(message)

    def verify(self, signed):
        return self.verify_key.verify(signed)
