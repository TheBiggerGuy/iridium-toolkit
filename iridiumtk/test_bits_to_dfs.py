#!/usr/bin/env python

import unittest
from io import BytesIO


from .bits_to_dfs import bits_to_dfs


class BitsToDfsTest(unittest.TestCase):
    TEST_VOC_LINE_1 = 'VOC: i-1443338945.6543-t1 033399141 1625872817  81% 0.027 179 L:no LCW(0,001111,100000000000000000000 E1) 01111001000100010010010011011011011001111    011000010000100001110101111011110010010111011001010001011101010001100000000110010100000110111110010101110101001111010100111001000110100110001110110    1010101010010010001000001110011000001001001010011110011100110100111110001101110010110101010110011101011100011101011000000000 descr_extra:'
    TEST_VOC_LINE_2 = 'VOC: i-1526039037-t1 000065686 1620359296 100%   0.003 179 DL LCW(0,T:maint,C:maint[2][lqi:3,power:0,f_dtoa:0,f_dfoa:127](3),786686 E0)                                       [df.ff.f3.fc.10.33.c3.1f.0c.83.c3.cc.cc.30.ff.f3.ef.00.bc.0c.b4.0f.dc.d0.1a.cc.9c.c5.0c.fc.28.01.cc.38.c2.33.e0.ff.4f]'
    TEST_VOC_LINE_3 = 'VOC: i-1526039037-t1 000065686 1620359296 100%   0.003 178 DL LCW(0,T:maint,C:maint[2][lqi:3,power:0,f_dtoa:0,f_dfoa:127](3),786686 E0)                                       [df.ff.f3.fc.10.33.c3.1f.0c.83.c3.cc.cc.30.ff.f3.ef.00.bc.0c.b4.0f.dc.d0.1a.cc.9c.c5.0c.fc.28.01.cc.38.c2.33.e0.ff]'

    def test_empty_input(self):
        output = BytesIO()
        bits_to_dfs([], output)
        self.assertEquals(output.getvalue(), '')

    def test_raw_data(self):
        output = BytesIO()
        with self.assertRaises(RuntimeError):
            bits_to_dfs(['RAW: i-1525892321-t1 0001338 1623702528 A:OK I:00000000027  79% 0.001 179 0011000000110000111100110001000000010011100100011000001000101111100010010101110100110101010101010101010101010101010101010101010101011100010111010001010101010101010101110011010011010101010101010101010111000101010101011101001101010101010101010101010101010101010101010101010101010101010101010101010101010101010101110001110101000111001101010101010100110101010101010101010101010101010101'], output)
        
        output = BytesIO()
        bits_to_dfs(['RAW: i-1525892321-t1 000045987 1626110208  83%   0.001 <001100000011000011110011> 1100000000000000 0000000000000000 0000000000000000 1001000000000000 0000000000000000 0000000000000000 0100001000110110 0111100001010110 1011001111101110 1010110101000101 1111111001110101 1011110101110001 1110000001110111 0110001000001010 0100100100111000 1000001111010100 1011001101011110 0100011011100010 1111110001010001 1100110110101111 0011100111100101 1110100100000110 0111011111110010 1111110011001000 1101000011000011 1011110101110111 0000101000000001 1000111010101100 1011000001010011 0111011100011101 0101011000011101 0111110001001101 0100001011001010 1101001110100010 0111011001000101 0100111001010110 0001111110101010 1110001100010111 0001010101100100 1001010100111011 1001111110001101 0110100100010010 0001110111101001 1000011010111100 00011001 ERR:Message: unknown Iridium message type'], output)
        self.assertEquals(output.getvalue(), '')

    def test_short_packet(self):
        output = BytesIO()
        bits_to_dfs([BitsToDfsTest.TEST_VOC_LINE_3], output)
        self.assertEquals(output.getvalue(), '')

    def test_multiple(self):
        output = BytesIO()
        bits_to_dfs([BitsToDfsTest.TEST_VOC_LINE_1, BitsToDfsTest.TEST_VOC_LINE_1, BitsToDfsTest.TEST_VOC_LINE_2], output)
        self.assertEquals(output.getvalue(), ('\x9e\x88$\xdb\xe6\x01' * 2) + '\xfb\xff\xcf?\x08\xcc\xc3\xf80\xc1\xc333\x0c\xff\xcf\xf7\x00=0-\xf0;\x0bX39\xa30?\x14\x803\x1cC\xcc\x07\xff\xf2')

    def test_filters_non_voc_lines(self):
        output = BytesIO()
        bits_to_dfs([BitsToDfsTest.TEST_VOC_LINE_1, 'NOT_VOC:', BitsToDfsTest.TEST_VOC_LINE_2], output)
        self.assertEquals(output.getvalue(), '\x9e\x88$\xdb\xe6\x01' + '\xfb\xff\xcf?\x08\xcc\xc3\xf80\xc1\xc333\x0c\xff\xcf\xf7\x00=0-\xf0;\x0bX39\xa30?\x14\x803\x1cC\xcc\x07\xff\xf2')


class MainTest(unittest.TestCase):
    def test_pass(self):
        pass


def main():
    unittest.main()


if __name__ == "__main__":
    main()
