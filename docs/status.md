---
layout: default
title:  Status
---

## Project Summary
Project IfYouCanDodgeAFireball involves creating an AI agent in Minecraft that can survive as long as possible against a ghast attack. Ghasts are aggressive flying monsters in Minecraft that shoot fireballs at players. Our final goal for this project is to create an agent that can survive an onslaught from multiple Ghasts. Currently, we have only trained an agent to survive against one immobile ghast.
 
#### A Ghast attacking a player
<img src="http://i.imgur.com/Mt1oxS9.jpg" width="600" height="400" align="middle"/>
 
## Approach
We decided to use Q-learning, a type of reinforcement learning, to approach the problem. We decided with Q-learning as we figured out that breaking our problem down into states, actions, rewards, and episodes, was what we needed to properly train the agent to dodge fireballs.
 
#### Q-learning pseudocode
<img src="http://i.imgur.com/oi6jv72.png" width="670" height="200" align="middle"/>
 
#### Q value formula in detail
<img src="http://i.imgur.com/7o9qCr5.png" width="750" height="500" align="middle"/>
 
The Q-learning algorithm selects the action with the highest Q-value for a given state. The Q-value is calculated based on rewards resulting from a state, and constants α (alpha) and γ (gamma). We also use constants ε (epsilon), and n to tweak how the algorithm behaves over time.