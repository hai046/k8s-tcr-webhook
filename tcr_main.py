#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler


class WebhookResquest(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/build/auto':
            self.build_auto()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def build_auto(self):
        content_len = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_len)
        print("receive data ", post_body)
        data = json.loads(post_body)

        repository = data['repository']

        namespace = repository['namespace']
        name = repository['name']
        repo_full_name = repository['repo_full_name']

        cmd='kubectl apply -f deployment-uat-%s'%(str(name)[:len("echo-")])
        print(cmd)

        pass


class tcr:

    def run(self, port=8123, server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print("http server_address ", server_address)
        httpd.serve_forever()


if __name__ == '__main__':
    t = tcr()
    t.run(handler_class=WebhookResquest)
