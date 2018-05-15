#!/usr/bin/env python

from datetime import datetime
from enum import Enum
import logging


import six


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LineParseException(Exception):
    pass


class LinkDirection(Enum):
    UPLINK = 'ul'
    DOWNLINK = 'dl'
    NO_DIRECTION = 'L:no'


# Example lines
# VOC: i-1430527570.4954-t1 421036605 1625859953  66% 0.008 219 L:no LCW(0,001111,100000000000000000000 E1) 101110110101010100101101111000111111111001011111001011010001000010010001101110011010011001111111011101111100011001001001000111001101001011001011000101111111101110110011111000000001110010001110101101001010011001101001010111101100011100110011110010110110101010110001010000100100101011010010100100100011010110101001
# VOC: i-1526039037-t1 000065686 1620359296 100%   0.003 179 DL LCW(0,T:maint,C:maint[2][lqi:3,power:0,f_dtoa:0,f_dfoa:127](3),786686 E0)                                       [df.ff.f3.fc.10.33.c3.1f.0c.83.c3.cc.cc.30.ff.f3.ef.00.bc.0c.b4.0f.dc.d0.1a.cc.9c.c5.0c.fc.28.01.cc.38.c2.33.e0.ff.4f]
# IRA: i-1526300857-t1 000159537 1626299264 100%   0.003 130 DL sat:80 beam:30 pos=(+54.57/-001.24) alt=001 RAI:48 ?00 bc_sb:07 PAGE(tmsi:0cf155ab msc_id:03) PAGE(NONE) descr_extra:011010110101111001110011001111100110
class BaseLine(object):
    def __init__(self, line):
        try:
            self._raw_line = line
            line_split = line.split()

            self._frame_type = line_split[0][:-1]

            raw_time_base = line_split[1]
            ts_base_ms = int(raw_time_base.split('-')[1].split('.')[0])

            time_offset_ns = int(line_split[2])
            self._timestamp = int(ts_base_ms + (time_offset_ns / 1000))

            self._frequnecy = int(line_split[3])
            self._confidence = int(line_split[4][:-1])
            self._level = float(line_split[5])
            self._symbols = int(line_split[6])

            if line_split[7] == 'DL':
                self._link_direction = LinkDirection.DOWNLINK
            elif line_split[7] == 'UL':
                self._link_direction = LinkDirection.UPLINK
            else:
                self._link_direction = LinkDirection.NO_DIRECTION
        except (IndexError, ValueError) as e:
            logger.error('Failed to parse line "%s"', line)
            six.raise_from(LineParseException('Failed to parse line "{}"'.format(line), e), e)

    @property
    def raw_line(self):
        return self._raw_line

    @property
    def frame_type(self):
        return self._frame_type

    @property
    def datetime(self):
        return datetime.utcfromtimestamp(self._timestamp)

    @property
    def datetime_unix(self):
        return self._timestamp

    @property
    def frequency(self):
        return self._frequnecy

    @property
    def confidence(self):
        return self._confidence

    @property
    def level(self):
        return self._level

    @property
    def symbols(self):
        return self._symbols

    @property
    def link_direction(self):
        return self._link_direction

    def is_uplink(self):
        return self._link_direction == LinkDirection.UPLINK

    def is_downlink(self):
        return self._link_direction == LinkDirection.DOWNLINK
