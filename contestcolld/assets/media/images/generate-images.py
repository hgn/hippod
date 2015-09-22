#!/usr/bin/python

import subprocess

def do(cmd):
    subprocess.call(cmd.split())


cmd = "inkscape --export-png=hippod-logo.png hippod-logo.svg"
do(cmd)

size = 200
cmd  = "convert -filter Triangle -define filter:support=2 "
cmd += "-thumbnail {} -unsharp 0.25x0.25+8+0.065 -dither ".format(size)
cmd += "None -posterize 136 -quality 82 -define "
cmd += "jpeg:fancy-upsampling=off -define png:compression-filter=5 "
cmd += "-define png:compression-level=9 -define png:compression-strategy=1 "
cmd += "-define png:exclude-chunk=all -interlace none -colorspace sRGB "
cmd += "-strip hippod-logo.png hippod-logo-{}.png".format(size)
do(cmd)

size = 100
cmd  = "convert -filter Triangle -define filter:support=2 "
cmd += "-thumbnail {} -unsharp 0.25x0.25+8+0.065 -dither ".format(size)
cmd += "None -posterize 136 -quality 82 -define "
cmd += "jpeg:fancy-upsampling=off -define png:compression-filter=5 "
cmd += "-define png:compression-level=9 -define png:compression-strategy=1 "
cmd += "-define png:exclude-chunk=all -interlace none -colorspace sRGB "
cmd += "-strip hippod-logo.png hippod-logo-{}.png".format(size)
do(cmd)

size = 40
cmd  = "convert -filter Triangle -define filter:support=2 "
cmd += "-thumbnail {} -unsharp 0.25x0.25+8+0.065 -dither ".format(size)
cmd += "None -posterize 136 -quality 82 -define "
cmd += "jpeg:fancy-upsampling=off -define png:compression-filter=5 "
cmd += "-define png:compression-level=9 -define png:compression-strategy=1 "
cmd += "-define png:exclude-chunk=all -interlace none -colorspace sRGB "
cmd += "-strip hippod-logo.png hippod-logo-{}.png".format(size)
do(cmd)
