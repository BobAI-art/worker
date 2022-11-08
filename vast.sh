function vast-search() {
  vast search offers 'disk_space > 59' 'inet_down > 30' 'inet_up > 30' 'gpu_ram > 23.9' 'verified = true' 'rentable = true' 'dph_total < 1' --raw | jq ".[] | {gpu_name, dph_total, id, geolocation}"
}

function vast-create() {
  vast create instance "$1" \
    --image portraits/model-trainer:latest \
    --disk 60 \
    --login "-u $(pass portraits/DOCKER_LOGIN) -p $(pass portraits/DOCKER_PASSWORD) docker.io" \
    --env "-e AWS_ACCESS_KEY_ID=AKIA5TUL5XFHCKNSZZU3 -e AWS_SECRET_ACCESS_KEY=$(pass portraits/MODEL_STORE_BUCKET_SECRET_ACCESS_KEY) -e HUGGINGFACE_TOKEN=$(pass portraits/HUGGINGFACE_TOKEN) -e PORTRAITS_BASE_URL=https://portraits.vercel.app/ -p 22:22"
}

function vast-ssh() {
  echo "export AWS_ACCESS_KEY_ID=AKIA5TUL5XFHCKNSZZU3\nexport AWS_SECRET_ACCESS_KEY=$(pass portraits/MODEL_STORE_BUCKET_SECRET_ACCESS_KEY)\nexport HUGGINGFACE_TOKEN=$(pass portraits/HUGGINGFACE_TOKEN)\nexport PORTRAITS_BASE_URL=https://portraits.vercel.app/"
}