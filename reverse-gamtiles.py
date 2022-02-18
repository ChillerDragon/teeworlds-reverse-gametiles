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

  reverse-gametiles.py --game 1:0 --collison 1:1
  reverse-gametiles.py --game 1:0 --freeze 1:1 --unhook 2:1'''
all_args = argparse.ArgumentParser(
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
all_args.add_argument('-c', '--collision', help='Position of hookable layer in the format "group_index:layer_index"')
all_args.add_argument('-u', '--unhook', help='Position of unhookable layer in the format "group_index:layer_index"') 
all_args.add_argument('-f', '--freeze',  help='Position of freeze layer in the format "group_index:layer_index"')
all_args.add_argument('-g', '--game', help='Position of game layer in the format "group_index:layer_index"')
all_args.add_argument('INPUT_MAP')
all_args.add_argument('OUTPUT_MAP')

args = vars(all_args.parse_args())

if not args['game']:
    print('Error: You have to provide a game layer using --game')
    sys.exit(1)

for arg in args:
    if args[arg]:
        # TODO: turn this into a regex match that also ensures indecies are numeric
        if len(args[arg].split(':')) != 2:
            print("Error: {} layer position has to be in format \"group_index:layer_index\"".format(arg))
            sys.exit(1)

game_group = int(args['game'].split(':')[0])
game_layer = int(args['game'].split(':')[1])

if args['collision']:
    collision_group = int(args['collision'].split(':')[0])
    collision_layer = int(args['collision'].split(':')[0])

m = twmap.Map(args['OUTPUT_MAP'])

GAME_COLLISION = 1
GAME_DEATH = 2
GAME_UNHOOK = 3
GAME_FREEZE = 9

for (y, x, flags), tile in numpy.ndenumerate(m.groups[game_group].layers[game_layer].tiles):
    if flags == 0 and tile == GAME_COLLISION and args['collision']:
        print(x, y, tile)
        m.groups[collision_group].layers[collision_layer].tiles[y][x][flags] = 1

m.save(args['OUTPUT_MAP'])

