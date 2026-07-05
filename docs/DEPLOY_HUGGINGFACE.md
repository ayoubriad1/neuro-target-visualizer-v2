# Deploying to Hugging Face Spaces (free, permanent)

This is the recommended free deployment path for this app. It requires
creating **one free Hugging Face account** — there is no genuinely free,
permanent, zero-account way to host a Python/Streamlit app on the public
internet (static-site hosts like Netlify/GitHub Pages can't run a Python
backend; every host that can run one requires at least an email signup).
The repo is already configured for it — the steps below are just the
account + push part I can't do on your behalf.

## What you get

- A permanent public URL: `https://huggingface.co/spaces/<your-username>/<space-name>`
  (and a direct app URL like `https://<your-username>-<space-name>.hf.space`).
- Runs unattended — your own computer does not need to stay on.
- Free "CPU basic" tier: enough for this app (no GPU needed), but it **sleeps
  after a period of inactivity** and takes ~30-60s to wake up on the next
  visit (cold start). This is a Hugging Face free-tier limitation, not
  something this repo can avoid.
- The AI Interpretation feature works exactly as it does locally: every
  visitor pastes their **own** Claude/ChatGPT API key in the sidebar. You are
  never billed for anyone else's usage of that feature.

## 1. Create a free Hugging Face account

Go to <https://huggingface.co/join> and sign up (email, or GitHub/Google
OAuth). No payment information is requested for the free tier.

## 2. Create a new Space

1. Go to <https://huggingface.co/new-space>.
2. **Space name**: anything, e.g. `neuroviz-v2`.
3. **License**: MIT (matches this repo's `LICENSE` file).
4. **Select the Space SDK**: **Docker** → **Blank** template (this repo already
   has its own `Dockerfile`, so skip any pre-made Docker template).
5. **Space hardware**: "CPU basic" (free).
6. **Visibility**: Public (required for a shareable link with no login).
7. Click **Create Space**. You'll land on an empty repo page at
   `https://huggingface.co/spaces/<your-username>/<space-name>`.

## 3. Push this repo's code to the Space

Hugging Face Spaces are git repos. From your local clone of `neuroviz-v2`:

```bash
git remote add hf https://huggingface.co/spaces/<your-username>/<space-name>
git push hf main
```

Git will prompt for credentials. Use your Hugging Face username, and for the
password, an **access token** (not your account password):

1. Go to <https://huggingface.co/settings/tokens>.
2. Create a new token with **Write** access.
3. Paste it as the password when `git push` prompts for one (or configure a
   credential helper so you don't have to paste it every time).

## 4. Wait for the build

Hugging Face automatically builds the `Dockerfile` on push. Watch progress
under the **"Logs"** tab of your Space page. First build takes a while
(installing nilearn/scipy/matplotlib/plotly — budget 5-10 minutes). Subsequent
pushes rebuild faster thanks to Docker layer caching.

Hugging Face Spaces' build environment blocks network access during the build
itself, so the `Dockerfile`'s best-effort pre-download of brain-surface
meshes/atlas data is skipped there (it doesn't fail the build - see the
Dockerfile's comment). That download simply happens on the **first real
visitor's request** instead, adding a one-time delay to that first render
(subsequent renders and visitors are fast, same as running locally).

Once the build finishes, the app is live at your Space's URL — no further
action needed, and no login required for anyone visiting that link.

## 5. Updating the deployed app later

Any time you push new commits to `hf main`, the Space rebuilds and redeploys
automatically:

```bash
git push hf main
```

## Troubleshooting

- **Build fails on `pip install`** — check the "Logs" tab for the exact
  package/version that failed; Hugging Face's build environment is standard
  `python:3.11-slim`-based like this repo's `Dockerfile`, so a local
  `docker build .` reproducing the same error is the fastest way to debug.
- **App loads but shows a blank/error page** — check the "Logs" tab for a
  Python traceback; this is the same container as `docker compose up --build`
  locally, so reproducing locally first is usually faster than iterating on
  the Space directly.
- **Space is asleep (slow first load)** — expected on the free tier after
  inactivity; the next visitor's request wakes it, no action needed.
- **Build fails with a "cache miss" message on the mesh/atlas pre-warm step**
  — this is expected and handled: that `RUN` step is allowed to fail (Hugging
  Face's build sandbox has no network access), and the build continues. If the
  build still fails there, check the "Logs" tab for the actual error above the
  cache-miss line; it usually points to a real dependency or syntax problem
  instead.
