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
trk234_dump
===========

Dump a TRK 2-34 File to ASCII

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 01-AUG-2014
Last Modified: 14-SEP-2023

Synopsis::

   trk234_dump.py <TNF File> <options>

Options::

   -f <type_integer>, the 'format_code' or type ID of the data type to dump
          (optional, if not specified, will dump ALL types)
   -m <max_number>, maximum number of SFDU data records to dump
   -h, access program help via the command line

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
    f.decode(sec_chdo=False, trk_chdo=False)

    # Loop through the SFDU records
    i = 1
    for s in f.sfdu_list:

        # Dump only the requested records, if specified
        if args.format_code is not None:
            if s.pri_chdo.format_code == args.format_code:
                s.decode(s.binarydata)
                print(s)
                i = i + 1
        else:
            s.decode(s.binarydata)
            print(s)
            i = i + 1

        # if we reach the maximum number of records to dump, exit loop
        if args.max is not None and i > args.max:
            break


# If called as a script, go to the main() function immediately
def execute():

    # Setup the parser
    parser = ArgumentParser(
        prog="trk234_dump",
        description="Dump all data from a TRK-2-34 file to plain-text",
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
        "-m",
        "--max",
        dest="max",
        type=int,
        default=None,
        help="maximum number of SFDU records to dump",
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

    main(args)
