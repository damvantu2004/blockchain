import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
import time

class BlockchainClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Blockchain Asset Management")
        
        # Cấu hình kết nối server
        self.SERVER_HOST = '192.168.1.100'  # Thay bằng IP máy server
        self.SERVER_PORT = 5000
        
        # Tạo tabs
        self.tab_control = ttk.Notebook(root)
        
        self.add_tab = ttk.Frame(self.tab_control)
        self.verify_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.add_tab, text='Đăng ký tài sản')
        self.tab_control.add(self.verify_tab, text='Xác thực tài sản')
        self.tab_control.pack(expand=1, fill="both")
        
        self.setup_add_asset_tab()
        self.setup_verify_asset_tab()

    def setup_add_asset_tab(self):
        # Form đăng ký tài sản
        ttk.Label(self.add_tab, text="Mã tài sản:").grid(row=0, column=0, padx=5, pady=5)
        self.asset_id_entry = ttk.Entry(self.add_tab)
        self.asset_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.add_tab, text="Tên tài sản:").grid(row=1, column=0, padx=5, pady=5)
        self.asset_name_entry = ttk.Entry(self.add_tab)
        self.asset_name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.add_tab, text="Chủ sở hữu:").grid(row=2, column=0, padx=5, pady=5)
        self.owner_entry = ttk.Entry(self.add_tab)
        self.owner_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.add_tab, text="Đăng ký", command=self.add_asset).grid(row=3, column=0, columnspan=2, pady=20)

    def setup_verify_asset_tab(self):
        # Form xác thực tài sản
        ttk.Label(self.verify_tab, text="Mã tài sản:").grid(row=0, column=0, padx=5, pady=5)
        self.verify_id_entry = ttk.Entry(self.verify_tab)
        self.verify_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(self.verify_tab, text="Xác thực", command=self.verify_asset).grid(row=1, column=0, columnspan=2, pady=20)

        # Hiển thị thời gian phản hồi
        self.response_time_label = ttk.Label(self.verify_tab, text="")
        self.response_time_label.grid(row=2, column=0, columnspan=2)

        # Kết quả xác thực
        self.result_text = tk.Text(self.verify_tab, height=10, width=40)
        self.result_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def send_request(self, request_data):
        """Gửi yêu cầu tới server qua socket"""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)  # Timeout 5 giây
        
        try:
            client.connect((self.SERVER_HOST, self.SERVER_PORT))
            
            # Gửi yêu cầu
            client.send(json.dumps(request_data).encode())
            
            # Nhận phản hồi
            response = client.recv(4096).decode()
            return json.loads(response)
        except socket.timeout:
            messagebox.showerror("Lỗi", "Không thể kết nối đến server (timeout)")
            return {'status': 'error', 'message': 'Connection timeout'}
        except ConnectionRefusedError:
            messagebox.showerror("Lỗi", "Server không hoạt động")
            return {'status': 'error', 'message': 'Server is down'}
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        finally:
            client.close()

    def add_asset(self):
        if not all([self.asset_id_entry.get(), self.asset_name_entry.get(), self.owner_entry.get()]):
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin")
            return
        
        request = {
            'type': 'add',
            'asset_id': self.asset_id_entry.get(),
            'asset_name': self.asset_name_entry.get(),
            'owner': self.owner_entry.get()
        }
        
        response = self.send_request(request)
        if response['status'] == 'success':
            messagebox.showinfo("Thành công", "Tài sản đã được đăng ký thành công!")
            # Clear form
            self.asset_id_entry.delete(0, tk.END)
            self.asset_name_entry.delete(0, tk.END)
            self.owner_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Lỗi", response['message'])

    def verify_asset(self):
        if not self.verify_id_entry.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã tài sản")
            return
        
        asset_id = self.verify_id_entry.get()
        request = {
            'type': 'verify',
            'asset_id': asset_id
        }
        
        # Đo thời gian phản hồi
        start_time = time.time()
        response = self.send_request(request)
        end_time = time.time()
        
        if response['status'] == 'error':
            self.response_time_label.config(text="")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"Lỗi: {response['message']}")
            return
        
        response_time = end_time - start_time
        self.response_time_label.config(
            text=f"Thời gian phản hồi: {response_time:.2f} giây"
        )
        
        self.result_text.delete(1.0, tk.END)
        if response.get('verified'):
            verification_text = f"""
            Kết quả xác thực:
            Mã tài sản: {response['asset_id']}
            Tên tài sản: {response['asset_name']}
            Chủ sở hữu: {response['owner']}
            Thời gian đăng ký: {response['timestamp']}
            """
        else:
            verification_text = "Không tìm thấy thông tin tài sản!"
        
        self.result_text.insert(1.0, verification_text)

if __name__ == '__main__':
    root = tk.Tk()
    app = BlockchainClient(root)
    root.mainloop()