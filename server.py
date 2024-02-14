import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import random
class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()

                start_time = time.time()
                response = "time[sec], temperature[degC], pressure[hPa], humidity[%], altitude[m], a0, a1, a2, a3"
                self.wfile.write(response.encode('utf-8'))
                count = 0
                while True:
                    elapsed_time = time.time() - start_time
                    response = f"{elapsed_time:.2f}, {random.uniform(20, 30):.1f}, {random.uniform(900, 999):.1f}, {random.uniform(30, 40):.1f}, {random.uniform(199, 220):.1f},{random.uniform(20, 30):.1f},{random.uniform(20, 30):.1f},{random.uniform(20, 30):.1f},{random.uniform(20, 30):.1f}\n"
                    self.wfile.write(response.encode('utf-8'))
                    print(response)
                    time.sleep(0.5)
                    count += 1
                    # if count > 10:
                    #     time.sleep(10)
        except ConnectionAbortedError:
            print("Connection closed.")

# サーバーのポート番号
port = 8756

# サーバーの作成とリクエストハンドラーの指定
httpd = HTTPServer(('localhost', port), MyRequestHandler)

print(f"Server started on http://localhost:{port}")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
except ConnectionAbortedError:
    pass

httpd.server_close()
print("Server stopped")
