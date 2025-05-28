# trk234
Python reader library and example usage scripts for the Deep Space Network's TRK 2-34 Tracking and Navigation Files (TNF) data format. This library is fully compliant with Revision N of the TRK-2-34 format, but is also valid for revisions beyond it. [^1]

These utilities were produced by the Planetary Radar and Radio Sciences Group (332K) at the Jet Propulsion Laboratory, California Institute of Technology.

## Data Overview

To use this library one must first understand the organization and structure of the TRK-2-34 data format [^1], **it is highly recommended to read the Software Interface Specification document [^1] before continuing**.

TNFs are the most primitive (and most voluminous) product of the closed-loop tracking system at the Deep Space Network. TRK 2-34 files are TNFs, and as such, may be referred to as either TNFs or TRK 2-34 depending on the user’s preference. Each TRK 2-34 file is produced in near-real time (NERT) as the spacecraft is being actively tracked by a given DSN station. SFDUs are ordered in the TRK 2-34 files in time-ascending order by the DSN.

TRK 2-34 files are binary files in Standard Formatted Data Unit (SFDU) format. There are 18 distinct types of SFDUs organized into five groups. 

| Number | Data Class   | Description                       | SFDU Length (bytes) |
|--------|--------------|-----------------------------------|---------------------|
|      0 | Uplink       | Uplink Carrier Phase              | 162                 |
|      1 | Downlink     | Downlink Carrier Phase            | 358                 |
|      2 | Uplink       | Uplink Sequential Ranging Phase   | 194                 |
|      3 | Downlink     | Downlink Sequential Ranging Phase | 304                 |
|      4 | Uplink       | Uplink PN Ranging Phase           | 276                 |
|      5 | Downlink     | Downlink PN Ranging Phase         | 388                 |
|      6 | Derived      | Doppler Count                     | 200                 |
|      7 | Derived      | Sequential Range                  | 330                 |
|      8 | Derived      | Angles                            | 178                 |
|      9 | Derived      | Ramp Frequency                    | 124                 |
|     10 | Inferometric | VLBI                              | 204                 |
|     11 | Derived      | DRVID                             | 182                 |
|     12 | Filtered     | Smoothed Noise                    | 164                 |
|     13 | Filtered     | Allan Deviation                   | 160                 |
|     14 | Derived      | PN Range                          | 348                 |
|     15 | Derived      | Tone Range                        | 194                 |
|     16 | Derived      | Carrier Frequency Observable      | 182 + 18n           |
|     17 | Derived      | Total Count Phase Observable      | 194 + 22n           |

## Installation

This is a Python library package with scripts and configuration files.

The library  can be installed by cloning the repository to your local machine and running:

```
git clone https://github.com/NASA-PDS/PyTrk234.git
cd PyTrk234
pip3 install . -v
python3 -c "import trk234"
```

Note the installation path. Add files from the `scripts/` directory to your execution path, and if using the `bin/` execution scripts, update the paths in the scripts appropriately.

## Library Architecture

A `Reader` class reads the TRK-2-34 file; from there, the file can be decoded and contents accessed through the `SFDU` class. One attribute in the `Reader` class is `sfdu_list`, which contains a list of `SFDU` classes. Each `SFDU` class contains
* `SFDU.label`: SFDU Label
* `SFDU.agg_chdo`: Aggregation CHDO
* `SFDU.pri_chdo`: Primary CHDO
* `SFDU.sec_chdo`: Secondary CHDO
* `SFDU.trk_chdo`: Tracking Data CHDO

Individual attributes from each of these, as documented in Column 2 of the data tables in the TRK-2-34 Software Interface Specification document [^1], contain the data.

### Examples
#### Example: Basic file decoding

The module reads and parses the SFDUs in a given TRK 2-34 binary file. To read a file, the basic syntax is:
```
import trk234

f = trk234.Reader('filename.tnf')
f.decode()

sfdus = f.sfdu_list
```

This will read the raw binary data and determine the SFDU breaking points, then parse it into a list of SFDUs. If you are dealing with a large file, and only need to decode certain parts of the SFDU, optionally place one of the following keyword arguments into the decode() function:

* `decode( label=False )` - Don't decode the label
* `decode( agg_chdo=False )` - Don't decode the Aggregation CHDO
* `decode( pri_chdo=False )` - Don't decode the Primary CHDO
* `decode( sec_chdo=False )` - Don't decode the Secondary CHDO
* `decode( trk_chdo=False )` - Don't decode the Tracking CHDO

If you disable the decoding of the label, you can't decode anything else (not recommended). If you disable decoding of the Primary CHDO, you can't decode the Tracking CHDO.

For example, it may be worth it to disable the Secondary CHDO and Tracking CHDO if you only need to know what data types are in the file, e.g.:
```
f.decode( sec_chdo=False, trk_chdo=False )
```
#### Example: Print Attribute
```
import trk234

f = trk234.Reader('15025s026.stdf')
f.decode()
for s in f.sfdu_list:
    print( s.pri_chdo.format_code )
```

#### Example: Get info on a file
```
import trk234

f = trk234.Reader('15025s026.stdf')
f.decode(trk_chdo=False) # Setting trk_chdo to false will not decode the Tracking CHDO, speeding processing time
info = trk234.Info( f )
print( info )
```

#### Dumping to ASCII
Warning: this might produce very large about of text, depending on the size of the data file.
```
import trk234

f = trk234.Reader('15025s026.stdf')
f.decode()
for s in f.sfdu_list:
    print( s )
```

#### Accessing attributes

Attributes are accessed from the respective CHDO. The qttribute names are idential to the "identifier" as specified in the TRK 2-34 documentation.

```
import trk234

f = trk234.Reader('15025s026.stdf')
f.decode()

time = []
sky_frequency = []
signal_power = []
for s in f.sfdu_list:
    if s.pri_chdo.format_code == 1:
        time.append( s.timestamp() )
        sky_frequency.append( s.trk_chdo.dl_freq )
        signal_power.append( s.trk_chdo.pcn0 )
```

## Script Usage

### Read Downlink Information

Reads downlink information (sky frequency, system noise temperature, carrier signal-to-noise ratio, loop bandwidth) and prints to the terminal. Optionally filter by DSN station number, downlink band, and/or tracking mode.

Usage: `trk234_dnlink.py [-h] [-l] [-d DSS] [-b BAND] [-m MODE] [-t] [-c] Input`

Basic Example: *print to a text file*
```
trk234_dnlink.py GRV_JUGR_2016240_0635X55MC001V01.TNF > downlink.txt
```

### Dump Contents to ASCII

Reads the TRK-2-34 data file, prints every attribute from each SFDU in a pseudo-JSON like format. Warning: this might produce very large about of text, depending on the size of the data file. Restrict the size of the dump with the options for maximum number and data type.

Usage: `trk234_dump.py [-h] [-f FORMAT_CODE] [-m MAX] Input`

Basic Example: *dump to text file*
```
trk234_dump.py GRV_JUGR_2016240_0635X55MC001V01.TNF > dump.txt
```

Complex Example: *dump only the first SFDU of carrier observable data type*
```
trk234_dump.py -m 1 -f 16 GRV_JUGR_2016240_0635X55MC001V01.TNF
```

### Extract an Individual Attribute

Reads the TRK-2-34 file, and prints the time history of a user-specified attribute from the TRK-2-34 documentation [^1]. Must provide the name of the attribute, and which part of the SFDU it is from (SFDU Label, Aggregation CHDO, Primary CHDO, Secondary CHDO or Tracking CHDO)

Usage: `trk234_extract [-h] [-f FORMAT_CODE] [-p] [-t] [-i IDENTIFIER] [--label] [--agg] [--pri] [--sec] [--trk] Input`
Required Options: one of `--label`, `--agg`, `--pri`, `--sec`, `--trk`, and `-i IDENTIFIER`

Example: *extract the spacecraft ID from all SFDUs*
```
trk234_extract.py --sec -i scft_id GRV_JUGR_2016240_0635X55MC001V01.TNF > scft_id.txt
```

### Print Information from File

Read a TRK-2-34 file and parse high-level information about the file, and print it to the terminal.

Usage: `trk234_info.py [-h] [-p] [-m] [-q] Input`

Example:
```
trk234_info2.py GRV_JUGR_2016240_0635X55MC001V01.TNF
```

Example Output:
```
         Report for File: GRV_JUGR_2016240_0635X55MC001V01.TNF
         Generation Date: 2023-268T22:22:36
              Start Time: 2016-240T06:35:48
                End Time: 2016-240T19:50:00
           Spacecraft ID: 61
         Downlink DSS ID: 55
          Downlink Bands: X, Ka
      Doppler Count Time: 1.0
           Uplink DSS ID: 55
            Uplink Bands: X
           Tracking Mode: 2W, None, 3W/43, 1W
       Number of Records: 283594
    Data Description IDs: C125, C123, C124
    Available Data Types: 0, 1, 2, 3, 7, 9, 11, 16, 17
                      00: Uplink Carrier Phase - 47596
                      01: Downlink Carrier Phase - 66247
                      02: Uplink Sequential Ranging Phase - 36570
                      03: Downlink Sequential Ranging Phase - 113
                      07: Sequential Ranging - 113
                      09: Ramps - 366
                      11: DRVID - 113
                      16: Carrier Observable - 66238
                      17: Total Phase Observable - 66238
```

### Purify/Filter a TRK-2-34 to SIS Compliance

Remove non-compliant SFDUs from a TRK-2-34 file and optionally filter the data file by downlink band, uplink band, and DSN station number.

**This is one of the required steps in labeling a TRK-2-34 file**

Usage: `trk234_purify [-h] [-v] [-p] [-b DL_BAND] [-a UL_BAND] [-d DL_DSS_ID] [-u UL_DSS_ID] [-f FORMAT_CODE] Input Output`

Example: *purify a TRK-2-34 file, removing the non-compliant CHDOs resulting from DSN marking some as bad*
```
trk234_purify.py 232511615SC61DSS35_noHdr.234 232511615SC61DSS35_noHdr.234.pure
```

Bulk Processing Example: *do this purification on a large number of data files*
```
find *234 -exec trk234_purify.py  {} {}.pure \; >> logfile.txt
```

### Read Uplink Information

Read the uplink ramp history from a TRK-2-34 file and print it out. The data printed is the ramp frequency and ramp rate.

Usage: `trk234_ramp.py [-h] [-d DSS] [-b BAND] [-t] Input`

Example: *print X-band ramps from DSS-55*
```
trk234_ramp.py -b X -d 55 GRV_JUGR_2016240_0635X55MC001V01.TNF > ramp_X_55.txt
```

### Sort a TRK-2-34 File by Data Type

Sort (regroup) a TRK-2-34 file by data type (aka format code) into ascending order. This will make the TRK-2-34 file easier to label for PDS, but the SFDUs will no longer be in time-increasing order.

**This is one of the required steps in labeling a TRK-2-34 file**

Usage: `trk234_regroup.py [-h] [-v] [-p] [--validate] Input Output`

Example:
```
trk234_regroup.py 232511615SC61DSS35_noHdr.234.pure 232511615SC61DSS35_noHdr.234.pure.sorted
```

Bulk Processing Example: *do this sorting on a large number of data files*
```
find *234.pure -exec trk234_regroup.py  {} {}.sorted \; >> logfile.txt
```

# Disclaimer Statement
Copyright (c) 2023, California Institute of Technology ("Caltech").
U.S. Government sponsorship acknowledged. Any commercial use must be 
negotiated with the Office of Technology Transfer at the California 
Institute of Technology.
 
This software may be subject to U.S. export control laws. By accepting this 
software, the user agrees to comply with all applicable U.S. export laws 
and regulations. User has the responsibility to obtain export licenses, or 
other export authority as may be required before exporting such information 
to foreign countries or providing access to foreign persons.

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions must reproduce the above copyright notice, this list of
  conditions and the following disclaimer in the documentation and/or other
  materials provided with the distribution.
* Neither the name of Caltech nor its operating division, the Jet Propulsion
  Laboratory, nor the names of its contributors may be used to endorse or
  promote products derived from this software without specific prior written
  permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


[^1]: https://pds-geosciences.wustl.edu/radiosciencedocs/urn-nasa-pds-radiosci_documentation/dsn_trk-2-34/
