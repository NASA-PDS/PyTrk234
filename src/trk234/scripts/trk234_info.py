#!/usr/bin/python3
# Copyright (c) 2023, California Institute of Technology ("Caltech").
# U.S. Government sponsorship acknowledged. Any commercial use must be
# negotiated with the Office of Technology Transfer at the California
# Institute of Technology.
#
# This software may be subject to U.S. export control laws. By accepting this
# software, the user agrees to comply with all applicable U.S. export laws
# and regulations. User has the responsibility to obtain export licenses, or
# other export authority as may be required before exporting such information
# to foreign countries or providing access to foreign persons.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions must reproduce the above copyright notice, this list of
#   conditions and the following disclaimer in the documentation and/or other
#   materials provided with the distribution.
# * Neither the name of Caltech nor its operating division, the Jet Propulsion
#   Laboratory, nor the names of its contributors may be used to endorse or
#   promote products derived from this software without specific prior written
#   permission.
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
"""

===========
trk234_info
===========

Print information about a TRK 2-34 File

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 05-AUG-2014
Last Modified: 14-SEP-2023

Synopsis::

   trk234_dump.py [options] <TNF File>

Options::

   -p, show a progress display
   -m, also display a tracking mode report by station
   -h, access program help via the command line

"""

import os
import sys
from argparse import ArgumentParser
import trk234


def main(args):
    """Main program function. This is the first executed code,
    and contains the necessary argument parsing and dump functions"""

    # Print function copied out of trk234.Info
    lprint = lambda x, y: "%22s  %s" % (x, y)

    # Read the TRK 2-34 file
    f = trk234.Reader(args.Input)

    # print quicklook if option is selected
    if args.quicklook:
        print("File load complete, running quick info...")
        info = trk234.Info(f, True)
        print(info)
        exit()

    # Decode data
    f.decode(progress=args.progress, trk_chdo=False)

    # Print info
    info = trk234.Info(f)
    print(info)

    # Do the tracking mode report
    if args.trk_mode_report:

        # Loop through each station
        for dss in info.dnlinkDssId:

            for band in info.dnlinkBand:

                # Extract SFDUs for only this station and determine the tracking mode
                sfdus = [
                    s
                    for s in f.sfdu_list
                    if s.dss_id()[1] == dss and s.radio_band()[1] == band
                ]

                # If none exist, skip it
                if len(sfdus) == 0:
                    continue
                # If some exist, print a header
                else:
                    print("%24s:" % ("DSS-%i %s-band Downlink" % (dss, band)))

                # Extract times and SFDUs
                times = [s.timestamp() for s in sfdus]
                # trk_mode = [ s.tracking_mode() for s in sfdus ]
                trk_mode = [
                    "DCC %02d %s" % (s.sec_chdo.dl_chan_num, s.tracking_mode())
                    for s in sfdus
                ]

                # Loop through the tracking modes and find out when they change ---
                # first sort by time so we're going time ascending order
                (t_sorted, trk_mode_sorted) = two_list_sort(times, trk_mode)

                # Get carrier loop bandwidth
                loop_bw = {}
                for s in sfdus:
                    if s.pri_chdo.format_code == 1:
                        s.decode(s.binarydata)
                        # loop_bw[s.tracking_mode()] = s.trk_chdo.carr_loop_bw
                        loop_bw[
                            "DCC %02d %s"
                            % (s.sec_chdo.dl_chan_num, s.tracking_mode())
                        ] = s.trk_chdo.carr_loop_bw

                # set the current mode empty so we print the first result
                current_mode = ""

                # start loop
                for i, (t, m) in enumerate(zip(t_sorted, trk_mode_sorted)):

                    # if the mode has changed, print the start time and set the current mode
                    if m != current_mode:

                        # if this isnt the first iteration, the stop time is the previous time. print it.
                        if i > 0:
                            if trk_mode_sorted[i - 1] != "None":
                                print(
                                    " - %s (Final Loop BW = %.1f Hz)\n"
                                    % (
                                        t_sorted[i - 1].strftime(
                                            "%Y-%jT%H:%M:%S"
                                        ),
                                        loop_bw[m],
                                    ),
                                    end=" ",
                                )

                        # Print the new mode and start time
                        if m != "None":
                            print(
                                "%23s @ %s" % (m, t.strftime("%Y-%jT%H:%M:%S")),
                                end=" ",
                            )
                        current_mode = m

                # exit loop, print the stop time.
                if m != "None":
                    print(
                        " - %s (Final Loop BW = %.1f Hz)\n"
                        % (t.strftime("%Y-%jT%H:%M:%S"), loop_bw[m])
                    )
                else:
                    print(
                        "%24s  %s"
                        % ("", "DCC predicts not loaded or specified")
                    )


def two_list_sort(list1, list2):
    """sort two lists by the first list:
    http://stackoverflow.com/questions/13668393/python-sorting-two-lists
    """
    sort = [
        list(x)
        for x in zip(*sorted(zip(list1, list2), key=lambda pair: pair[0]))
    ]
    return (sort[0], sort[1])


def execute():

    # Setup the parser
    parser = ArgumentParser(
        prog="trk234_info",
        description="Print information about a TRK-2-34 file",
    )

    # Add arguments
    parser.add_argument(
        "Input", type=str, help="the name of the TRK-2-34 file to read"
    )
    parser.add_argument(
        "-p",
        dest="progress",
        default=False,
        action="store_true",
        help="show a progress display bar as processing occurs",
    )
    parser.add_argument(
        "-m",
        dest="trk_mode_report",
        default=False,
        action="store_true",
        help="also display a downlink tracking mode report by station",
    )
    parser.add_argument(
        "-q",
        dest="quicklook",
        default=False,
        action="store_true",
        help="do quicklook only (does not do a complete info search)",
    )

    # Parse the command line automatically
    args = parser.parse_args()

    # Error checking - does the file exist
    if not os.path.exists(args.Input):
        parser.error("File %s does not exist" % args.Input)

    main(args)
