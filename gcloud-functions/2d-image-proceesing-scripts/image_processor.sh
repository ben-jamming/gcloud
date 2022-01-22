gcloud functions deploy ocr-extract \
--runtime python39 \
--trigger-bucket imagecollection \
--entry-point process_image \
--set-env-vars "^:^GCP_PROJECT=mchacks-339005:RESULT_TOPIC=image-data"