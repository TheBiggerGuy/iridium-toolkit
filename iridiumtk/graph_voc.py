#!/usr/bin/python

import sys
import os
import subprocess
import fileinput
import logging
from datetime import datetime
import argparse
from collections import namedtuple
import subprocess


import matplotlib.pyplot as plt
import numpy as np
import dateparser


from .line_parser import VocLine


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


KHZ = 1000
MHZ = KHZ * 1000

# https://www.sigidwiki.com/wiki/Iridium
ChannelInfo = namedtuple('ChannelInfo', ['description', 'frequency'])
SIMPLEX_CHANELS = {
    ChannelInfo('Guard Channel', 1626.020833 * MHZ),
    ChannelInfo('Guard Channel', 1626.062500 * MHZ),
    ChannelInfo('Quaternary Messaging', 1626.104167 * MHZ),
    ChannelInfo('Tertiary Messaging', 1626.145833 * MHZ),
    ChannelInfo('Guard Channel', 1626.187500 * MHZ),
    ChannelInfo('Guard Channel', 1626.229167 * MHZ),
    ChannelInfo('Ring Alert', 1626.270833 * MHZ),
    ChannelInfo('Guard Channel', 1626.312500 * MHZ),
    ChannelInfo('Guard Channel', 1626.354167 * MHZ),
    ChannelInfo('Secondary Messaging', 1626.395833 * MHZ),
    ChannelInfo('Primary Messaging', 1626.437500 * MHZ),
    ChannelInfo('Guard Channel', 1626.479167 * MHZ),
}
DUPLEX_CHANELS = frozenset(SIMPLEX_CHANELS)

DUPLEX_CHANELS = set()
for n in xrange(1, 240):
    frequency = (1616 + 0.020833 * (2 * n - 1)) * MHZ
    DUPLEX_CHANELS.add(ChannelInfo('Channel {}'.format(n), frequency))
DUPLEX_CHANELS = frozenset(DUPLEX_CHANELS)

ALL_CHANELS = frozenset((SIMPLEX_CHANELS | DUPLEX_CHANELS))


class VoiceDataPlayer(object):
    def __init__(self):
        self.ir77_ambe_decode = subprocess.Popen(['ir77_ambe_decode'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.aplay = subprocess.Popen(['aplay'], stdin=self.ir77_ambe_decode.stdout, stderr=subprocess.PIPE)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def play_bits(self, bits):
        self.ir77_ambe_decode.stdin.write(bits)

    def close(self):
        self.ir77_ambe_decode.stdin.close()
        logger.info('aplay "%s"', self.aplay.communicate()[1].strip())

        logger.info('Waiting for ir77_ambe_decode/aplay')
        self.ir77_ambe_decode.wait()
        self.aplay.wait()
        logger.info('ir77_ambe_decode/aplay closed')
    
class OnClickHandler(object):
    def __init__(self, lines):
        self.lines = lines
        self.t_start = None
        self.t_stop = None
        self.f_min = None
        self.f_max = None

    def onclick(self, event):
        logger.info('button=%d, x=%d, y=%d, xdata=%f, ydata=%f',
            event.button, event.x, event.y, event.xdata, event.ydata)

        if event.button == 1:
            self.t_start = event.xdata
            self.f_min = event.ydata
            self.t_stop = None
            self.f_max = None
        if event.button == 3:
            self.t_stop = event.xdata
            self.f_max = event.ydata
        
        if self.t_start and self.t_stop:
            self.cut_convert_play(self.t_start, self.t_stop, self.f_min, self.f_max)

    def filter_voc(self, t_start, t_stop, f_min, f_max):
        for voc_line in self.lines:
            ts = voc_line.datetime_unix
            f = voc_line.frequency
            if t_start <= ts and ts <= t_stop and \
               f_min <= f and f <= f_max:
                yield voc_line

    def cut_convert_play(self, t_start, t_stop, f_min, f_max):
        logger.info('Starting to play...')
        if t_start > t_stop:
            tmp = t_stop
            t_stop = t_start
            t_start = tmp
        if f_min > f_max:
            tmp = f_max
            f_max = f_min
            f_min = tmp

        with VoiceDataPlayer() as player:
            for voc_frame in self.filter_voc(t_start, t_stop, f_min, f_max):
                voice_bits = voc_frame.voice_bits
                if voice_bits is not None:
                    player.play_bits(voice_bits)

        logger.info('Finished Playing')


def read_lines(input_files, start_time_filter, end_time_filter):
    for line in fileinput.input(files=input_files):
        line = line.strip()
        if 'A:OK' in line and "Message: Couldn't parse:" not in line:
            raise RuntimeError('Expected "iridium-parser.py" parsed data. Found raw "iridium-extractor" data.')
        if 'VOC: ' in line and not "LCW(0,001111,100000000000000000000" in line:
            voc_line = VocLine(line)
            if start_time_filter and start_time_filter > voc_line.datetime:
                continue
            if end_time_filter and end_time_filter < voc_line.datetime:
                continue
            yield voc_line

def main():
    parser = argparse.ArgumentParser(description='Convert iridium-parser.py VOC output to DFS')
    parser.add_argument('--start', metavar='DATETIME', default=None, help='Filter events before this time')
    parser.add_argument('--end', metavar='DATETIME', default=None, help='Filter events after this time')
    parser.add_argument('input', metavar='FILE', nargs='*', help='Files to read, if empty or -, stdin is used')
    args = parser.parse_args()

    input_files = args.input if len(args.input) > 0 else ['-']
    start_time_filter = dateparser.parse(args.start) if args.start else None
    end_time_filter = dateparser.parse(args.end) if args.end else None

    lines = list(read_lines(input_files, start_time_filter, end_time_filter))
    number_of_lines = len(lines)
    logger.info('Read %d VOC lines from input', number_of_lines)

    if number_of_lines == 0:
        print('No usable data found')
        sys.exit(1)

    plot_data_time = np.empty(number_of_lines, dtype=np.float64)
    plot_data_freq = np.empty(number_of_lines, dtype=np.uint32)
    for i, voc_line in enumerate(lines):
        #plot_data_time[i] = np.datetime64(voc_line.datetime().isoformat())
        plot_data_time[i] = np.uint32(voc_line.datetime_unix)
        plot_data_freq[i] = np.float64(voc_line.frequency)

    fig = plt.figure()
    #fig.autofmt_xdate()
    on_click_handler = OnClickHandler(lines)
    fig.canvas.mpl_connect('button_press_event', on_click_handler.onclick)
    
    subplot = fig.add_subplot(1, 1, 1)
    subplot.scatter(plot_data_time, plot_data_freq)
    #subplot.xaxis_date()

    for channel in ALL_CHANELS:
        if 'Guard' in channel.description:
            color = 'tab:gray'
        elif 'Messaging' in channel.description:
            color = 'tab:orange'
        elif 'Ring' in channel.description:
            color = 'tab:red'
        else:
            color = 'tab:green'
        subplot.axhline(channel.frequency, color=color, alpha=0.3, label=channel.description)

    plt.title('Click once left and once right to define an area.\nThe script will try to play iridium using ir77_ambe_decode and aplay.')
    plt.xlabel('time')
    plt.ylabel('frequency')
    plt.show()


if __name__ == "__main__":
    main()
