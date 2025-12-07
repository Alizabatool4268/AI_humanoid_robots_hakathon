---
id: ros2-fundamentals
title: ROS 2 Fundamentals
sidebar_label: '1. ROS 2 Fundamentals'
sidebar_position: 2
---

# ROS 2 Fundamentals

## Short Introduction

This chapter introduces the fundamental concepts of ROS 2 (Robot Operating System 2), which is essential for developing humanoid robotics applications. ROS 2 provides the communication framework, tools, and libraries needed to build complex robotic systems. Understanding these basics is crucial for working with humanoid robots, as they rely on distributed systems to coordinate movement, perception, and decision-making.

## Core Concepts

ROS 2 is a flexible framework for writing robot software that provides services designed for a heterogeneous computer cluster. Unlike traditional software frameworks, ROS 2 is actually a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms.

At its core, ROS 2 uses a distributed architecture where multiple processes (called nodes) work together to achieve complex behaviors. These nodes communicate with each other using several mechanisms including:

- **Topics**: For asynchronous message passing using a publish/subscribe model
- **Services**: For synchronous request/response communication
- **Actions**: For long-running tasks with feedback, status, and cancellation

Topics implement a publish/subscribe model where nodes can publish messages to a topic and other nodes can subscribe to that topic to receive messages. This allows for asynchronous communication between different parts of your robot system. Services provide a request/response pattern for synchronous communication when you need to ensure a response before proceeding. Actions are used for long-running tasks that require feedback, such as moving a robot arm to a specific position while monitoring progress.

ROS 2 also uses packages as the basic unit of organization for code. A package contains nodes, libraries, configuration files, and other resources needed for a specific functionality. Packages help organize code and make it reusable across different projects. Each package has a `package.xml` file that describes dependencies and metadata.

## Simple Example or Scenario

Consider a humanoid robot that needs to move its arm to pick up an object. The robot might have separate nodes for perception (detecting the object), planning (determining how to reach the object), and control (sending commands to the arm's motors).

The perception node publishes the object's location to a topic called "object_position". The planning node subscribes to this topic and, when it receives the object's location, it computes a trajectory for the arm and sends it to the control node via a service call. The control node then executes the movement and might publish feedback to a topic called "arm_status" to indicate the current position of the arm.

This example demonstrates how different nodes can work together through ROS 2's communication mechanisms to achieve a complex task like object manipulation. In a real implementation, the control node might use an action server to handle the arm movement, allowing for feedback on the progress of the movement and the ability to cancel the action if needed.

## Relevance to Humanoid Robotics

ROS 2 is particularly important for humanoid robotics because these robots are inherently complex systems with multiple subsystems that need to communicate seamlessly. A humanoid robot typically has sensors (cameras, IMUs, force/torque sensors), actuators (motors for joints), and processing units (for perception, planning, and control) that all need to work together.

The distributed nature of ROS 2 allows different teams to work on different aspects of the humanoid robot simultaneously. For example, one team can work on locomotion while another works on manipulation, and these systems can be integrated later through ROS 2's communication infrastructure.

Additionally, ROS 2 provides many packages specifically designed for humanoid robots, such as navigation stacks, manipulation libraries, and simulation tools. The Unified Robot Description Format (URDF) is used to describe robot models, including kinematic and dynamic properties, which is essential for humanoid robots with complex joint structures.

## Short Summary

ROS 2 fundamentals form the backbone of communication and organization in humanoid robotics projects. Understanding nodes, topics, services, actions, and packages is essential for building complex robotic systems. These concepts enable the distributed and modular approach necessary for developing humanoid robots with multiple interacting subsystems.