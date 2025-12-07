# Quickstart: AI-Native Textbook on Physical AI & Humanoid Robotics

This guide will help you quickly set up and browse the AI-Native Textbook on Physical AI & Humanoid Robotics locally.

## Prerequisites

- Node.js (v18.0 or later)
- npm (v7.0 or later)

## Setup Instructions

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/AI-humanoid-robots-hakathon/AI-humanoid-robots-hakathon.git
    cd AI-humanoid-robots-hakathon
    ```

2.  **Install dependencies**:

    Navigate to the `frontend/` directory (where Docusaurus is initialized) and install the required Node.js packages:

    ```bash
    cd frontend/
    npm install
    ```

3.  **Start the development server**:

    Once dependencies are installed, you can start the Docusaurus development server:

    ```bash
    npm start
    ```

    This will open the textbook in your browser at `http://localhost:3000` (or a similar address).

## Docusaurus Commands

- `npm start`: Start the development server
- `npm run build`: Build the static website for deployment
- `npm run serve`: Serve the built website locally
- `npm run deploy`: Deploy the website to GitHub Pages
- `npm run clear`: Clear the build cache
- `npm run write-translations`: Extract translation strings
- `npm run write-heading-ids`: Generate heading IDs for linking

## Browsing the Textbook

- Use the sidebar navigation to explore different chapters and modules.
- The search bar can be used to find specific topics within the textbook.

## Building for Deployment

To build the static website for deployment (e.g., to GitHub Pages):

```bash
npm run build
```

The generated static files will be located in the `build/` directory within your Docusaurus project.
