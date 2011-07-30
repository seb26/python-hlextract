# Copyright (c) 2011 seb26. All rights reserved.
# Source code is licensed under the terms of the Modified BSD License.

import os
from collections import defaultdict

class HLExtract:

    def __init__(self, steamdir, username):
        self.config = {}
        self.config['dir'] = {}
        self.config['dir']['steamapps'] = os.path.join(steamdir, 'steamapps')
        self.config['dir']['common'] = os.path.join(steamdir, 'steamapps', 'common')
        self.config['dir']['usr'] = os.path.join(steamdir, 'steamapps', username)

        self.defn = {
            'vpk': [
                'portal2',
                'left4dead',
                'left4dead2',
                'swarm'
                ],

            'proper_name': [
                ('tf', 'team fortress 2'),
                ('portal', 'portal'),
                ('portal2', 'portal 2'),
                ('left4dead', 'left 4 dead'),
                ('left4dead2', 'left 4 dead 2'),
                ('swarm', 'alien swarm')
                ]
            }

        self.hlcmd = {}
        self.debug = {}

    def getName(self, string, form='proper'):
        if form == 'proper':
            xform = 1 # Proper name form (see defn.py)
        else:
            xform = 0 # Abbreviated form
        result = [n for n in self.defn['proper_name'] if n[0] == string]
        if len(result) == 1:
            return result[0][xform]
        elif len(result) == 0:
            return None
        else:
            return result[0]

    def extract(self, package, outdir, extr, **kwargs):
        if 'vpk' and 'game' in kwargs:
            if kwargs['vpk'] is True and kwargs['game'] not in self.defn['vpk']:
                raise Exception('game does not use .vpk: %s' % kwargs['game'])
            elif kwargs['vpk'] is True:
                tpkg = os.path.splitext(package)
                if package == 'pak01_dir.vpk':
                    self.hlcmd['p'] = os.path.join(
                        self.config['dir']['common'], self.getName(kwargs['game']), kwargs['game'], 'pak01_dir.vpk')
                elif tpkg[1] == '.gcf':
                    raise Exception('defined package is .gcf while vpk set to true')
                elif tpkg[1] == '.vpk' and tpkg[0] != 'pak01_dir':
                    raise Exception('can only extract from pak01_dir.vpk, %s not supported' % package)
        else:
            self.hlcmd['p'] = os.path.join(self.config['dir']['steamapps'], package)

        if type(extr) is list:
            edir = {}
            temp = defaultdict(list)
            for fn in extr:
                wdir = os.path.split(fn)[0]
                temp[wdir].append(fn) # Add each fn to the appropriate working dir list.
            for t in temp.items():
                fdir = t[0]
                f = t[1]
                edir[fdir] = '-e "' + '" -e "'.join(f) + '"'
            self.debug['runcount'] = len(edir.items())
            self.hlcmd['dir'] = edir.items()
            for t in self.hlcmd['dir']:
                xpath = os.path.join(outdir, package, t[0])
                if not os.path.exists(xpath):
                    pass # os.makedirs(xpath)
                self._cmd(self.hlcmd['p'], xpath, t[1], options=kwargs['options'], silent=False)
        else:
            pass # Do singlepath stuff heer.

    def _cmd(self, p, d, e, *args, **kwargs):
        self.hlcmd['cmd'] = []
        self.hlcmd['cmd'].extend([ '-p "%s"' % p, '-d "%s"' % d, e ])

        if 'validate' in kwargs:
            self.hlcmd['cmd'].append(kwargs['validate'])
        if 'list' in kwargs and kwargs['list'] is not False:
            self.hlcmd['cmd'].append('-' + kwargs['list'])
        if 'options' in kwargs:
            allowed = 'smqvor' # Valid HLExtract options (see README) - Excluding 'f' as it is dangerous during testing.
            silent = False
            if 's' in kwargs['options']:
                silent = True
            self.hlcmd['cmd'].append('-' + ' -'.join([i for i in kwargs['options'] if i in allowed]))
        cmd = r'bin\HLExtract.exe' + ' ' + ' '.join(self.hlcmd['cmd'])
        print cmd # Debuggin'. Don't be mad.
        process = os.popen(cmd)
        if 'silent' not in kwargs or silent is False:
            for z in process.readlines():
                print z.strip()
        process.close()