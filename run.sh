#!/bin/bash

export LD_LIBRARY_PATH=$(gcc-config -L):$LD_LIBRARY_PATH

python runner.py
