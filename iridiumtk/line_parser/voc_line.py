#!/usr/bin/env python

import logging
from io import BytesIO


from .base_line import BaseLine, LineParseException


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


# Example lines
# VOC: i-1430527570.4954-t1 421036605 1625859953  66% 0.008 219 L:no LCW(0,001111,100000000000000000000 E1) 101110110101010100101101111000111111111001011111001011010001000010010001101110011010011001111111011101111100011001001001000111001101001011001011000101111111101110110011111000000001110010001110101101001010011001101001010111101100011100110011110010110110101010110001010000100100101011010010100100100011010110101001
# VOC: i-1526039037-t1 000065686 1620359296 100%   0.003 179 DL LCW(0,T:maint,C:maint[2][lqi:3,power:0,f_dtoa:0,f_dfoa:127](3),786686 E0)                                       [df.ff.f3.fc.10.33.c3.1f.0c.83.c3.cc.cc.30.ff.f3.ef.00.bc.0c.b4.0f.dc.d0.1a.cc.9c.c5.0c.fc.28.01.cc.38.c2.33.e0.ff.4f]
class VocLine(BaseLine):
    def __init__(self, line):
        super(VocLine, self).__init__(line)
        try:
            line_split = line.split()
            assert line_split[0] == 'VOC:', 'Non VOC line passed to VocLine'

            self.lcw = line[8]

            if int(line_split[6]) < 179:
                self._voice_data = None
            else:
                self._voice_data = line_split[10]
        except (IndexError, ValueError) as e:
            logger.error('Failed to parse line "%s"', line)
            raise LineParseException(f'Failed to parse line "{line}"') from e

    @property
    def voice_bits(self):
        data = self._voice_data
        if data is None:
            return None
        if data[0] == "[":
            return bytes.fromhex(data[1:-1].replace('.', ' '))
        else:
            result = bytearray()
            for bits_of_byte in chunks(data, 8):
                byte = 0
                for i in range(0, len(bits_of_byte)):
                    if bits_of_byte[i] == '0':
                        continue
                    elif bits_of_byte[i] == '1':
                        byte = byte | (1 << i)
                    else:
                        raise LineParseException(f'Unknown byte format: {data}')
                result.append(byte)
            return result
