# Copyright (c) 2011 seb26. All rights reserved.
# Source code is licensed under the terms of the Modified BSD License.

import os
from subprocess import Popen, PIPE, STDOUT
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

    def getPackagePath(self, package, **kwargs):
        tpkg = os.path.splitext(package)
        if 'game' in kwargs and tpkg[1] == '.vpk':
            if kwargs['game'] in self.defn['vpk']:
                if tpkg[0] == 'pak01_dir':
                    path = os.path.join(
                        self.config['dir']['common'], self.getName(kwargs['game']), kwargs['game'], 'pak01_dir.vpk')
                    return path
                if tpkg[0] != 'pak01_dir' and tpkg[1] == '.vpk':
                    raise Exception, 'can only extract from pak01_dir.vpk, defined vpk not supported: ' + package
            else:
                raise Exception, 'defined game does not use .vpk: ' + kwargs['game']
        else:
            path = os.path.join(self.config['dir']['steamapps'], package)
            return path

    def extract(self, package, outdir, extr, **kwargs):
        p = self.getPackagePath(package, game=kwargs['game'])
        if 'game' in kwargs:
            pdirname = os.path.join(package, kwargs['game'])
        else:
            pdirname = package
        if 'multidir' in kwargs and kwargs['multidir'] is True:
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
                    xpath = os.path.join(outdir, pdirname, t[0])
                    if not os.path.exists(xpath):
                        os.makedirs(xpath)
                    self.cmd_close(p, xpath, t[1], options=kwargs['options'], silent=False)
            else:
                raise Exception('multidir is set but given object is not a list of multiple items')
        else:
            if type(extr) is list:
                if len(extr) > 1:
                    extr_cmd = '-e "' + '" -e "'.join(extr) + '"'
                elif len(extr) == 1:
                    extr_cmd = r'-e "%s"' % extr
            elif type(extr) is str:
                extr_cmd = r'-e "%s"' % extr
            xpath = os.path.join(outdir, pdirname)
            if not os.path.exists(xpath):
                pass # os.makedirs(xpath)
            self.cmd_close(p, xpath, extr_cmd, options=kwargs['options'], silent=False)


    def cmd_console(self, package, **kwargs):
        """ EXPERIMENTAL """
        cmd_output = []
        cmd_output.append('-p "%s"' % p)
        for z in cmdl:
            cmd_output.append(z)
        cmd = r'bin\HLExtract.exe' + ' ' + ' '.join(cmd_output)

        """ Begin code that I don't fully understand yet. """
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        output = []
        for z in p.stdout.readlines():
            output.append(z.strip('\r\n'))
        return output


    def cmd_close(self, p, d, ev, **kwargs):
        """ Run a HLExtract process and then terminate.
        p - package name (if vpk, set to 'pak01_dir.vpk' and set 'game' appropriately)
        d - directory to extract to
        ev - items to extract / validate (in the form: -e "path\to\file.txt" (or -t))
        kwargs: options
            options - string, containing options to pass to HLExtract (accepts s, m, q, v, o, r (see readme))
        """
        cmd_close = []
        cmd_close.extend([ '-p "%s"' % p, '-d "%s"' % d, ev ])

        if 'list' in kwargs and kwargs['list'] is not False:
            cmd_close.append('-' + kwargs['list'])
        silent = False
        if 'options' in kwargs:
            allowed = 'smqvor' # Valid HLExtract options (see README)
            if 's' in kwargs['options']:
                silent = True
            cmd_close.append('-' + ' -'.join([i for i in kwargs['options'] if i in allowed]))
        cmd = r'bin\HLExtract.exe' + ' ' + ' '.join(cmd_close)
        print cmd # Debuggin'. Don't be mad.
        process = os.popen(cmd)
        if silent is False:
            for z in process.readlines():
                print z.strip()
        process.close()


    def cmd_output(self, p, cmdl):
        """ Run HLExtract and return the output.
        p - package (needs full path, use getPackagePath())
        cmdl - list, containing commands e.g.: [ '-c', '-s', '-x "cmd"' ]
        """
        cmd_output = []
        cmd_output.append('-p "%s"' % p)
        for z in cmdl:
            cmd_output.append(z)
        cmd = r'bin\HLExtract.exe' + ' ' + ' '.join(cmd_output)

        """ Begin code that I don't fully understand yet. """
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        output = []
        for z in p.stdout.readlines():
            output.append(z.strip('\r\n'))
        return output
