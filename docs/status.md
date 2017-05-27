---
layout: default
title:  Status
---

## Project Summary
Project IfYouCanDodgeAFireball involves creating an AI agent in Minecraft that can survive as long as possible against a ghast attack. Ghasts are aggressive flying monsters in Minecraft that shoot fireballs at players. Our final goal for this project is to create an agent that can survive an onslaught from multiple Ghasts. Currently, we have only trained an agent to survive against one immobile ghast.
 
#### Illustrated version of our agent running from Ghast fireballs
<img src="http://i.imgur.com/Mt1oxS9.jpg" width="600" height="400"/>
 
## Approach
We wanted to start small at the beginning, so we set up a simple environment where both the agent and a Ghast are inside an enclosed rectangular area. We set boundaries around the Ghast so that the Ghast’s movement is restricted, as otherwise the Ghast will move too close and it becomes too difficult for the agent to dodge the fireballs. As of right now, the agent can only move left and right to dodge fireballs, as we wanted to keep the list of actions small for now.

#### Environment Setup
<img src="http://i.imgur.com/7fP5THM.png" width="600" height="300"/>

We are using Q-learning, a type of reinforcement learning, to approach the problem. We decided with Q-learning as we figured out that breaking our problem down into states, actions, rewards, and episodes, was what we needed to properly train the agent to dodge fireballs.
 
#### Q-learning pseudocode
<img src="http://i.imgur.com/oi6jv72.png" width="670" height="200"/>
 
#### Q value formula
<img src="http://i.imgur.com/eAyNfY1.png"/>
 
The Q-learning algorithm selects the action with the highest Q-value for a given state. The Q-value is calculated based on rewards resulting from a state, and constants α (alpha) and γ (gamma). We also use constants ε (epsilon), and n to tweak how the algorithm behaves over time.

#### Constant values that seemed to work well for our environment:
α = 0.6 - We set a high learning rate because we feel the environment is simple and so the agent should learn what to do quickly.
γ = 1 - This is the default decay rate and it seems to work well for our purposes.
ε = 0 - Epsilon refers to how often our AI will do a random action rather than the action with the highest Q-value. We set this to zero as our state space is currently very small and so the agent benefits very little from random actions.
n = 1 - The default n, refers to number of backsteps to update. Works well for our purposes.

#### State Space
We have currently 

#### Rewards