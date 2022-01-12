#!/usr/bin/env python

"""pyhelmmanager

maintain helmnaker application and pipeline

Usage:
  pyhelmmanager <module> <func> [<args>...]

Options:
  -h --help            Show this screen.
"""

from docopt import docopt
import sys
import pyhelmmanager.helm_scripts
from pyhelmmanager.helm_scripts import *

def main():
    """
    run module

    example:
    pyrpmsepc java <git_url> <version>
    """
    args = docopt(__doc__, options_first=True)
    module = args['<module>']
    func = args['<func>']
    argv = [module, func]+args['<args>']
    module_script = getattr(pyhelmmanager.helm_scripts, module)
    module_args = docopt(module_script.__doc__, argv=argv)
    return getattr(module_script, func)(module_args)

if __name__ == '__main__':
    main()
