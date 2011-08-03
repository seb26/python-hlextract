# Copyright (c) 2011 seb26. All rights reserved.
# Source code is licensed under the terms of the Modified BSD License.

import os
import re
from subprocess import Popen, PIPE, STDOUT
from collections import defaultdict

class HLExtract:

    def __init__(self, steamdir, username, volatile=False):
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

        if volatile is True:
            self.hlcmd['v'] = True
        else:
            self.hlcmd['v'] = False


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


    def info(self, package, infol, **kwargs):
        if 'game' in kwargs:
            p = self.getPackagePath(package, game=kwargs['game'])
        else:
            p = self.getPackagePath(package)
        if type(infol) is list:
            info = [ 'info ' + i for i in infol ]
            return self.cmd_console(p, info)
        else:
            return self.cmd_console(p, list('info ' + infol))


    def find(self, package, items, **kwargs):
        """ Find an item (file or dir) inside the package.
        package - package name (if vpk, set to 'pak01_dir.vpk' and also set 'game' appropriately)
        items - list or str (if only 1 item to search) of item names to search for.
        kwargs:
            game - set if vpk
        """
        if 'game' in kwargs:
            p = self.getPackagePath(package, game=kwargs['game'])
        else:
            p = self.getPackagePath(package)
        if type(items) is list:
            send = [ 'find ' + i for i in items ]
        else:
            send = list('find ' + items)
        res = self.cmd_console(p, send)
        resd = defaultdict(list)
        if len(res) != 0:
            for t in res.items():
                item = t[0][5:]
                resd[item].append(t[1].values()[0])
            return resd
        else:
            return False


    def extract(self, package, outdir, extr, **kwargs):
        if 'game' in kwargs:
            p = self.getPackagePath(package, game=kwargs['game'])
            pdirname = os.path.join(package, kwargs['game'])
        else:
            p = self.getPackagePath(package)
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


    def validate(self, package, validr, **kwargs):
        if 'game' in kwargs:
            p = self.getPackagePath(package, game=kwargs['game'])
            pdirname = os.path.join(package, kwargs['game'])
        else:
            p = self.getPackagePath(package)
            pdirname = package
        if type(validr) is list:
            validr_cmd = '-s -t "' + '" -t "'.join(validr) + '"'
        else:
            validr_cmd = '-s -t "%s"' % validr
        output = self.cmd_output(p, validr_cmd)
        if output is None:
            return True # Everything validated successfully
        else:
            return False # There were some issues. Expand on this later (need to get hands on broken GCF for testing).


    def defrag(self, package, **kwargs):
        """ Defrags package (-f flag).
        Ignores volatile state.
        """
        if 'game' in kwargs:
            p = self.getPackagePath(package, game=kwargs['game'])
            pdirname = os.path.join(package, kwargs['game'])
        else:
            p = self.getPackagePath(package)
            pdirname = package
        defrag_cmdl = []
        defrag_cmdl.append('-f') # Defrag package.
        defrag_cmdl.append('-s') # Silent.
        if 'options' in kwargs:
            defrag_cmdl.append(self._cmd_options(options))
        defrag_cmd = ' '.join(defrag_cmdl)
        return None # self.cmd_close(p,


    def _cmd_options(self, options):
        """ Returns a formatted string when given options.
        Example:
            'xftv' returns '-x -f -t -v'
            ['x', 'f', 't', 'v'] returns '-x -f -t -v'
        """
        allowed = 'smqvor'
        return '-' + ' -'.join([i for i in options if i in allowed])


    def cmd_console(self, p, cmdl, **kwargs):
        """ Runs a HLExtract -c process and returns results as a dict.
        p - package name (if vpk, set to 'pak01_dir.vpk' and also set 'game' appropriately)
        cmdl - list containing commands, e.g.: [ 'status', r'info root\tf' ]

        Results are returned as a dict with the key name corresponding to the command.
        Example:
            x = cmd_console(package, [ 'status', r'info root\tf' ])
            Results for 'status' and 'info root\tf' are stored in
            x['status'] and x['info root\tf'] respectively.
        """
        cmd_output = []
        cmd_output.append('-p "%s"' % p)
        if self.hlcmd['v'] is True:
            cmd_output.append('-v')
        cmd_output.append('-c')
        cmd_output.append('-s') # Need silent on to enable cleaner parsing.
        cmdl_x = '-x "' + '" -x "'.join(cmdl) + '"'
        cmd_output.append(cmdl_x)
        cmd_output.append('-x "exit"') # Closing the process so it doesn't run forever.
        cmd = r'bin\HLExtract.exe' + ' ' + ' '.join(cmd_output)

        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        output = []
        for z in p.stdout.readlines():
            output.append(z.strip('\r\n'))
        d = defaultdict(list)
        info = {}
        for line in output:
            r = re.compile(r'.+?>(.+)')
            m = r.match(line)
            if m:
                key = m.group(1)
            elif line == '':
                continue
            else:
                d[key].append(line.strip(' '))
        for y in d.items():
            x = [ i.split(': ') for i in y[1]]
            info[y[0]] = dict((t[0].lower(), t[1]) for t in x if len(t) == 2)
        return info


    def cmd_close(self, p, d, ev, **kwargs):
        """ Run a HLExtract process and then terminate.
        p - package name (if vpk, set to 'pak01_dir.vpk' and also set 'game' appropriately)
        d - directory to extract to
        ev - items to extract / validate (in the form: -e "path\to\file.txt" (or -t))
        kwargs: options
            options - string, additional HLExtract cmdline options.
        """
        cmd_close = []
        cmd_close.extend([ '-p "%s"' % p, '-d "%s"' % d, ev ])
        if self.hlcmd['v'] is True:
            cmd_close.append('-v')
        if 'list' in kwargs and kwargs['list'] is not False:
            cmd_close.append('-' + kwargs['list'])
        silent = False
        if 'options' in kwargs:
            options = self._cmd_options(kwargs['options'])
            if 's' in options:
                silent = True
        cmd = r'bin\HLExtract.exe' + ' ' + ' '.join(cmd_close)
        print cmd # Debuggin'. Don't be mad.
        process = os.popen(cmd)
        if silent is False:
            for z in process.readlines():
                print z.strip()
        process.close()


    def cmd_output(self, p, cmdl, **kwargs):
        """ Run HLExtract and return the output.
        p - package (needs full path, use getPackagePath())
        cmdl - list, containing commands e.g.: [ '-ld', '-f' ]
        kwargs:
            options - string, containing options
        """
        cmd_output = []
        cmd_output.append('-p "%s"' % p)
        if 'options' in kwargs:
            cmd_output.append(self._cmd_options(kwargs['options']))
        if self.hlcmd['v'] is True:
            cmd_output.append('-v')
        if type(cmdl) is list:
            cmd_output.extend(cmdl) # Simply extend with the list of commands gien.
        else:
            cmd_output.append(cmdl)
        cmd = r'bin\HLExtract.exe' + ' ' + ' '.join(cmd_output)

        """ Begin code that I don't fully understand yet. """
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        output = []
        for z in p.stdout.readlines():
            output.append(z.strip('\r\n'))
        return output