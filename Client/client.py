
import sys
import socket
import struct
import threading
import time

TYPE_DATA = 21845 #0101010101010101
retransmissionTime = 0.1 #RTT value
dataPackets = []
windowLock = threading.Lock()
previousAck = -1 # intial value
inTransitSize = 0
timeStamp = []

'''
rdt_send() checks with the window size N, if less than N segments are outstanding it transmits the newly
formed segment to the server in a UDP packet.
@params serverAddress, clientSocket, N
This function uses locks in order to ensure synchronization.
'''

def rdt_send(serverAddress, clientSocket, N):
    global dataPackets
    global previousAck
    global inTransitSize
    global timeStamp

    timeStamp = [len(dataPackets)]

    while previousAck + 1 < len(dataPackets):
        windowLock.acquire() # Locks the execution
        packetCount = previousAck + inTransitSize + 1
        # Checking size with respect to window size so as to send the packets
        if inTransitSize < N and  packetCount < len(dataPackets):
            clientSocket.sendto(dataPackets[packetCount], serverAddress)
            # Current time is recorded as the timestamp for the sent packet
            timeStamp[packetCount] = time.time()
            inTransitSize += 1
        if inTransitSize > 0:
            # If there is a time out then displaying the respective sequence number
            if (time.time() - timeStamp[previousAck + 1]) > retransmissionTime:
                print("Time out, Sequence Number = {}".format(str(previousAck + 1)))
                inTransitSize = 0
        windowLock.release() # Unlocks the execution


def ack_receiver(clientSocket):
    print()


'''
Calculates the checksum which needs to be added to the header of the packet
@params data
@return checkSum which is a 16 bit value
'''
def checksum_calculation(data):
    checkSum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            sumOf16bits = ord(data[i]) + (ord(data[i + 1]) << 8)
            sumOf16bits += checkSum
            checkSum =  (sumOf16bits & 0xffff) + (sumOf16bits >> 16)
    return ~(checkSum) & 0xffff


'''
create_packet() creates packets by appending header with the data
Header has sequenceNum, checkSum, TYPE_DATA
TYPE_DATA value indicates that this is a data packet
@params sequenceNum, data
@return dataPacket
'''
def create_packet(sequenceNum, data):
    checkSum = checksum_calculation(data)
    header = struct.pack('!IHH', sequenceNum, checkSum, TYPE_DATA)
    dataPacket = header + data
    return dataPacket


'''
read_and_create_packet() checks if the given can be opened and read.
calls create_packet() for appending the header and for creating the packet
@params fileName, MSS which specify the name of the file and Maximum segment size
'''
def read_and_create_packet(fileName, MSS):
    global dataPackets

    try:
        with open(fileName, 'rb') as filePtr: #read binary format
            sequenceNum = 0
            data = ''
            while True:
                readOnebyte = filePtr.read(1) # Reading one byte at a time
                data += readOnebyte
                if data == '':
                    break
                if len(data) == MSS or readOnebyte == '':
                    dataPackets.append(create_packet(sequenceNum, data))
                    data = ''
                    sequenceNum += 1
            filePtr.close() # Closing the file pointer
    except: # throws an exception if file can not be opened
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

    clientIP = socket.gethostbyname(socket.gethostname()) # IP address of the client
    clientPortNum = 1025 # Arbitary port number which is not well-known

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.bind((clientIP, clientPortNum))
    serverAddress = (serverIP, serverPortNum)

    read_and_create_packet(fileName, MSS)

    # Starting the timer
    startTime = time.time()

    # Creating threads
    ackReceiveThread = threading.Thread(target = ack_receiver, args = (clientSocket,))
    rdtSendThread = threading.Thread(target = rdt_send, \
                    args = (serverAddress, clientSocket, N))

    # Starting threads
    ackReceiveThread.start()
    rdtSendThread.start()

    # Wait until all the threads are complete
    ackReceiveThread.join()
    rdtSendThread.join()

    print("\nTransfer Complete!\n")

    # Time taken to send all the packets
    print("Total time taken {} seconds.\n".format(time.time() - startTime))

    # Closing the socket if it is still open
    if clientSocket:
        clientSocket.close()


'''
Displays error message if the command line arguments are not given as expected
'''
def error_message_for_arguments():
    print("\nPlease enter the details in the below format:")
    print("python client.py <Server IP Address> <Server Port> <File Name> <Window Size> <Maximum Segment Size>\n")

if __name__ == '__main__':
    main()
