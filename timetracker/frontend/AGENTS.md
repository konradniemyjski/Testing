# Agent Instructions (frontend)

- This Nuxt 3 app uses `<script setup>` with TypeScript; keep new components consistent with existing style and folder layout.
- Use Pinia stores under `frontend/stores` for shared state rather than ad-hoc global variables.
- Prefer running commands with `npm --prefix frontend <script>` from the repo root to match CI expectations.
- Avoid editing `node_modules` or generated build outputs; focus on source files under `pages`, `components`, `stores`, and `composables`.
