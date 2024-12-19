#!/usr/bin/env python

# log_gpu_cpu_stats
#   Logs GPU and CPU stats either to stdout, or to a CSV file.
#   See usage below.

# Copyright (c) 2019,  Scott C. Lowe <scott.code.lowe@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

import psutil
import sys
import time

import contextlib

@contextlib.contextmanager
def smart_open(filename=None, mode='a'):
    """
    Context manager which can handle writing to stdout as well as files.

    If filename is None, the handle yielded is to stdout. If writing to
    stdout, the connection is not closed when leaving the context.
    """
    if filename:
        hf = open(filename, mode)
    else:
        hf = sys.stdout

    try:
        yield hf
    finally:
        if hf is not sys.stdout:
            hf.close()

class Logger():
    def __init__(
            self,
            fname=None, style=None, date_format=None,
            refresh_interval=1, iter_limit=None,
            show_header=True, header_only_once=True,
            show_units=True, sep=',',
            ):

        self.fname = fname if fname else None
        if style is not None:
            self.style = style
        elif self.fname is None:
            self.style = 'tabular'
        else:
            self.style = 'csv'
        self.date_format = date_format
        self.refresh_interval = refresh_interval
        self.iter_limit = iter_limit
        self.show_header = show_header
        self.header_only_once = header_only_once
        self.header_count = 0
        self.show_units = show_units
        self.sep = sep
        self.col_width = 10
        self.time_field_width = 15 if self.date_format is None else \
            max(self.col_width, len(time.strftime(self.date_format)))

        if self.date_format is None:
            self.time_field_name = 'Timestamp' + \
                (' (s)' if self.show_units else '')
        else:
            self.time_field_name = 'Time'

        self.cpu_field_names = [
            'CPU' + (' (%)' if self.show_units else ''),
            'RAM' + (' (%)' if self.show_units else ''),
            'Swap' + (' (%)' if self.show_units else ''),
            'CPU Temp' + (' (°C)' if self.show_units else ''),
            'CPU Freq' + (' (MHz)' if self.show_units else ''),
        ]

    @property
    def tabular_format(self):
        fmt = '{:>' + str(self.time_field_width) + '} |'
        fmt += ('|{:>' + str(self.col_width) + '} ') \
            * len(self.cpu_field_names)

        return fmt

    def write_header_csv(self):
        """
        Write header in CSV format.
        """
        with smart_open(self.fname, 'a') as hf:
            print(self.time_field_name + self.sep, end='', file=hf)
            print(*self.cpu_field_names, sep=self.sep, end='', file=hf)
            print("\n", end='', file=hf)  # add a newline

    def write_header_tabular(self):
        """
        Write header in tabular format.
        """
        with smart_open(self.fname, 'a') as hf:
            cols = [self.time_field_name]
            cols += self.cpu_field_names
            print(self.tabular_format.format(*cols), file=hf)

            # Add separating line
            print('-' * (self.time_field_width + 1), end='', file=hf)
            print(
                '+',
                ('+' + '-' * (self.col_width + 1)) \
                    * len(self.cpu_field_names),
                sep='', end='', file=hf)

            print("\n", end='', file=hf)  # add a newline

    def poll_cpu(self):
        """
        Fetch current CPU, RAM, Swap utilization, CPU temperature, and CPU frequency,
        including per-core CPU utilization.

        Returns
        -------
        tuple
            A tuple containing:
            - Overall CPU utilization (percentage)
            - RAM utilization (percentage)
            - Swap utilization (percentage)
            - CPU temperature (Celsius)
            - CPU frequency (MHz)
            - Per-core CPU utilization (list of percentages)
        """
        return (
            psutil.cpu_percent(),
            psutil.virtual_memory().percent,
            psutil.swap_memory().percent,
            psutil.sensors_temperatures()['cpu_thermal'][0].current,
            psutil.cpu_freq().current,
            psutil.cpu_percent(percpu=True),  # Add per-core CPU usage
        )


    def write_record(self):
        with smart_open(self.fname, 'a') as hf:
            stats = list(self.poll_cpu())
            overall_stats = stats[:-1]  # All stats except per-core usage
            per_core_stats = stats[-1]  # Per-core CPU usage

            if self.date_format is None:
                t = time.time()
            else:
                t = time.strftime(self.date_format)

            # Insert timestamp
            overall_stats.insert(0, t)

            # Combine overall stats and per-core stats for logging
            all_stats = overall_stats + list(per_core_stats)

            if self.style == 'csv':
                print(','.join([str(stat) for stat in all_stats]), file=hf)
            elif self.style == 'tabular':
                print(self.tabular_format.format(*all_stats), file=hf)
            else:
                raise ValueError('Unrecognised style: {}'.format(self.style))


    def write_header(self):
        if self.show_header:
            # Add per-core headers dynamically
            core_count = psutil.cpu_count(logical=True)
            core_headers = [
                f'Core {i}' + (' (%)' if self.show_units else '')
                for i in range(core_count)
            ]
            self.cpu_field_names.extend(core_headers)

            if self.style == 'csv':
                self.write_header_csv()
            elif self.style == 'tabular':
                self.write_header_tabular()
            else:
                raise ValueError('Unrecognised style: {}'.format(self.style))
            self.header_count += 1

    def __call__(self, n_iter=None):
        if self.show_header and (self.header_count < 1
                                 or not self.header_only_once):
            self.write_header()
        n_iter = self.iter_limit if n_iter is None else n_iter
        i_iter = 0
        while True:
            t_begin = time.time()
            self.write_record()
            i_iter += 1
            if n_iter is not None and n_iter > 0 and i_iter >= n_iter:
                break
            t_sleep = self.refresh_interval + t_begin - time.time() - 0.001
            if t_sleep > 0:
                time.sleep(t_sleep)


def main(**kwargs):
    logger = Logger(**kwargs)
    logger()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l', '--loop',
        help = 'Loop every INTERVAL seconds. Default is 1 second.',
        metavar = 'INTERVAL',
        dest = 'refresh_interval',
        type = float,
        default = 1.0,
    )
    parser.add_argument(
        '-n', '--niter',
        help = 'Repeat at most MAXITER times. Default is -1, which'
               ' corresponds to forever (send interrput signal to terminate).',
        metavar = 'MAXITER',
        dest = 'iter_limit',
        type = int,
        default = -1,
    )
    parser.add_argument(
        '-H', '--no-header',
        help = 'Disable header in table output. Default is enabled.',
        dest = 'show_header',
        action = 'store_false',
    )
    parser.add_argument(
        '--header',
        help = 'Enable header in table output. Default is enabled.',
        dest = 'show_header',
        action = 'store_true',
        default = True,
    )
    parser.add_argument(
        '-c', '--csv',
        help = 'Output in csv style. Default style is csv if FILE is set.',
        dest = 'style',
        action = 'store_const',
        const = 'csv',
    )
    parser.add_argument(
        '-t', '--tabular',
        help = 'Output in ascii table style. Default style is tabular'
               ' if FILE is not set (output is sent to stdout).',
        dest = 'style',
        action = 'store_const',
        const = 'tabular',
    )
    parser.add_argument(
        '-s', '--date-seconds',
        help = 'Show time in seconds since Unix epoch (with ms precision'
               ' reported). Enabled by default.',
        dest = 'date_format',
        action = 'store_const',
        const = None,
    )
    parser.add_argument(
        '-I', '--date-iso',
        help = 'Show time in ISO format.',
        dest = 'date_format',
        action = 'store_const',
        const = '%Y-%m-%dT%H:%M:%S%z',
    )
    parser.add_argument(
        '--date-local',
        help = 'Show time in ISO-compliant, but more human friendly format,'
               ' omitting the time zone component and using a space as date/'
               'time separator.',
        dest = 'date_format',
        action = 'store_const',
        const = '%Y-%m-%d %H:%M:%S',
    )
    parser.add_argument(
        '-d', '--date-custom',
        help = 'Show time in custom format, FORMAT.',
        dest = 'date_format',
        action = 'store',
    )
    parser.add_argument(
        '--units',
        help = 'In the header, include units for each column.'
               ' Enabled by default.',
        dest = 'show_units',
        action = 'store_true',
        default = True,
    )
    parser.add_argument(
        '--no-units',
        help = 'In the header, omit units. Default is to include units.',
        dest = 'show_units',
        action = 'store_false',
        default = True,
    )
    parser.add_argument(
        'fname',
        help = 'If present, output is appended to FILE. If omitted,'
               ' output is sent to stdout.',
        metavar = 'FILE',
        default = None,
        nargs = '?',
    )
    args = parser.parse_args()
    main(**vars(args))