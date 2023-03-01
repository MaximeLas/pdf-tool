import os
import requests

from bs4 import BeautifulSoup

from pdfminer.high_level import extract_text

from logger import logger
from helpers import (
    get_files_in_dir,
    get_abs_path,
    is_txt_file_present_for_pdf,
    is_pdf,
    get_file_name_from_path_or_url,
    get_base_url_from_url
)


def delete_all_pdf_or_txt_files_in_dir(dir: str) -> None:
    if dir and not os.path.isdir(dir):
        return

    files_to_delete = [file for file in get_files_in_dir(dir) if file.endswith(('.pdf', '.txt'))]

    for file_name in files_to_delete:
        os.remove(os.path.join(dir, file_name))
        logger.debug(f'Deleted {file_name}\n')
    
    logger.info(f'✅ Deleted {len(files_to_delete)} files in {get_abs_path(dir)}\n')


def create_txt_file_from_pdf(path_pdf: str) -> bool:
    try:
        text = extract_text(path_pdf)
        path_txt = path_pdf.replace('.pdf','.txt')

        output_file = open(path_txt, 'w')
        output_file.write(text)
        output_file.close()

        logger.debug(f'Created TXT file -> {path_txt}\n')
    except Exception as e:
        file_name = get_file_name_from_path_or_url(path_pdf)

        logger.warning(f'❗ Caught exception {e=} when trying to convert {file_name}\n')
        return False
    
    return True


def convert_all_pdfs_to_txt_in_dir(dir: str) -> None:
    logger.info(f'❥ Converting all PDF files to TXT files in {get_abs_path(dir)}\n')

    success_count = fail_count = 0

    for count, file_name in enumerate(get_files_in_dir(dir)):
        logger.debug(f'({count}) Converting {file_name} to TXT')

        path = os.path.join(dir, file_name)

        if not is_pdf(path):
            logger.debug('Skipping because the file is not a PDF\n')
        elif is_txt_file_present_for_pdf(path):
            logger.debug('Skipping because a TXT file already exists for the PDF\n')
        elif create_txt_file_from_pdf(path):
            success_count += 1
        else:
            fail_count +=1

    if fail_count > 0:
        logger.info(f'❌ Unsuccessfully converted {fail_count} PDF file(s) to TXT files')

    logger.info(f'✅ Successfully converted {success_count} PDF file(s) to TXT files\n')


def download_all_pdfs_from_url(url: str, dst_dir: str) -> None:
    logger.info(f'❥ Downloading all PDFs from {url} in {get_abs_path(dst_dir)}\n')

    # Requests URL and get response object
    response = requests.get(url)
    
    # Parse text obtained
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all hyperlinks present on webpage
    links = soup.find_all('a')
    
    # Get base URL to prepend any relative URL we may have to deal with
    base_url = get_base_url_from_url(url)

    # Create directory if needed
    if len(links) > 0 and dst_dir:
        os.makedirs(dst_dir, exist_ok=True)

    # Get all pdf links
    pdf_links = [link for link in links if '.pdf' in link.get('href', [])]

    success_count = fail_count = 0

    for count, link in enumerate(pdf_links):
        try:
            # Get response object for link
            pdf_url: str = link.get('href')
            logger.debug(f'({count}) Downloading PDF from {pdf_url}')

            # Prepend base URL if needed
            is_relative_url = 'https://' not in pdf_url
            if is_relative_url:
                pdf_url = os.path.join(base_url, pdf_url)
                logger.debug(f'Absolute URL: {pdf_url}')

            # Get path for new pdf file
            file_name_pdf = get_file_name_from_path_or_url(pdf_url)
            path_pdf = os.path.join(dst_dir or '', file_name_pdf)

            # Skip if pdf already exists in destination
            if os.path.isfile(path_pdf):
                logger.debug(f'Skip as file already exists in {path_pdf}\n')
                continue

            response = requests.get(pdf_url)

            if not response.ok:
                logger.warning(f'❗ Skipping due to getting error code {response.status_code} for {pdf_url}\n')
                fail_count += 1
                continue

            # Write content in pdf file
            pdf = open(path_pdf, 'wb')
            pdf.write(response.content)
            pdf.close()

            logger.debug(f'File downloaded -> {path_pdf}\n')
            success_count += 1
        except Exception as e:
            logger.warning(f'❗ Caught exception {e=} when trying to download file {count} from {link}\n')
            fail_count += 1
    
    if fail_count > 0:
        logger.info(f'❌ Unsucessfully downloaded {fail_count} PDF file(s)')

    logger.info(f'✅ Successfully downloaded {success_count} PDF file(s)\n')
