# Deploy Simpantun

Frontend on Vercel (static), backend on Google Cloud Run (container).
They are separate origins, so the frontend is built with `VITE_API_BASE`
pointing at the Cloud Run URL, and the backend allows that origin via
`ALLOWED_ORIGINS`.

## 1. Backend: Cloud Run

### One-time setup

Install the gcloud CLI (it is not currently on this machine), then:

```bash
gcloud auth login
gcloud projects create simpantun-api --name="Simpantun"   # or reuse an existing project
gcloud config set project simpantun-api
```

Cloud Run needs a billing account attached, even though the usage below stays
inside the perpetual free tier. Attach one in the console under Billing.

Enable the APIs the source-based deploy uses:

```bash
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com
```

### Deploy

Run from the repository root. `--source .` builds the Dockerfile on Cloud
Build, so a local Docker daemon is not needed.

```bash
gcloud run deploy simpantun-api \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --cpu-boost \
  --timeout 300 \
  --concurrency 4 \
  --min-instances 0 \
  --max-instances 1
```

Why these values:

- **`--memory 4Gi`** — one gunicorn worker loads ~2GB of CLIP + EasyOCR
  weights. Cloud Run's 512MiB default OOM-kills the container during model
  loading, which looks like a server that randomly dies.
- **`--cpu 2` / `--cpu-boost`** — model loading is CPU-bound and measured at
  ~82s. Boost gives extra CPU during startup so the first request is not lost.
- **`--concurrency 4`** — matches `--threads 4` in the Dockerfile's gunicorn
  command. Higher would stack simultaneous OCR/CLIP inference on one instance
  and risk memory spikes.
- **`--max-instances 1`** — see the uploads caveat below. It also caps how
  fast the free tier can be burned.
- **`--min-instances 0`** — scales to zero when idle, so quota is only spent
  on real traffic. The cost is a cold start (~1.5 min) on the first request
  after idling.

The first build is slow: it bakes the model weights into the image so later
cold starts do not re-download ~2GB.

### Free tier

Cloud Run's free allowance renews monthly and does not expire: 2 million
requests, 360,000 GiB-seconds, 180,000 vCPU-seconds. At 4GiB and 2 vCPU that
works out to roughly **25 hours of active instance time per month** — memory
is the binding limit (360,000 / 4). Because the service scales to zero, idle
time costs nothing. Note the free egress allowance is North America only, so
in `asia-southeast1` outbound bytes are billable; responses here are small
JSON, so this is cents at most, but avoid echoing images back in responses.

To trade cold-start comfort for more hours, `--memory 2Gi --cpu 1` doubles the
allowance to ~50 hours, but leaves very little headroom above the ~2GB model
footprint.

### Lock CORS to the frontend

After the Vercel domain exists:

```bash
gcloud run services update simpantun-api \
  --region asia-southeast1 \
  --set-env-vars ALLOWED_ORIGINS=https://<your-app>.vercel.app
```

Leaving it unset defaults to `*` (see `app/__init__.py`), which is fine while
testing but should be narrowed before sharing the link.

## 2. Frontend: Vercel

The Vercel project `simpantun` exists but its GitHub link failed to attach.
In the Vercel dashboard: Settings -> Git -> Connect Git Repository ->
`Hfzuddin/Simpantun`. If the repo is not listed, install the Vercel GitHub App
for the `Hfzuddin` account first.

Then Settings -> Environment Variables:

```
VITE_API_BASE = https://simpantun-api-<hash>-<region>.a.run.app
```

No trailing slash. Vite inlines this at **build** time, so set it before
deploying, and redeploy after any change to it.

`vercel.json` already builds `frontend/` into `dist/` and rewrites SPA routes
to `index.html`.

## Known issue: uploaded images are stored in memory

`app/routes.py` writes each uploaded image into the container filesystem and
returns a URL pointing back at the service. On Cloud Run that filesystem is
in-memory and nothing ever deletes those files, so memory grows with every
image analysed until the instance is OOM-killed. Files also vanish when an
instance recycles, and are invisible to any other instance — hence
`--max-instances 1` above as a stopgap.

The write is not actually needed: `process_pipeline` is handed the base64
image directly, and the frontend already holds the same image in its
`preview` state. Dropping the write and having `ResultPage` render the local
preview removes the memory growth, the 404s and the extra egress at once.
