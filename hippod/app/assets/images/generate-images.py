#!/usr/bin/python

import subprocess

def do(cmd):
    subprocess.call(cmd.split())


def generate_and_scale(filename):
    cmd = "inkscape --export-png={}.png {}.svg".format(filename, filename)
    do(cmd)

    size = 200
    cmd  = "convert -filter Triangle -define filter:support=2 "
    cmd += "-thumbnail {} -unsharp 0.25x0.25+8+0.065 -dither ".format(size)
    cmd += "None -posterize 136 -quality 82 -define "
    cmd += "jpeg:fancy-upsampling=off -define png:compression-filter=5 "
    cmd += "-define png:compression-level=9 -define png:compression-strategy=1 "
    cmd += "-define png:exclude-chunk=all -interlace none -colorspace sRGB "
    cmd += "-strip {}.png {}-{}.png".format(filename, filename, size)
    do(cmd)

    size = 100
    cmd  = "convert -filter Triangle -define filter:support=2 "
    cmd += "-thumbnail {} -unsharp 0.25x0.25+8+0.065 -dither ".format(size)
    cmd += "None -posterize 136 -quality 82 -define "
    cmd += "jpeg:fancy-upsampling=off -define png:compression-filter=5 "
    cmd += "-define png:compression-level=9 -define png:compression-strategy=1 "
    cmd += "-define png:exclude-chunk=all -interlace none -colorspace sRGB "
    cmd += "-strip {}.png {}-{}.png".format(filename, filename, size)
    do(cmd)

    size = 40
    cmd  = "convert -filter Triangle -define filter:support=2 "
    cmd += "-thumbnail {} -unsharp 0.25x0.25+8+0.065 -dither ".format(size)
    cmd += "None -posterize 136 -quality 82 -define "
    cmd += "jpeg:fancy-upsampling=off -define png:compression-filter=5 "
    cmd += "-define png:compression-level=9 -define png:compression-strategy=1 "
    cmd += "-define png:exclude-chunk=all -interlace none -colorspace sRGB "
    cmd += "-strip {}.png {}-{}.png".format(filename, filename, size)
    do(cmd)

generate_and_scale("hippod-logo")
