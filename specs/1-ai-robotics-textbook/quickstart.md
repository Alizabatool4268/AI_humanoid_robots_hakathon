# Quickstart: AI-Native Textbook on Physical AI & Humanoid Robotics

This guide will help you quickly set up and browse the AI-Native Textbook on Physical AI & Humanoid Robotics locally.

## Prerequisites

- Node.js (v18.0 or later)
- npm (v7.0 or later)

## Setup Instructions

1.  **Clone the repository**:

    ```bash
    git clone [REPOSITORY_URL]
    cd [REPOSITORY_NAME]
    ```
    (Replace `[REPOSITORY_URL]` and `[REPOSITORY_NAME]` with actual values once known.)

2.  **Install dependencies**:

    Navigate to the `frontend/` directory (or wherever Docusaurus is initialized) and install the required Node.js packages:

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

## Browsing the Textbook

- Use the sidebar navigation to explore different chapters and modules.
- The search bar can be used to find specific topics within the textbook.

## Building for Deployment

To build the static website for deployment (e.g., to GitHub Pages):

```bash
npm run build
```

The generated static files will be located in the `build/` directory within your Docusaurus project.
