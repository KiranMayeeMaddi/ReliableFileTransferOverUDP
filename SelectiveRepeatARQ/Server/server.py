# -*- coding: utf-8 -*-
'''
server.py
Go Back N protocol using UDP Sockets
'''
import sys
import socket
import struct
import random

# Constants
TYPE_DATA = 21845  # 0101010101010101
TYPE_ACK = 43690  # 1010101010101010

'''
checksum_verification() Calculates and verifies the checksum with the obtained checksum in the packet
@params data, obtained check sum
@return A 16 bit value
'''
def checksum_verification(data, obtainedCheckSum):
    checkSum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            sumOf16bits = ord(data[i]) + (ord(data[i + 1]) << 8)
            sumOf16bits += checkSum
            checkSum =  (sumOf16bits & 0xffff) + (sumOf16bits >> 16)
    return (checkSum & 0xffff) & (obtainedCheckSum)

'''
create_ack_header() creates the header for the acknowledgement
@params sequence number
@return acknowledgement packet
'''
def create_ack_header(sequenceNum):
    ackPacket = struct.pack('!IHH', sequenceNum, 0, TYPE_ACK)
    return ackPacket

'''
dessemble_packet() checks if the obtained packet is the data backet and separates sequence number, checksum and data
@params packet
@return isValidDataPacket: bool check for the data packet, sequenceNum, data
'''
def dessemble_packet(packet):
    header = struct.unpack('!IHH', packet[0:8])
    sequenceNum, checkSum, data = header[0], header[1], packet[8:]
    isValidDataPacket = False
    verifiedChecksum = checksum_verification(data, checkSum)
    if verifiedChecksum == 0 and header[2] == TYPE_DATA:
        isValidDataPacket = True
    return isValidDataPacket, sequenceNum, data


def main():
    if len(sys.argv) != 4:
        error_message_for_arguments()
        exit()

    # Getting the values of server port number, file name, probability at which a packet can be lost
    serverPortNum = 7735 if sys.argv[1] != '7735' else int(sys.argv[1])
    fileName = sys.argv[2]
    probLoss = float(sys.argv[3])

    serverIP = socket.gethostbyname(socket.gethostname()) # IP address of the server (current machine)

    print("\nServer IP Address: {}\nServer Port Number: {}\n".format(serverIP, serverPortNum))

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind socket to a port number
    serverSocket.bind((serverIP, serverPortNum))

    buffer = {}
    maxSeqNum = 0

    filePtr = open(fileName, 'wb')
    flag = True
    while flag or len(buffer) <= maxSeqNum:
        # Read from UDP socket into message, getting client’s address (clientIP and port)
        data, clientAddress = serverSocket.recvfrom(2048)
        isValidDataPacket, sequenceNum, data = dessemble_packet(data)

        if isValidDataPacket:
            if random.uniform(0, 1) > probLoss:  # packet accepted
                ackPacket = create_ack_header(sequenceNum)
                serverSocket.sendto(ackPacket, clientAddress)
                if data == "EOF":
                    flag = False
                    maxSeqNum = sequenceNum
                    print("End of file is reached at sequence number {}".format(str(sequenceNum)))
                buffer[int(sequenceNum)] = data
            else:
                print("Packet Loss, Sequence Number = {}".format(str(sequenceNum)))

    print("File Received. Closing Connection!")

    for i in range(maxSeqNum - 1):
        filePtr.write(buffer[i])
    # Closing file pointer and socket connection
    filePtr.close()
    serverSocket.close()

'''
Displays error message if the command line arguments are not given as expected
'''
def error_message_for_arguments():
    print("\nPlease enter the details in the below format:")
    print("python server.py  <Server Port> <File Name> <Probability> \n")

if __name__ == '__main__':
    main()
