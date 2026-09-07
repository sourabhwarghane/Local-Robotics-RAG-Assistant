from pathlib import Path
import pymupdf
from bs4 import BeautifulSoup
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".rst",
    ".msg",
    ".html",
    ".htm",
}


def clean_text(text):
    """
    Basic text cleaning.

    Removes excessive blank lines and unnecessary spaces.
    More advanced cleaning will be added later if required.
    """

    lines = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines)


def get_category(file_path, root_folder):
    """
    Finds the main knowledge-base category from the folder structure.

    Example:
    data/raw/ros2/file.rst -> ros2
    data/raw/amr/file.docx -> amr
    """

    try:
        relative_path = file_path.relative_to(root_folder)

        if len(relative_path.parts) > 1:
            return relative_path.parts[0]

    except ValueError:
        pass

    return "unknown"


def load_pdf(file_path, root_folder):
    """
    Extract text page-by-page from a PDF.

    Keeping individual PDF pages is useful because later
    our RAG system can cite the page number.
    """

    documents = []

    pdf = pymupdf.open(file_path)

    for page_number, page in enumerate(pdf, start=1):
        text = clean_text(page.get_text())
        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": file_path.name,
                "source_path": str(file_path),
                "category": get_category(file_path, root_folder),
                "file_type": "pdf",
                "page": page_number,
            }
        )
    pdf.close()
    return documents


def load_docx(file_path, root_folder):
    """
    Extract paragraph text from a DOCX document.
    """

    document = Document(file_path)
    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    text = clean_text("\n".join(paragraphs))

    if not text:
        return []

    return [
        {
            "text": text,
            "source": file_path.name,
            "source_path": str(file_path),
            "category": get_category(file_path, root_folder),
            "file_type": "docx",
            "page": None,
        }
    ]


def load_text_file(file_path, root_folder):
    """
    Loads plain-text based formats.

    This function handles:
    .txt
    .rst
    .msg
    """

    try:
        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except Exception as error:
        print(f"Could not read {file_path.name}: {error}")
        return []

    text = clean_text(text)

    if not text:
        return []

    return [
        {
            "text": text,
            "source": file_path.name,
            "source_path": str(file_path),
            "category": get_category(file_path, root_folder),
            "file_type": file_path.suffix.lower().replace(".", ""),
            "page": None,
        }
    ]


def load_html(file_path, root_folder):
    """
    Extract visible text from downloaded HTML documentation.
    """

    try:
        html = file_path.read_text(encoding="utf-8", errors="ignore")

    except Exception as error:
        print(f"Could not read {file_path.name}: {error}")
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Remove elements that normally contain page noise.
    for element in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):
        element.decompose()

    text = soup.get_text(separator="\n")

    text = clean_text(text)

    if not text:
        return []

    return [
        {
            "text": text,
            "source": file_path.name,
            "source_path": str(file_path),
            "category": get_category(file_path, root_folder),
            "file_type": "html",
            "page": None,
        }
    ]


def load_single_file(file_path, root_folder):
    """
    Select the appropriate loader according to file extension.
    """

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path, root_folder)

    elif extension == ".docx":
        return load_docx(file_path, root_folder)

    elif extension in {".txt", ".rst", ".msg"}:
        return load_text_file(file_path, root_folder)

    elif extension in {".html", ".htm"}:
        return load_html(file_path, root_folder)

    return []


def load_documents(folder_path):
    """
    Recursively loads every supported document
    from the knowledge-base directory.
    """

    root_folder = Path(folder_path)

    documents = []

    files_found = 0

    for file_path in root_folder.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        files_found += 1

        try:
            loaded_documents = load_single_file(
                file_path,
                root_folder,
            )

            documents.extend(loaded_documents)

            print(
                f"Loaded: {file_path.name} "
                f"({len(loaded_documents)} section(s))"
            )

        except Exception as error:

            print(f"ERROR loading {file_path}: {error}")

    print()
    print(f"Supported files found : {files_found}")
    print(f"Document sections     : {len(documents)}")

    return documents
