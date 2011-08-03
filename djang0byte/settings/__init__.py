from base import *

try:
    from local import *
except ImportError, e:
    import sys
    sys.stderr.write('Unable to read settings/local.py\nTry copy settings/dist.py to settings/local.py\n')
    sys.stderr.write("%s\n" %e)
    sys.exit(1)
