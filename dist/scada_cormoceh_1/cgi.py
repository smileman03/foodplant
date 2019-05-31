import socket
import time
from win_inet_pton import *
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8080))
serversocket.listen(5)
print 'Server is waiting for connections.'
while True:
    conn, addr = serversocket.accept()
    data = conn.recv(1024)

    print 'Connection:', addr
    print '------------------------------'
    print "Request Data from Browser"
    print '------------------------------'
    print data
    str="""<p><img src="/motor.gif" width="189" height="255" alt="lorem"></p>"""
    conn.send("""
       <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <style>
                body, html {
                    padding: 0;
                    margin: 0;
                    width: 100%;
                    height: 100%;
                }
            </style>
            <script>

            </script>
            </head>
                <body><p><img src="/Koala.jpg" width="189" height="255" alt="lorem"></p></body >
            </html >
    """)

    conn.close()

    time.sleep(0.1)