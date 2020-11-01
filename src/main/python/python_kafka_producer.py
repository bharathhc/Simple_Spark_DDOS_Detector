from kafka import KafkaProducer
import configparser


def send_message(kafka_producer, kafka_topic, file_path):
    """
    Reads a file and sends the content of the file to Kafka Topic
    :param kafka_producer: Kafka Producer
    :param kafka_topic: Kafka Topic
    :param file_path: Path of the file to be read
    :return:
    """
    with open(file_path, 'r') as f:
        file_list = f.readlines()

    for line in file_list:
        kafka_producer.send(kafka_topic, value=bytes(line, 'utf-8'))


config = configparser.ConfigParser()
config.read('config.ini')

# Read kafka properties from config.ini
bootstrap_server = config['KAFKA_PROPERTIES']['kafka_bootstrap_servers']
topic = config['KAFKA_PROPERTIES']['kafka_topic']
log_file_path = config['DEPENDENCIES']['log_file_path']


producer = KafkaProducer(bootstrap_servers=bootstrap_server)

# Send message to Kafka Producer
send_message(producer, topic, log_file_path)
print("Completed writing to topic", topic)
