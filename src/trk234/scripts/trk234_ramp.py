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
trk234_ramp
===========

Extract uplink ramp and frequency from a TRK 2-34 file

The output file is in the format:

YYYY DOY SPM RAMP_RATE RAMP_FREQUENCY

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 12-FEB-2015
Last Modified: 14-SEP-2023

Synopsis::

   trk234_dnlink.py <TNF File> <options>

Options::

   -d <dss_id>, print the DSS ID Number
   -b <band>, the band of the signal to print (S, X, K, L)
   -t, use an ISOT timestamp (YYYY-DDDTHH:MM:SS.ffffff) instead of YYY DDD SPM format
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

        # Only look at data type 09 - RAMPS
        if sfdu.pri_chdo.format_code == 9:

            # Now decode the secondary chdo and tracking chdo - (label, agg_chdo, pri_chdo already decoded)
            sfdu.decode(
                sfdu.binarydata, label=False, agg_chdo=False, pri_chdo=False
            )

            # Skip invalid SFDUs
            if sfdu.is_decoded == False:
                continue

            # Extract time
            year = sfdu.sec_chdo.year
            doy = sfdu.sec_chdo.doy
            sec = sfdu.sec_chdo.sec

            # Get DSS info
            dss = sfdu.sec_chdo.ul_dss_id
            band = trk234.bands[sfdu.sec_chdo.ul_band]

            # Get ramp info
            ramp_freq = sfdu.trk_chdo.ramp_freq
            ramp_rate = sfdu.trk_chdo.ramp_rate
            ramp_type = sfdu.trk_chdo.ramp_type

            # Do we meet the DSS_ID?
            if args.dss == dss or args.dss == 0:
                # Do we meet the band requirement?
                if args.band == band or args.band == "":
                    # Print the information in the right time format
                    if args.timestamp:
                        ts = sfdu.timestamp().strftime("%Y-%jT%H:%M:%S.%f")
                        print("%24s %13.6f %18.6f" % (ts, ramp_rate, ramp_freq))
                    else:
                        print(
                            "%4i %3i %12.6f %13.6f %18.6f"
                            % (year, doy, sec, ramp_rate, ramp_freq)
                        )


# If called as a script, go to the main() function immediately
def execute():

    # Setup the parser
    parser = ArgumentParser(
        prog="trk234_ramp",
        description="Extract uplink ramp data from TRK-2-34 file",
    )

    # Add arguments
    parser.add_argument(
        "Input", type=str, help="the name of the TRK-2-34 file to read"
    )
    parser.add_argument(
        "-d",
        "--dss",
        dest="dss",
        default=0,
        type=int,
        help="print only data from this DSN station",
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
        "-t",
        "--isot",
        dest="timestamp",
        default=False,
        action="store_true",
        help="print time in YYYY-DDDTHH:MM:SS.fff format instead",
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
    if args.dss < 0 or args.dss > 255:
        parser.error("invalid DSS ID number. enter a number between 1 and 255")

    main(args)
