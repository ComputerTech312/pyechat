from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtNetwork import QSslSocket

from src.irc.event.event import Event
from src.irc.file_logger import Logger
import datetime

class IRCClient(QObject):
    received_message = pyqtSignal(str)

    def __init__(self, server, port, nickname, realname, channel, use_ssl=False):
        super().__init__()

        self.event = Event()

        self.socket = QSslSocket()
        self.socket.readyRead.connect(self.on_ready_read)
        self.socket.errorOccurred.connect(self.on_error_occurred)
        self.socket.connected.connect(self.start_encryption)

        self.server = server
        self.port = port
        self.nickname = nickname
        self.realname = realname
        self.channel = channel
        self.use_ssl = use_ssl

        self.logger = Logger('logs/irc_client.log')
        self.logger.info(f'Initialized IRCClient with server={server}, port={port}, nickname={nickname}, realname={realname}, channel={channel}, use_ssl={use_ssl}')

    @pyqtSlot()
    def start_encryption(self):
        pass

    def connect_to_host(self):
        if self.use_ssl and not QSslSocket.supportsSsl():
            self.logger.error("This system does not support SSL.")
            return

        self.logger.info(f'Connecting to host {self.server}:{self.port}')
        if self.use_ssl:
            self.socket.connectToHostEncrypted(self.server, self.port)
        else:
            self.socket.connectToHost(self.server, self.port)
        self.send_command(f'NICK {self.nickname}')
        self.send_command(f'USER {self.nickname} 0 * :{self.realname}')
        self.logger.info(f'Connected to host {self.server}:{self.port} with SSL={self.use_ssl}')

    def decode(self, bytes):
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try: 
                return bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        self.logger.error('None of the encodings could decode the bytes.')
        raise UnicodeDecodeError("None of the encodings could decode the bytes.")

    def parse_message(self, message):

        tags = {}
        server_time = None
        if message.startswith('@'):
            tags_str, message = message[1:].split(' ', 1)
            tags = dict(tag.split('=') for tag in tags_str.split(';'))
            if 'time' in tags:
                server_time = datetime.datetime.fromisoformat(tags['time'].replace('Z', '+00:00'))

        parts = message.split()
        if len(parts) < 2:
            return None, None, [], tags, server_time
        source = parts[0][1:] if parts[0].startswith(':') else None
        command = parts[1] if source else parts[0]
        args_start = 2 if source else 1
        args = []
        trailing_arg_start = None
        for i, part in enumerate(parts[args_start:], args_start):
            if part.startswith(':'):
                trailing_arg_start = i
                break
            else:
                args.append(part)
        if trailing_arg_start is not None:
            args.append(' '.join(parts[trailing_arg_start:])[1:])
        return source, command, args, tags, server_time

    @pyqtSlot()
    def on_ready_read(self):
        while self.socket.canReadLine():
            line = self.socket.readLine().data()
            line = self.decode(line).strip()
            self.received_message.emit(line)
            self.logger.debug(f'Received line: {line}')

            source, command, args, _, _ = self.parse_message(line)

            if command == 'NICK' and source.split('!')[0] == self.nickname:
                self.nickname = args[0]

            if command == 'PING':
                nospoof = args[0][1:] if args[0].startswith(':') else args[0]
                self.send_command(f'PONG :{nospoof}')

            elif 'End of /MOTD command.' in line:
                self.send_command(f'JOIN {self.channel}')
                self.send_command(f'NAMES {self.channel}')

    @pyqtSlot(QSslSocket.SocketError)
    def on_error_occurred(self, socket_error):
        self.logger.error(f'Error occurred on the socket: {self.socket.errorString()}')

    def send_command(self, command):
        self.logger.info(f'Sending command: {command}')
        if ' ' in command:
            cmd, args = command.split(' ', 1)
            if cmd in ['JOIN', 'PART']:
                args = args.split(' ', 1)[0]
            self.socket.write(f'{cmd} {args}\r\n'.encode())
            self.logger.info(f'Sent command: {cmd} {args}')
        else:
            self.socket.write(f'{command}\r\n'.encode())
            self.logger.info(f'Sent command: {command}')

    