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

from collections import defaultdict, deque

from collections import namedtuple
EntityInfo = namedtuple('EntityInfo', 'x, y, z, yaw, pitch, name, colour, variation, quantity')
EntityInfo.__new__.__defaults__ = (0, 0, 0, 0, 0, "", "", "", 1)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)         # flush print output immediately

mission_file_no_ext = 'ghast_survival_mission'              # CS175 Project. Ghast Survival

player_start_x_pos_raw = 0     # Player's start x pos, the AI should learn to move away from this.
player_x_pos           = 0     # Player's x location. Used for state calculation
player_x_pos_raw       = 0     # Player's raw x pos
player_life            = 10    # Player's life
fireball_distance      = 1000  # Distance between fireball and player
fireball_dx            = 1000  # Delta x between fireball and player
fireball_dz            = 1000  # Delta z between fireball and player

player_start_life = 10      # Player's life at beginning of episode
episode_reward    = 0       # Reward obtained from last episode
episode_running   = False   # Set to true at the beginning of episode
episode_finished  = False

# ------------------------------------------------------------------------------------------------ #
# ----------------------------------------- FUNCTIONS -------------------------------------------- #
# ------------------------------------------------------------------------------------------------ #

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

def set_world_observations(agent_host, waiting_for_episode):
    global player_life
    global player_start_life
    global player_x_pos

    global player_start_x_pos_raw
    global player_x_pos_raw

    global fireball_distance
    global fireball_dx
    global fireball_dz

    global episode_running
    global episode_finished
    global episode_reward

    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        ob = json.loads(msg)

        # weird doesnt work, maybe need to specify mission spec
        # agent_host.sendCommand("hotbar.1 1")  # Press the hotbar key
        # agent_host.sendCommand("hotbar.1 0")  # Release hotbar key - agent should now be holding diamond_sword

        # make the agent aim the ghast:
        # yaw = ob.get(u'Yaw', 0)
        # delta_yaw = angvel(0, yaw, 100.0)           # -180left, 180right
        # pitch = ob.get(u'Pitch', 0)
        # delta_pitch = angvel(-5.0, pitch, 100.0)     # -90top, 90down
        # agent_host.sendCommand("turn " + str(delta_yaw))
        # agent_host.sendCommand("pitch " + str(delta_pitch))

        # debug:
        # agent_host.sendCommand("attack 1")

        #print "-----------------------------------------------------------"
        #print json.dumps(ob, indent=4, sort_keys=True)
        #print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        # Player location
        player_location = [0, 0, 0] # Used to calculate distance between fireball and player.
        if "XPos" in ob:
            player_x_pos_raw = ob[u'XPos']
            player_x_pos = int(ob[u'XPos'])
            player_location[0] = player_x_pos
        if "YPos" in ob:
            player_location[1] = int(ob[u'YPos'])
        if "ZPos" in ob:
            player_location[2] = int(ob[u'ZPos'])

        if "entities" in ob:
            entities = [EntityInfo(**k) for k in ob["entities"]]
            fireball_active = False
            for entity in entities:
                if entity[5] == "Fireball":
                    fireball_active = True

                    if waiting_for_episode: # Start new episode
                        episode_running = True
                        episode_reward = 0      # Reset episode reward.
                        episode_finished = False
                        player_start_x_pos_raw = player_x_pos_raw # Set player start x pos, the fireball should be aiming here.

                    fireball_location = [1000, 1000, 1000] # Used to calculate distance between fireball and player.
                    fireball_location[0] = entity[0]
                    fireball_location[1] = entity[1]
                    fireball_location[2] = entity[2]

                    fireball_distance = int(distance(player_location, fireball_location))
                    fireball_dx = int(player_location[0] - fireball_location[0])
                    fireball_dz = int(player_location[2] - fireball_location[2])
                    # print "Fireball distance: ", fireball_distance

            if not fireball_active and episode_running:   # If there's no fireball active then the episode is over.
                episode_running = False
                episode_finished = True

        if "Life" in ob:
            life = int(ob[u'Life'])
            player_life = life

            if waiting_for_episode and episode_running:     # If new episode has begun.
                player_start_life = life

    for error in world_state.errors:
        print "Error:",error.text

# ------------------------------------------------------------------------------------------------ #
# ----------------------------------------END FUNCTIONS------------------------------------------- #
# ------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------ #
# ----------------------------------------AGENT CLASS--------------------------------------------- #
# ------------------------------------------------------------------------------------------------ #

class Dodger(object):
    def __init__(self, alpha=0.3, gamma=1, n=1):
        """Constructing an RL agent.

        Args
            alpha:  <float>  learning rate      (default = 0.3)
            gamma:  <float>  value decay rate   (default = 1)
            n:      <int>    number of back steps to update (default = 1)
        """
        self.epsilon = 0.2  # chance of taking a random action instead of the best
        self.q_table = {}
        self.n, self.alpha, self.gamma = n, alpha, gamma

    def is_solution(reward):
        return reward == 100

    # We use the distance from your start position to give feedback. Being farther from the start position returns better feedback.
    def get_curr_feedback(self):
        x_dist = abs(player_start_x_pos_raw - player_x_pos_raw)

        if x_dist < 1.5: # Only positive if we are more than 1 unit away from our start position.
            return episode_reward + ((1.5 - x_dist) * -50)

        return episode_reward + int(x_dist * 50)

    def calculate_reward(self):
        health_reward = 0

        if player_start_life > player_life:    # Player got damaged.
            delta_health = int(player_start_life - player_life)
            health_reward = -50 * delta_health # Negative reward for getting hit by fireball.
            return episode_reward + health_reward

        x_dist = abs(player_start_x_pos_raw - player_x_pos_raw)

        return episode_reward + int(x_dist * 50)

    def get_curr_state(self):
        # Location of player, fireball delta x, fireball delta z
        # "10,-3,7"
        # print "State: ", player_x_pos, fireball_dx, fireball_dz

        corner_val = 0 # Not in a corner

        if player_x_pos == -4:
            corner_val = -2 # Right corner
        elif player_x_pos == -3:
            corner_val = -1 # Second to right corner

        if player_x_pos == 4:
            corner_val = 2  # Left corner
        elif player_x_pos == 3:
            corner_val = 1  # Second to left corner

        return corner_val, fireball_dx, fireball_dz

    def choose_action(self, curr_state, possible_actions, eps, q_table):
        """Chooses an action according to eps-greedy policy. """
        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0

        rnd = random.random()

        # print ""
        print "current state :", self.get_curr_state(), self.get_curr_feedback(), q_table[curr_state].items()

        if rnd < eps:   # below eps, give random action:
            # print "random : ", rnd
            a = random.randint(0, len(possible_actions) - 1)
        else:  # do e greedy policy:
            # get highest q value:

            highestQValue = max(q_table[curr_state].items(), key=lambda item: item[1])
            # print "highestQValue : ", highestQValue[1]

            # check if multiple actions have same q value
            tempContainer = []

            for i, item in enumerate(q_table[curr_state].items()):
                if abs(item[1] - highestQValue[1]) <= 0.0001:
                    tempContainer.append(item)

            # print "in my container:", tempContainer

            tmprnd = random.randint(0, len(tempContainer) - 1)
            # print "egreedy action : ", tempContainer[tmprnd][0]
            return tempContainer[tmprnd][0]

        # print "random action : ", possible_actions[a]
        return possible_actions[a]    

    def get_possible_actions(self, agent_host, is_first_action=False):
        """Returns all possible actions that can be done at the current state. """
        action_list = ["nothing"]

        if player_x_pos > -4:
            action_list.append("move_right")
        
        if player_x_pos < 4:
            action_list.append("move_left")

        return action_list

    def act(self, agent_host, action):
        print action + ",",

        global episode_reward
        
        # Actions are move_left, move_right, nothing
        if action == "move_left":
            agent_host.sendCommand("strafe -1")
            episode_reward -= 1
            return -1
        elif action == "move_right":
            agent_host.sendCommand("strafe 1")
            episode_reward -= 1
            return -1
        else:
            agent_host.sendCommand("strafe 0")  # Do nothing

        return 0

    def update_q_table(self, tau, S, A, R, T):
        """Performs relevant updates for state tau.

        Args
            tau: <int>  state index to update
            S:   <dequqe>   states queue
            A:   <dequqe>   actions queue
            R:   <dequqe>   rewards queue
            T:   <int>      terminating state index
        """
        curr_s, curr_a, curr_r = S.popleft(), A.popleft(), R.popleft()
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[S[-1]][A[-1]]

        old_q = self.q_table[curr_s][curr_a]
        self.q_table[curr_s][curr_a] = old_q + self.alpha * (G - old_q)

    def run(self, agent_host):
        global episode_finished

        S, A, R = deque(), deque(), deque() # S = states, A = actions, R = rewards
        done_update = False
        while not done_update:
            s0 = self.get_curr_state()
            possible_actions = self.get_possible_actions(agent_host, True)
            a0 = self.choose_action(s0, possible_actions, self.epsilon, self.q_table)
            S.append(s0)
            A.append(a0)
            R.append(0)

            T = sys.maxint
            for t in xrange(sys.maxint):
                set_world_observations(agent_host, not episode_running)

                time.sleep(0.25)

                if episode_running or episode_finished:
                    if t < T:
                        self.act(agent_host, A[-1])
                        R.append(self.get_curr_feedback())

                        if episode_finished:
                            # Terminating state
                            T = t + 1
                            S.append('Term State')
                            final_reward = self.calculate_reward()
                            R.append(final_reward)
                            print "Reward:", final_reward

                            episode_finished = False
                            
                            if player_life > 0:
                                print "Stop move"
                                agent_host.sendCommand("strafe 0")
                        else:
                            s = self.get_curr_state()
                            S.append(s)
                            possible_actions = self.get_possible_actions(agent_host)
                            next_a = self.choose_action(s, possible_actions, self.epsilon, self.q_table)
                            A.append(next_a)

                    tau = t - self.n + 1
                    if tau >= 0:
                        self.update_q_table(tau, S, A, R, T)

                    if tau == T - 1:
                        while len(S) > 1:
                            tau = tau + 1
                            self.update_q_table(tau, S, A, R, T)
                        done_update = True
                        break

# ------------------------------------------------------------------------------------------------ #
# ----------------------------------------END AGENT CLASS----------------------------------------- #
# ------------------------------------------------------------------------------------------------ #

if __name__ == '__main__':
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

    started = False

    num_reps = 30000
    dodger = Dodger()
    for iRepeat in range(num_reps):
        if player_life <= 0 or not started: # Player died so we restart the level.
            player_life = 10                # Reset player health
            started = True                  # Indicated that we have started the first mission.

            print "Quit mission"
            agent_host.sendCommand("quit") # Re-start mission

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

            # Waits for mission to start.
            world_state = agent_host.getWorldState()
            while not world_state.has_mission_begun:
                time.sleep(0.1)
                world_state = agent_host.getWorldState()
        else:
            print (iRepeat+1), 'Learning Q-Table:',
            dodger.run(agent_host)

        time.sleep(1)

    print "Mission ended"