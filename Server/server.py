'''
server.py
Go Back N protocol using UDP Sockets
Authors :-
Sai Kiran Mayee Maddi 200257327 smaddi@ncsu.edu
Abhishek Arya 200206728 aarya@ncsu.edu
'''

import socket

def checksum_verification(data, obtainedCheckSum):
    checkSum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            sumOf16bits = ord(data[i]) + (ord(data[i + 1]) << 8)
            sumOf16bits += checkSum
            checkSum =  (sumOf16bits & 0xffff) + (sumOf16bits >> 16)
    return (checkSum & 0xffff) & (obtainedCheckSum)


def main():
    if len(sys.argv) != 4:
        error_message_for_arguments()
        exit()

    serverPortNum = sys.argv[1]
    fileName = 7735 if sys.argv[2] != '7735' else int(sys.argv[2])
    probability = sys.argv[3]

    serverIP = socket.gethostbyname(socket.gethostname())

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind((serverIP, serverPortNum))




def error_message_for_arguments():
    print("\nPlease enter the details in the below format:")
    print("python server.py  <Server Port> <File Name> <Probability> \n")

if __name__ == '__main__':
    main()
