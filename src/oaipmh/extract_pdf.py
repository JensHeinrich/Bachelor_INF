
from pathlib import Path
from typing import Union

import datasets

from PyPDF2 import PdfReader

# https://pypdf2.readthedocs.io/en/latest/user/suppress-warnings.html#exceptions
from pdfminer.high_level import extract_text as fallback_text_extraction


logger = datasets.utils.logging.get_logger("PdfExtractor")

def get_text_from_pdf(ft: Union[str,Path]) -> str:
    """Extract text from a pdf file

    Args:
        ft (Union[StrByteType,Path]): Path to the pdf file

    Returns:
        str: Text content of the pdf file or empty string if both extractors fail 
    """ 

    text = ""

    try:
        reader = PdfReader(ft)
        logger.info(f"Handling {ft}")

        pbar =  datasets.utils.logging.tqdm(
                reader.pages,
                unit="pages",
                # total=len(reader.pages),
                disable=not datasets.utils.logging.is_progress_bar_enabled(),
            )
        mapped = [page.extract_text() for page in pbar]
        text = "\n\n".join(mapped)

    except Exception as exc:
        logger.error(f"Error processing {ft} with pypdf2: {exc}")
    
        try:
            text = fallback_text_extraction(ft)

        except Exception as exc:
            logger.error(f"Error processing {ft} with pdfminer.six: {exc}")

    finally: # ensure the text is always returned
        return text

 