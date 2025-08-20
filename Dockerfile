########################  base image & metadata  ########################
FROM python:3.11-slim AS base
LABEL maintainer="padityashukla26@gmail.com"

########################  system packages  ##############################
# (install only what you really need – gcc is shown as an example)
RUN apt-get update && apt-get install -y \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

########################  python deps (builder)  ########################
FROM base AS builder
WORKDIR /build
# copy files that declare dependencies first to leverage Docker cache
COPY requirements.txt setup.py pyproject.toml* poetry.lock* ./
RUN pip install --upgrade pip \
 && pip wheel --wheel-dir /wheels -r requirements.txt

########################  runtime image  ################################
FROM base
WORKDIR /app

# copy python wheels from builder stage and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --find-links=/wheels --no-index /wheels/*.whl

# copy source code and static/templates
COPY . .

########################  container config  #############################
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE ${PORT}

# FastAPI + Uvicorn serves both API and UI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
