---
layout: default
title:  Status
---

## Project Summary
Our project is to create an AI agent in Minecraft that can survive against a ghast attack.

![ghast](http://www.minecraftseedspc.com/wp-content/uploads/2015/11/Ghast_Minecraft_06.jpg)

Ghasts are enemies in Minecraft that fly around and shoot fireballs at the player. We want to create an agent that dodges ghasts fireballs or even fights back against the ghast by deflecting the fireballs by swinging a sword.

For input, we want to give the agent information about the state of the world such as ghast location, fireball location, player location and boundaries. We will also give the agent simple possible inputs such as moving left/right and attacking.

The agent should produce behavior that will allow the agent to survive against the ghast attack. This includes dodging a fireball, deflecting the fireball back at the ghast, and possibly damaging or destroying the ghast by deflecting the fireball.

## Approach
There are two ways we are thinking of achieving the goal of this project. One way is to use Q-learning (reinforcement learning) and the other is to use neural networks for image processing of the screen.

## Evaluation
Our metric will involve associating rewards with what happens to the player. Dodging and reflecting fireballs will yield positive rewards while taking damaging and making movement will yield negative rewards. We will keep track of a overall score that is equal to the sum of all reward values. The baseline metric would be getting killed by the ghast after getting hit by fireballs and we would improve this metric by retaining as much health as possible while dodging and deflecting fireballs.

We will be able to qualitatively determine whether or not our AI agent behaves appropriately by observing an agent that at the very least dodges incoming fireballs. Our moonshot case would be to create an AI agent that not only dodges fireballs but deflects them back at the ghast in order to destroy the enemy ghast. Eventually we may be able to create an agent that fights off multiple ghasts at a time.

## Remaining Goals and Challenges