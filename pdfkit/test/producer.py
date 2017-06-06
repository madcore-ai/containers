from kafka import KafkaProducer
from kafka.errors import KafkaError

def send(data):
    print(data)
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

    # Asynchronous by default
    future = producer.send('pdf-generate-result',data)

    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError:
        pass

    # print (record_metadata.topic)
    # print (record_metadata.partition)
    # print (record_metadata.offset)
