#  coding: utf-8 
import socketserver
import re
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class httpHandler:
    
    def setHeader(self, status_code, mime_type="html", new_attrs={}):
        attrs = {"Connection": "close",
            "Content-Type": "text/{}".format(mime_type)
        }
        attrs.update(new_attrs)
        #probably gonna add content-length
        header = "HTTP/1.1 {}\r\n".format(status_code)
        
        for k, v in attrs.items():
            header += "{}: {}\r\n".format(k, v)
        
        return header+'\r\n'
        
    def pathParser(self, path):
        #check root path
        print("this is: {}".format(path))
        endWithSlash = re.search(r"/$", path)
        fileFormat = re.search(r"/.*\.([a-zA-Z]+)$", path)

        if endWithSlash:
            path += "index.html"
            return(200, path, None)
        elif fileFormat:
            return (200, path, fileFormat[1])
        else:
            #redirect
            path += '/'
            return (301, path, None)

    def security_check(self, path, prefix="www"):
        realResPath = os.path.join(os.getcwd(), prefix)
        realReqPath = os.path.realpath(path)
        cmPrefix = os.path.commonprefix([realReqPath, realResPath])

        print("req: ", realReqPath)
        print("res: ", realResPath)

        if cmPrefix == realResPath:
            return True
        print("not secure")
        return False

    def response(self):
        return
        
class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        reqHandler = httpHandler()
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        if not self.data:
            return

        httpHeader = re.search(r"(.*)\r\n", self.data.decode('utf-8'))[1]
        method = re.search(r"([A-Za-z]+)\s", httpHeader)[1]
        
        if method == 'GET':
            path = re.search(r"(/.*)\sHTTP", httpHeader)[1]
            #check if path exists
            print(path)
            prefix = "www"
            if os.path.exists(prefix+path) and reqHandler.security_check(prefix+path):
                status, modified_path, fileFormat = reqHandler.pathParser(path)
                print("modPath: {}".format(modified_path))
                if status == 301:
                    sendData = reqHandler.setHeader(status, new_attrs={"Location": modified_path})
                    self.request.sendall(bytes(sendData, "utf-8"))
                    print("redirect")
                    return

                #status 200 ok
                try:
                    with open(prefix+modified_path, 'r') as f:
                        if fileFormat == "css":
                            sendData = reqHandler.setHeader(status, mime_type="css")
                        else:
                            sendData = reqHandler.setHeader(status, mime_type="html")

                        sendData += f.read()
                except:
                    sendData = reqHandler.setHeader("404 Not Found")
                    print('404')
            else:
                #return 404
                sendData = reqHandler.setHeader("404 Not Found")
                print('404')
        else:
            #return 403
            sendData = reqHandler.setHeader("405 Method Not Allowed")
            print("405")
        
        self.request.sendall(bytes(sendData, "utf-8"))
        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()