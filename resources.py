import hashlib
import re
from pydantic import BaseModel

class Node(BaseModel):
    addr: str
    type: str
    token: str | None = None
    hash: str | None = None

    def check_sanity(self):
        if self.addr is None or self.type is None:
            return False

        if re.match(r'(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}:' #ipv4
                    r'([0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$', #port
                    self.addr) is None: #check if it has a valid ip addr
            return False

        if re.match('front|back', self.type) is None:
            return False

        return True

    def to_dict(self):
        return {"addr": self.addr, "type": self.type}

    def get_hash(self) -> str:
        if self.hash is None:
            serialized = str(self.addr).encode('utf-8') + str(self.type).encode('utf-8')
            self.hash = hashlib.md5(serialized).hexdigest()
        return self.hash