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

from typing import Optional, Tuple

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


def find_single_layer_by_name(game_type: str, image_name: str, m) -> Optional[Tuple[int, int]]:
    g_candidate = None
    l_candidate = None
    gi = -1
    for group in m.groups:
        gi += 1
        li = -1
        for layer in group.layers:
            li += 1
            if layer.kind() != 'Tiles':
                continue
            if layer.image is None:
                continue
            if m.images[layer.image].name == image_name:
                if g_candidate is not None:
                    print(f"failed to guess {image_name} too many candidates")
                    return None
                g_candidate = gi
                l_candidate = li
    if g_candidate and l_candidate:
        print(f"found {game_type} layer")
        return (l_candidate, g_candidate)
    print(f"failed to guess {game_type} no candidates")
    return None

def guess_collision(m) -> int:
    global collision_layer
    global collision_group

    gm = find_single_layer_by_name("collision", "grass_main", m)
    if gm:
        collision_layer = gm[0]
        collision_group = gm[1]
        return 1
    return 1

def guess_unhook(m) -> int:
    global unhook_layer
    global unhook_group

    gm = find_single_layer_by_name("unhook", "generic_unhookable", m)
    if gm:
        unhook_layer = gm[0]
        unhook_group = gm[1]
        return 41
    return 1

m = twmap.Map(args['INPUT_MAP'])

collision_layer = -1
collision_group = -1
unhook_group = -1
unhook_layer = -1
freeze_group = -1
freeze_layer = -1

if args['collision']:
    collision_group = int(args['collision'].split(':')[0])
    collision_layer = int(args['collision'].split(':')[1])
if args['unhook']:
    unhook_group = int(args['unhook'].split(':')[0])
    unhook_layer = int(args['unhook'].split(':')[1])
    edited_unhook = m.groups[unhook_group].layers[unhook_layer].tiles
if args['freeze']:
    freeze_group = int(args['freeze'].split(':')[0])
    freeze_layer = int(args['freeze'].split(':')[1])
    edited_freeze = m.groups[freeze_group].layers[freeze_layer].tiles

edited_collision = None
edited_unhook = None
edited_freeze = None

coll_tile = 1
unhook_tile = 41

# no arg given try to detect it
if collision_layer == -1:
    print("no collision layer specified. trying to gues ...")
    coll_tile = guess_collision(m)
if unhook_layer == -1:
    print("no unhook layer specified. trying to gues ...")
    unhook_tile = guess_unhook(m)

if collision_layer != -1:
    edited_collision = m.groups[collision_group].layers[collision_layer].tiles

if unhook_layer != -1:
    edited_unhook = m.groups[unhook_group].layers[unhook_layer].tiles

if freeze_layer != -1:
    edited_freeze = m.groups[freeze_group].layers[freeze_layer].tiles

GAME_COLLISION = 1
GAME_DEATH = 2
GAME_UNHOOK = 3
GAME_FREEZE = 9

progress = 0
for (y, x, flags), tile in numpy.ndenumerate(m.game_layer().tiles):
    progress += 1
    # if progress % 100 == 0:
    #     print(x, y)
    if flags == 0:
        # TODO: use smart default indecies here to place
        #       for example use shadow for freeze if tileset name is grass_main
        #       use index 41 if tileset is generic_unhookable
        if tile == GAME_COLLISION and edited_collision is not None:
            edited_collision[y][x][flags] = coll_tile
        elif tile == GAME_UNHOOK and edited_unhook is not None:
            edited_unhook[y][x][flags] = unhook_tile
        elif tile == GAME_FREEZE and edited_freeze is not None:
            edited_freeze[y][x][flags] = 1

if edited_collision is not None:
    m.groups[collision_group].layers[collision_layer].tiles = edited_collision
if edited_unhook is not None:
    m.groups[unhook_group].layers[unhook_layer].tiles = edited_unhook
if edited_freeze is not None:
    m.groups[freeze_group].layers[freeze_layer].tiles = edited_freeze

m.save(args['OUTPUT_MAP'])

