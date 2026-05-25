# Frontend

This folder provides the Astro + React frontend for the meal planning web application. This frontend is deployed live at [https://ict-3909-fyp.vercel.app/](https://ict-3909-fyp.vercel.app/).

## Overview

The frontend is built with [Astro](https://astro.build) and [React](https://react.dev), styled with [Tailwind CSS](https://tailwindcss.com), and uses [nanostores](https://github.com/nanostores/nanostores) for client-side state management. It communicates with the FastAPI backend to fetch ingredients and recipes and to generate personalised meal plans.

## Setup and Usage

Ensure that [Node.js](https://nodejs.org/en) is installed (v24 or higher). Then, from this directory:

1. Install dependencies:
    ```bash
    npm i
    ```
2. Start the development server:
    ```bash
    npm run dev
    ```
    The app will be available at `http://localhost:3000`.
