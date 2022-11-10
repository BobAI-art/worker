FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-runtime AS base

RUN apt-get update && apt-get install git unzip curl vim tmux -y
# RUN apt-get update && apt-get install git openssh-server unzip curl vim tmux -y

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN apt-get install -y openssh-server
WORKDIR /app

RUN curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.17.7-linux-x86_64.tar.gz  \
    && tar xzvf filebeat-7.17.7-linux-x86_64.tar.gz \
    && mv filebeat-7.17.7-linux-x86_64/filebeat /app/filebeat \
    && rm -rf filebeat-7.17.7-linux-x86_64.tar.gz filebeat-7.17.7-linux-x86_64

ADD . /app
RUN ./docker/setup.sh
EXPOSE 22



ADD ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
# tmux new-session -d -s main && tmux attach-session -t main
# new-session -d -s main && tmux send-keys -t main 'python3 main.py' C-m && tmux attach-session -t main
