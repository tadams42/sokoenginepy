#!/bin/sh

#
# $1 - path to binary
# $2 - path to output file
#

nm -CD $1 | cut -c "18-" | sort > $2
