import numpy

class editdistance_xor:

    def __init__(self):
        '''
        --Do something--
        '''

    def eval(string1, string2):
        number1 = int(string1,2)
        number2 = int(string2,2)
        result = numpy.bitwise_xor(number1,number2)
        binary = bin(result)[2:]
        ans = binary.count('1')
        return ans
