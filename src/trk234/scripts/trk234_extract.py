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

==============
trk234_extract
==============

Extract a time history of a specific parameter from a TRK 2-34 file

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 09-DEC-2014
Last Modified: 14-SEP-2023

Synopsis::

   trk234_extract.py <TNF File> <options>

Options::

   -f <type_integer>, the 'format_code' or type ID of the data type to dump
          (optional, if not specified, will dump ALL types)
   -i <identifier>, the 'identifier' from the TRK 2-34 documentation to extract (required)
   -p, show a progress display for reading the file
   -h, access program help via the command line
   -t, print an ISO-T timestamp in YYYY-DDDTHH:MM:SS.fff format instead
   --label OR --agg OR --pri OR --sec OR --trk, the location where the identifer is in the file

"""

import os
import sys
from argparse import ArgumentParser
import trk234


def main(args):
    """Main program function. This is the first executed code,
    and contains the necessary argument parsing and dump functions"""

    # Read the TRK 2-34 file
    f = trk234.Reader(args.Input)
    f.decode(progress=args.progress)

    # Loop through the SFDU records
    for s in f.sfdu_list:

        # Skip invalid SFDUs
        if s.is_decoded == False:
            continue

        # Dump only the requested records, if specified
        if args.format_code is not None:
            if s.pri_chdo.format_code == args.format_code:
                print_line(s, args)
        else:
            print_line(s, args)


def print_line(sfdu, args):
    """function that prints a single line of TRK 2-34 data from the extract"""

    # Extract what we need
    year = sfdu.sec_chdo.year
    doy = sfdu.sec_chdo.doy
    sec = sfdu.sec_chdo.sec

    # Extract the requested identifier from CHDO
    param = None
    if args.label:
        if hasattr(sfdu.label, args.identifier):
            param = getattr(sfdu.label, args.identifier)
    if args.agg:
        if hasattr(sfdu.agg_chdo, args.identifier):
            param = getattr(sfdu.agg_chdo, args.identifier)
    if args.pri:
        if hasattr(sfdu.pri_chdo, args.identifier):
            param = getattr(sfdu.pri_chdo, args.identifier)
    if args.sec:
        if hasattr(sfdu.sec_chdo, args.identifier):
            param = getattr(sfdu.sec_chdo, args.identifier)
    if args.trk:
        if hasattr(sfdu.trk_chdo, args.identifier):
            param = getattr(sfdu.trk_chdo, args.identifier)

    # Print, but only if it exists
    if param is not None:
        if args.timestamp:
            ts = sfdu.timestamp().strftime("%Y-%jT%H:%M:%S.%f")
            print("%24s %17s " % (ts, str(param)))
        else:
            print("%4i %3i %12.6f %17s" % (year, doy, sec, str(param)))


# If called as a script, go to the main() function immediately
def execute():

    # Setup the parser
    parser = ArgumentParser(
        prog="trk234_extract",
        description="Extract a time-ordered specific identifier TRK-2-34 file",
    )

    # Add arguments
    parser.add_argument(
        "Input", type=str, help="the name of the TRK-2-34 file to read"
    )
    parser.add_argument(
        "-f",
        "--format_code",
        dest="format_code",
        type=int,
        help="the format code/type ID of the data type to dump",
    )
    parser.add_argument(
        "-p",
        dest="progress",
        default=False,
        action="store_true",
        help="show a progress display bar as processing occurs",
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
        "-i",
        "--id",
        dest="identifier",
        type=str,
        help="the identifier of the parameter from TRK 2-34 documentation to extract (required, plus one flag below)",
    )
    parser.add_argument(
        "--label",
        dest="label",
        default=False,
        action="store_true",
        help="flag the identifier is from the SFDU Label",
    )
    parser.add_argument(
        "--agg",
        dest="agg",
        default=False,
        action="store_true",
        help="flag the identifier as from the Aggregation CHDO label",
    )
    parser.add_argument(
        "--pri",
        dest="pri",
        default=False,
        action="store_true",
        help="flag the identifier as from the primary CHDO",
    )
    parser.add_argument(
        "--sec",
        dest="sec",
        default=False,
        action="store_true",
        help="flag the identifier as from the secondary CHDO",
    )
    parser.add_argument(
        "--trk",
        dest="trk",
        default=False,
        action="store_true",
        help="flag the identifier as from the tracking CHDO",
    )

    # Parse the command line automatically
    args = parser.parse_args()

    # Error checking - does the file exist
    if not os.path.exists(args.Input):
        parser.error("File %s does not exist" % args.Input)

    # Validate the format code
    if args.format_code is not None:
        if args.format_code < 0 or args.format_code > 17:
            parser.error("the format code/type ID must be between 0 and 17")

    # An identifier is required
    if args.identifier is None:
        parser.error('an identifier is required to extract, such as "dop_cnt"')

    # Only one of the flags is required to determine where to look in the file
    ll = [args.label, args.agg, args.pri, args.sec, args.trk]
    if sum(ll) == 0:
        parser.error(
            "one flag is required to determine where to look in the file for the identifer\n"
            + "   --label    flag it as from the SFDU Label\n"
            + "   --agg      flag it as from the Aggregation CHDO Label\n"
            + "   --pri      flag it as from the primary CHDO\n"
            + "   --sec      flag it as from the secondary CHDO\n"
            + "   --trk      flag it as from the tracking CHDO"
        )
    if sum(ll) > 1:
        parser.error("only one flag is required")

    main(args)
