#!/usr/bin/env bash

cat << EOF >> ~/.bashrc
if [[ \$- =~ i ]] && [[ -z "\$TMUX" ]] && [[ -n "\$SSH_TTY" ]]; then
  tmux attach-session -t main || tmux new-session -s main
fi
EOF

mkdir -p ~/.ssh
cat << EOF > ~/.ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPckpVf+6azCAnMcuCSw4Ag4PQvxOFdu/bLNRiDxXgHOmVLzmKjJ3WbUUNkLxHKgEzidgI1oHOgd+Z7F4IopdVgOodhppPNSk8/SIF87soMLh36zVh3rCoWln4YQtNXIislSRrVTc8Q78sHCs4KYm7a9Lt2LI+TfkXIfbCemFDOGz3bVV9SPinMEhLSGcJ6TRRK0kbwJ05fq4dWeDtgz1AecuuDs2CktcYC6dpP7D6FSjgMtF//iAFvQhKFJo0PuWmqojcZAS9vcohVqlJjZZymzakA7JqKR1hYMZxMUZY+Nv0skhO6FOQuzp9cuO6K4yrD/jqC6EvAOpui30scaof damian@swistowski.org
EOF
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
