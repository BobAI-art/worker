FROM pytorch/pytorch AS base

RUN apt-get update && apt-get install git -y

ADD requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r /app/requirements.txt

FROM pytorch/pytorch
COPY --from=base /opt/conda/lib/python3.9/site-packages/ ./
ADD . /app