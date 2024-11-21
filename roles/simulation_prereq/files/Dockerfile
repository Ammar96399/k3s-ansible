FROM python:3.9-slim

WORKDIR /app

COPY sysbench_from_csv.py /app/sysbench_from_csv.py
# COPY requirements.txt /app/requirements.txt

COPY event_driven_simulation/event_driven_observatory/ /app/event_driven_observatory/

# RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    stress-ng \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python", "sysbench_from_csv.py"]
