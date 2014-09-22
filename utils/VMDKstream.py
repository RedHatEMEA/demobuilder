#!/usr/bin/env python
# encoding: utf-8

# https://github.com/imcleod/VMDK-stream-converter

# Copyright (C) 2011 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.
#
# First cut module to convert raw disk images into stream-optimized VMDK files
#
# See the "Specification Document" referenced in Wikipedia for more details:
#
# http://en.wikipedia.org/wiki/VMDK
#
# Divergence from spec noted below
#
# The stream-optimized format is required for importing images via the vSphere
# SOAP API

import struct
import sys
import os
import math
import string
import zlib

class VMDKStreamException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

# Header Constants
MAGIC_NUMBER = 0x564D444B # 'V' 'M' 'D' 'K'

# Marker Constants
MARKER_EOS = 0 # end of stream
MARKER_GT = 1 # grain table
MARKER_GD = 2 # grain directory
MARKER_FOOTER = 3 # footer (repeat of header with final info)

# Other Constants
SECTOR_SIZE = 512

# Descriptor Template
image_descriptor_template='''# Description file created by VMDK stream converter
version=1
# Believe this is random
CID=7e5b80a7
# Indicates no parent
parentCID=ffffffff
createType="streamOptimized"

# Extent description
RDONLY #SECTORS# SPARSE "call-me-stream.vmdk"

# The Disk Data Base
#DDB

ddb.adapterType = "lsilogic"
# #SECTORS# / 63 / 255 rounded up
ddb.geometry.cylinders = "#CYLINDERS#"
ddb.geometry.heads = "255"
ddb.geometry.sectors = "63"
# Believe this is random
ddb.longContentID = "8f15b3d0009d9a3f456ff7b28d324d2a"
ddb.virtualHWVersion = "7"'''


def create_sparse_header(inFileSectors, descriptorSize,
                         gdOffset = 0xFFFFFFFFFFFFFFFF):
    # While theoretically variable we set these based on current VMWare
    # convention
    grainSize = 128
    numGTEsPerGT = 512
    overHead = 128
    formatVersion = 3 # NOTE: Conflicts with VMWare docs - determined by trial/error

    descriptorOffset = 1

    # The following are always fixed in the "stream-optimized" format we are
    # creating
    compressAlgorithm = 1
    flags = 0x30001
    rgdOffset = 0

    # We are building from scratch so an unclean shutdown is not possible
    uncleanShutdown = 0

    # Build the struct
    header_list = [ MAGIC_NUMBER, formatVersion, flags, inFileSectors,
                    grainSize, descriptorOffset, descriptorSize, numGTEsPerGT,
                    rgdOffset, gdOffset, overHead, uncleanShutdown,
                    '\n', ' ', '\r', '\n', compressAlgorithm ]
    for i in range(433):
	header_list.append(0)
    header_struct = "=IIIQQQQIQQQBccccH433B"
    return struct.pack(header_struct, *header_list)

def create_marker(numSectors, size, marker_type):
    marker_list = [ numSectors, size, marker_type ]
    for i in range(496):
	marker_list.append(0)
    marker_struct = "=QII496B"
    return struct.pack(marker_struct, *marker_list)

def create_grain_marker(location, size):
    # The grain marker is special in that the data follows immediately after it
    # without a pad
    return struct.pack("=QI", location, size)

def divro(num, den):
    # Divide always rounding up and returning an integer
    # Is there some nicer way to do this?
    return int(math.ceil((1.0*num)/(1.0*den)))

def pad_to_sector(stringlen):
    # create a pad that, when concated onto a string of stringlen
    # makes it an integer number of sectors
    # return pad and length of input_string + pad in sectors
    pad = ""
    if stringlen % SECTOR_SIZE:
        # This does need padding
        for i in range(SECTOR_SIZE - (stringlen % SECTOR_SIZE)):
            pad += '\0'
    finallen = (stringlen + len(pad))/SECTOR_SIZE
    return pad, finallen

def sector_pointer(file_object):
    # return file point in sectors
    # raise an exception if not sector aligned
    file_location = file_object.tell()
    if file_location % SECTOR_SIZE:
        raise VMDKStreamException("Asked for a sector pointer on a file whose r/w pointer is not sector aligned")
    else:
        return file_location / SECTOR_SIZE


def write_grain_table(outfile, grain_table, gtes_per_gt = 512):
    # Write grain_table to outfile including header
    # return the sector on which the table starts

    zero_grain_table = [ ]
    for i in range(gtes_per_gt):
        zero_grain_table.append(0)

    if grain_table == zero_grain_table:
        # We don't need to write this and can put zeros in the directory
        return 0
    else:
        grain_table_marker = create_marker(numSectors = (gtes_per_gt * 4) / SECTOR_SIZE,
                                           size = 0, marker_type = MARKER_GT)
        outfile.write(grain_table_marker)
        table_location = sector_pointer(outfile)
        outfile.write(struct.pack("%dI" % gtes_per_gt, *grain_table))
        return table_location

def debug_print(message):
    #print message
    pass

def convert_to_stream(infilename, outfilename):
    debug_print("DEBUG: opening %s to write to %s" % (infilename, outfilename))

    infileSize = os.path.getsize(infilename)
    infileSectors = divro(infileSize, 512)
    debug_print("DEBUG: input file is (%s) bytes - (%s) sectors long" % (infileSize, infileSectors))

    # Fixed by convention
    # TODO: Make variable here and in header fuction
    grainSectors=128
    totalGrains=divro(infileSectors, grainSectors)
    debug_print("DEBUG: total grains will be (%s)" % (totalGrains))

    # Fixed by convention
    # TODO: Make variable here and in header fuction
    numGTEsPerGT = 512
    totalGrainTables=divro(totalGrains, numGTEsPerGT)
    debug_print("DEBUG: total Grain Tables needed will be (%s)" % (totalGrainTables))

    grainDirectorySectors=divro(totalGrainTables*4, SECTOR_SIZE)
    debug_print("DEBUG: sectors in Grain Directory will be (%s)" % (grainDirectorySectors))

    grainDirectoryEntries=grainDirectorySectors*128
    debug_print("DEBUG: Number of entries in Grain Directory - (%s)" % (grainDirectoryEntries))

    infileCylinders=divro(infileSectors, (63*255))
    debug_print("DEBUG: Cylinders (%s)" % infileCylinders)

    # Populate descriptor
    tmpl = image_descriptor_template
    tmpl = string.replace(tmpl, "#SECTORS#", str(infileSectors))
    tmpl = string.replace(tmpl, "#CYLINDERS#", str(infileCylinders))
    image_descriptor = tmpl

    image_descriptor_pad, desc_sectors = pad_to_sector(len(image_descriptor))
    debug_print("DEBUG: Descriptor takes up (%s) sectors" % desc_sectors)
    image_descriptor += image_descriptor_pad

    image_header = create_sparse_header(inFileSectors = infileSectors,
                                        descriptorSize = desc_sectors)

    outfile = open(outfilename, "wb")
    outfile.write(image_header)
    outfile.write(image_descriptor)

    # Fixed by convention
    # TODO: Make variable here and in header function
    overHead = 128

    # Pad the output file to fill the overHead
    for i in range((overHead-sector_pointer(outfile)) * SECTOR_SIZE):
        outfile.write('\0')

    # grainDirectory - list of integers representing the global level 0 grain
    # directory
    grainDirectory = [ ]

    # currentGrainTable - list that can grow to numGTEsPerGT integers
    # representing the active grain table
    currentGrainTable = [ ]

    # For slightly more efficient comparison
    grainSize = grainSectors * SECTOR_SIZE
    zeroChunk = ""
    for i in range(grainSize):
        zeroChunk += '\0'

    # We are ready to start reading
    infile = open(infilename, "rb")

    try:
        inputSectorPointer = sector_pointer(infile)
        inChunk = infile.read(grainSize)
        while inChunk != "":
            if inChunk == zeroChunk:
                # All zeros - no need to create a grain - just mark zero in GTE
                currentGrainTable.append(0)
            else:
                # Create a compressed grain
                currentGrainTable.append(sector_pointer(outfile))
		compChunk = zlib.compress(inChunk)
                grain_marker = create_grain_marker(inputSectorPointer,
                                                   len(compChunk))
		grainPad, writeSectors = pad_to_sector(len(compChunk) + len(grain_marker))
		outfile.write(grain_marker)
		outfile.write(compChunk)
		outfile.write(grainPad)

            if len(currentGrainTable) == numGTEsPerGT:
                # Table is full
                table_location =  write_grain_table(outfile, currentGrainTable,
                                                    gtes_per_gt = numGTEsPerGT)
                # function does zero check so we don't have to
                grainDirectory.append(table_location)
                currentGrainTable = [ ]
            # do not update pointer unless we read a full grain last time
            # incomplete grain read indicates EOF and may result in non-sector
            # alignment
            if len(inChunk) == grainSize:
                inputSectorPointer = sector_pointer(infile)
            # read the next chunk
            inChunk = infile.read(grainSize)
    finally:
        # Write out the final grain table if needed
        if len(currentGrainTable):
            debug_print("Partial grain table present - padding and adding it to dir")
            for i in range(numGTEsPerGT-len(currentGrainTable)):
                currentGrainTable.append(0)
            table_location = write_grain_table(outfile, currentGrainTable,
                                               gtes_per_gt = numGTEsPerGT)
            grainDirectory.append(table_location)
        else:
            debug_print("Current grain table is empty so we need not write it out")

        # pad out grain directory then write it
        for i in range(grainDirectoryEntries - totalGrainTables):
            grainDirectory.append(0)
        grain_directory_marker = create_marker(grainDirectorySectors, 0,
                                               MARKER_GD)
        outfile.write(grain_directory_marker)
        gdLocation = sector_pointer(outfile)
        grainDirectoryStruct = "%dI" % grainDirectoryEntries
        debug_print("Grain directory length (%d)" % (len(grainDirectory)))
        debug_print("Grain directory: ")
        debug_print(grainDirectory)
        outfile.write(struct.pack(grainDirectoryStruct, *grainDirectory))

        # footer marker
        outfile.write(create_marker(1, 0, MARKER_FOOTER))

        # footer
        footer = create_sparse_header(inFileSectors = infileSectors,
                                      descriptorSize = desc_sectors,
                                      gdOffset = gdLocation)
        outfile.write(footer)

        # EOS marker
        outfile.write(create_marker(0, 0, MARKER_EOS))
        outfile.close()
        infile.close()

if __name__ == '__main__':
    convert_to_stream(sys.argv[1], sys.argv[2])
