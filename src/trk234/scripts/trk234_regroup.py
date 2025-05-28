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
trk234_regroup
==============

Regroup a TRK 2-34 file such that all common record types are together. If
you have a file with SFDUs that are in the following order:

   01, 00, 02, 03, 04, 05, 06, 01, 00, 16

This program will reorder them in:

  00, 00, 01, 01, 02, 03, 04, 05, 06, 16

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 11-AUG-2014
Last Modified: 14-SEP-2023

Synopsis::

   trk234_regroup.py [options] <TNF_input> <TNF_output>

Options::

   -v, verbose mode: display what is being done
   -p, prompt before writing file
   -h, access program help via the command line
   --validate, validate the output file by comparing it to the input file

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
    f.decode(sec_chdo=False, trk_chdo=False)
    sfdus = f.sfdu_list
    print_log("Sorting %s by file type ascending" % args.Input, args.verbose)

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

    # List of data types to sort
    sort_types = range(0, 18)

    # Group SFDUs and write to file
    for i in sort_types:

        # Get matching SDFUs
        sfdu_list = [x for x in sfdus if x.pri_chdo.format_code == i]

        # For each SFDU in that list, write to the binary file
        for s in sfdu_list:
            fout.write(s.binarydata)

        # Print log
        print_log(
            "   Wrote %i SFDUs in file of data type %02i to output"
            % (len(sfdu_list), i),
            args.verbose,
        )

    # Finished. close file
    fout.close()
    print_log("Finished binary file write", args.verbose)

    # Validate if requested - we will check the number of SFDUs and the number of each type
    if args.validate:

        # Open the output file for reading
        f2 = trk234.Reader(args.Input)
        f2.decode(sec_chdo=False, trk_chdo=False)
        sfdus2 = f2.sfdu_list

        # Check number of SFDUs
        n1 = len(sfdus)
        n2 = len(sfdus2)
        if n1 != n2:
            print("WARNING: files contain different number of SFDUs!")

        # Check the number of each kind of each SFDU
        n_type1 = trk234.types(sfdus)
        n_type2 = trk234.types(sfdus2)
        if n_type1 != n_type2:
            print("WARNING: files contain different numbers of data types!")

        # Print validation results
        print("Output Validation Results:")
        print("%10s%10s%10s" % ("SFDU Type", "Input", "Output"))
        print("%10s%10i%10i" % ("Total", n1, n2))
        for i in sort_types:
            print("%10i%10i%10i" % (i, n_type1[i], n_type2[i]))


def print_log(message, verbose):
    """write a message to the screen if verbose is true"""
    if verbose:
        print(message)


# If called as a script, go to the main() function immediately
def execute():

    # Setup the parser
    parser = ArgumentParser(
        prog="trk234_regroup",
        description="Sort a TRK-2-34 file by data type in ascending order",
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
        "--validate",
        dest="validate",
        default=False,
        action="store_true",
        help="validate the output file",
    )

    # Parse the command line automatically
    args = parser.parse_args()

    # Error checking - does the file exist
    if not os.path.exists(args.Input):
        parser.error("File %s does not exist" % args.Input)

    main(args)
