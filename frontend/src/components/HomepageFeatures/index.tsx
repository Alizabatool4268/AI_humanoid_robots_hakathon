import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import React from 'react';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Content this book covers',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <ul>
       <li> ROS 2 fundamentals (nodes, topics, services, URDF) </li>
       <li> Gazebo simulation, physics, Unity visualization </li>
       <li> NVIDIA Isaac Sim, Isaac ROS, Nav2 </li>
       <li>  Vision-Language-Action robotics</li>
       <li>  Conversational robotics (Whisper + LLM planning)</li>
        <li>Capstone: Autonomous humanoid robot executing spoken tasks</li>

      </ul>
    ),
  },
  {
    title: 'Simple UI',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        This book has a simple and user friendly interface.
      </>
    ),
  },
  {
    title: 'Simplicity over complexity',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        The book follows a simple structure of simple stuff over complex stuff
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
