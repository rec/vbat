#!/usr/bin/env python

from optparse import OptionParser
from vbat.Vbat import Vbat

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-i', '--image', dest='imagefile')
    parser.add_option('-n', '--name', dest='name')
    (options, arguments) = parser.parse_args()
    assert options.name, 'No name was specified.'
    vbati = Vbat(options.name)
    if options.imagefile:
        print vbati.image_test(options.imagefile)
    else:
        while True:
            print vbati.run()
