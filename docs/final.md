---
layout: default
title:  Final Report
---

## Video
[![Click here to be redirected to our video demonstration](https://img.youtube.com/vi/wnPaqCjGIgA/0.jpg)](https://www.youtube.com/watch?v=wnPaqCjGIgA)

## Project Summary
Project IfYouCanDodgeAFireball involves creating an AI agent in Minecraft that can survive as long as possible against a ghast attack. Ghasts are aggressive flying monsters in Minecraft that shoot fireballs at players. A direct hit from a fireball can do up to 3 damage to an unarmoured player, and since players in Minecraft only have a default health of 10, our agent must intelligently avoid fireballs in order to maximize its lifetime.

### Image of a Ghast in Minecraft
<img src="http://www.minecraftseedspc.com/wp-content/uploads/2015/11/Ghast_Minecraft_06.jpg" width="400" height="350"/>

The final goal for this project was to create an agent that can survive an onslaught from multiple Ghasts. We were successfully able to achieve our goal. Read on to learn about our approach to the problem and our solution that successfully creates a fireball dodging agent.

## Approaches
We expanded upon our previous environment by spawning 3 ghasts instead of 1 and we now allow the agent to move in 4 directions rather than just 2 (left and right). The agent is constrained to a 20x20 movement area that the agent must use to dodge all incoming fireballs.

The 3 ghasts are located in front of the agent around 25 units up and 20 units away from the agent. The ghasts location are constrained while the AI is running.

### Environment Setup Image
<img src="http://i.imgur.com/g9E6Did.png"/>

We are using Q-learning, a type of reinforcement learning, to approach the problem. We decided with Q-learning as we figured out that breaking our problem down into states, actions, rewards, and episodes, was what we needed to properly train the agent to dodge fireballs.
 
### Q-learning pseudocode
<img src="http://i.imgur.com/oi6jv72.png"/>
 
### Q value formula
<img src="http://i.imgur.com/eAyNfY1.png"/>
 
The Q-learning algorithm selects the action with the highest Q-value for a given state. The Q-value is calculated based on rewards resulting from a state, and constants α (alpha) and γ (gamma). We also use constants ε (epsilon), and n to tweak how the algorithm behaves over time.

#### Constant values that seemed to work well for our environment:
α = 0.6 - Based on our observations, an alpha close to 1 helps the agent learn faster. Since our solution does not rely on randomness, a higher alpha seems to allow the agent to learn more quickly.

γ = 1 - This is the default decay rate and it seems to work well for our purposes.

ε = 0.01 - Epsilon refers to how often our AI will do a random action rather than the action with the highest Q-value. We set this close to 0 as our agent benefits very little from random actions.

n = 1 - The default n, refers to number of backsteps to update. Works well for our purposes.

### State Space
In our status report we showed two different methods of calculating our state. Now we only have 1 reliable method of state calculation.

#### Encoding agent location
The agent's location is very important information in determining how to dodge fireballs, since if the agent is close to a wall, their movement becomes restricted. Since our agent's walking area is a 20x20 square, encoding the agent's location into the state would add 400 times more states. Instead we decided to encode something we called a 'corner value' that describes a zone where the agent is within the movement area.

##### Visualization of corner values in relation to environment
<img src="http://i.imgur.com/vbAyiNu.png"/>

For example, if the agent's corner value is '8', then the agent would realize that it would be unable to move left. Corner values 1-8 represent zones where the agent's movement is restricted. Corner values 9-16 are used as 'warning zones' to let the agent know that it is getting close to a movement restricting zone. Corner value 0 represents the zone where the agent has the most freedom to move.

#### Encoding fireball cluster target location


## Evaluation


## References
