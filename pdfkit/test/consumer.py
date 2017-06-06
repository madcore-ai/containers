from kafka import KafkaConsumer
import pdfkit
import pdfkit.test.render

consumer = KafkaConsumer("pdf-generate-request")

for msg in consumer:
    value = msg.value
    # data = json.loads(value)
    pdfkit.test.render.render(value)

