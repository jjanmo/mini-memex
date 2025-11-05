from asyncio import protocols
import socket

class URL:
    # URL에서 scheme, host, path를 분리(http://example.com/index.html)
    # scheme: http
    # host: example.com
    # path: /index.html
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme =="http" # http 임을 단언함 > http가 아니면 에러 발생

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        # socket 생성
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        s.connect((self.host, 80))

        # request 생성(정확히는 아래 코드에는 요청서 헤더만 존재하고 바디는 없음)
        request = f"GET {self.path} HTTP/1.0\r\nHost: {self.host}\r\n\r\n"
        s.send(request.encode('utf-8'))

        response = s.makefile('r', encoding='utf-8', newline='\r\n')
        status_line = response.readline()
        version, status_code, explanation = status_line.split(' ', 2)
        assert status_code == '200', "Not 200"

        response_headers = {}
        while True:
            line = response.readline()
            if line == '':
                break
            if line == '\r\n':
                break
            header, value = line.split(': ', 1)
            response_headers[header.casefold()] = value.strip()

            assert "transfer-encoding" not in response_headers, "Transfer-Encoding is not supported"
            assert "content-encoding" not in response_headers, "Content-Encoding is not supported"

        body = response.read()
        s.close()
        return body

def show(body):
    in_tag = False
    for character in body:
        if character == "<":
            in_tag = True
        elif character == ">":
            in_tag = False
        elif not in_tag:
            print(character, end="")

def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
