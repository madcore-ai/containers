from kafka import KafkaProducer
#oducer = KafkaProducer(bootstrap_servers='kafka-kf.kafka.svc.cluster.local:9092')
producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('test', 'hello')
