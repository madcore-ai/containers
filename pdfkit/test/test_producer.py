from kafka import KafkaConsumer

consumer = KafkaConsumer("pdf-generate-result")

for msg in consumer:
    value = msg.value
    import base64, os
    with open(os.path.expanduser('test.pdf'), 'wb') as fout:
         fout.write(base64.decodestring(value))