import React from 'react';
import { render, screen } from '@testing-library/react';
import HomepageFeatures from './index';

describe('HomepageFeatures', () => {
  it('renders without crashing', () => {
    render(<HomepageFeatures />);
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });

  it('displays feature items', () => {
    render(<HomepageFeatures />);

    // Check if feature items are present (using generic selectors since we don't know the exact content structure)
    const features = screen.getAllByRole('listitem');
    expect(features.length).toBeGreaterThan(0);
  });
});