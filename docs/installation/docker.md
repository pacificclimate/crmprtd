# Container image (for Kestra / orchestrated tasks)

The repository ships a `Dockerfile` that packages crmprtd and all of its
console scripts into a single image. It is intended to be driven by
[Kestra](https://kestra.io/) (or any orchestrator) as a task runner: the image
does **not** pin an `ENTRYPOINT`, so a task supplies whichever sub-command it
needs to run.

## Available sub-commands

Every `[project.scripts]` entry point is on `PATH` inside the image:

| Command            | Purpose                                             |
| ------------------ | --------------------------------------------------- |
| `crmprtd_pipeline` | Download → Process for one network (the cron shape) |
| `crmprtd_download` | Download phase only (emits raw data on stdout)      |
| `crmprtd_process`  | Process phase only (Normalize → Align → Insert)     |
| `crmprtd_gulpy`    | Process helper (`gulpy_plus_plus`)                  |
| `bulk_pipeline`    | Bulk (multi-network / infill) pipeline              |
| `bulk_process`     | Bulk process phase                                  |

Splitting Download and Process into separate tasks maps directly onto the
planned Kestra decomposition of the pipeline.

## Published images

Images are built and pushed to Docker Hub automatically by the
[`docker-publish`](../../.github/workflows/docker-publish.yml) workflow on every
branch push and on semantic-version tags:

- `pcic/crmprtd:<branch-or-tag>` — every push (e.g. `pcic/crmprtd:master`, or a
  release tag `pcic/crmprtd:5.0.7`)
- `pcic/crmprtd:latest` — updated on pushes to `master`

```bash
docker pull pcic/crmprtd:latest
```

## Build

To build locally instead of pulling:

```bash
docker build -t crmprtd .
```

The build is two-stage: a builder compiles `psycopg2` and `lxml` and resolves
the locked dependency set (including the `pcic-pypi` source for `pycds`) into a
virtualenv; the runtime stage carries only that venv, the package source, and
the shared libraries (`libpq5`, `libxml2`, `libxslt1.1`).

The Python and Poetry versions are build args:

```bash
docker build --build-arg PYTHON_VERSION=3.13 --build-arg POETRY_VERSION=2.1.3 -t crmprtd .
```

## Run

A bare run prints pipeline help:

```bash
docker run --rm crmprtd
```

Invoke any sub-command by passing it as the container command:

```bash
docker run --rm crmprtd crmprtd_download -N ec ...
docker run --rm crmprtd crmprtd_process -N ec ...
```

Database credentials and auth are **not** baked into the image. Supply the
connection string and any auth file at run time, e.g.:

```bash
docker run --rm \
  -e PGPASSWORD=... \
  -v /path/to/rtd_auth.yaml:/home/crmprtd/.rtd_auth.yaml:ro \
  crmprtd crmprtd_pipeline -N ec -c "postgresql://user@host:5432/crmp"
```

## Shared working directory (Swarm / NFS)

When Download and Process run as **separate** tasks (the Kestra/Swarm shape)
they hand data off through the filesystem rather than a shell pipe:

- `crmprtd_download` writes raw downloaded data to **stdout**.
- `crmprtd_process` reads raw data from **stdin**.

So a Download task must persist its output somewhere a later Process task —
possibly on a different Swarm node — can read it. Mount a shared volume (an NFS
export, in production) into every crmprtd container and keep the raw cache and
logs on it.

**Recommended in-container mount point: `/data`.** The image pre-creates
`/data` owned by the runtime user, so a fresh named volume mounted there is
writable out of the box. Treat it as the working directory for all cross-task
artifacts (raw caches, logs). The image's default cache/log locations fall
under the user's home (`/home/crmprtd/...`), which is container-local and lost
when the task exits — always point the sub-commands at `/data` explicitly.

Decomposed handoff, sharing one volume between the two tasks:

```bash
# Download task: cache raw data onto the shared volume.
docker run --rm -v crmprtd_data:/data \
  crmprtd sh -c 'crmprtd_download -N ec --log_filename /data/ec/download.log \
    > /data/ec/raw.xml'

# Process task (later, possibly another node): read that raw data back in.
docker run --rm -v crmprtd_data:/data \
  crmprtd sh -c 'crmprtd_process -N ec --log_filename /data/ec/process.log \
    -c "postgresql://user@host:5432/crmp" < /data/ec/raw.xml'
```

The single-shot `crmprtd_pipeline` still writes a cache too; put it on `/data`
with `--cache_filename` / `--log_filename` so runs are inspectable and
re-drivable:

```bash
docker run --rm -v crmprtd_data:/data \
  crmprtd crmprtd_pipeline -N ec \
    --cache_filename /data/ec/cache.xml \
    --log_filename /data/ec/pipeline.log \
    -c "postgresql://user@host:5432/crmp"
```

> **NFS permissions:** the container runs as UID **1000** (user `crmprtd`).
> Make sure the exported directory is writable by that UID (or squash/map it
> accordingly on the NFS server), otherwise the tasks cannot write their cache
> or logs.

## Kestra usage

In a Kestra flow, reference the image and provide the sub-command as the task
`commands` (using a task runner that runs in Docker). Mount the shared `/data`
volume into each task so the Download output survives for the Process task:

```yaml
- id: download_ec
  type: io.kestra.plugin.scripts.python.Commands
  containerImage: crmprtd:latest
  taskRunner:
    type: io.kestra.plugin.scripts.runner.docker.Docker
    volumes:
      - "crmprtd_data:/data"
  commands:
    - crmprtd_download -N ec --log_filename /data/ec/download.log > /data/ec/raw.xml

- id: process_ec
  type: io.kestra.plugin.scripts.python.Commands
  containerImage: crmprtd:latest
  taskRunner:
    type: io.kestra.plugin.scripts.runner.docker.Docker
    volumes:
      - "crmprtd_data:/data"
  commands:
    - crmprtd_process -N ec --log_filename /data/ec/process.log -c "{{ secret('CRMP_DSN') }}" < /data/ec/raw.xml
```
