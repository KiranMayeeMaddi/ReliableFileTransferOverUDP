
import sys
from socket import *
import struct

TYPE_DATA = 21845 #0101010101010101
retransmissionTime = 0.1 #RTT value
dataPackets = []




def ack_receiver(clientSocket):
    print()

def rdf_send(serverAddress, clientSocket, N):
    print()


def checksum_calculation(data):
    checkSum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            sumOf16bits = ord(data[i]) + (ord(data[i + 1]) << 8)
            sumOf16bits += checkSum
            checkSum =  (sumOf16bits & 0xffff) + (sumOf16bits >> 16)
    return ~(checkSum) & 0xffff


def create_packet(sequenceNum, data):
    checkSum = checksum_calculation(data)
    header = struct.pack('!IHH', sequenceNum, checkSum, TYPE_DATA)
    dataPacket = header + data
    return dataPacket

def read_and_create_packet(fileName, MSS):
    try:
        with open(fileName, 'rb') as filePtr:
            sequenceNum = 0
            data = ''
            while True:
                readOnebyte = filePtr.read(1)
                data += readOnebyte
                if data == '':
                    break
                if len(data) == MSS or readOnebyte == '':
                    dataPackets.append(create_packet(sequenceNum, data))
                    data = ''
                    sequenceNum += 1
            filePtr.close()
    except:
        sys.exit("\nError! Open file operation cannot be performed.\n")

def main():
    if len(sys.argv) != 6:
        error_message_for_arguments()
        exit()

    # Getting values from the command line
    serverIP = sys.argv[1]
    # Changing to the required port number
    serverPortNum = 7735 if sys.argv[2] != '7735' else int(sys.argv[2])
    fileName = sys.argv[3]       # Name of the file to be transferred
    N = int(sys.argv[4])         # Window size
    MSS = int(sys.argv[5])       # Maximum segment size

    clientIP = socket.gethostbyname(socket.gethostname())
    clientPortNum = '1025'

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(clientIP, clientPortNum)
    serverAddress = (serverIP, serverPortNum)

    read_and_create_packet(fileName, MSS)

    startTime = time.time()

    ackReceiveThread = threading.Thread(target = ack_receiver, args = (clientSocket))
    rdtSendThread = threading.Thread(target = rdt_send, \
                    args = (serverAddress, clientSocket, N))

    ackReceiveThread.start()
    rdtSendThread.start()

    ackReceiveThread.join()
    rdtSendThread.join()

    print("\nSending Complete!\n")

    print("Total time taken {} seconds.\n".format(time.time() - startTime))

    if clientSocket:
        clientSocket.close()



def error_message_for_arguments():
    print("\nPlease enter the details in the below format:")
    print("python client.py <Server IP Address> <Server Port> <File Name> <Window Size> <Maximum Segment Size>\n")

if __name__ == '__main__':
    main()
