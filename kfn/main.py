import os
import f2n
import argparse
import sys


def process_account(account_dir, layers):
    if not os.path.exists(os.path.join(account_dir, 'allmail')):
        print '[+] Directory {0} doesn\' exist'.format(os.path.join(account_dir, 'allmail'))
        return
    f2n_instance = f2n.F2n(layers, account_dir)

    for root, dirs, files in os.walk(os.path.join(account_dir, 'allmail')):
        for file in files:
            filename = root.split("/")[-1] + "/" + file
            filefullname = os.path.join(root, file)
            print 'Reading ', filefullname
            f2n_instance.process(filefullname)

def main():
    LAYERS = set(['map01', 'url01', 'headers', 'attachments'])
    parser = argparse.ArgumentParser(prog="")

    parser.add_argument('-d', '--dirname', required=True)
    parser.add_argument('-l', '--layers', required=True)
    args = parser.parse_args()

    if args.dirname:
        if not os.path.exists(args.dirname):
            print '[+] Directory doesn\' exist'
            sys.exit(1)
    layers = set(args.layers.split(','))
    layers = list(LAYERS.intersection(layers))

    for account_dir in os.walk(args.dirname).next()[1]:
        process_account(os.path.join(args.dirname, account_dir), layers)

if __name__ == '__main__':
    main()
