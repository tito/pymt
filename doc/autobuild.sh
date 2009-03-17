#!/usr/bin/env bash
# 
# autobuild.sh
# @author Mathieu Virbel <tito@bankiz.org>
#
# This script is to generate the whole PyMT documentation
#

DEST_DIR=`dirname $0`/sources


# Import the whole pymt package,
# and get the files included by pymt.
echo "## Find all files included in pymt package"

echo "from pymt import *" > autobuild.tmp
python -v autobuild.tmp 2>&1 | grep pymt | grep cleanup | awk '{print $3}' | sort > autobuild.list
rm autobuild.tmp

# Generate pages for each files
echo "## Generate page for each files"

# Copy template to the final rst
cat $DEST_DIR/api-tree.tpl > $DEST_DIR/api-tree.rst

# Iterate all the modules
for MODULE in $(cat autobuild.list); do

	# Get informatiosn
	FILENAME=api-$MODULE.rst

	echo " + $FILENAME"

	# First line of doc
	echo "import pymt
try:
	print [x for x in $MODULE.__doc__.split(\"\n\") if len(x) > 1][0]
except:
	print 'NO DOCUMENTATION FOR $MODULE'" > autobuild-module.py
	SUMMARY=`python autobuild-module.py 2>/dev/null`
	rm autobuild-module.py
	echo "   SUMMARY: $SUMMARY"

	# Do remplacement
	cat $DEST_DIR/api-module.tpl | sed "s/\$SUMMARY/$SUMMARY/g" | sed "s/\$MODULE/$MODULE/g" > $DEST_DIR/$FILENAME

	# Add file on rst index
	echo "    $FILENAME" >> $DEST_DIR/api-tree.rst

done

# Cleanup
echo "## Cleanup"
rm autobuild.list

# Regenerate documentation
echo "## Regenerate documentation"
make html
