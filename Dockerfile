FROM codex:5000/astral/uv:python3.12-bookworm-slim

WORKDIR /app

ENV OPENBLAS_NUM_THREADS=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_DEFAULT_INDEX=http://mirrors.aliyun.com/pypi/simple

COPY . /app

# RUN uv sync
RUN uv sync -vv \
  && rm -f .python-version \
  && rm -f pyproject.toml \
  && rm -f uv.lock

EXPOSE 8000

# CMD ["uv", "run", "fastapi", "run", "fastapi_app.py", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uv", "run", "gunicorn", "-c", "gunicorn.conf.py", "fastapi_app:app"]