# Copyright (c) 2011 seb26. All rights reserved.
# Source code is licensed under the terms of the Modified BSD License.

# TESTS

# print HLExtract('team fortress 2 content.gcf', tf2_content, None, multidir=True, multidir_path=r'X:\test01')
# print HLExtract('team fortress 2 content.gcf', r'X:\test02', tf2_content)
# print HLExtract('team fortress 2 content.gcf', r'X:\test02', r'x')


# ------------------------

test_extract = [
    r'root\tf\servers', # directory test
    r'root\tf\scripts\game_sounds_vo.txt', # 2 files from the same dir test
    r'root\tf\scripts\game_sounds_vo_handmade.txt'
    ]

test_extract_swarm = [
    r'root\particles', # directory test
    r'root\resource\gameevents.res', # 2 files from the same dir test
    r'root\resource\hltvevents.res',
    r'root\resource\ui\locator.res'
    ]

"""

# multdir test
print HLExtract('team fortress 2 content.gcf', r'X:\Sebi\Desktop\testpy\python-hlextract\test01', test_extract, multidir=True)

# singledir test (single file)
print HLExtract('team fortress 2 content.gcf', r'X:\Sebi\Desktop\testpy\python-hlextract\test02', r'root\tf\scripts\items\items_game.txt')

# singledir test (file list)
print HLExtract('team fortress 2 content.gcf', r'X:\Sebi\Desktop\testpy\python-hlextract\test02', test_extract)

"""

# multidir vpk
print HLExtract('pak01_dir.vpk', r'X:\Sebi\Desktop\testpy\python-hlextract\test03', test_extract_swarm, game='swarm')