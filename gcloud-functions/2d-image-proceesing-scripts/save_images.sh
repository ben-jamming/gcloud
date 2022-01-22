gcloud functions deploy ocr-save \
--runtime python39 \
--trigger-topic image-data \
--entry-point save_result \
--set-env-vars "GCP_PROJECT=mchacks-339005,RESULT_BUCKET=image_labels"