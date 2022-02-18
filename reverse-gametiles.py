#!/usr/bin/env python3
"""
    reverse-gamtiles.py

    add texture tilesets based on gamelayer
    allows mappers to map in gametiles and then auto generate design
"""

import sys
import twmap
import numpy
import argparse

example_text = '''example:

  reverse-gametiles.py --collison 1:1
  reverse-gametiles.py --freeze 1:1 --unhook 2:1'''
all_args = argparse.ArgumentParser(
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
all_args.add_argument('-c', '--collision', help='Position of hookable layer in the format "group_index:layer_index"')
all_args.add_argument('-u', '--unhook', help='Position of unhookable layer in the format "group_index:layer_index"') 
all_args.add_argument('-f', '--freeze',  help='Position of freeze layer in the format "group_index:layer_index"')
all_args.add_argument('INPUT_MAP')
all_args.add_argument('OUTPUT_MAP')

args = vars(all_args.parse_args())

for arg in args:
    if args[arg]:
        # TODO: turn this into a regex match that also ensures indecies are numeric
        if arg.upper() == arg:
            continue
        if len(args[arg].split(':')) != 2:
            print("Error: {} layer position has to be in format \"group_index:layer_index\"".format(arg))
            sys.exit(1)

m = twmap.Map(args['INPUT_MAP'])

if args['collision']:
    collision_group = int(args['collision'].split(':')[0])
    collision_layer = int(args['collision'].split(':')[1])
    edited_collision = m.groups[collision_group].layers[collision_layer].tiles
if args['unhook']:
    unhook_group = int(args['unhook'].split(':')[0])
    unhook_layer = int(args['unhook'].split(':')[1])
    edited_unhook = m.groups[unhook_group].layers[unhook_layer].tiles
if args['freeze']:
    freeze_group = int(args['freeze'].split(':')[0])
    freeze_layer = int(args['freeze'].split(':')[1])
    edited_freeze = m.groups[freeze_group].layers[freeze_layer].tiles


GAME_COLLISION = 1
GAME_DEATH = 2
GAME_UNHOOK = 3
GAME_FREEZE = 9

progress = 0
for (y, x, flags), tile in numpy.ndenumerate(m.game_layer().tiles):
    progress += 1
    if progress % 100 == 0:
        print(x, y)
    if flags == 0:
        if tile == GAME_COLLISION and args['collision']:
            edited_collision[y][x][flags] = 1
        elif tile == GAME_UNHOOK and args['unhook']:
            edited_unhook[y][x][flags] = 1
        elif tile == GAME_FREEZE and args['freeze']:
            edited_freeze[y][x][flags] = 1

if args['collision']:
    m.groups[collision_group].layers[collision_layer].tiles = edited_collision
if args['unhook']:
    m.groups[unhook_group].layers[unhook_layer].tiles = edited_unhook
if args['freeze']:
    m.groups[freeze_group].layers[freeze_layer].tiles = edited_freeze

m.save(args['OUTPUT_MAP'])

