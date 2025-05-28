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

=============
trk234_dnlink
=============

Extract Pc/No and Power from a TRK 2-34 File. It will extract
from DATA TYPE 01 (DOWNLINK CARRIER PHASE)

The output file is in the format:

YYYY DOY SPM SKYFREQ SNT PCNO LOOPBW

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 01-AUG-2014
Last Modified: 14-SEP-2023

Synopsis::

   trk234_dnlink.py <TNF File> <options>

Options::

   -l, print only if in lock
   -d <dss_id>, print the DSS ID Number
   -b <band>, the band of the signal to print (S, X, K, L)
   -m <mode>, the mode of the signal (1, 2, 3)
   -t, use an ISOT timestamp (YYYY-DDDTHH:MM:SS.ffffff) instead of YYY DDD SPM format
   -c, write to Excel-compatible CSV instead
   -h, access program help via the command line

"""

import os
import sys
from argparse import ArgumentParser
import trk234


def main(args):
    """Main program function. This is the first executed code,
    and contains the necessary argument parsing and dump functions"""

    # Read the TRK 2-34 file. only decode the label, aggregation CHDO and primary CHDO to start
    # not decoding the secondary CHDO and tracking CHDO saves a lot of time
    f = trk234.Reader(args.Input)
    f.decode(sec_chdo=False, trk_chdo=False)

    # Loop through the SFDU records
    for sfdu in f.sfdu_list:

        # Only look at data type 01
        if sfdu.pri_chdo.format_code == 1:

            # Now decode the secondary chdo and tracking chdo - (label, agg_chdo, pri_chdo already decoded)
            sfdu.decode(
                sfdu.binarydata, label=False, agg_chdo=False, pri_chdo=False
            )

            # Skip invalid SFDUs
            if sfdu.is_decoded == False:
                continue

            # Extract what we need
            year = sfdu.sec_chdo.year
            doy = sfdu.sec_chdo.doy
            sec = sfdu.sec_chdo.sec
            pcn0 = sfdu.trk_chdo.pcn0
            snt = sfdu.trk_chdo.system_noise_temp
            skyfreq = sfdu.trk_chdo.dl_freq
            resid = sfdu.trk_chdo.dop_resid
            lockstat = sfdu.sec_chdo.carr_lock_stat
            dl_dss = sfdu.sec_chdo.dl_dss_id
            ul_dss = sfdu.sec_chdo.ul_prdx_stn
            band = trk234.bands[sfdu.sec_chdo.dl_band]
            loop_bw = sfdu.trk_chdo.carr_loop_bw
            channel = sfdu.sec_chdo.dl_chan_num

            # Do we meet the lock status?
            if args.in_lock and lockstat == 4 or not args.in_lock:
                # Do we meet the DSS_ID?
                if args.dl_dss == dl_dss or args.dl_dss == 0:
                    # Do we meet uplink DSS ID
                    if args.ul_dss == ul_dss or args.ul_dss == 0:
                        # Do we meet the band requirement?
                        if args.band == band or args.band == "":
                            # Do we met the DTT channel number?
                            if args.chan == channel or args.chan == 0:
                                # Do we meet the tracking mode requirement?
                                if (
                                    args.mode == sfdu.tracking_mode()
                                    or args.mode == ""
                                ):
                                    # Print the information in the right time format
                                    if args.timestamp:
                                        ts = sfdu.timestamp().strftime(
                                            "%Y-%jT%H:%M:%S.%f"
                                        )
                                        print(
                                            "%24s %17.5f %14.4f %5.1f %5.1f %5.1f"
                                            % (
                                                ts,
                                                skyfreq,
                                                resid,
                                                snt,
                                                pcn0,
                                                loop_bw,
                                            )
                                        )
                                    elif args.csv:
                                        ts = sfdu.timestamp().strftime(
                                            '"%Y-%m-%d %H:%M:%S.%f"'
                                        )
                                        print(
                                            "%s,%.5f,%.4f,%.1f,%.1f,%.1f"
                                            % (
                                                ts,
                                                skyfreq,
                                                resid,
                                                snt,
                                                pcn0,
                                                loop_bw,
                                            )
                                        )
                                    else:
                                        print(
                                            "%4i %3i %12.6f %17.5f %14.4f %5.1f %5.1f %5.1f"
                                            % (
                                                year,
                                                doy,
                                                sec,
                                                skyfreq,
                                                resid,
                                                snt,
                                                pcn0,
                                                loop_bw,
                                            )
                                        )


def execute() -> None:

    # Setup the parser
    parser = ArgumentParser(
        prog="trk234_dnlink",
        description="Extract downlink tracking data from TRK-2-34 file",
    )

    # Add arguments
    parser.add_argument(
        "Input", type=str, help="the name of the TRK-2-34 file to read"
    )
    parser.add_argument(
        "-l",
        "--in-lock",
        dest="in_lock",
        default=False,
        action="store_true",
        help="only print if the carrier is in-lock",
    )
    parser.add_argument(
        "-d",
        "--dss",
        dest="dl_dss",
        default=0,
        type=int,
        help="print only data from this downlink DSN station",
    )
    parser.add_argument(
        "-u",
        "--ul_dss",
        dest="ul_dss",
        default=0,
        type=int,
        help="print only data where uplink came from this DSN station",
    )
    parser.add_argument(
        "-b",
        "--band",
        dest="band",
        default="",
        type=str,
        help="print only data from this band (S, X, Ka, L)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        default="",
        type=str,
        help="print only data from is mode (1W, 2W, 3W/XX)",
    )
    parser.add_argument(
        "--chan",
        dest="chan",
        default=0,
        type=int,
        help="print data only from this DCC Channel number",
    )
    parser.add_argument(
        "-t",
        "--isot",
        dest="timestamp",
        default=False,
        action="store_true",
        help="print time in YYYY-DDDTHH:MM:SS.fff format instead",
    )
    parser.add_argument(
        "-c",
        "--csv",
        dest="csv",
        default=False,
        action="store_true",
        help="write a CSV file instead which can be read in excel",
    )

    # Parse the command line automatically
    args = parser.parse_args()

    # Error checking - does the file exist
    if not os.path.exists(args.Input):
        parser.error("File %s does not exist" % args.Input)

    # validate the band input
    if args.band not in trk234.bands.values() and args.band != "":
        parser.error("invalid band. valid bands are: S, X, Ka, Ku, or L")

    # Validate the DSS input
    if args.dl_dss < 0 or args.dl_dss > 255:
        parser.error(
            "invalid downlink DSS ID number. enter a number between 1 and 255"
        )

    # Validate the DSS input
    if args.ul_dss < 0 or args.ul_dss > 255:
        parser.error(
            "invalid uplink DSS ID number. enter a number between 1 and 255"
        )

    # validate the mode input
    if args.mode[0:2] not in ["1W", "2W", "3W"] and args.mode != "":
        parser.error(
            "invalid mode, please use 1W, 2W or 3W/XX, where XX is the transmitting station"
        )

    main(args)

    return None
