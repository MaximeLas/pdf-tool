import os
import re
from urllib.parse import unquote

import logger


def get_files_in_dir(dir: str = None) -> list[str]:
    return os.listdir(dir or None)

def get_abs_path(dir: str) -> str:
    return os.path.abspath(dir)

def is_txt_file_present_for_pdf(path: str) -> bool:
    assert is_pdf(path)
    return os.path.isfile(path.replace('.pdf','.txt'))

def is_pdf(path_or_file_name: str) -> bool:
    return path_or_file_name.endswith('.pdf')

def get_file_name_from_path_or_url(url: str) -> str:
    return url if '/' not in url else unquote(url.rsplit('/',1)[1])

def get_base_url_from_url(url: str) -> str:
    try:
        return re.match('.*://[^/]*', url).group()
    except Exception as e:
        logger.warning(f'❗ Caught exception {e=} when trying to get base url of {url}\n')
        return ''
