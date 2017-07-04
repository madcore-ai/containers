from flanker import mime
import os
import f2n
import argparse
import sys


def main():
    LAYERS = set(['map01', 'url01', 'headers', 'attachments'])
    parser = argparse.ArgumentParser(prog="")

    parser.add_argument('-d', '--dirname', required=True, default='')
    parser.add_argument('-l', '--layers', required=True)
    args = parser.parse_args()

    if args.dirname:
        if not os.path.exists(args.dirname) or \
            not os.path.exists(os.path.join(args.dirname, 'allmail')):
                print '[+] Directory doesn\' exist'
                sys.exit(1)
    layers = set(args.layers.split(','))
    layers = list(LAYERS.intersection(layers))

    f2n_instance = f2n.F2n(layers, args.dirname)

    for root, dirs, files in os.walk(os.path.join(args.dirname, 'allmail')):
        for file in files:
            filename = root.split("/")[-1] + "/" + file
            filefullname = os.path.join(root, file)
            print 'Reading ', filefullname
            message_string = open(filefullname, "rb").read()
            msg = mime.from_string(message_string)
            f2n_instance.process(msg)
        break

if __name__ == '__main__':
    main()
