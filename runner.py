#!/usr/bin/python
from subprocess import Popen

filename = "bot.py"
while True:
    print("\nStarting " + filename)
    p = Popen("python " + filename, shell=True)
    p.wait()
