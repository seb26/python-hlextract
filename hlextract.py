# Copyright (c) 2011 seb26. All rights reserved.
# Source code is licensed under the terms of the Modified BSD License.

import os
import sys
import shutil
import re
from collections import defaultdict

import config
import defn

config = config.config
defn = defn.defn

def proper_name(s, form='proper'):
    """Gives a proper name or abbreviated form, if given either.
    s - the string to use.
    form - type of name in the next param ('proper' [default] or 'abbrev').
    [FIXME] Bug: 'left 4 dead' and 'left 4 dead 2' no like each other.
    """
    if form == 'proper':
        xform = 1 # Proper name form (see defn.py)
    elif form == 'abbrev':
        xform = 0 # Abbreviated form
    else:
        pass # Pootis kul error raisin' heer.
    result = [n for n in defn['proper_name'] if n[0] == s]
    if len(result) == 1:
        return result[0][xform]
    else:
        return result[0]


def HLExtract(pkg, dpath, e, **kwargs):
    # Process arguments heer.
    pkg_t = pkg.split(os.extsplit)
    if pkg_t[1] == 'vpk' and kwargs['game'] in defn['vpk']:
        xpkg = os.path.join(config['dir']['common'], proper_name(kwargs['game']), kwargs['game'], 'pak01_dir.vpk')
    elif pkg_t[1] == 'vpk' and pkg_t[0] != 'pak01_dir.vpk':
        raise Exception('Error: HLExtract does not support extracting from non-directory .VPKs:', pkg_t[0])
    else:
        xpkg = os.path.join(config['dir']['steamapps'], pkg)
    if 'multidir' in kwargs and kwargs['multidir'] is True:
        if type(e) == type(list()):
            extr = {}
            mdir = defaultdict(list)
            for fn in e:
                wdir = os.path.split(fn)[0]
                mdir[wdir].append(fn) # Add each fn to the appropriate working dir list.
            for t in mdir.items():
                fdir = t[0]
                f = t[1]
                extr[fdir] = '-e "' + '" -e "'.join(f) + '"'
            print 'Run count:', len(extr.items())
            for fdir, f in extr.items():
                xdpath = os.path.join(dpath, pkg, fdir)
                xdir = os.path.join(dpath, pkg)
                if not os.path.exists(xdpath):
                    os.makedirs(xdpath) # Make missing directories here.
                process = os.popen(r'bin\HLExtract -p "%s" -d "%s" %s' % (xpkg, xdpath, f))
                for i in process.readlines():
                    print i.strip()
                process.close()
        else:
            raise Exception('multidir is set but extract object is not a list')
    else:
        if type(e) == type(list()) and len(e) > 1:
            edir = '-e "' + '" -e "'.join(e) + '"'
        elif type(e) == type(list()) and len(e) == 1:
            edir = r'-e "%s"' % e
        elif type(e) == type(str()):
            edir = r'-e "%s"' % e
        if not os.path.exists(dpath):
            os.mkdir(dpath)
        process = os.popen(r'bin\HLExtract -p "%s" -d "%s" %s' % (xpkg, dpath, edir))
        for i in process.readlines():
            print i.strip()
        process.close()