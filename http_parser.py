from typing import Optional, Dict, Tuple
import socket


class HTTPRequest:
    DEFAULT_MAX_BODY_SIZE = 10 * 1024
   
    def __init__(self):
        self.method: str = ""
        self.path: str = ""
        self.version: str = ""
        self.headers: Dict[str, str] = {}
        self.body: bytes = b""
        self.host: Optional[str] = None
        self.content_type: Optional[str] = None
        self.content_length: Optional[int] = None
        self.user_agent: Optional[str] = None
   
    @classmethod
    def parse(cls, data: bytes) -> 'HTTPRequest':
        request = cls()
       
        try:
            if b'\r\n\r\n' in data:
                headers_section, body_section = data.split(b'\r\n\r\n', 1)
                lines = headers_section.split(b'\r\n')
            elif b'\n\n' in data:
                headers_section, body_section = data.split(b'\n\n', 1)
                lines = headers_section.split(b'\n')
            else:
                lines = data.split(b'\r\n') if b'\r\n' in data else data.split(b'\n')
                body_section = b''
        except Exception as e:
            raise ValueError(f"Failed to parse HTTP request structure: {e}")
       
        if not lines:
            raise ValueError("Empty HTTP request")
       
        request._parse_request_line(lines[0])
        request._parse_headers(lines[1:])
        request._parse_body(body_section, data)
        return request
   
    def _parse_request_line(self, line: bytes):
        try:
            parts = line.decode('utf-8').strip().split(' ')
            if len(parts) != 3:
                raise ValueError(f"Invalid request line format: expected 3 parts, got {len(parts)}")
           
            self.method = parts[0].upper()
            self.path = parts[1]
            self.version = parts[2]
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode request line: {e}")
   
    def _parse_headers(self, lines: list):
        for line in lines:
            line_str = line.decode('utf-8', errors='ignore').strip()
            if not line_str:
                continue
           
            if ':' not in line_str:
                continue
           
            name, value = line_str.split(':', 1)
            name = name.strip().lower()  
            value = value.strip()
            self.headers[name] = value
       
        self.host = self.headers.get('host')
        self.content_type = self.headers.get('content-type')
        self.user_agent = self.headers.get('user-agent')
       
        if 'content-length' in self.headers:
            try:
                self.content_length = int(self.headers['content-length'])
            except ValueError:
                self.content_length = None
   
    def _parse_body(self, initial_body: bytes, full_data: bytes):
        
        if self.content_length is not None:
            self.body = initial_body[:self.content_length]
        else:
            self.body = initial_body[:self.DEFAULT_MAX_BODY_SIZE]
   
    def __repr__(self) -> str:
        return (f"HTTPRequest(method={self.method}, path={self.path}, "
                f"version={self.version}, headers={len(self.headers)}, "
                f"body_length={len(self.body)})")


class HTTPResponse:
   
    def __init__(self, status_code: int = 200, status_text: str = "OK"):
       
        self.status_code = status_code
        self.status_text = status_text
        self.headers: Dict[str, str] = {}
        self.body: bytes = b""
        self.version = "HTTP/1.1"
   
    def set_header(self, name: str, value: str) -> 'HTTPResponse':
        self.headers[name] = value
        return self
   
    def set_body(self, body: bytes) -> 'HTTPResponse':
        self.body = body
        return self
   
    def set_text_body(self, text: str, encoding: str = 'utf-8') -> 'HTTPResponse':
        self.body = text.encode(encoding)
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = f'text/plain; charset={encoding}'
        return self
   
    def build(self) -> bytes:
        self.headers['Content-Length'] = str(len(self.body))
        status_line = f"{self.version} {self.status_code} {self.status_text}\r\n"
        headers_section = ""
        for name, value in self.headers.items():
            headers_section += f"{name}: {value}\r\n"
        response = status_line.encode('utf-8')
        response += headers_section.encode('utf-8')
        response += b"\r\n"  
        response += self.body
        return response
   
    def __repr__(self) -> str:
        return (f"HTTPResponse(status={self.status_code}, "
                f"headers={len(self.headers)}, body_length={len(self.body)})")


class SimpleHTTPServer:
   
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.socket = None
   
    def start(self, handler_func):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
       
        print(f"Server listening on {self.host}:{self.port}")
       
        try:
            while True:
                client_socket, address = self.socket.accept()
                print(f"Connection from {address}")
               
                try:
                    data = client_socket.recv(1024 * 1024)
                    if not data:
                        continue
                    request = HTTPRequest.parse(data)
                    print(f"Received: {request}")
                    response = handler_func(request)
                    client_socket.sendall(response.build())
                   
                except Exception as e:
                    print(f"Error handling request: {e}")
                    error_response = HTTPResponse(500, "Internal Server Error")
                    error_response.set_text_body(f"Error: {str(e)}")
                    client_socket.sendall(error_response.build())
               
                finally:
                    client_socket.close()
       
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            if self.socket:
                self.socket.close()


if __name__ == "__main__":
    def example_handler(request: HTTPRequest) -> HTTPResponse:
        response = HTTPResponse()
       
        if request.path == "/":
            response.set_text_body("Welcome to the HTTP Server!")
        elif request.path == "/echo":
            info = f"""Request Information:
Method: {request.method}
Path: {request.path}
Version: {request.version}
Host: {request.host}
User-Agent: {request.user_agent}
Content-Type: {request.content_type}
Content-Length: {request.content_length}
Body: {request.body.decode('utf-8', errors='ignore')}
"""
            response.set_text_body(info)
        else:
            response = HTTPResponse(404, "Not Found")
            response.set_text_body("Page not found")
       
        return response
   
    server = SimpleHTTPServer('localhost', 8080)
    server.start(example_handler)