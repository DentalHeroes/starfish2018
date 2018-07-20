# ****************************************************************************
# * To read data from the DTH11 sensor, you first send it a start pulse for  *
# * a minimum of 18ms (There are 1,000 milliseconds in one second.) A pulse  *
# * consists of setting the pin high for a period of time followed by        *
# * setting it low.                                                          *
# * The sensor will then respond with a response pulse and start sending 40  *
# * bits of data. It sends data by allowing or cutting off the supply of     *
# * voltage to the pin (pull-up and pull-down). It pulls up and pulls down   *
# * in a series 40 times. The length of time the signal is pulled up         *
# * indicates whether the bit is a 0 (26 us) or a 1 (70 us). (There are      *
# * 1,000,000 microseconds in one second.)                                   *
# * Note that because Linux (the operating system on the Raspberry Pi) is    *
# * not a "real-time" operating system, it is not able to always accurately  *
# * measure the length of each signal from the sensor. Because of this the   *
# * data is sometimes not read back properly.                                *
# * After send the data, the sensor sends a low signal for 54us and then     *
# * high.                                                                    *
# * The data itself consists of five bytes (there are 8 bits in a byte). The *
# * first two bytes are the humidity. The second two bytes are the           *
# * temperature. Each value is a decimal number. The first byte is the       *
# * whole number to the left of the decimal, while the second is the         *
# * fractional part (right of the decimal). The final byte is a checksum     *
# * used to verify that the data is valid. It contains the sum of the        *
# * humidity and temperature values.                                         *
# *                                                                          *
# * Computers internally store numbers in what is called binary notation.    *
# * each number is made up of the symbols '0' and '1'. This is similar to    *
# * the familiar decimal notation where each number is made up of the        *
# * symbols '0'-'9'.                                                         *
# * A decimal number works by calculating the symbol in each position by the *
# * multiplier for the position. This is commonly referred to as a "place",  *
# * such as the one's place, ten's place, etc.                               *
# * For example:                                                             *
# * 123                                                                      *
# * The 3 is in the one's place. The one's place is also equivalent to 10^0. *
# * (This is 10 to the zero). The 2 is in the ten's place. This is 10^1. The *
# * 1 is in the hundred's place. This is 10^2 (or 10*10). You can denote the *
# * position's "place" above each number like so:                            *
# * 100  10   1                                                              *
# *   1   2   3                                                              *
# * To get the value of the number, you take 1*100 + 2*10 + 3.               *
# * Now take a binary number:                                                *
# * 01111011                                                                 *
# * In binary, the "place's" are (from right to left) 2^0 (1), 2^1 (2),      *
# * 2^2 (4), 2^3 (8), 2^4 (16), etc. If you denote the position's "place"    *
# * above each number again you get:                                         *
# * 128  64  32  16   8   4   2   1                                          *
# *   0   1   1   1   1   0   1   1                                          *
# * To get the value of the number, you take                                 *
# * 0*128 + 1*64 + 1*32 + 1*16 + 1*8 + 0*4 + 1*2 + 1*1.                      *
# * Or 0 + 64 + 32 + 16 + 8 + 0 + 2 + 1.                                     *
# * Or 123.                                                                  *
# ****************************************************************************

import RPi.GPIO as GPIO
import time

# This class is used to return the data from the sensor
class DHT11Result:
    ERR_NONE = 0
    ERR_MISSING_DATA = 1
    ERR_BAD_CHECKSUM = 2
    
    errorCode = ERR_NONE
    humidity = -1
    temperature = -1

    def __init__(self, errorCode, humidity, temperature):
        self.errorCode = errorCode
        self.humidity = humidity
        self.temperature = temperature

    def is_valid(self):
        return self.errorCode == DTH11Result.ERR_NONE

# The main sensor class
class DTH11:
    __pin = 0

    def __init__(self, pin):
        self.__pin = pin
        GPIO.setmode(GPIO.BOARD)

    def read(self):
        # Set pin as OUTPUT
        GPIO.setup(self.__pin, GPIO.OUT)

        # Send the initial high pulse (50ms high, 20ms low)
        self.__sendAndSleep(GPIO.HIGH, 0.05) 
        self.__sendAndSleep(GPIO.LOW, 0.02)

        # Set pin as INPUT (initially pulled up...we're expecting the sensor
        # to pull down first)
        GPIO.setup(self.__pin, GPIO.IN, GPIO.PUD_UP)

        # Read the raw state of the pin
        rawState = self.__readInput()

        # Parse the rawState into pull up signal lengths
        pullUpLengths = self.__parseRawState(rawState)

        # If we do not have 40 bits at this point, then there was some kind of
        # problem
        if len(pullUpLengths) != 40:
            return DHT11Result(DHT11Result.ERR_MISSING_DATA, 0, 0)

        # We now have an array of the number of times each signal was read 
        # from the pin. Next, calculate the bits from these lengths of the
        # pull up periods
        bits = self.__calculateBits(pullUpLengths)

        # Transform the bits into bytes
        data = self.__bitsToBytes(bits)

        # Calculate and check the checksum
        checksum = self.__calculateChecksum(data)
        if data[4] != checksum:
            return DHT11Result(DHT11Result.ERR_BAD_CHECKSUM, 0, 0)

        # If we get this far, we have valid data and should return it. Note
        # that we only return the whole number parts of the data. The DHT11 
        # specs state that while there are places for the fractional parts of
        # each number (used by other similar sensors), they are not actually
        # used.
        return DHT11Result(DHT11Result.ERR_NONE, data[0], data[2])

    # Sends the output to the pin and then sleeps
    def __sendAndSleep(self, output, seconds):
        GPIO.output(self.__pin, output)
        time.sleep(seconds)

    # Continually reads the state of the pin until it has not changed a 
    # maximum number of times.
    def __readInput(self):
        unChangedCount = 0
        maximumUnchangedCount = 100

        last = -1
        rawState = []
        while True:
            current = GPIO.input(self.__pin)
            rawState.append(current)
            if last != current:
                unChangedCount = 0
                last = current
            else:
                unChangedCount += 1
                if unChangedCount > maximumUnchangedCount:
                    break;
        return rawState

    # Parses the raw state, separating it into a series of how long each 
    # signal each signal lasted.
    def __parseRawState(self, rawState):
        # The state that we are waiting for next
        STATE_INIT_PULL_DOWN = 1
        STATE_INIT_PULL_UP = 2
        STATE_DATA_FIRST_PULL_DOWN = 3
        STATE_DATA_PULL_UP = 4
        STATE_DATA_PULL_DOWN = 5

        readyForState = STATE_INIT_PULL_DOWN

        lengths = []
        current_length = 0

        for i in range(len(rawState)):
            current = rawState[i]
            current_length += 1

            if readyForState == STATE_INIT_PULL_DOWN:
                if current == GPIO.LOW:
                    # This is the initial starting pull down that precedes the
                    # initial pulse
                    readyForState = STATE_INIT_PULL_UP
                    continue
                else:
                    continue
            if readyForState == STATE_INIT_PULL_UP:
                if current == GPIO.HIGH:
                    # Indicates the initial starting pull up that precedes the
                    # data                    
                    readyForState = STATE_DATA_FIRST_PULL_DOWN
                    continue
                else:
                    continue
            if readyForState == STATE_DATA_FIRST_PULL_DOWN:
                if current == GPIO.LOW:
                    # The intial starting pull up is completed and the next
                    # pull up is the data
                    readyForState = STATE_DATA_PULL_UP
                    continue
                else:
                    continue
            if readyForState == STATE_DATA_PULL_UP:
                if current == GPIO.HIGH:
                    # A new bit has started, the length of time (in this case
                    # the number of raw states before it changes) it is pulled
                    # up indicates whether it is a 0 or a 1
                    current_length = 0
                    readyForState = STATE_DATA_PULL_DOWN
                    continue
                else:
                    continue
            if readyForState == STATE_DATA_PULL_DOWN:
                if current == GPIO.LOW:
                    # The end of the bit signal. The length (the number of
                    # times it was read) is stored.
                    lengths.append(current_length)
                    readyForState = STATE_DATA_PULL_UP
                    continue
                else:
                    continue
        return lengths

    # Calculates the bits from the pull up lengths. There are short (0)
    # and long (1) lengths.
    def __calculateBits(self, pullUpLengths):
        longestPullUp = 0        
        shortestPullUp = 1000

        # First we find the longest and shortest pull up lengths
        for i in range(0, len(pullUpLengths)):
            length = pullUpLengths[i]
            if length < shortestPullUp:
                shortestPullUp = length
            if length > longestPullUp:
                longestPullUp = length

        # We then find the middle and use it as a baseline to decide if a
        # length was either short (0) or long (1)
        middle = shortestPullUp + (longestPullUp - shortestPullUp) / 2
        bits = []

        # Finally, we loop through the lengths and determine if they're a 0 or
        # 1, storing the decisions as a new array of bits
        for i in range(0, len(pullUpLengths)):
            bit = 0
            if pullUpLengths[i] > middle:
                bit = 1
            bits.append(bit)

        return bits

    # Converts the bits to bytes. A byte consists of 8 bits. 
    # This function uses a few special operators to streamline the
    # conversion.
    # The left shift (<<) operator shifts the bits in a byte to the left and
    # inserts a 0.
    # For example:
    #   00001111 << 1 becomes
    #   00011110
    # Note that this works for any number notation. We're using binary
    # notation to show how it works, but as an example:
    #   4 << 1 becomes
    #   8
    # This is because, if you convert it to binary notation, you get:
    #   00000100 << 1 becomes (00000100 is 4)
    #   00001000              (00001000 is 8)
    #
    # The or operator (|) compares two bits and returns a result. It returns a
    # 1 if either the first bit or the second bit are 1; otherwise, it returns
    # 0. It is used in this method to essentially append the bit to the end of
    # the byte.
    # For example:
    #   00000000 | 00000001 = 00000001
    #   00000000 | 00000000 = 00000000
    #   00000001 | 00000001 = 00000001
    #   00000000 | 1        = 00000001
    # Again, note that this works for any number notation. For example:
    # 4 | 1 = 5
    # Because:
    # 00000100 | 00000001 = 00000101 (00000100 is 4 and 00000101 is 5)
    #
    # The modulus (%) operator returns the remainder left from dividing two 
    # numbers. It is used here to determine if i is a multiple of 8. A number 
    # X is a mutiple of another number Y if X divided by Y leaves a remainder
    # of zero. This is used to break up the bits into 8 bit bytes.
    # For example:
    #   10 % 3 = 1 (10 / 3 = 3, with a remainder of 1)
    #   8 % 3 = 2 (8 / 3 = 2, with a remainder of 2)
    def __bitsToBytes(self, bits):
        bytes = []
        byte = 0

        for i in range(0, len(bits)):
            byte = byte << 1
            byte = byte | bits[i]
            if ((i + 1) % 8 == 0):
                bytes.append(byte)
                byte = 0
        return bytes

    # Calculates the checksum from the data.
    def __calculateChecksum(self, data):
        return data[0] + data[1] + data[2] + data[3]
