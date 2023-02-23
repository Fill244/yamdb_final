import csv
import logging
from logging.handlers import TimedRotatingFileHandler

from django.apps import apps
from django.core.management.base import BaseCommand

from api.management.commands._exceptions import AttrException

file_log = TimedRotatingFileHandler(
    filename='csv_to_db_log.log', when='midnight', interval=30, backupCount=7)
stream_log = logging.StreamHandler()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=(stream_log, file_log),)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creating model objects according the file path specified'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help="file path")
        parser.add_argument('--model_name', type=str, help="model name")
        parser.add_argument(
            '--app_name', type=str,
            help="django app name that the model is connected to")

    def handle(self, *args, **options):
        file_path = None

        try:
            for key in ('path', 'app_name', 'model_name'):
                if not options[key]:
                    raise AttrException(f'нет ключа --{key}')

            file_path = options['path']
            _model = apps.get_model(options['app_name'], options['model_name'])

            with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
                reader = csv.reader(csv_file, delimiter=',', quotechar='"')
                head = next(reader)
                logger.info(f'пишем в поля - {head} таблицы {_model.__name__}'
                            f' приложения {options["app_name"]}')

                for row in reader:
                    _object_dict = {}
                    for i in range(len(head)):
                        if head[i] in ('author', 'category',
                                       'genre', 'review'):
                            _object_dict[head[i] + '_id'] = int(row[i])
                        else:
                            _object_dict[head[i]] = row[i]
                    _model.objects.get_or_create(**_object_dict)
                logger.info('файл успешно сохранён в базе данных')

        except FileNotFoundError as err:
            file_name = "".join(file_path.split('/')[-1])
            logger.error(err)
            logger.debug(f'проверьте наличие файла "{file_name}"'
                         f' в папке static/data')

        except LookupError as err:
            logger.error(err)
            logger.debug(f'в приложении "{options["app_name"]}"'
                         f' нет модели "{options["model_name"]}"')

        except AttrException as err:
            logger.error(f'для работы программы нужны все три ключа: {err}')
            logger.debug('передайте все три ключа "--path", "--app_name",'
                         ' "--model_name" в параметры')
