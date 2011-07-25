# Copyright (c) 2011 seb26. All rights reserved.
# Source code is licensed under the terms of the Modified BSD License.

import os

config = {

    'username': 'unleashed26',
    'steamdir': r'C:\Program Files\Steam'

    }

# Edit above this only.

config['dir'] = {}
config['dir']['steamapps'] = os.path.join(config['steamdir'], 'steamapps')
config['dir']['common'] = os.path.join(config['steamdir'], 'steamapps', 'common')
config['dir']['usr'] = os.path.join(config['steamdir'], 'steamapps', config['username'])