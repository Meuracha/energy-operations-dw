FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data written here should be mounted as a volume so it survives container restarts —
# see the `docker run -v` example in README.md
RUN mkdir -p /app/data/raw /app/data/processed

# Default: drop into a shell so you can run extract/transform/load scripts one at a time
# and inspect output between steps. Override with `docker run ... python extract/extract_investor.py`
# to run a specific script directly instead.
CMD ["/bin/bash"]
