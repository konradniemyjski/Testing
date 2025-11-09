# Worklog Nuxt frontend

This directory contains the Vue 3 + Nuxt 3 rewrite of the Worklog interface. It integrates with the FastAPI backend and provides authentication, project management, and time tracking views.

## Local development

```bash
npm install
npm run dev
```

The development server runs on `http://localhost:3000` by default. Update the backend URL with the `NUXT_PUBLIC_API_BASE` environment variable if needed.

## Production build

```bash
npm run build
npm run preview
```

The preview command starts the built server for smoke testing before deploying.
