# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Sample mission loader
# Used to check the mission repository

import MalmoPython
import os
import json         # For parsing observations
import sys
import math         # For calculating distance between fireball/player
import time
import random

from collections import namedtuple
EntityInfo = namedtuple('EntityInfo', 'x, y, z, yaw, pitch, name, colour, variation, quantity')
EntityInfo.__new__.__defaults__ = (0, 0, 0, 0, 0, "", "", "", 1)

# ------------------------------------------------------------------------------------------------ #
# ----------------------------------------- FUNCTIONS -------------------------------------------- #

def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2 + (p0[2] - p1[2])**2)

def angvel(target, current, scale):
    '''Use sigmoid function to choose a delta that will help smoothly steer from current angle to target angle.'''
    delta = target - current
    while delta < -180:
        delta += 360;
    while delta > 180:
        delta -= 360;
    return (2.0 / (1.0 + math.exp(-delta/scale))) - 1.0
# ----------------------------------------END FUNCTIONS------------------------------------------- #

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

mission_file_no_ext = 'ghast_survival_mission' # CS175 Project. Ghast Survival

player_location    = [0, 0, 0]                   # Player location. Used to calculate distance between player and fireball.
player_x_pos       = 0                           # Player's x location. Used for state calculation
player_life        = 10                          # Player's life
fireball_location  = [1000, 1000, 1000]          # Fireball location. Used to calculate distance between player and fireball.
fireball_distance  = 1000                        # Distance between fireball and player
actions            = ["move_left", "move_right"] # Possible actions
curr_state         = -1                          # Current state

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)
if agent_host.receivedArgument("test"):
    exit(0) # TODO: discover test-time folder names

mission_file = mission_file_no_ext + ".xml"
with open(mission_file, 'r') as f:
    print "Loading mission from %s" % mission_file
    mission_xml = f.read()
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission.setViewpoint(0) #1 for 3rd person view

# Set up a recording
my_mission_record = MalmoPython.MissionRecordSpec()  # Records nothing by default
# Attempt to start a mission
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission(my_mission, my_mission_record)
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print "Error starting mission:",e
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print "Waiting for the mission to start ",
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    sys.stdout.write(".")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text

print
print "Mission running ",

total_reward = 0.0

# main loop:
while world_state.is_mission_running:
    time.sleep(0.1)

    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        ob = json.loads(msg)

        # weird doesnt work, maybe need to specify mission spec
        # agent_host.sendCommand("hotbar.1 1")  # Press the hotbar key
        # agent_host.sendCommand("hotbar.1 0")  # Release hotbar key - agent should now be holding diamond_sword

        # make the agent aim the ghast:
        yaw = ob.get(u'Yaw', 0)
        delta_yaw = angvel(0, yaw, 100.0)           # -180left, 180right
        pitch = ob.get(u'Pitch', 0)
        delta_pitch = angvel(-5.0, pitch, 100.0)     # -90top, 90down
        agent_host.sendCommand("turn " + str(delta_yaw))
        agent_host.sendCommand("pitch " + str(delta_pitch))

        # debug:
        agent_host.sendCommand("attack 1")

        #print "-----------------------------------------------------------"
        #print json.dumps(ob, indent=4, sort_keys=True)
        #print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        if "Life" in ob:
            life = int(ob[u'Life'])
            if life < player_life: # We got damaged by a fireball
                agent_host.sendCommand("chat aaaaaaaaargh!!!")
            player_life = life

        # Player location
        if "XPos" in ob:
            player_x_pos = int(ob[u'XPos'])
            player_location[0] = player_x_pos
        if "YPos" in ob:
            player_location[1] = int(ob[u'YPos'])
        if "ZPos" in ob:
            player_location[2] = int(ob[u'ZPos'])

        if "entities" in ob:
            entities = [EntityInfo(**k) for k in ob["entities"]]
            for entity in entities:
                if entity[5] == "Fireball":
                    fireball_location[0] = entity[0]
                    fireball_location[1] = entity[1]
                    fireball_location[2] = entity[2]

                    fireball_distance = distance(player_location, fireball_location)
                    print "Fireball distance: ", fireball_distance

    for error in world_state.errors:
        print "Error:",error.text

print "Mission ended"
print "Total reward = " + str(total_reward)
