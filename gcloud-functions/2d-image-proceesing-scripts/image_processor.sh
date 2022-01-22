gcloud functions deploy process_image \
--runtime python39 \
--trigger-bucket imagecollection \
--entry-point process_image \
--set-env-vars "^:^GCP_PROJECT=mchacks-339005:RESULT_TOPIC=image-data"