import pika
from pika.exceptions import ConnectionClosed
import backoff
import configparser

config = configparser.ConfigParser()
config.read('../Config/project_settings.ini')


# TODO get from config
class Sender:
    USER = config['RabbitMQ']['user']
    PASSWORD = config['RabbitMQ']['password']
    HOST = config['RabbitMQ']['host']
    PORT = config['RabbitMQ']['port']

    def __init__(self, queue_name):
        self.queue = queue_name
        self.key = queue_name
        self._connect()

    def _connect(self):
        self.credentials = pika.PlainCredentials(self.USER, self.PASSWORD)
        self.parameters = pika.ConnectionParameters(host=self.HOST, port=self.PORT)  # , credentials=self.credentials)
        self.connection = pika.BlockingConnection(parameters=self.parameters)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue, durable=True)

    @backoff.on_exception(backoff.expo, ConnectionClosed, max_tries=5)
    def send(self, body):
        try:
            self.channel.basic_publish(
                exchange='', routing_key=self.key, body=body,
                properties=pika.BasicProperties(delivery_mode=2, )
            )
            print('message sent')
            self.connection.close()
        except ConnectionClosed:
            self._connect()
            raise ConnectionClosed


class Receiver(Sender):
    def __init__(self, queue_name):
        super().__init__(queue_name)

    def consume(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue, on_message_callback=callback)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
        except (pika.exceptions.AMQPChannelError, pika.exceptions.ConnectionClosed) as e:
            print(e)
            exit(1)
