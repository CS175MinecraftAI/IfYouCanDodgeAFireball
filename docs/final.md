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

#### Visualization of corner values in relation to environment
<img src="http://i.imgur.com/vbAyiNu.png"/>

For example, if the agent's corner value is '8', then the agent would realize that it would be unable to move left. Corner values 1-8 represent zones where the agent's movement is restricted. Corner values 9-16 are used as 'warning zones' to let the agent know that it is getting close to a movement restricting zone. Corner value 0 represents the zone where the agent has the most freedom to move in the middle of the area.

#### Encoding fireball cluster target location
If a player wants to dodge fireballs, then they need to move away from the fireballs projected target location. Our approach is very similar. When the agent detects that a new fireball has been shot by a ghast, the agent assumes the fireball is aimed at the agent's current location. The agent keeps track of all currently live fireballs and their projected target locations and calculates the 'midpoint' between all target locations called the 'fireball cluster point'. The fireball cluster point is what the agent should try to move away from. We discretely encode the delta x and delta y between the agent's current location and the fireball cluster point.

#### Visualization of midpoint calculation
<img src="http://i.imgur.com/7BRUKrS.png"/>

#### State space size
It is quite simple to estimate the size of our state space. We encode our state space into a 3-tuple (corner_value, delta_x_cluster_loc, delta_y_cluster_loc). There are 17 corner values, and typically the delta_x and delta_y distance between the agent's location and the fireball cluster point ranges from -5 to positive 5, which is a range of 10.

Estimated state space size = 17 * 10 * 10 = 1,700 states

### Rewards
An episode ends after 1 round of fireballs or when the agent dies. The end of an episode does not signify anything too important, however we do give the agent a reward around every 0.1 seconds as the agent attempts to dodge fireballs.

We give a higher reward to the agent the farther the agent moves from the fireball cluster point. We give a negative reward to the agent if it is within a distance of 3 to the fireball cluster point or if they are hit by a fireball, and we give a positive reward to the agent if its distance to the fireball cluter point is greater than 3. By giving the agent these rewards, we are training the agent to avoid the fireball cluster point and to therefore dodge multiple fireballs.

## Evaluation
We will asses our AI using both qualitative and quantitative methods and demonstrate how our agent runs under different situations.

## Quantitative evaluation
Players in Minecraft can wear armor that allows them to take less damage. We have ran our AI using an agent wearing diamond armor (no helmet) and without any armor. The graphs below demonstrate how long the agent survives over a number of lives with and without armor.

### Armoured player
The graph below demonstrates how long the armoured agent typically survives over 15 lives. Note that we ran the AI 5 separate times at 15 lives each. The thicker yellow line represents the average of survival times over life.
<img src="http://i.imgur.com/H0ic7BY.png"/>

If we fit a linear regression line on the average line, it appears that the survival time is increasing the higher the life number.
<img src="http://i.imgur.com/yjeiD9n.png"/>

### Unarmoured player
The graph below demonstrates how long the unarmoured agent typically survives over 40 lives. Note that we ran the AI 5 separate times at 40 lives each and averaged the survival time over life.
<img src="http://i.imgur.com/gltox8d.png"/>

If we fit a linear regression line on the average line, it appears that the survival time is increasing the higher the life number.
<img src="http://i.imgur.com/92QChDz.png"/>

The unarmoured agent's performance is less consistent due to the fact that one small mistake can cause death rather quickly in comparison to the armoured agent.

From both graphs it is easy to see that the agent dies quickly at early lives and over time learns how to survive longer.

## Qualitative evaluation
One way to qualitatively evaluate the AI is to simply watch it dodge fireballs and try to see if the AI is actually trying to dodge fireballs or if the AI is just dodging randomly. We have made a video located at the top of this page to demonstrate how the agent learns to dodge fireballs over a training period of about 20 minutes.

## References
In order to understand the Q-Learning algorithm, we used the class book and assignment 2 as most of our reference material.

We also used the below websites in order to figure out how to edit entity data, send commands, and other useful information about Minecraft.