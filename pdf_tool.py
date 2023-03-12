import argparse
import logging

from logger import set_log_level_for_console
from helpers import get_abs_path
from utilities import (
    download_all_pdfs_from_url,
    convert_all_pdfs_to_txt_in_dir,
    delete_all_pdf_or_txt_files_in_dir
)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = 'PDF Tool',
        description = 'Download PDF files present in URL and convert them to TXT files',
        epilog = '© Publico')

    parser.add_argument('url', nargs='?', help='the URL from which to download the PDF files')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-d', '--dir', action='store', default='',
                        help='the directory where the new files should be stored (default: current directory)')
    parser.add_argument('-rm', '--delete', action='store_true',
                        help='whether to delete all existing PDF & TXT files in the given directory')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    if args.interactive:
        print('\nLet me ask you a few questions and I promise I will make you happy! (◕ ‿ ◕)')

    # Example of URL -> 'https://www.nps.gov/articles/000/historic-preservation-fund-sample-grant-applications.htm'
    url = (
        input('\nWhat is the URL from which from which to download the PDF files?\n> ')
        if args.interactive else
        args.url)

    dir = (
        input('\nWhat is the directory where the new files should be stored? (default: current directory)\n> ')
        if args.interactive else
        args.dir)

    should_delete = (
        (input(f'\nDelete all existing pdf/txt files in {get_abs_path(dir)}? (yes/no)\n> ') in ['Y', 'y', 'Yes', 'yes', 'YES'])
        if args.interactive else
        args.delete)
    
    if args.verbose:
        set_log_level_for_console(logging.DEBUG)

    print('\nThanks dude, let me get to work now! ╭∩╮(･◡･)╭∩╮\n')

    if should_delete:
        delete_all_pdf_or_txt_files_in_dir(dir)

    if url:
        download_all_pdfs_from_url(url, dir)

    convert_all_pdfs_to_txt_in_dir(dir)
