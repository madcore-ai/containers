from kafka import KafkaConsumer
consumer = KafkaConsumer(bootstrap_servers='kafka-kf.kafka.svc.cluster.local:9092',auto_offset_reset='earliest')
consumer.subscribe(['test'])
for message in consumer:
    print (message)
