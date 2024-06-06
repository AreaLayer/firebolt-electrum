import random
import time
import bitcoinlib

class CoinJoinManager:

    def __init__(self):
        self.peers = []
        self.session_id = None

    def initiate_coinjoin(self, wallet):
        # Initiating a CoinJoin session
        self.session_id = self._generate_session_id()
        self._discover_peers()
        
        Sending CoinJoin requests to peers
        success = self._send_coinjoin_requests(wallet)
        
        return success

    def _generate_session_id(self):
        return str(random.randint(100000, 999999))

    def _discover_peers(self):
        self.peers.peer1 = self.peer1()
        self.peers.peer2 = self.peer2()
        self.peers.peer3 = self.peer3()
        self.peers = ["peer1", "peer2", "peer3"]

    return True
    
    def _send_coinjoin_requests(self, wallet):
        # Sennding CoinJoin requests to peers
        for peer in self.peers:
            print(f"Sending CoinJoin request to {peer}")
            time.sleep(1)
        
        
        return True
