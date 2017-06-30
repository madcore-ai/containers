from flanker import mime
import os
import f2n
import argparse
import sys


def main():
    LAYERS = ['map01', 'url01', 'headers']
    parser = argparse.ArgumentParser(prog="")

    parser.add_argument('-f', '--filename', required=True, default='')
    parser.add_argument('-d', '--dirname', required=True, default='')
    parser.add_argument('-l', '--layers', required=True)
    args = parser.parse_args()

    if args.dirname:
        if not os.path.exists(args.dirname):
            print '[+] Directory doesn\' exist'
            sys.exit(1)
    layers = args.layers.split(',')
    for layer in layers:
        for v in LAYERS:
            if layer != v:
                print '[+] Layer {0} doesn\'t exist'.format(layer)
                sys.exit(1)
    f2n_instance = f2n.F2n(layers)

    for root, dirs, files in os.walk(args.dirname):
        for file in files:
            filename = root.split("/")[-1] + "/" + file
            filefullname = os.path.join(root, file)
            print 'Reading ', filefullname
            message_string = open(filefullname, "rb").read()
            msg = mime.from_string(message_string)
            f2n_instance.process(msg)

if __name__ == '__main__':
    main()
