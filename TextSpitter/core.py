"""
Core application that contains the `FileExtractor` class object
"""

import logging
import mimetypes
from io import BytesIO
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import IO

from docx import Document

# --- Module-level imports for optional PDF libraries ---
try:
    import pymupdf  # type: ignore
except ImportError:
    pymupdf = None  # Will be None if not installed

try:
    import pypdf  # type: ignore
except ImportError:
    pypdf = None  # Will be None if not installed
# --- End of module-level imports ---

logger = logging.getLogger(__name__)


class FileExtractor:
    """
    Wrapper for extracting file contents to string
    """

    def __init__(
        self,
        file_obj: (
            str | Path | IO | BytesIO | SpooledTemporaryFile | bytes | None
        ) = None,  # Expanded type hint
        filename: str | None = None,
        file_attr: str = "name",
    ):
        """
        The extractor wrapper will initialize by assigning the filename to the
        object's file property; if a file-like object is provided instead of a
        name, then a file_ext arg will be required.

        `filename` is now a fallback for `file_obj.name` if `file_obj` is a
        type without a `name` attribute (e.g.: SpooledTemporaryFile). In this
        instance, the `filename` is used to determine the file extension and
        should not be a fully qualified path.

        Args:
            file_obj: str | Path | IO | BytesIO | SpooledTemporaryFile |
            bytes | None
            filename: : str | None
            file_attr: str
        """

        if filename and not file_obj:
            self.file = Path(filename)
            self.file_ext = filename.split(".")[
                -1
            ].lower()  # Standardize extension to lowercase
            self.file_name = self.file.name
        elif file_obj is not None:  # Ensure file_obj is not None
            if isinstance(file_obj, str):
                file_obj = Path(file_obj)  # Convert string path to Path object

            # Check if file_obj is a Path object or has the specified file_attr
            if isinstance(file_obj, Path):
                self.file = file_obj
                self.file_name = self.file.name
                self.file_ext = (
                    self.file.suffix[1:].lower() if self.file.suffix else ""
                )  # Get ext from Path
            elif hasattr(file_obj, file_attr) and isinstance(
                getattr(file_obj, file_attr), str
            ):
                self.file = file_obj
                f_name = getattr(file_obj, file_attr)
                self.file_name = f_name
                self.file_ext = f_name.split(".")[-1].lower()
            elif (
                filename
            ):  # Fallback to using filename if file_obj has no name attribute
                self.file = file_obj  # This could be BytesIO,
                # SpooledTemporaryFile, bytes
                self.file_name = filename
                self.file_ext = filename.split(".")[-1].lower()
            else:
                # If file_obj is a stream without a name and no filename is
                # provided
                if isinstance(file_obj, (BytesIO, SpooledTemporaryFile, bytes)):
                    raise Exception(
                        "A 'filename' with an extension is required when "
                        "'file_obj' is a stream or bytes "
                        "and does not have a usable name attribute."
                    )
                raise Exception(
                    f"Your file object (type: {type(file_obj)}) does not "
                    f"contain a usable '{file_attr}' attribute, and no "
                    f"fallback 'filename' was provided. Please provide a "
                    f"'filename' with an extension."
                )
        else:  # Neither filename nor file_obj provided
            raise ValueError(
                "Either 'file_obj' or 'filename' must be provided."
            )

    @staticmethod
    def get_file_type(
        file_name_or_path: str | Path,
    ) -> str:  # Added return type hint
        """
        A static method that guesses the mime type for a given file object.
        The return value is taken from the sliced value from
        `mimetypes.guess_type`
        Args:
            file_name_or_path: str | Path

        Returns:
            str: The subtype of the mime type (e.g., 'pdf',
            'vnd.openxmlformats-officedocument.wordprocessingml.document')
        """
        mime_type, _ = mimetypes.guess_type(
            str(file_name_or_path)
        )  # Ensure it's a string for guess_type
        if mime_type:
            return mime_type.split("/")[1]
        # Fallback if mimetypes can't guess, rely on extension (already in
        # self.file_ext)
        if isinstance(file_name_or_path, Path):
            ext = file_name_or_path.suffix[1:].lower()
        else:  # str
            ext = str(file_name_or_path).split(".")[-1].lower()

        # Map common extensions to mime subtypes if mimetypes fails
        ext_to_mime_subtype = {
            "docx": "vnd.openxmlformats-officedocument.wordprocessingml"
            ".document",
            "pdf": "pdf",
            "txt": "plain",
            "csv": "csv",
            # Add programming language mappings
            "py": "x-python",
            "js": "javascript",
            "java": "x-java-source",
            "c": "x-c",
            "cpp": "x-c++",
            "html": "html",
            "css": "css",
            "json": "json",
            "xml": "xml",
        }
        return ext_to_mime_subtype.get(
            ext, "octet-stream"
        )  # Default to octet-stream

    @staticmethod
    def is_programming_language_file(file_ext: str) -> bool:
        """
        Check if the file extension corresponds to a programming language file.

        Args:
            file_ext: File extension (without dot)

        Returns:
            bool: True if it's a programming language file
        """
        programming_extensions = {
            "py",
            "js",
            "ts",
            "java",
            "cpp",
            "c",
            "h",
            "hpp",
            "cs",
            "php",
            "rb",
            "go",
            "rs",
            "swift",
            "kt",
            "scala",
            "r",
            "sql",
            "sh",
            "bash",
            "zsh",
            "ps1",
            "bat",
            "cmd",
            "html",
            "htm",
            "css",
            "scss",
            "sass",
            "less",
            "xml",
            "json",
            "yaml",
            "yml",
            "toml",
            "ini",
            "cfg",
            "conf",
            "md",
            "rst",
            "tex",
            "latex",
            "vue",
            "jsx",
            "tsx",
            "dart",
            "pl",
            "pm",
            "lua",
            "vim",
            "asm",
            "s",
            "f",
            "f90",
            "f95",
            "cob",
            "cobol",
            "pas",
            "pp",
            "ml",
            "fs",
            "fsx",
            "elm",
            "clj",
            "cljs",
            "ex",
            "exs",
            "erl",
            "hrl",
            "jl",
            "nim",
            "cr",
            "zig",
        }
        return file_ext.lower() in programming_extensions

    def get_contents(self) -> bytes:
        """
        Reads the contents from self.file and returns it as bytes.
        self.file can be a Path, or a file-like stream object (BytesIO,
        SpooledTemporaryFile), or raw bytes.
        """
        if hasattr(
            self.file, "read"
        ):  # Handles BytesIO, SpooledTemporaryFile, and other IOBase streams
            # This is a file-like object (stream)
            try:
                self.file.seek(0)  # Rewind the stream if possible
            except (
                AttributeError,
                ValueError,
                IOError,
            ):  # More specific exceptions for seek issues
                # Some streams might not support seek (e.g., if already
                # closed or certain types)
                # or it might not be necessary. Log if needed.
                # logger.debug(f"Stream {type(self.file)} does not support
                # seek or is in a state that prevents it.")
                pass

            data = self.file.read()

            if isinstance(data, str):
                # This case should be rare if streams are handled as binary,
                # but as a safeguard:
                logger.warning(
                    "Read data from stream as string, encoding to UTF-8."
                )
                return data.encode("utf-8", errors="ignore")
            elif not isinstance(data, bytes):
                raise TypeError(
                    f"Expected bytes from stream read, got {type(data)}"
                )
            return data  # Should already be bytes

        elif isinstance(self.file, Path):
            with self.file.open("rb") as f:  # Always read Path objects as bytes
                return f.read()

        elif isinstance(self.file, bytes):
            return self.file  # Already bytes

        else:
            # This path should ideally not be reached if __init__ correctly
            # sets self.file
            # or if the input types are constrained.
            raise TypeError(
                f"FileExtractor: self.file is of an unexpected type "
                f"'{type(self.file)}' and does not have a 'read' attribute, "
                f"nor is it a Path or bytes."
            )

    def code_file_read(self) -> str:
        """
        Reads contents from programming language files (.py, .js, .java, etc.)
        with enhanced encoding detection and preserves original formatting.

        Returns:
            str: The file content as a string
        """
        contents_bytes = self.get_contents()

        # Common encodings for source code files
        encodings_to_try = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings_to_try:
            try:
                content = contents_bytes.decode(encoding)
                logger.info(
                    f"Successfully decoded {self.file_name} using {encoding}"
                )
                return content
            except UnicodeDecodeError:
                continue

        # If all encodings fail, use utf-8 with replacement
        logger.warning(
            f"Could not decode code file {self.file_name} with standard "
            f"encodings, using utf-8 with replacement characters."
        )
        return contents_bytes.decode("utf-8", errors="replace")

    def pdf_file_read(self) -> str:  # Added return type hint
        """
        This current code provides a workaround in case MuPDF (a dependency
        for PyMuPDF) is not usable in the development environment. For such
        instances, the module relies on PyPDF to extract text data. However,
        because of the likelihood of white spaces being rampant in the
        extracted string data, those characters get filtered out.
        """
        contents = self.get_contents()  # This should now reliably return bytes
        text = ""  # Default to empty string

        try:
            if not pymupdf:  # Check if module-level import was successful
                raise ImportError(
                    "pymupdf module not available or import failed."
                )

            # PyMuPDF's Document constructor can take bytes directly via the
            # 'stream' argument
            with pymupdf.open(
                stream=contents, filetype="pdf"
            ) as pdf_file:  # Use with for resource management
                raw_text = [page.get_text("text") for page in pdf_file]
            text = "".join(raw_text)
        except Exception as e_pymupdf:
            logger.warning(
                f"PyMuPDF failed ({e_pymupdf}), trying PyPDF2 for PDF:"
                f" {self.file_name}"
            )
            try:
                if not pypdf:  # Check if module-level import was successful
                    raise ImportError(
                        "pypdf module not available or import failed."
                    )

                # PyPDF2 needs a stream, so wrap bytes in BytesIO
                pdf_stream = BytesIO(contents)
                pdf_reader = pypdf.PdfReader(pdf_stream)
                raw_text = [
                    page.extract_text()
                    for page in pdf_reader.pages
                    if page.extract_text()  # Ensure text is not None or empty
                ]
                text = "".join(raw_text)
            except Exception as e_pypdf:
                logger.error(
                    f"Both PyMuPDF and PyPDF2 failed for PDF "
                    f"{self.file_name}: {e_pypdf}"
                )
                # text remains "" as initialized
        return text

    def docx_file_read(self) -> str:  # Added return type hint
        """
        Reads contents from an MS Word file, extracts text data from paragraph
        objects, and then concatenates them to form a returnable string value.
        Returns:
            str
        """
        contents = self.get_contents()  # This should now reliably return bytes

        # python-docx's Document constructor needs a file-like object (stream)
        # or a path to a .docx file. We have bytes, so wrap in BytesIO.
        try:
            f_stream = BytesIO(contents)
            document = Document(f_stream)
            raw_text = [p.text for p in document.paragraphs]
            text = "\n".join(raw_text)
        except Exception as e:
            logger.error(
                f"Error reading DOCX file {self.file_name}: {e}", exc_info=True
            )
            text = ""  # Return empty string on failure
        return text

    def text_file_read(self) -> str:  # Added return type hint
        """
        Reads contents from a text file, and returns the string value

        Returns:
            str
        """
        contents_bytes = (
            self.get_contents()
        )  # This should now reliably return bytes
        try:
            # Attempt to decode as UTF-8, with fallbacks
            return contents_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return contents_bytes.decode("latin-1")
            except UnicodeDecodeError:
                logger.warning(
                    f"Could not decode text file {self.file_name} with utf-8 "
                    f"or latin-1, trying with replacement."
                )
                return contents_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            logger.error(
                f"Error reading text file {self.file_name}: {e}", exc_info=True
            )
            return ""

    def csv_file_read(
        self, newline: str | None = None
    ) -> str:  # Added return type hint
        """
        Reads contents from a CSV file, and returns the string value.
        Note: This method currently just returns the raw string content.
        Actual CSV parsing is commented out.

        Returns:
            str
        """
        contents_bytes = (
            self.get_contents()
        )  # This should now reliably return bytes
        try:
            # Attempt to decode as UTF-8, with fallbacks (common for CSV)
            return contents_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return contents_bytes.decode("latin-1")
            except UnicodeDecodeError:
                logger.warning(
                    f"Could not decode CSV file {self.file_name} with utf-8 "
                    f"or latin-1, trying with replacement."
                )
                return contents_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            logger.error(
                f"Error reading CSV file {self.file_name}: {e}", exc_info=True
            )
            return ""
