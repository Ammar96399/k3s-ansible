FROM python:3.9-slim

WORKDIR /app

COPY sysbench_from_csv.py /app/sysbench_from_csv.py
# COPY requirements.txt /app/requirements.txt

COPY long_term_observatory/ /app/long_term_observatory/

# RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    stress-ng \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python", "sysbench_from_csv.py"]
