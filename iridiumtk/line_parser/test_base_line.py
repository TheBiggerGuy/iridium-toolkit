#!/usr/bin/env python

from datetime import datetime
import unittest


from .base_line import BaseLine


class BaseLineTest(unittest.TestCase):
    TEST_VOC_LINE_1 = 'VOC: i-1443338945.6543-t1 033399141 1625872817  81% 0.027 179 L:no LCW(0,001111,100000000000000000000 E1) 01111001000100010010010011011011011001111    011000010000100001110101111011110010010111011001010001011101010001100000000110010100000110111110010101110101001111010100111001000110100110001110110    1010101010010010001000001110011000001001001010011110011100110100111110001101110010110101010110011101011100011101011000000000 descr_extra:'
    TEST_VOC_LINE_2 = 'VOC: i-1526039037-t1 000065686 1620359296 100%   0.003 179 DL LCW(0,T:maint,C:maint[2][lqi:3,power:0,f_dtoa:0,f_dfoa:127](3),786686 E0)                                       [df.ff.f3.fc.10.33.c3.1f.0c.83.c3.cc.cc.30.ff.f3.ef.00.bc.0c.b4.0f.dc.d0.1a.cc.9c.c5.0c.fc.28.01.cc.38.c2.33.e0.ff.4f]'

    def test_empty_input(self):
        with self.assertRaises(Exception):
            BaseLine('')

    def test_old_format_datetime(self):
        base_line = BaseLine(BaseLineTest.TEST_VOC_LINE_1)
        self.assertEquals(base_line.datetime_unix, 1443372344)
        self.assertEquals(base_line.datetime, datetime.utcfromtimestamp(1443372344))

    def test_new_format_datetime(self):
        base_line = BaseLine(BaseLineTest.TEST_VOC_LINE_2)
        self.assertEquals(base_line.datetime_unix, 1526039102)
        self.assertEquals(base_line.datetime, datetime.utcfromtimestamp(1526039102))

    def test_frequency(self):
        base_line = BaseLine(BaseLineTest.TEST_VOC_LINE_2)
        self.assertEquals(base_line.frequency, 1620359296)

    def test_frame_type(self):
        base_line = BaseLine(BaseLineTest.TEST_VOC_LINE_2)
        self.assertEquals(base_line.frame_type, 'VOC')

    def test_raw_line(self):
        for line in [BaseLineTest.TEST_VOC_LINE_1, BaseLineTest.TEST_VOC_LINE_2]:
            base_line = BaseLine(line)
            self.assertEquals(base_line.raw_line, line)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
