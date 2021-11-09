#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

import requests


class WebhookResquest(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/build/auto'):
            self.build_auto()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def build_auto(self):
        key = self.headers.get("key")
        content_len = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_len)
        print("receive data ", post_body)
        data = json.loads(post_body)

        event_data = data['event_data']
        repository = event_data['repository']

        tag = event_data['resources'][0]['tag']

        if tag == 'latest':
            return
        resource_url = event_data['resources'][0]['resource_url']
        namespace = repository['namespace']
        name = repository['name']
        repo_full_name = repository['repo_full_name']
        print(name, tag)
        cmd = 'kubectl apply -f ../k8s/deployment-uat-%s.yaml' % (str(name)[len("echo-"):])
        # patch image
        cmd = "kubectl patch statefulset %s -n cheese-uat --type='json' -p='[{\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/image\", \"value\":\"%s\"}]'" % (
            name,
            resource_url)
        print(cmd)
        # cmd = "" % (str(name)[len("echo-"):])
        f = os.popen(cmd)
        cmd_result = f.read()
        self.send_chat_msg(key, "## 执行更新 \n项目：%s/%s \n镜像：%s\n结果：%s" % (namespace, name, resource_url, cmd_result))
        pass

    def send_chat_msg(self, key, msg, chat_mentioned_list=None):
        chat_body = {'msgtype': 'markdown', 'markdown': {"content": msg}}
        if None != chat_mentioned_list:
            chat_body['mentioned_list'] = chat_mentioned_list

        jsonBody = json.dumps(chat_body)

        print(chat_body, len(chat_body))

        headers = {"Content-type": "application/json;UTF-8", "Accept": "text/plain"}
        response = requests.post(url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s' % (key), headers=headers,
                                 data=jsonBody)
        data = response.text

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
