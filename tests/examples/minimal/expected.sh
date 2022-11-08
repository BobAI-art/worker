wget https://example.com/foo-bar.jpg -O ./model-data/owner-id/model-id/photos/foo-bar.jpg
wget https://example.com/foo-bar-2.jpg -O ./model-data/owner-id/model-id/photos/foo-bar-2.jpg
python -m download_model runwayml/stable-diffusion-v1-5 v1-5-pruned-emaonly.ckpt
mkdir -p ./regularizations/Default/fetch-bar
git clone https://github.com/foo-bar.git ./regularizations/Default/fetch-bar
python -m train --base configs/stable-diffusion/v1-finetune_unfrozen.yaml -t --actual_resume /some/path --reg_data_root ./regularizations/Default/fetch-bar/samples -n model-id --gpus 0, --data_root ./model-data/owner-id/model-id/photos --max_training_steps 2020 --class_word bar --token the-subject-slug --no-test
mv ./logs/Default/fetch-stable-diffusion-regularization/model.ckpt ./model-data/owner-id/model-id/model.ckpt
aws s3 cp ./model-data/owner-id/model-id/model.ckpt s3://portraits-model-store/model-data/owner-id/model-id/model.ckpt --no-progress --region eu-west-2
rm -rf ./logs