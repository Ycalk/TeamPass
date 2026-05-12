#!/bin/sh

# 1. Подставляем переменные в шаблон S3
sed -e "s/\${S3_ACCESS_KEY}/${S3_ACCESS_KEY}/g" \
    -e "s/\${S3_SECRET_KEY}/${S3_SECRET_KEY}/g" \
    /template.json > /tmp/s3.json

(
  while ! wget -q -O /dev/null http://127.0.0.1:9333/; do
    sleep 1
  done

  if [ -n "${S3_BUCKET_NAME}" ]; then
    echo "s3.bucket.create -name ${S3_BUCKET_NAME}" | /usr/bin/weed shell -master=127.0.0.1:9333
  fi
) &

exec /usr/bin/weed server -dir=/data -s3 -s3.port=8333 -s3.config=/tmp/s3.json