---
layout: default
title:  Status
---

# Project Summary
Project IfYouCanDodgeAFireball involves creating an AI agent in Minecraft that can survive as long as possible against a ghast attack. Ghasts are aggressive flying monsters in Minecraft that shoot fireballs at players. Our final goal for this project is to create an agent that can survive an onslaught from multiple Ghasts. Currently, we have only trained an agent to survive against one immobile ghast.
 
### Illustrated version of our agent running from Ghast fireballs
<img src="http://i.imgur.com/Mt1oxS9.jpg" width="600" height="400"/>
 
# Approach
We wanted to start small at the beginning, so we set up a simple environment where both the agent and a Ghast are inside an enclosed rectangular area. We set boundaries around the Ghast so that the Ghast’s movement is restricted, as otherwise the Ghast will move too close and it becomes too difficult for the agent to dodge the fireballs. As of right now, the agent can only move left and right to dodge fireballs, as we wanted to keep the list of actions small for now. The area is 8 x 8 x 30 blocks.

### Environment Setup
<img src="http://i.imgur.com/7fP5THM.png"/>

We are using Q-learning, a type of reinforcement learning, to approach the problem. We decided with Q-learning as we figured out that breaking our problem down into states, actions, rewards, and episodes, was what we needed to properly train the agent to dodge fireballs.
 
### Q-learning pseudocode
<img src="http://i.imgur.com/oi6jv72.png"/>
 
### Q value formula
<img src="http://i.imgur.com/eAyNfY1.png"/>
 
The Q-learning algorithm selects the action with the highest Q-value for a given state. The Q-value is calculated based on rewards resulting from a state, and constants α (alpha) and γ (gamma). We also use constants ε (epsilon), and n to tweak how the algorithm behaves over time.

#### Constant values that seemed to work well for our environment:
α = 0.6 - Based on our observations, an alpha close to 1 helps the agent learn faster. Since our state space is small, a higher alpha seems to allow the agent to learn more quickly.

γ = 1 - This is the default decay rate and it seems to work well for our purposes.

ε = 0 - Epsilon refers to how often our AI will do a random action rather than the action with the highest Q-value. We set this to zero as our state space is currently very small and so the agent benefits very little from random actions.

n = 1 - The default n, refers to number of backsteps to update. Works well for our purposes.

### State Space
We have currently have two methods for calculating the state of the world. We will show the differences between both methods in explanation and in terms of agent performance.

#### Encoding Agent Location
The first bit of information we wanted to encode into the state was the agent's location. Since the agent can only more 1-dimensionally, this is only 1 value. However we reduced the player’s location to five different values, giving each a numeric value: left_corner +2, middle_left +1, middle 0 , middle_right -1, right_corner -2.  When the agent is in the middle, it is unobstructed by a wall, therefore it can move either left or right to dodge.  When the agent is getting closer to the left wall, it would want to avoid moving left and cornering itself, and vice versa for the right wall. We call this value the "corner value" of the agent.

#### Visualization of the corner value
<img src="http://i.imgur.com/Sk4tyQg.png"/>

#### State method 1: Fireball distance to agent
One method of calculating state is to create a 3-tuple where the tuple contains (corner value, fireball delta x, fireball delta z) where fireball delta x and z refer to the positional difference between the fireball and the agent.

State size calculation: 5 (corner values) * 8 (maximum delta_x from fireball) * 30 (maximum delta_z from fireball) = 1200 states

#### State method 2: Distance to start
Upon further thinking, we observed that the agent just needs to move away from its initial position -- since the Ghast aims for that location. This involves encoding a 2-tuple where the tuple contains (corner value, distance to start position).

State size calculation: 5 (corner values) * 8 (maximum distance from start) = 40 states

### Rewards
We currently consider the length of 1 episode to be the lifetime of 1 fireball. Since we wait 500 ms after issuing an action, each episode contains around 4 episode steps.

Before the fireball reaches the agent, we give feedback on the agent's current movements. The feedback is based off how far the agent is from their start position, nd so staying still will yield a negative reward. This encourages the agent to move. If the agent manages to dodge a fireball, the final reward is positive and is scaled by how far the agent is when the fireball passes the agent. If the agent gets hit by a fireball, the reward is negative and is scaled by how much life the agent lost. We do this because the agent can lose less health if it is not hit head on by the fireball.

