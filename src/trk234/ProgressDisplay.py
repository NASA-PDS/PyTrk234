#!/usr/bin/python
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
TRK234: A module to read TRK 2-34 files

progress display file. Creates a simple display on the stderr output showing
the progress of a loop.

Author: Dustin Buccino
Email: dustin.r.buccino@jpl.nasa.gov
Affiliation: Planetary Radar and Radio Sciences, Group 332K
             Jet Propulsion Laboratory, California Institute of Technology
Date Created: 23-SEP-2015
Last Modified: 14-SEP-2023

"""

import sys

# ---------------------------------------------------------------------------
class ProgressDisplay:
   """
      Progress display (for decoding the SFDU). Example usage:

      p = ProgressDisplay()
      for i in range(0,20):
         p.update(i/20.0)
      p.kill()
   """

   def __init__(self, maxIndex, npts=30, char='*'):
      """ class constructor """
      self.n = float(maxIndex)
      self.npts = npts
      self.char = char
      self.prev = 0
      sys.stderr.write(' '*8 + '0%' + ' '*(npts-6) +'100%\n' + ' '*8)

   def update(self, i):
      """ update the increment in the loop """
      new  = int( i/self.n * self.npts )
      if new > self.prev:
        sys.stderr.write( self.char )
      self.prev = new

   def kill(self):
      sys.stderr.write( '\n' )
      
# ---------------------------------------------------------------------------
