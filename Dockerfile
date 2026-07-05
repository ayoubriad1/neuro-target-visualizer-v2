FROM python:3.11-slim

# System deps required by nilearn/matplotlib and by headless Chrome itself
# (kaleido >=1.0 no longer bundles its own Chromium - it downloads a real
# Chrome-for-Testing build via `plotly_get_chrome` below, which needs these
# shared libraries present to actually run headless). libgconf-2-4 is
# deliberately absent: it's an obsolete GConf2 library removed from Debian
# Bookworm's repos (the base of python:3.11-slim), and headless Chrome
# doesn't need it anyway.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libnss3 \
        libfontconfig1 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libcairo2 \
        fonts-liberation \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces (and most managed container platforms) run Docker
# images as a non-root user; create one up front so nilearn's ~/nilearn_data
# cache directory is writable. Harmless for plain `docker run`/`docker compose`.
RUN useradd -m -u 1000 appuser
USER appuser
ENV HOME=/home/appuser \
    PATH=/home/appuser/.local/bin:$PATH
WORKDIR $HOME/app

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# kaleido >=1.0 requires a real Chrome install (it no longer bundles one) and
# ships this helper to fetch a compatible Chrome-for-Testing build - without
# it, any PNG export via kaleido (the "3D Surface" view) fails at runtime with
# "RuntimeError: Kaleido requires Google Chrome to be installed."
RUN plotly_get_chrome -y

COPY --chown=appuser:appuser . .

# Best-effort pre-warm of nilearn's fsaverage mesh + atlas caches at build
# time, so the first request from a researcher isn't the one paying the
# download cost (and so it works offline afterwards / behind restrictive lab
# network policies). Some managed build environments (e.g. Hugging Face
# Spaces) block network egress during the build itself, so this is allowed
# to fail without failing the whole image build - in that case, the exact
# same fetch just happens lazily on the first real request instead (the
# @st.cache_resource/@st.cache_data decorators handle that transparently).
RUN (python -c "from nilearn import datasets; datasets.fetch_surf_fsaverage('fsaverage5'); datasets.fetch_surf_fsaverage('fsaverage6')" \
    && python -c "from atlas_regions import get_region_mask; [get_region_mask(n) for n in ('Thalamus', 'Anterior Cingulate Cortex', 'Substantia Nigra')]") \
    || echo "Pre-warm skipped (no network at build time) - will fetch lazily on first request instead."

# 7860 is the conventional port for Hugging Face Spaces' Docker SDK; also
# fine for any other host (docker-compose maps it to 7860 on localhost too).
EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
