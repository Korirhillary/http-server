
### HTTP Server & Request Parser ###

# overview 
  This project implements a minimal HTTP/1.x server and request parser from scratch using Python and low-level TCP sockets.
  The goal is to demonstrate an understanding of the HTTP protocol, request structure, and  response synthesis — without relying on any HTTP libraries or frameworks.
  All parsing logic, header handling, body extraction, and response construction are implemented manually.

### Features

* Manual parsing of HTTP request line, headers, and body
* Accurate handling of Content-Length
* Safe request body truncation when Content-Length is absent
* Low-level TCP server using Python’s socket module
* Clear separation between parsing, server logic, and request handling

### Parsed Request Fields
Each incoming request is parsed into a structured HTTPRequest object exposing:
* HTTP method
* Request path
* HTTP version
* Host header (if present)
* Content-Type (if present)
* User-Agent (if present)
* Content-Length (if present)
* Complete request body (bytes)
* All headers as a dictionary

### Response Generation
Responses are constructed using a dedicated HTTPResponse builder that guarantees:
* Correct HTTP status line formatting
* Proper CRLF (\r\n) line endings
* Automatic and accurate Content-Length
* Clean separation of headers and body
The response builder allows method chaining for clarity and ease of use.

### TCP Server Implementation
A simple TCP-based HTTP server is implemented using Python’s socket module:
* Listens for incoming connections
* Reads raw request bytes from the socket
* Parses requests using the custom HTTP parser
* Passes requests to a user-defined handler
* Sends properly formatted HTTP responses back to the client

No high-level networking or HTTP abstractions are used.

## Project Structure
.
├── http_parser.py     # HTTP request parser, response builder, and server
├── README.md          # Project documentation

## How It Works

1. A client establishes a TCP connection to the server.
2. Raw bytes are read from the socket.
3. Headers and body are separated using the HTTP header delimiter.
4. The request line and headers are parsed manually.
5. The request body is read based on Content-Length (or truncated safely).
6. A handler function processes the request.
7. A valid HTTP response is constructed and sent back to the client.

## Usage

### Running the Server

bash
python http_parser.py

The server listens on:

localhost:8080

### Example Requests

*GET request*

bash
curl http://localhost:8080/


*POST request*

bash
curl -X POST http://localhost:8080/echo -d "Hello World"

## Example Handler

python
def example_handler(request: HTTPRequest) -> HTTPResponse:
    response = HTTPResponse()
    response.set_text_body(f"Received {request.method} request")
    return response


## Design Decisions

### Why Not Use Existing Libraries?

The purpose of this project is to demonstrate understanding of:

* HTTP protocol structure
* Manual request parsing
* Low-level socket communication

Using libraries such as http.server, requests, or frameworks would defeat this goal.

### Why Enforce a Body Size Limit?

When Content-Length is absent, there is no reliable way to determine body size.
To prevent memory exhaustion or denial-of-service scenarios, a *10 KB safety limit* is enforced.

### Error Handling

* Malformed requests raise parsing errors
* Server-side errors result in a 500 Internal Server Error response
* Invalid or unknown paths return 404 Not Found

## Limitations

This implementation intentionally keeps scope minimal:
* This implementation assumes the full HTTP request is available in the received byte buffer.  
  Production servers must read from the socket until Content-Length bytes are received.
* No chunked transfer encoding
* No HTTPS/TLS
* No persistent connections
* No request pipelining

These are outside the scope of this assignment but could be added in future iterations.

## Conclusion

This project demonstrates a clear and correct implementation of an HTTP server and request parser built entirely from first principles. Emphasis is placed on correctness, clarity, safety, and adherence to the HTTP specification.

The code is intentionally simple, readable, and well-documented to make the underlying protocol mechanics easy to understand and review.

## Author

*Korir Hillary*
Software Engineer / Full‑Stack Developer