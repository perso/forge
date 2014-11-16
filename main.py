#!/usr/bin/python

import sys

from game import Application


def main(args):

    app = Application()
    try:
        app.start()
    except:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
