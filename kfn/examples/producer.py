from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='kafka-kf.kafka.svc.cluster.local:9092')
producer.send('test', 'hello')
