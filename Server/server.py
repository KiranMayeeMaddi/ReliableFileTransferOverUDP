'''
server.py
Go Back N protocol using UDP Sockets
Authors :-
Sai Kiran Mayee Maddi 200257327 smaddi@ncsu.edu
Abhishek Arya 200206728 aarya@ncsu.edu
'''

import socket

# Constants
TYPE_DATA = 21845  # 0101010101010101
TYPE_ACK = 43690  # 1010101010101010


def checksum_verification(data, obtainedCheckSum):
    checkSum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            sumOf16bits = ord(data[i]) + (ord(data[i + 1]) << 8)
            sumOf16bits += checkSum
            checkSum =  (sumOf16bits & 0xffff) + (sumOf16bits >> 16)
    return (checkSum & 0xffff) & (obtainedCheckSum)


def create_ack_header(sequenceNum):
    ackPacket = struct.pack('!IHH', sequenceNum, 0, TYPE_ACK)  # SEQUENCE NUMBER BEING ACKED
    return ackPacket


def dessemble_packet(packet):
    header = struct.unpack('!IHH', packet[0:8])
    sequenceNum, checkSum, data = header[0], header[1], packet[8:]
    isValidDataPacket = False
    verifiedChecksum = checksum_verification(data,check_sum)
    if verifiedChecksum == 0 and header[2] == TYPE_DATA:
        isValidDataPacket = False
    return isValidDataPacket, sequenceNum, data


def main():
    if len(sys.argv) != 4:
        error_message_for_arguments()
        exit()

    # Getting the values of server port number, file name, probability at which a packet can be lost
    serverPortNum = 7735 if sys.argv[1] != '7735' else int(sys.argv[1])
    fileName = sys.argv[2]
    probability = sys.argv[3]

    serverIP = socket.gethostbyname(socket.gethostname()) # IP address of the server (current machine)

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind((serverIP, serverPortNum))

    previousSeqNum = -1

    filePtr = open(fileName, 'wb')
    flag = True
    while flag:
        # Read from UDP socket into message, getting client’s address (clientIP and port)
        data, clientAddress = serverSocket.recvfrom(2048)
        isValidDataPacket, sequenceNum, data = dessemble_packet(data)

        if isValidDataPacket:
            if random.uniform(0, 1) > prob:  # packet accepted
                if sequenceNum == previousSeqNum + 1:
                    ackPacket = create_ack_header(sequenceNum)
                    serverSocket.sendto(ackPacket, clientAddress)
                    if data == "EOF":
                        flag = False
                        print("End of file is receached at sequence number {}".format(sequenceNum))
                        break
                    filePtr.write(data)
                    previousSeqNum = sequenceNum
            else:
                print("Packet Loss, Sequence Number = {}".format(str(sequence_number))

    print("File Received. Closing Connection!")

    # Closing file pointer and socket connection
    filePtr.close()
    serverSocket.close()


def error_message_for_arguments():
    print("\nPlease enter the details in the below format:")
    print("python server.py  <Server Port> <File Name> <Probability> \n")

if __name__ == '__main__':
    main()
