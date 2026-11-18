from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Получаем настройки БД из переменных окружения (которые зададим в docker-compose)
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "app")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "1234")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

class SimpleAPI(BaseHTTPRequestHandler):
    def _send_response(self, status, data=None):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if data:
            self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == '/health':
            self._send_response(200, {"status": "ok", "service": "task-service"})
        elif self.path == '/tasks':
            try:
                conn = get_db_connection()
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM tasks;")
                tasks = cur.fetchall()
                cur.close()
                conn.close()
                self._send_response(200, tasks)
            except Exception as e:
                self._send_response(500, {"error": str(e)})
        else:
            self._send_response(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path == '/tasks':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING id;",
                    (post_data.get('title'), post_data.get('description'))
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close()
                self._send_response(201, {"id": new_id, "status": "created"})
            except Exception as e:
                self._send_response(500, {"error": str(e)})
        else:
            self._send_response(404, {"error": "Not Found"})

# Для простоты мы покажем только GET и POST. PUT и DELETE по аналогии.
# На защите главное показать, что база работает.

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), SimpleAPI)
    print("Starting server on port 8080...")
    server.serve_forever()