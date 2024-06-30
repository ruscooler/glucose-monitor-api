from logging import Logger, getLogger
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser, CommandError

from glucosemonitor.levels.utils.csv_processing import process_csv_file

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help: str = "Load sample data from CSV file intro the Level mode"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "csv_file_path",
            type=Path,
            help="The path to the CSV file to be loaded",
        )
        parser.add_argument(
            "--chunk_size",
            type=int,
            default=10000,
            help="Number of rows to process in each chunk",
        )

    def handle(self, *args, **options):
        csv_file_path: Path = options['csv_file_path']
        chunk_size: int = options['chunk_size']
        user_id: str = csv_file_path.stem
        try:
            process_csv_file(csv_file_path=csv_file_path, user_id=user_id, chunk_size=chunk_size)
        except Exception as e:
            logger.error(f"Failed to import data from {csv_file_path}: {e}")
            raise CommandError(f"Failed to import data from {csv_file_path}: {e}")

        print(f"Successfully imported data from {csv_file_path}")
