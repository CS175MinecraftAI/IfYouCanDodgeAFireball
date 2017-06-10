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

mission_file_no_ext = 'ghast_survival_mission_extended'              # CS175 Project. Ghast Survival

fireball_num = 1 # Represents a group of fireballs that are headed towards the same point.
fireball_target_map = { } # Maps fireball name to target location

player_delta_life = 10 # Player's life at beginning of episode
player_life       = 10 # Player's life

# Only storing x,z because we don't care about y (up/down)
mid_point  = [0, 0]
player_loc = [0, 0]

actions = ["nothing", "move_left", "move_right", "move_forward", "move_backward"]

random_policy = True

num_of_fireball = 0
resting = True
last_reward = 0

# ------------------------------------------------------------------------------------------------ #
# ----------------------------------------- FUNCTIONS -------------------------------------------- #
# ------------------------------------------------------------------------------------------------ #

def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2 + (p0[2] - p1[2])**2)

def distance_2d(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def angvel(target, current, scale):
    '''Use sigmoid function to choose a delta that will help smoothly steer from current angle to target angle.'''
    delta = target - current
    while delta < -180:
        delta += 360;
    while delta > 180:
        delta -= 360;
    return (2.0 / (1.0 + math.exp(-delta/scale))) - 1.0

def resummon_Ghast(name):
    if len(name) >= 4 or len(name) == 0:
        return 0
    print "Ghasts_alive : ", name

    if "Ghast_1" not in name:
        agent_host.sendCommand('chat /summon Ghast 0 230 35 {CustomName:Ghast_1}')
    if "Ghast_2" not in name:
        agent_host.sendCommand('chat /summon Ghast 0 230 -15 {CustomName:Ghast_2}')
    if "Ghast_3" not in name:
        agent_host.sendCommand('chat /summon Ghast -30 230 10 {CustomName:Ghast_3}')
    if "Ghast_4" not in name:
        agent_host.sendCommand('chat /summon Ghast 30 230 10 {CustomName:Ghast_4}')

    # if "Ghast_5" not in name:
    #     agent_host.sendCommand('chat /summon Ghast -30 230 35 {CustomName:Ghast_5}')
    # if "Ghast_6" not in name:
    #     agent_host.sendCommand('chat /summon Ghast 30 230 35 {CustomName:Ghast_6}')
    # if "Ghast_7" not in name:
    #     agent_host.sendCommand('chat /summon Ghast -30 230 -15 {CustomName:Ghast_7}')
    # if "Ghast_8" not in name:
    #     agent_host.sendCommand('chat /summon Ghast 30 230 -15 {CustomName:Ghast_8}')

    print "respawned ghast!"

def set_world_observations(agent_host):
    global fireball_num
    global fireball_target_map

    global player_loc
    global mid_point

    global player_life
    global player_delta_life

    # We give fireballs a unique name to identify them. We can group multiple fireballs together this way that are headed towards the same target location.
    # We do not re-name fireballs that have already been named
    agent_host.sendCommand('chat /entitydata @e[type=Fireball,r=30,name=Fireball] {CustomName:Fireball_' + str(fireball_num) + '}')
    
    fireball_num += 1
    if fireball_num > 1000: # Reset fireball_num after a while.
        fireball_num = 1

    world_state = agent_host.getWorldState()
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        ob = json.loads(msg)

        # Player location
        if "XPos" in ob:
            player_loc[0] = ob[u'XPos']
        if "ZPos" in ob:
            player_loc[1] = ob[u'ZPos']

        if (int(player_loc[1]) > 19 or int(player_loc[1]) < 0 or int(player_loc[0]) > 10 or int(player_loc[0]) < -8): # Teleport out
            agent_host.sendCommand('chat /tp 0.5 227 11')
            fireball_target_map = { }   # Otherwise distance to mid_point will be high and thus yield a false high reward.
            mid_point = [1000, 1000]    # Reset mid_point as well.
            set_world_observations(agent_host)
            return

        fireballs_alive = [] # Fireballs that are alive
        ghasts_alive = []

        if "entities" in ob:
            entities = [EntityInfo(**k) for k in ob["entities"]]
            for entity in entities:
                name = entity[5]

                if "Fireball_" in name: # Entity is a re-named fireball
                    fireballs_alive.append(name) # This fireball is alive

                    if name not in fireball_target_map.keys(): # Add new fireball
                        fireball_target_map[name] = [player_loc[0], player_loc[1]] # Maps fireball custom name to target point

                if "Ghast_" in name:  # Entity is a re-named ghast
                    ghasts_alive.append(name)  # This ghast is alive

        # summon ghast if it despawned:
        resummon_Ghast(ghasts_alive)

        # Now we have to delete fireballs from fireball_target_map that are dead
        for key in fireball_target_map.keys():
            if key not in fireballs_alive:
                del fireball_target_map[key]

        # Now we have to calculate the mid_point
        num_points = len(fireball_target_map)
        mid_point = [0, 0] # Reset mid point

        #print "Our location ", player_loc
        #print "VALUES: ", fireball_target_map

        if num_points > 0:
            for target in fireball_target_map.values():
                mid_point[0] += target[0]
                mid_point[1] += target[1]

            mid_point[0] /= float(num_points)
            mid_point[1] /= float(num_points)

            #print "mid_point: ", mid_point
        else:
            mid_point = [1000, 1000] # Mid_point defaults to player location

        if "Life" in ob:
            life = ob[u'Life']

            if life < player_life:
                player_delta_life = player_life - life
            else:
                player_delta_life = 0

            player_life = life

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
        #self.epsilon = 0.2  # chance of taking a random action instead of the best

        self.q_table = {}
        self.n, self.alpha, self.gamma = n, alpha, gamma

        self.epsilon = 0.01
        self.alpha = 0.9
        self.gamma = 0.4

    def hard_coded_policy(self): # TODO XD
        return 0

    def calculate_reward(self):
        if (mid_point[0] == 1000): # Default mid_point
            return 0

        dist_to_midpoint = distance_2d(player_loc, mid_point) # No rounding
        distance_reward = 0
        if (dist_to_midpoint <= 3):
            distance_reward = (3 - dist_to_midpoint) * -10
        else:
            distance_reward = dist_to_midpoint * 10

        # Can add player delta life to reward calculation if needed
        return (player_delta_life * -10) + distance_reward

    def get_corner_val(self):
        corner_val = 0 # Not in a corner

        loc_x = int(player_loc[0])
        loc_z = int(player_loc[1])

        if (loc_z > 18): # Cannot move forward
            if (loc_x > 9):
                corner_val = 1
            elif (loc_x < -7):
                corner_val = 3
            else:
                corner_val = 2
        elif (loc_z < 1):
            if (loc_x > 9):
                corner_val = 7
            elif (loc_x < -7):
                corner_val = 5
            else:
                corner_val = 6
        elif (loc_x > 9):
            corner_val = 8
        elif (loc_x < -7):
            corner_val = 4

        return corner_val

    def get_curr_state(self):
        dx_midpoint = int(mid_point[0] - player_loc[0])
        dz_midpoint = int(mid_point[1] - player_loc[1])

        if (mid_point[0] == 1000):
            dx_midpoint = None
            dz_midpoint = None

        return self.get_corner_val(), dx_midpoint, dz_midpoint

    def choose_action(self, curr_state, possible_actions, eps, q_table):

        global last_reward

        """Chooses an action according to eps-greedy policy. """
        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0

        rnd = random.random()
        a = 0

        if rnd < eps:   # below eps, give random action:
            # print "random : ", rnd
            if random_policy:
                a = random.randint(0, len(possible_actions) - 1)
                
                print "rand:", possible_actions[a], ",current state:", self.get_curr_state(), q_table[curr_state].items()
                print "reward :", self.calculate_reward()
                return possible_actions[a]
            else:
                return self.hard_coded_policy()

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

            if not resting:
                print "best:", tempContainer[tmprnd][0], "current state :", self.get_curr_state(), q_table[curr_state].items()
                last_reward = self.calculate_reward()
                print "reward :", last_reward

            return tempContainer[tmprnd][0]  

    def get_possible_actions(self, agent_host, is_first_action=False):
        """Returns all possible actions that can be done at the current state. """
        global resting
        global num_of_fireball
        global last_reward

        if mid_point[0] == 1000:
            if not resting:
                print "No Fireball!------------------------------------------------------"
                num_of_fireball += 1
                print "# of fireballs:", num_of_fireball
                print "Last Reward : ", last_reward
            resting = True
            return ["nothing"]

        resting = False

        action_list = ["nothing", "move_left", "move_right", "move_forward", "move_backward"]

        corner_val = self.get_corner_val()

        if (corner_val == 1 or corner_val == 2 or corner_val == 3):
            action_list.remove("move_forward")

        if (corner_val == 1 or corner_val == 8 or corner_val == 7):
            action_list.remove("move_left")

        if (corner_val == 3 or corner_val == 4 or corner_val == 5):
            action_list.remove("move_right")

        if (corner_val == 7 or corner_val == 6 or corner_val == 5):
            action_list.remove("move_backward")

        return action_list

    def act(self, agent_host, action):
        # global episode_reward
        
        # Actions are move_left, move_right, nothing
        if action == "move_left":
            agent_host.sendCommand("strafe -2")
        elif action == "move_right":
            agent_host.sendCommand("strafe 2")
        elif action == "move_forward":
            agent_host.sendCommand("move 2")
        elif action == "move_backward":
            agent_host.sendCommand("move -2")
        else: # Do nothing
            agent_host.sendCommand("strafe 0")
            agent_host.sendCommand("move 0")

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
        S, A, R = deque(), deque(), deque() # S = states, A = actions, R = rewards
        done_update = False
        while not done_update:
            set_world_observations(agent_host)

            s0 = self.get_curr_state()
            possible_actions = self.get_possible_actions(agent_host, True)
            a0 = self.choose_action(s0, possible_actions, self.epsilon, self.q_table)
            S.append(s0)
            A.append(a0)
            R.append(0)

            T = sys.maxint
            for t in xrange(sys.maxint):
                agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_1] {Pos:[0d,250d,35d]}')
                agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_2] {Pos:[0d,250d,-15d]}')
                agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_3] {Pos:[-30d,250d,10d]}')
                agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_4] {Pos:[30d,250d,10d]}')

                # agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_5] {Pos:[-30d,250d,35d]}')
                # agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_6] {Pos:[30d,250d,35d]}')
                # agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_7] {Pos:[-30d,250d,-15d]}')
                # agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100,name=Ghast_8] {Pos:[30d,250d,-15]}')

                set_world_observations(agent_host)

                if t < T:
                    if player_life <= 0: # Player dies, end of episode
                        # Terminating state
                        T = t + 1
                        S.append('Term State')
                        final_reward = self.calculate_reward()
                        R.append(final_reward)
                    else:
                        self.act(agent_host, A[-1]) # Do an action
                        time.sleep(0.1) # Gives time to act before getting feedback.
                        print "Did:", A[-1], "Reward:", self.calculate_reward(), "State:", self.get_curr_state() 
                        R.append(self.calculate_reward())

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

            agent_host.sendCommand("quit") # Re-start mission

            mission_file = mission_file_no_ext + ".xml"
            with open(mission_file, 'r') as f:
                print "Last Reward : ", last_reward
                print "Loading mission from %s" % mission_file
                mission_xml = f.read()
                my_mission = MalmoPython.MissionSpec(mission_xml, True)
                my_mission.setViewpoint(1) #1 for 3rd person view

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
                        time.sleep(1)

            # Waits for mission to start.
            world_state = agent_host.getWorldState()
            while not world_state.has_mission_begun:
                time.sleep(0.1)
                world_state = agent_host.getWorldState()

            agent_host.sendCommand('chat /kill @e[type=Ghast]')
            time.sleep(0.2)

            agent_host.sendCommand('chat /summon Ghast 0 230 35 {CustomName:Ghast_1}')
            agent_host.sendCommand('chat /summon Ghast 0 230 -15 {CustomName:Ghast_2}')
            agent_host.sendCommand('chat /summon Ghast -30 230 10 {CustomName:Ghast_3}')
            agent_host.sendCommand('chat /summon Ghast 30 230 10 {CustomName:Ghast_4}')

            # agent_host.sendCommand('chat /summon Ghast -30 230 35 {CustomName:Ghast_5}')
            # agent_host.sendCommand('chat /summon Ghast 30 230 35 {CustomName:Ghast_6}')
            # agent_host.sendCommand('chat /summon Ghast -30 230 -15 {CustomName:Ghast_7}')
            # agent_host.sendCommand('chat /summon Ghast 30 230 -15 {CustomName:Ghast_8}')

            agent_host.sendCommand('chat /entitydata @e[type=Ghast,r=100] {Invulnerable:1}') # Make Ghast invulnerable so they don't kill eachother.
        else:
            print "Iteration", (iRepeat/2), 'Learning Q-Table'
            start_time = time.time()
            dodger.run(agent_host)
            elapsed_time = time.time() - start_time
            print "Episode", (iRepeat/2), "length:", elapsed_time
            if num_of_fireball > 500:
                exit()

        time.sleep(0.5)

    print "Mission ended"