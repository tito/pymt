#!/usr/bin/env bash

echo "from pymt import *" > autobuild.tmp
python -v autobuild.tmp 2>&1 | grep pymt | grep cleanup | awk '{print $3}' | sort > autobuild.list
rm autobuild.tmp

cat api-tree.tpl > api-tree.rst
for MODULE in $(cat autobuild.list); do
	FILENAME=api-$MODULE.rst
	SUMMARY=$MODULE
	echo "Generate $FILENAME"
	cat api-module.tpl | sed "s/\$SUMMARY/$SUMMARY/g" | sed "s/\$MODULE/$MODULE/g" > $FILENAME
	echo "    $FILENAME" >> api-tree.rst
done

rm autobuild.list
