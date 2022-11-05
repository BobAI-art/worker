function vast-search() {
  vast search offers 'disk_space > 59' 'inet_down > 30' 'inet_up > 30' 'gpu_ram > 23.9' 'verified = true' 'rentable = true' 'dph_total < 1' --raw | jq ".[] | {gpu_name, dph_total, bundle_id}"
}