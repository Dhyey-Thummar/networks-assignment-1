import os

HOST = ''
PORT = 4040
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
PATH = os.getcwd()

colors = {
    'reset': f"\033[0m",
    'red': f"\033[31m",
    'blue': f"\033[34m",
    'green': f"\033[32m",
}


def recv_msg(sock):
    """ Wait for data to arrive on the socket, then parse into
    messages using b'\0' as message delimiter """
    data = bytearray()
    msg = ''
    # Repeatedly read 4096 bytes off the socket, storing the bytes
    # in data until we see a delimiter
    while not msg:
        recvd = sock.recv(4096)
        if not recvd:
            # Socket has been closed prematurely
            raise ConnectionError()
        data = data + recvd
        if b'\0' in recvd:
            # we know from our protocol rules that we only send
            # one message per connection, so b'\0' will always be
            # the last character
            msg = data.rstrip(b'\0')
    msg = msg.decode('utf-8')
    return msg


def prep_msg(msg):
    """ Prepare a string to be sent as a message """
    msg += '\0'
    return msg.encode('utf-8')


def send_msg(sock, msg):
    """ Send a string over a socket, preparing it first """
    data = prep_msg(msg)
    sock.sendall(data)


def CWD(sock):
    """ Current Working Directory """
    cwd = os.getcwd()
    send_msg(sock, cwd)


def LS(sock):
    """ List files in current directory """
    files = ""
    path = os.getcwd()
    for file in os.listdir(path):
        files += file + "    "
    if files == "":
        files = "Directory is empty"
    send_msg(sock, files)


def CD(sock, msg):
    """ Change directory """
    path = msg[3:]
    try:
        if path == "~":
            os.chdir(PATH)
        else:
            os.chdir(path)
        send_msg(sock, "OK")
    except:
        send_msg(sock, "NOK")


def DWD(sock, msg):
    """ Download file """
    path = msg[4:]
    try:
        filename = os.path.basename(path)
        filesize = os.path.getsize(path)
        sock.send(f"{filename}{SEPARATOR}{filesize}".encode())
        with open(path, "rb") as f:
            print("Sending file...")
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sock.sendall(data)
        print("File sent")
    except:
        send_msg(sock, "NOK")
    finally:
        return