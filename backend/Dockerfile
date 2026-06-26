FROM python:3.11-slim

WORKDIR /app

# China mirrors — without these, builds on Tencent Cloud take hours (cross-border to deb.debian.org)
RUN sed -i 's|deb.debian.org|mirrors.tencent.com|g; s|security.debian.org|mirrors.tencent.com|g' /etc/apt/sources.list.d/debian.sources

ENV PIP_INDEX_URL=https://mirrors.tencent.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.tencent.com \
    PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential libpq-dev curl libcurl4-openssl-dev     libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libdbus-1-3     libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3     libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2     libatspi2.0-0 libcups2 nodejs ffmpeg &&     rm -rf /var/lib/apt/lists/*

# d2 diagram engine (DAG layout). Used by diagram_service to render DSL→SVG.
# libcairo2 stays: Chromium (playwright) links it.
# ponytail: pinned release tarball via ghfast.top mirror (github.com blocked from
# CN build host); bundled dagre layout; upgrade path = bump version / mirror.
ARG D2_VERSION=0.7.1
RUN curl -fsSL "https://ghfast.top/https://github.com/terrastruct/d2/releases/download/v${D2_VERSION}/d2-v${D2_VERSION}-linux-amd64.tar.gz" \
    -o /tmp/d2.tgz && tar -xzf /tmp/d2.tgz -C /tmp && \
    mv /tmp/d2-v${D2_VERSION}/bin/d2 /usr/local/bin/d2 && \
    chmod +x /usr/local/bin/d2 && rm -rf /tmp/d2.tgz /tmp/d2-v* && \
    d2 --version

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m playwright install --with-deps chromium

RUN python3 -c "from markitdown import MarkItDown" 2>/dev/null ||     pip install --no-cache-dir "markitdown[all] @ git+https://github.com/microsoft/markitdown.git"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
