#!/bin/sh
BASE=`dirname $0`
SCRIPT=$BASE/../users/elad/JoyControl.py
export PYTHONPATH=$PYTHON_PATH:$BASE/../lib
python $SCRIPT $*

