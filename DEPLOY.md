# Deploy Simpantun

Frontend on Vercel (static), backend on Google Cloud Run (container). They are
separate origins, so the frontend is built with `VITE_API_BASE` pointing at the
Cloud Run URL, and the backend allows that origin via `ALLOWED_ORIGINS`.

Google Cloud project: **`pantun`**.

## 1. Backend: Cloud Run

### One-time setup

The gcloud CLI is not installed on this machine yet. After installing it:

```bash
gcloud auth login
gcloud config set project pantun

gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com
```

Cloud Run needs a billing account attached even though the usage below stays
inside the perpetual free tier.

### Check what is already deployed

A service already exists in this project and has been going down intermittently.
Before redeploying, confirm what it is currently configured with — the most
likely cause is the 512MiB default memory, which OOM-kills the container while
the ~2GB of CLIP + EasyOCR weights load.

```bash
gcloud run services list --project pantun

gcloud run services describe <SERVICE> --region <REGION> --project pantun \
  --format="value(spec.template.spec.containers[0].resources.limits)"
```

To confirm an OOM rather than a timeout, look for "Memory limit of ... exceeded":

```bash
gcloud logging read \
  'resource.type=cloud_run_revision AND severity>=WARNING' \
  --project pantun --limit 50 --format="value(textPayload)"
```

### Deploy

Run from the repository root. `--source .` builds the Dockerfile on Cloud Build,
so a local Docker daemon is not needed.

```bash
gcloud run deploy simpantun-api \
  --source . \
  --project pantun \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --cpu-boost \
  --timeout 300 \
  --concurrency 4 \
  --min-instances 0 \
  --max-instances 2
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
- **`--max-instances 2`** — caps how fast the free tier can be burned. Uploads
  are no longer stored server-side, so instances no longer need to be pinned
  to one.
- **`--min-instances 0`** — scales to zero when idle, so quota is only spent on
  real traffic. The cost is a cold start (~1.5 min) on the first request after
  idling.

The first build is slow: it bakes the model weights into the image so later cold
starts do not re-download ~2GB.

### Free tier

Cloud Run's free allowance renews monthly and does not expire: 2 million
requests, 360,000 GiB-seconds, 180,000 vCPU-seconds. At 4GiB and 2 vCPU that is
roughly **25 hours of active instance time per month** — memory is the binding
limit (360,000 / 4). Because the service scales to zero, idle time costs nothing.

Two allowances are much smaller and worth watching:

- **Artifact Registry: 0.5GB free.** This image is several GB (PyTorch plus
  baked-in model weights), and every deploy pushes a new one. Set a cleanup
  policy to keep only the most recent versions, or storage cost creeps up.
- **Free egress is North America only.** In `asia-southeast1` outbound bytes are
  billable. Responses here are small JSON, which is why the API no longer echoes
  uploaded images back to the client.

### Lock CORS to the frontend

After the Vercel domain exists:

```bash
gcloud run services update simpantun-api \
  --region asia-southeast1 --project pantun \
  --set-env-vars ALLOWED_ORIGINS=https://<your-app>.vercel.app
```

Leaving it unset defaults to `*` (see `app/__init__.py`), which is fine while
testing but should be narrowed before sharing the link.

## 2. Frontend: Vercel

The Vercel project `simpantun` exists but its GitHub link failed to attach. In
the dashboard: Settings -> Git -> Connect Git Repository -> `Hfzuddin/Simpantun`.
If the repo is not listed, install the Vercel GitHub App for the `Hfzuddin`
account first.

Then Settings -> Environment Variables:

```
VITE_API_BASE = https://simpantun-api-<hash>-<region>.a.run.app
```

No trailing slash. Vite inlines this at **build** time, so set it before
deploying, and redeploy after any change to it.

`vercel.json` already builds `frontend/` into `dist/` and rewrites SPA routes to
`index.html`.

## 3. Optional: deploy both halves on every push

Vercel already rebuilds on each push once the repo is linked. For Cloud Run, use
the service's "Set up continuous deployment" wizard in the console (it installs
the Cloud Build GitHub App, which needs a browser).

Add path filters so one side does not rebuild for the other's changes:

- Cloud Build trigger:
  `--included-files="app/**,dataset/**,Dockerfile,requirements.txt,config.py,run.py"`
- Vercel, Settings -> Git -> Ignored Build Step:
  `git diff --quiet HEAD^ HEAD -- frontend/ vercel.json`

Cloud Build's free tier is 2,500 build-minutes per month; this image takes
roughly 15-20 minutes to build, so unfiltered triggers would waste it quickly.
