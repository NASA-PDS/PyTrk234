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
trk234_purify
=============

Remove any SFDUs that do not match the CHDO data descriptions of C123, C124,
C125, C126 or C127

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 05-FEB-2015
Last Modified: 14-SEP-2023

Synopsis::

   trk234_purify.py [options] <TNF_input> <TNF_output>

Options::
   -b <band>, downlink band (S, X, K, L) to filter by
   -a <band>, uplink band (S, X, K, L) to filter by
   -d <dss>, downlink DSS ID to filter by
   -u <dss>, uplink DSS ID to filter by
   -f <type id>, data type (0-17) to filter by
   -v, verbose mode: display what is being done
   -p, prompt before writing file
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
    print_log("Reading %s" % args.Input, args.verbose)
    f = trk234.Reader(args.Input)
    f.decode(trk_chdo=False)
    sfdus = f.sfdu_list

    # Open the output file for writing
    if args.prompt:
        msg = "Confirm write of file %s" % args.Output
        confirm = True if raw_input("%s (y/N) " % msg).lower() == "y" else False
        if not confirm:
            sys.exit()
    fout = open(args.Output, "wb")
    print_log(
        "Beginning writing of binary data to %s" % args.Output, args.verbose
    )

    # Loop through each SFDU and determine if it matches the criteria
    for s in f.sfdu_list:

        # If its not in the data descriptions, skip it
        if s.label.data_description_id not in trk234.data_descriptions.keys():
            print_log(
                'Discarding SFDU %d - invalid CHDO data description of "%s"'
                % (s.number, s.label.data_description_id),
                args.verbose,
            )
            continue

        # If its not in the format codes, skip it
        if s.pri_chdo.format_code not in trk234.format_codes.keys():
            print_log(
                "Discarding SFDU %d - invalid CHDO format code of %d"
                % (s.number, s.pri_chdo.format_code),
                args.verbose,
            )
            continue

        # Test for format code
        if args.format_code is not None:
            if args.format_code != s.pri_chdo.format_code:
                print_log(
                    "Discarding SFDU %d - does not match user specified format code (%d, this one = %d)"
                    % (s.number, args.format_code, s.pri_chdo.format_code),
                    args.verbose,
                )
                continue

        # Test for uplink dss ID, only if valid
        if args.ul_dss_id is not None and hasattr(s.sec_chdo, "ul_dss_id"):
            if args.ul_dss_id != s.sec_chdo.ul_dss_id:
                print_log(
                    "Discarding SFDU %d - does not match user specified uplink DSS ID (%d, this one = %d)"
                    % (s.number, args.ul_dss_id, s.sec_chdo.ul_dss_id),
                    args.verbose,
                )
                continue

        # Test for uplink band, only if valid
        if args.ul_band is not None and hasattr(s.sec_chdo, "ul_band"):
            if args.ul_band != trk234.bands[s.sec_chdo.ul_band]:
                print_log(
                    "Discarding SFDU %d - does not match user specified uplink band (%s, this one = %s)"
                    % (
                        s.number,
                        args.ul_band,
                        trk234.bands[s.sec_chdo.ul_band],
                    ),
                    args.verbose,
                )
                continue

        # Test for downlink dss ID, only if valid
        if args.dl_dss_id is not None and hasattr(s.sec_chdo, "dl_dss_id"):
            if args.dl_dss_id != s.sec_chdo.dl_dss_id:
                print_log(
                    "Discarding SFDU %d - does not match user specified downlink DSS ID (%d, this one = %d)"
                    % (s.number, args.dl_dss_id, s.sec_chdo.dl_dss_id),
                    args.verbose,
                )
                continue

        # Test for downlink band, only if valid
        if args.dl_band is not None and hasattr(s.sec_chdo, "dl_band"):
            if args.dl_band != trk234.bands[s.sec_chdo.dl_band]:
                print_log(
                    "Discarding SFDU %d - does not match user specified downlink band(%s, this one = %s)"
                    % (
                        s.number,
                        args.dl_band,
                        trk234.bands[s.sec_chdo.dl_band],
                    ),
                    args.verbose,
                )
                continue

        # write to file
        fout.write(s.binarydata)

    # Finished. close file
    fout.close()
    print_log("Finished binary file write", args.verbose)


def print_log(message, verbose):
    """write a message to the screen if verbose is true"""
    if verbose:
        print(message)


def execute():

    # Setup the parser
    parser = ArgumentParser(
        prog="trk234_purify",
        description="Remove non-compliant SFDUs from a TRK-2-34 file and optionally filter data",
    )

    # Add arguments
    parser.add_argument(
        "Input", type=str, help="the name of the TRK-2-34 file to read"
    )
    parser.add_argument(
        "Output", type=str, help="the name of the TRK-2-34 file to write"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="enable verbose mode",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        dest="prompt",
        default=False,
        action="store_true",
        help="prompt before writing file",
    )
    parser.add_argument(
        "-b",
        "--dl_band",
        dest="dl_band",
        default=None,
        type=str,
        help="downlink band to filter by (S, X, Ka, L)",
    )
    parser.add_argument(
        "-a",
        "--ul_band",
        dest="ul_band",
        default=None,
        type=str,
        help="uplink band to filter by (S, X, Ka, L)",
    )
    parser.add_argument(
        "-d",
        "--dl_dss_id",
        dest="dl_dss_id",
        default=None,
        type=int,
        help="downlink DSS ID to filter by",
    )
    parser.add_argument(
        "-u",
        "--ul_dss_id",
        dest="ul_dss_id",
        default=None,
        type=int,
        help="downlink DSS ID to filter by",
    )
    parser.add_argument(
        "-f",
        "--format_code",
        dest="format_code",
        type=int,
        help="the format code/type ID of the data type to dump",
    )

    # Parse the command line automatically
    args = parser.parse_args()

    # Error checking - does the file exist
    if not os.path.exists(args.Input):
        parser.error("File %s does not exist" % args.Input)

    # validate the band input
    if args.dl_band not in trk234.bands.values() and args.dl_band is not None:
        parser.error("invalid band. valid bands are: S, X, Ka, Ku, or L")
    if args.ul_band not in trk234.bands.values() and args.dl_band is not None:
        parser.error("invalid band. valid bands are: S, X, Ka, Ku, or L")

    main(args)
