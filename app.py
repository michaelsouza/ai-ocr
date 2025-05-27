"""Mistral OCR - Convert PDF to Markdown with Ollama Fallback"""

import os
import argparse
import base64
from typing import Optional, Tuple, List, Any  # Added Any
import io  # For image bytes with Ollama if needed, not directly used with path method
import tempfile  # For temporary image files for Ollama

from dotenv import load_dotenv
from mistralai import Mistral  # Assuming this is the correct import for Mistral client
import PyPDF2
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm
from rich.syntax import Syntax

# Ollama and PDF-to-Image specific imports
try:
    import ollama
    from pdf2image import (
        convert_from_path,
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFSyntaxError,
    )

    # Pillow is a dependency of pdf2image, usually imported as PIL.Image
except ImportError:
    # This allows the script to run basic help/argument parsing even if these are missing,
    # but actual Ollama functionality will fail later with a more specific message.
    ollama = None
    convert_from_path = None
    PDFInfoNotInstalledError = PDFPageCountError = PDFSyntaxError = (
        Exception  # Placeholder
    )
    print(
        "Warning: 'ollama' or 'pdf2image' libraries not found. Ollama fallback will not be available."
        "Please install them with 'pip install ollama pdf2image Pillow' and ensure Poppler is installed."
    )


# Load environment variables from .env file
load_dotenv()


def parse_and_validate_arguments(console: Console) -> Optional[argparse.Namespace]:
    """Parses command-line arguments and validates the PDF path."""
    parser = argparse.ArgumentParser(
        description="Process a PDF file from a PDF path, with Ollama fallback."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file to be processed.")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        console.print(f"[bold red]Error:[/] The file {args.pdf_path} does not exist.")
        return None
    if not args.pdf_path.lower().endswith(".pdf"):
        console.print(f"[bold red]Error:[/] The file {args.pdf_path} is not a PDF.")
        return None
    return args


def initialize_mistral_client(console: Console) -> Optional[Mistral]:
    """Initializes and returns the Mistral client if API key is set."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        console.print(
            "[bold yellow]Warning:[/] MISTRAL_API_KEY environment variable not set. Mistral processing will be skipped."
        )
        return None
    try:
        return Mistral(api_key=api_key)
    except Exception as e:
        console.print(f"[bold red]Error initializing Mistral client:[/] {e}")
        return None


def get_pdf_details(
    pdf_path: str, console: Console
) -> Tuple[Optional[bytes], Optional[int]]:
    """Reads PDF content and gets the number of pages."""
    with console.status("[bold green]Reading PDF file...", spinner="dots"):
        try:
            with open(pdf_path, "rb") as pdf_file_obj:
                pdf_content = pdf_file_obj.read()
            # Re-open for PyPDF2 as it needs a seekable stream after full read
            with open(pdf_path, "rb") as pdf_file_for_pypdf2:
                pdf_reader = PyPDF2.PdfReader(pdf_file_for_pypdf2)
                num_pages = len(pdf_reader.pages)
            return pdf_content, num_pages
        except Exception as e:
            console.print(
                f"[bold red]Error reading PDF {os.path.basename(pdf_path)}:[/] {e}"
            )
            return None, None


def display_pdf_info(pdf_filename: str, num_pages: int, console: Console):
    """Displays PDF information in a Rich panel."""
    console.print(
        Panel(
            f"[bold]PDF Details[/]\nFilename: [cyan]{pdf_filename}[/]\nPages: [yellow]{num_pages}[/]",
            border_style="green",
            title="File Information",
        )
    )


def confirm_and_configure_processing(
    num_pages: int, pdf_filename: str, console: Console
) -> Tuple[bool, bool]:
    """Asks user for confirmation to proceed and Mistral image inclusion preference."""
    proceed = Confirm.ask(
        f"Do you want to proceed with processing {num_pages} pages of '{pdf_filename}'?"
    )
    if not proceed:
        return False, False  # (proceed, include_mistral_images_in_output)

    include_mistral_images = Confirm.ask(
        "For Mistral OCR: Do you want to include images (as base64) in the output and save them locally?"
    )
    console.print(
        f"If using Mistral, images will {'[green]be included[/]' if include_mistral_images else '[yellow]not be included[/]'} in the output."
    )
    return True, include_mistral_images


def upload_pdf_to_mistral(
    client: Mistral, pdf_path: str, pdf_content: bytes, console: Console
) -> Optional[str]:
    """Uploads the PDF file to Mistral and returns the signed URL."""
    with console.status("[bold blue]Uploading PDF to Mistral...", spinner="dots"):
        try:
            uploaded_file = client.files.upload(
                file={
                    "file_name": os.path.basename(pdf_path),
                    "content": pdf_content,
                },
                purpose="ocr",
            )
            signed_url_response = client.files.get_signed_url(
                file_id=uploaded_file.id, expiry=1
            )  # expiry in minutes
            return signed_url_response.url
        except Exception as e:
            console.print(f"[bold red]Error uploading PDF to Mistral:[/] {e}")
            return None


def process_ocr_with_mistral(
    client: Mistral, document_url: str, include_image_base64: bool, console: Console
) -> Optional[Any]:  # Using Any for Mistral's response type
    """Processes the document URL with Mistral OCR."""
    with console.status("[bold blue]Processing OCR with Mistral...", spinner="dots"):
        try:
            response = client.ocr.process(
                model="mistral-ocr-latest",
                document={"type": "document_url", "document_url": document_url},
                include_image_base64=include_image_base64,
            )
            return response
        except Exception as e:
            console.print(f"[bold red]Error during Mistral OCR processing:[/] {e}")
            return None


def _save_image_from_base64_data(image_filename: str, b64_data: str, console: Console):
    """Decodes base64 image data and saves it to a file."""
    try:
        comma_index = b64_data.find(",")
        if comma_index != -1:
            b64_string = b64_data[comma_index + 1 :]
        else:
            b64_string = b64_data
            # console.print(
            #     f"[yellow]Warning:[/] Could not find comma separator in base64 prefix for {image_filename}. Assuming full string is base64."
            # )
        image_bytes = base64.b64decode(b64_string)
        with open(image_filename, "wb") as f:
            f.write(image_bytes)
    except Exception as img_e:
        console.print(
            f"[bold red]Error processing and saving image {image_filename}:[/] {img_e}"
        )


def extract_pages_content_and_save_images_mistral(
    ocr_response: Any, include_image_base64: bool, console: Console
) -> List[str]:
    """Extracts markdown from Mistral OCR pages and saves images if requested, with progress."""
    all_markdown_parts = []
    # Calculate total tasks for the progress bar
    total_tasks = len(ocr_response.pages)
    if include_image_base64:
        for page in ocr_response.pages:
            total_tasks += len(page.images) if page.images else 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        page_processing_task = progress.add_task(
            "[bold green]Processing Mistral OCR content...", total=total_tasks
        )

        for page in ocr_response.pages:
            progress.update(
                page_processing_task,
                advance=1,
                description=f"[bold green]Processing page {page.index + 1}/{len(ocr_response.pages)} (Mistral)...",
            )

            if include_image_base64 and page.images:
                for image in page.images:
                    progress.update(
                        page_processing_task,
                        advance=1,
                        description=f"[bold cyan]Saving image {image.id} (page {page.index + 1}) from Mistral...",
                    )
                    _save_image_from_base64_data(image.id, image.image_base64, console)

            all_markdown_parts.append(page.markdown)
    return all_markdown_parts


# --- Ollama Fallback Functions ---
def process_image_with_ollama(
    image_path: str, console: Console, ollama_model: str, prompt: str
) -> Optional[str]:
    """Sends an image to Ollama and returns the text description."""
    if ollama is None:  # Should not happen if check is done before calling this flow
        console.print("[bold red]Ollama library not available.[/]")
        return None
    try:
        # The ollama client library handles reading the image file and base64 encoding it.
        res = ollama.chat(
            model=ollama_model,
            messages=[{"role": "user", "content": prompt, "images": [image_path]}],
        )
        return res["message"]["content"]
    except Exception as e:
        console.print(
            f"[bold red]Error processing image {os.path.basename(image_path)} with Ollama ({ollama_model}):[/] {e}"
        )
        if "connect" in str(e).lower() or "connection refused" in str(e).lower():
            console.print(
                f"[bold yellow]Hint: Ensure the Ollama application is running and the model '{ollama_model}' is pulled (e.g., 'ollama pull {ollama_model}').[/]"
            )
        return None


def process_pdf_with_ollama_fallback(
    pdf_path: str,
    console: Console,
    num_pages: int,
    ollama_model: str,
) -> Optional[str]:
    """
    Fallback OCR processing using Ollama. Converts PDF pages to images
    and sends them to an Ollama vision model.
    """
    if ollama is None or convert_from_path is None:
        console.print(
            "[bold red]Ollama or pdf2image library not available. Cannot proceed with Ollama fallback.[/]"
        )
        console.print(
            "[bold yellow]Please run 'pip install ollama pdf2image Pillow' and ensure Poppler is installed.[/]"
        )
        return None

    all_page_texts = []
    console.print(f"[cyan]Using Ollama (model: {ollama_model}) for OCR as fallback.[/]")

    default_ollama_prompt = "Extract all text from this image. If it's a document page, provide the text content as accurately as possible. Preserve formatting like paragraphs and line breaks where appropriate."
    ollama_prompt_text = os.getenv("OLLAMA_DEFAULT_PROMPT", default_ollama_prompt)

    try:
        ollama_models_info = ollama.list()
        available_models = [
            model_info["name"] for model_info in ollama_models_info.get("models", [])
        ]

        # Ollama model names can be like 'llava:latest' or just 'llava'
        is_model_available = any(
            ollama_model == m.split(":")[0] or ollama_model == m
            for m in available_models
        )

        if not is_model_available:
            console.print(
                f"[bold red]Error: Ollama model '{ollama_model}' (or '{ollama_model}:latest') is not available locally.[/]"
            )
            console.print(
                f"[yellow]Available models: {', '.join(available_models) if available_models else 'None'}[/]"
            )
            console.print(
                f"[yellow]Please pull the model using 'ollama pull {ollama_model}'[/]"
            )
            return None
    except Exception as e:
        console.print(f"[bold red]Ollama is not available or not responding: {e}[/]")
        console.print(
            f"[bold yellow]Please ensure the Ollama application is running and accessible.[/]"
        )
        return None

    with tempfile.TemporaryDirectory() as temp_dir_path:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            # Total steps: num_pages for conversion + num_pages for Ollama processing
            ollama_task = progress.add_task(
                f"[cyan]Processing with Ollama ({ollama_model})...", total=num_pages * 2
            )

            for i in range(num_pages):
                page_num_actual = i + 1  # 1-indexed for user display and pdf2image
                progress.update(
                    ollama_task,
                    advance=1,
                    description=f"[cyan]Converting page {page_num_actual}/{num_pages} to image...",
                )

                temp_image_path = os.path.join(
                    temp_dir_path, f"page_{page_num_actual}.png"
                )

                try:
                    page_images_pil = convert_from_path(
                        pdf_path,
                        first_page=page_num_actual,
                        last_page=page_num_actual,
                        fmt="png",
                        dpi=200,  # Standard DPI for OCR
                        thread_count=1,  # Process one page at a time
                        output_folder=temp_dir_path,  # Save directly to temp dir
                        paths_only=True,  # Get paths directly
                    )
                    if not page_images_pil:
                        raise Exception("convert_from_path returned empty list.")
                    # pdf2image with paths_only=True and output_folder creates files like:
                    # /tmp/randomname/LONGUUID-1.png. We need to find this file.
                    # Or, save manually:
                    # page_images_pil = convert_from_path(pdf_path, first_page=page_num_actual, last_page=page_num_actual, fmt="png", dpi=200, thread_count=1)
                    # if not page_images_pil: raise Exception("convert_from_path returned empty list.")
                    # page_images_pil[0].save(temp_image_path, "PNG")
                    # Reverting to manual save for clarity and control
                    page_images_pil_list = convert_from_path(
                        pdf_path,
                        first_page=page_num_actual,
                        last_page=page_num_actual,
                        fmt="png",
                        dpi=200,
                        thread_count=1,
                    )
                    if not page_images_pil_list:
                        raise Exception(
                            "convert_from_path returned an empty list of images."
                        )
                    pil_image = page_images_pil_list[0]
                    pil_image.save(temp_image_path, "PNG")

                except (
                    PDFInfoNotInstalledError,
                    PDFPageCountError,
                    PDFSyntaxError,
                ) as e:
                    console.print(
                        f"[bold red]Poppler error converting PDF page {page_num_actual}: {e}[/]"
                    )
                    console.print(
                        "[bold yellow]Ensure Poppler (poppler-utils) is installed and in your system's PATH.[/]"
                    )
                    all_page_texts.append(
                        f"\n[ERROR: Poppler failed to convert page {page_num_actual} to image. Ensure Poppler is installed.]\n"
                    )
                    progress.update(
                        ollama_task, advance=1
                    )  # Account for skipped Ollama step
                    continue
                except Exception as e:
                    console.print(
                        f"[bold red]Error converting PDF page {page_num_actual} to image: {e}[/]"
                    )
                    all_page_texts.append(
                        f"\n[ERROR: Failed to convert page {page_num_actual} to image: {e}]\n"
                    )
                    progress.update(ollama_task, advance=1)
                    continue

                progress.update(
                    ollama_task,
                    advance=1,
                    description=f"[cyan]Page {page_num_actual}/{num_pages} to Ollama ({ollama_model})...",
                )

                page_text = process_image_with_ollama(
                    temp_image_path, console, ollama_model, prompt=ollama_prompt_text
                )

                if page_text:
                    all_page_texts.append(page_text)
                else:
                    all_page_texts.append(
                        f"\n[ERROR: Ollama ({ollama_model}) failed to process page {page_num_actual}. See logs above.]\n"
                    )

    if not any(
        text and not text.strip().startswith("[ERROR:") for text in all_page_texts
    ):
        console.print(
            f"[bold red]Ollama ({ollama_model}) processing yielded no usable text content.[/]"
        )
        return None

    return "\n\n---\n\n".join(all_page_texts)


# --- Common Utility Functions ---
def generate_output_filename(pdf_path: str) -> str:
    """Generates the output Markdown filename based on the PDF path."""
    base_name_without_ext, _ = os.path.splitext(os.path.basename(pdf_path))
    return base_name_without_ext + ".md"


def save_markdown_to_file(final_markdown: str, output_filename: str):
    """Saves the final markdown content to a file."""
    with open(output_filename, "w", encoding="utf-8") as fd:
        fd.write(final_markdown)


def display_results_summary(
    output_filename: str, final_markdown: str, console: Console
):
    """Displays a success message and a preview of the generated markdown."""
    console.print(
        Panel(
            f"[bold green]Success![/] Output saved to [cyan]{output_filename}[/]",
            border_style="green",
            title="Processing Complete",
        )
    )
    console.print("\n[bold]Preview of generated markdown (first 500 chars):[/]")
    markdown_preview = (
        final_markdown[:500] + "..." if len(final_markdown) > 500 else final_markdown
    )
    console.print(
        Syntax(markdown_preview, "markdown", theme="monokai", line_numbers=True)
    )


#
# --- Main Orchestration Function ---
#
def main():
    """Main function that orchestrates the PDF processing workflow."""
    load_dotenv()
    console = Console()

    args = parse_and_validate_arguments(console)
    if not args:
        return

    pdf_content, num_pages = get_pdf_details(args.pdf_path, console)
    if pdf_content is None or num_pages is None:
        return

    pdf_filename_basename = os.path.basename(args.pdf_path)
    display_pdf_info(pdf_filename_basename, num_pages, console)

    proceed, include_mistral_images_in_output = confirm_and_configure_processing(
        num_pages, pdf_filename_basename, console
    )
    if not proceed:
        console.print("[yellow]Processing cancelled by user.[/]")
        return

    final_markdown: Optional[str] = None
    mistral_attempted_and_failed = False

    # --- Try Mistral First ---
    mistral_client = initialize_mistral_client(console)
    if mistral_client:
        console.print("\n[cyan]Attempting to process with Mistral OCR...[/]")
        try:
            signed_url_str = upload_pdf_to_mistral(
                mistral_client, args.pdf_path, pdf_content, console
            )
            if signed_url_str:
                ocr_response = process_ocr_with_mistral(
                    mistral_client,
                    signed_url_str,
                    include_mistral_images_in_output,
                    console,
                )
                if ocr_response and hasattr(ocr_response, "pages"):
                    all_markdown_parts = extract_pages_content_and_save_images_mistral(
                        ocr_response, include_mistral_images_in_output, console
                    )
                    final_markdown = "\n\n---\n\n".join(all_markdown_parts)
                    console.print(
                        "[green]Successfully processed PDF with Mistral OCR.[/green]"
                    )
                else:
                    console.print(
                        "[yellow]Mistral OCR processing step failed or returned empty/invalid response.[/yellow]"
                    )
                    mistral_attempted_and_failed = True
            else:
                console.print("[yellow]Failed to upload PDF to Mistral.[/yellow]")
                mistral_attempted_and_failed = True
        except Exception as e:
            console.print(
                f"[yellow]An error occurred during Mistral processing: {e}.[/yellow]"
            )
            mistral_attempted_and_failed = True
    else:
        # Mistral client couldn't be initialized (e.g., API key missing)
        # No explicit message here, initialize_mistral_client already printed a warning.
        mistral_attempted_and_failed = (
            True  # Counts as failed attempt if client not available
        )

    # --- Fallback to Ollama if Mistral was not used or failed ---
    if final_markdown is None:  # This implies Mistral path was skipped or failed
        if mistral_attempted_and_failed:
            console.print(
                "\n[yellow]Mistral OCR processing was not successful.[/yellow]"
            )
        else:  # This case implies Mistral client wasn't even initialized
            console.print(
                "\n[yellow]Mistral client not available or configured.[/yellow]"
            )

        ollama_model_name = os.getenv("OLLAMA_MODEL_VISION", "llava")

        use_ollama = Confirm.ask(
            f"Do you want to attempt fallback processing with Ollama (model: [bold cyan]{ollama_model_name}[/bold cyan])?",
            default=True,
        )
        if use_ollama:
            if ollama is None or convert_from_path is None:
                console.print(
                    "[bold red]Cannot use Ollama: 'ollama' or 'pdf2image' libraries are not installed properly.[/]"
                )
                console.print(
                    "[bold yellow]Please run 'pip install ollama pdf2image Pillow' and ensure Poppler is installed.[/]"
                )
            else:
                final_markdown = process_pdf_with_ollama_fallback(
                    args.pdf_path, console, num_pages, ollama_model=ollama_model_name
                )
                if final_markdown:
                    console.print(
                        f"[green]Successfully processed PDF with Ollama ({ollama_model_name}).[/green]"
                    )
                else:
                    console.print(
                        f"[bold red]Ollama fallback processing with {ollama_model_name} also failed or yielded no content.[/]"
                    )
        else:
            console.print("[yellow]Ollama fallback declined by user.[/yellow]")

    # --- Post-processing (if any method succeeded) ---
    if final_markdown is not None:
        output_md_filename = generate_output_filename(args.pdf_path)
        save_markdown_to_file(final_markdown, output_md_filename)
        display_results_summary(output_md_filename, final_markdown, console)
    else:
        console.print(
            Panel(
                "[bold red]Failed to generate markdown content from any available method (Mistral or Ollama).",
                border_style="red",
                title="Processing Incomplete",
            )
        )


if __name__ == "__main__":
    main()
