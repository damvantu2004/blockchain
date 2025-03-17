import socket
import json
import sqlite3
import hashlib
import signal
import sys
from datetime import datetime

class BlockchainServer:
    def __init__(self):
        self.blockchain = []
        self.init_db()
        self.restore_blockchain()
        self.server = None
        self.running = True
        
    def cleanup(self):
        """Dọn dẹp tài nguyên trước khi tắt"""
        if hasattr(self, 'conn'):
            self.conn.close()
        if self.server:
            self.server.close()
        self.running = False
        print("\nĐã đóng kết nối database và socket.")
        print("Server đã tắt thành công!")
        sys.exit(0)

    def init_db(self):
        """Khởi tạo database SQLite"""
        self.conn = sqlite3.connect('blockchain.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                asset_id TEXT PRIMARY KEY,
                asset_name TEXT,
                owner TEXT,
                timestamp REAL,
                prev_hash TEXT
            )
        ''')
        self.conn.commit()

    def restore_blockchain(self):
        """Khôi phục blockchain từ SQLite"""
        self.cursor.execute('SELECT * FROM blocks ORDER BY timestamp')
        blocks = self.cursor.fetchall()
        for block in blocks:
            self.blockchain.append({
                'asset_id': block[0],
                'asset_name': block[1],
                'owner': block[2],
                'timestamp': block[3],
                'prev_hash': block[4]
            })

    def create_block(self, asset_id, asset_name, owner):
        """Tạo khối mới"""
        prev_hash = self.blockchain[-1]['prev_hash'] if self.blockchain else '0' * 64
        
        block = {
            'asset_id': asset_id,
            'asset_name': asset_name,
            'owner': owner,
            'timestamp': datetime.now().timestamp(),
            'prev_hash': prev_hash
        }
        
        # Tính hash của block hiện tại
        block_string = json.dumps(block, sort_keys=True)
        block['hash'] = hashlib.sha256(block_string.encode()).hexdigest()
        
        return block

    def add_asset(self, asset_id, asset_name, owner):
        """Thêm tài sản mới vào blockchain"""
        # Tạo block mới
        new_block = self.create_block(asset_id, asset_name, owner)
        
        # Thêm vào blockchain trong RAM
        self.blockchain.append(new_block)
        
        # Lưu vào SQLite
        self.cursor.execute('''
            INSERT INTO blocks (asset_id, asset_name, owner, timestamp, prev_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            new_block['asset_id'],
            new_block['asset_name'],
            new_block['owner'],
            new_block['timestamp'],
            new_block['prev_hash']
        ))
        self.conn.commit()
        
        return {'status': 'success', 'message': 'Asset registered successfully'}

    def verify_asset(self, asset_id):
        """Xác thực tài sản bằng cách duyệt tuần tự"""
        for block in self.blockchain:
            if block['asset_id'] == asset_id:
                return {
                    'status': 'success',
                    'verified': True,
                    'asset_id': block['asset_id'],
                    'asset_name': block['asset_name'],
                    'owner': block['owner'],
                    'timestamp': block['timestamp']
                }
        return {'status': 'error', 'verified': False, 'message': 'Asset not found'}

def signal_handler(sig, frame):
    """Xử lý khi nhận signal Ctrl+C"""
    print("\nĐang tắt server...")
    if 'blockchain_server' in globals():
        blockchain_server.running = False

def start_server():
    # Đăng ký signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Khởi tạo server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    
    # Lấy IP của máy server
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)
    server.settimeout(1)
    
    global blockchain_server
    blockchain_server = BlockchainServer()
    blockchain_server.server = server
    
    print("\n=== Blockchain Server ===")
    print(f"Server IP: {server_ip}")
    print("Trong file client.py, sửa dòng:")
    print(f"self.SERVER_HOST = '{server_ip}'")
    print("\nNhấn Ctrl+C để tắt server")

    try:
        while blockchain_server.running:
            try:
                client, addr = server.accept()
                print(f"Kết nối từ {addr}")
                
                data = client.recv(4096).decode()
                request = json.loads(data)
                
                if request['type'] == 'add':
                    response = blockchain_server.add_asset(
                        request['asset_id'],
                        request['asset_name'],
                        request['owner']
                    )
                elif request['type'] == 'verify':
                    response = blockchain_server.verify_asset(request['asset_id'])
                
                client.send(json.dumps(response).encode())
                client.close()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Lỗi khi xử lý kết nối: {e}")
                continue
    except Exception as e:
        print(f"Lỗi server: {e}")
    finally:
        blockchain_server.cleanup()

if __name__ == '__main__':
    start_server()