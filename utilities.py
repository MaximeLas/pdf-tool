import os
import requests

from bs4 import BeautifulSoup

from pdfminer.high_level import extract_pages, extract_text

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
    is_success = False

    try:
        text = extract_text(path_pdf)
        path_txt = path_pdf.replace('.pdf','.txt')

        output_file = open(path_txt, 'w')
        output_file.write(text)
        output_file.close()
        is_success = True
        logger.debug(f'Created TXT file -> {path_txt}\n')
    except Exception as e:
        file_name = get_file_name_from_path_or_url(path_pdf)
        logger.warning(f'❗ Caught exception {e=} when trying to convert {file_name}\n')
    
    return is_success


def convert_all_pdfs_to_txt_in_dir(dir: str) -> None:
    logger.info(f'❥ Converting all PDF files to TXT files in {get_abs_path(dir)}\n')

    corrupted: list[str] = []
    success_count = 0

    for file_name in get_files_in_dir(dir):
        logger.debug(f'File -> {file_name}')

        path = os.path.join(dir, file_name)

        if is_pdf(path) and not is_txt_file_present_for_pdf(path):
            is_success = create_txt_file_from_pdf(path)

            if is_success:
                success_count += 1
            else:
                corrupted.append(file_name)
        else:
            logger.debug(
                'Skipping because ' +
                'the given file is not a PDF\n'
                if not is_pdf(path) else
                'a TXT file already exists for the given PDF\n')

    if len(corrupted) > 0:
        logger.info(f'❌ Failed the conversion of {len(corrupted)} PDF file(s) to TXT files')

    logger.info(f'✅ Finished the conversion of {success_count} PDF file(s) to TXT files\n')


def download_all_pdfs_from_url(url: str, dst_dir: str) -> None:
    logger.info(f'❥ Downloading all PDFs from {url}\n')

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

    for count, link in enumerate(pdf_links):
        logger.debug(f'Downloading file: {count}')

        # Get response object for link
        pdf_url: str = link.get('href')
        
        # Prepend base URL if needed
        is_relative_url = 'https://' not in pdf_url
        absolute_url = base_url + pdf_url if is_relative_url else pdf_url

        logger.debug(f'URL: {absolute_url}')
        response = requests.get(absolute_url)

        # Get path for new pdf file
        file_name_pdf = get_file_name_from_path_or_url(absolute_url)
        path_pdf = os.path.join(dst_dir or '', file_name_pdf)

        # Write content in pdf file
        pdf = open(path_pdf, 'wb')
        pdf.write(response.content)
        pdf.close()

        logger.debug(f'File {count} downloaded -> {path_pdf}\n')
    
    logger.info(f'✅ Finished the download of {len(pdf_links)} PDF file(s) in {get_abs_path(dst_dir)}\n')
