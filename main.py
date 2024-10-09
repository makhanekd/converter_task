from genericpath import isdir
from os import scandir
from time import sleep
from typing import Generator, Literal, cast

from loguru import logger
from PIL import Image, UnidentifiedImageError
from result import Err, Ok, Result
from tqdm import tqdm

PathDir = str
PathFile = str


class ConvertImage:
    def __init__(
        self,
        source_format: Literal['png'],
        target_format: Literal['jpeg'],
        type_cycle: Literal['recursive', 'generator'],
    ) -> None:
        self.source_format = source_format
        self.target_format = target_format
        self.type_cycle = type_cycle

    def run(self, path_dir: PathDir) -> None:
        match self._check_dir(path_dir):
            case Ok(path_dir):
                self.choice_type_cycle(path_dir)
            case Err(e):
                logger.error(e)
                return

    def choice_type_cycle(self, path_dir: PathDir) -> None:
        match self.type_cycle:
            case 'recursive':
                self._run_convert(path_dir)
            case 'generator':
                self._run_convert_generator(path_dir)

    def _run_convert(self, path_dir: PathDir) -> None:
        files = self._get_files_recursive(path_dir)
        with tqdm(files) as t:
            for file in t:
                t.set_description(f'Start converting  {file}')
                sleep(1)
                t.write(f'Start converting {file}')

                match self._convert(file):
                    case Ok(file):
                        t.set_description(f'File {file} converted')
                        sleep(1)
                        t.write(f'File {file} converted')
                    case Err(file):
                        t.set_description(f'File {file} not converted')
                        sleep(1)
                        t.write(f'File {file} not converted')

    def _run_convert_generator(self, path_dir: PathDir) -> None:
        for file in self._get_files_recursive_generator(path_dir):
            logger.info(f'Start converting {file}')
            sleep(1)

            match self._convert(file):
                case Ok(file):
                    logger.info(f'File {file} converted')
                    sleep(1)
                case Err(file):
                    logger.warning(f'File {file} not converted')
                    sleep(1)

    def _check_dir(self, path_dir) -> Result[PathDir, str]:
        if not path_dir:
            return Err('Path is empty')
        if not isdir(path_dir):
            return Err(f'Path {path_dir} is not a directory or does not exist')
        return Ok(path_dir)

    def _get_files_recursive(self, path_dir: PathDir) -> list[PathFile]:
        files = []
        for entry in scandir(path_dir):
            if entry.is_file() and entry.name.endswith(self.source_format):
                files.append(entry.path)
            elif entry.is_dir():
                files.extend(self._get_files_recursive(entry.path))
        return files

    def _get_files_recursive_generator(self, path_dir: PathDir) -> Generator[str, None, None]:
        for entry in scandir(path_dir):
            if entry.is_file() and entry.name.endswith(self.source_format):
                yield entry.path
            elif entry.is_dir():
                yield from self._get_files_recursive_generator(entry.path)

    def _convert(self, file: PathFile) -> Result[PathFile, str]:
        try:
            im = Image.open(file)
            im = im.convert('RGB')
            im.save(file.replace(self.source_format, self.target_format))
            return Ok(file)
        except UnidentifiedImageError:
            logger.warning(f'File {file} is not an image')
            return Err(file)
        except FileNotFoundError:
            logger.warning(f'File {file} deleted or moved while converting')
            return Err(file)


def main():
    while True:
        type_cycle = input('Enter type cycle (recursive/generator) or 1 for exit: ')
        if type_cycle in ['recursive', 'generator']:
            while True:
                input_text = input('Enter path or 1 for exit: ')
                if input_text == '1':
                    break
                else:
                    converter = ConvertImage('png', 'jpeg', cast(Literal['recursive', 'generator'], type_cycle))
                    converter.run(input_text)
        elif type_cycle == '1':
            break
        else:
            logger.error('Wrong type cycle')


if __name__ == '__main__':
    main()
