from kafka import KafkaConsumer
import json
from jinja2 import Environment, FileSystemLoader
from chart.datetimechart import DateTimeChart
import pdfkit
import render

consumer = KafkaConsumer("pdf-generate-request")

for msg in consumer:
    value = msg.value
    # data = json.loads(value)
    render.render(value)

