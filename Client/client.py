
import sys
import socket
import struct
import threading
import time

# Constants
TYPE_DATA = 21845  # 0101010101010101
TYPE_ACK = 43690  # 1010101010101010
retransmissionTime = 0.1  # RTT value

# Initialization
dataPackets = []
previousAck = -1 # intial value
inTransitSize = 0
timeStamp = []
windowLock = threading.Lock()

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
            # Attach server name, port to message; send into socket
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

'''
ackValidityCheck() checks if the received packet is ACK or not
@params Acknowldgement Packet
@return acknowledgement packet validity and sequence number
'''
def ackValidityCheck(ackData):
    ack = struct.unpack('!IHH', ackData)
    # A 16-bit field that is all zeroes, and
    # A 16-bit field that has the value TYPE_ACK (1010101010101010), indicates that this is an ACK packet
    if ack[1] == 0 and ack[2] == TYPE_ACK:
        return True, ack[0] # ack[0] specifies sequence number
    else:
        print("This is not an ACK Packet")
        return False, ack[0] # ack[0] specifies sequence number


'''
ack_receiver() Checks for ACK packet and proceeds with updating the transit size and acknowledgement count
Maintains synchronization because of locks
@params clientSocket
'''
def ack_receiver(clientSocket):
    global dataPackets
    global previousAck
    global inTransitSize
    global timeStamp

    try:
        while previousAck + 1 < len(dataPackets):
            if inTransitSize > 0:
                # Read reply characters from socket into string
                ackData, serverAddress = clientSocket.recvfrom(2048)

                isValidAck, sequenceNum = ackValidityCheck(ackData)
                windowLock.acquire() # Locks the execution
                if isValidAck:
                    # Specifies the acknowledgement for the correct retransmissionTime
                    # Thus, we increase the number of sent acknowledgement count
                    # And reduce the in transit size
                    if previousAck + 1 == sequenceNum:
                        previousAck += 1
                        inTransitSize -= 1
                    else:
                        inTransitSize = 0
                else:
                    inTransitSize = 0

                windowLock.release() # Unlocks the execution
    except:
        clientSocket.close()
        sys.exit("Connection Closed!")


'''
checksum_calculation() Calculates the checksum which needs to be added to the header of the packet
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
    clientPortNum = 1026 # Arbitary port number which is not well-known

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
