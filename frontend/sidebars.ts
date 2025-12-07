import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  textbookSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro/intro'],
      collapsed: false,
    },
    {
      type: 'category',
      label: '1. ROS 2 Fundamentals',
      items: ['ros2-fundamentals/ros2-fundamentals'],
      collapsed: false,
    },
    {
      type: 'category',
      label: '2. Gazebo Simulation, Physics, Unity Visualization',
      items: ['gazebo-unity/gazebo-unity'],
      collapsed: false,
    },
    {
      type: 'category',
      label: '3. NVIDIA Isaac Sim, Isaac ROS, Nav2',
      items: ['nvidia-isaac/nvidia-isaac'],
      collapsed: false,
    },
    {
      type: 'category',
      label: '4. Vision-Language-Action Robotics',
      items: ['vision-language-action/vision-language-action'],
      collapsed: false,
    },
    {
      type: 'category',
      label: '5. Conversational Robotics (Whisper + LLM Planning)',
      items: ['conversational-robotics/conversational-robotics'],
      collapsed: false,
    },
    {
      type: 'category',
      label: '6. Capstone: Autonomous Humanoid Robot',
      items: ['capstone/capstone'],
      collapsed: false,
    },
  ],
};

export default sidebars;
