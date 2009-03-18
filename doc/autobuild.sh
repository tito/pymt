#!/usr/bin/env bash
# 
# autobuild.sh
# @author Mathieu Virbel <tito@bankiz.org>
#
# This script is to generate the whole PyMT documentation
# This is a shell script, doing bad bad bad thing.
# Feel free to rewrite this in python :)
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
toctree[1]=$DEST_DIR/api-tree.rst
lasttoctree="tree"
lastlevel=1

# Iterate all the modules
for MODULE in $(cat autobuild.list); do

	# Get informatiosn
	FILENAME=api-$MODULE.rst

	LEVEL=$(echo $MODULE | sed 's/[^.]//g' | wc -c)
	LEVEL=$(($LEVEL))
	if [ $LEVEL -gt $lastlevel ]; then
		toctree[$LEVEL]=$DEST_DIR/api-$lasttoctree.rst

		# Create toctree
		echo """
.. toctree::
""" >> $DEST_DIR/api-$lasttoctree.rst
	fi
		

	echo " + $FILENAME (l$((LEVEL)))"

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
	echo "    $FILENAME" >> ${toctree[$LEVEL]}

	# Save this module as toctree if change
	lasttoctree=$MODULE
	lastlevel=$(($LEVEL))

done

# Cleanup
echo "## Cleanup"
rm autobuild.list

# Regenerate documentation
echo "## Regenerate documentation"
make html
