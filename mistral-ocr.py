import os
import argparse
from dotenv import load_dotenv
from mistralai import Mistral
import base64
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

# Load environment variables from .env file
load_dotenv()

# Initialize Rich console
console = Console()


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process a PDF file from a PDF path.")
    parser.add_argument("pdf_path", help="Path to the PDF file to be processed.")
    args = parser.parse_args()

    pdf_path = args.pdf_path
    if not os.path.exists(pdf_path):
        console.print(f"[bold red]Error:[/] The file {pdf_path} does not exist.")
        return
    if not pdf_path.lower().endswith(".pdf"):
        console.print(f"[bold red]Error:[/] The file {pdf_path} is not a PDF.")
        return

    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        console.print(
            "[bold red]Error:[/] MISTRAL_API_KEY environment variable not set."
        )
        return

    client = Mistral(api_key=api_key)

    try:
        # Show processing message
        with console.status("[bold green]Reading PDF file...", spinner="dots"):
            # Read PDF and get page count
            with open(pdf_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)

        # Display PDF info in a panel
        console.print(
            Panel(
                f"[bold]PDF Details[/]\nFilename: [cyan]{os.path.basename(pdf_path)}[/]\nPages: [yellow]{num_pages}[/]",
                border_style="green",
                title="File Information",
            )
        )

        confirm = Confirm.ask(
            f"Do you want to proceed with processing {num_pages} pages?"
        )
        if not confirm:
            console.print("[yellow]Processing cancelled by user.[/]")
            return

        include_image_base64 = Confirm.ask(
            "Do you want to include images in the output?"
        )
        console.print(
            f"Images will {'[green]be included[/]' if include_image_base64 else '[yellow]not be included[/]'} in the output."
        )

        # Upload the PDF file to Mistral
        with console.status("[bold blue]Uploading PDF to Mistral...", spinner="dots"):
            uploaded_file = client.files.upload(
                file={
                    "file_name": os.path.basename(pdf_path),
                    "content": pdf_content,
                },
                purpose="ocr",
            )
            signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

        with console.status("[bold blue]Processing OCR...", spinner="dots"):
            response = client.ocr.process(
                model="mistral-ocr-latest",
                document={"type": "document_url", "document_url": signed_url.url},
                include_image_base64=include_image_base64,
            )

        all_markdown_parts = []

        # Calculate total tasks (pages + images if included)
        total_tasks = len(response.pages)
        if include_image_base64:
            for page in response.pages:
                total_tasks += len(page.images) if page.images else 0

        # Process each page in the response with a single progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task(
                "[bold green]Processing content...", total=total_tasks
            )

            for page in response.pages:
                progress.update(
                    task,
                    advance=1,
                    description=f"[bold green]Processing page {page.index + 1}/{len(response.pages)}...",
                )

                # Process and save images for the current page
                if include_image_base64 and page.images:
                    for image in page.images:
                        progress.update(
                            task,
                            advance=1,
                            description=f"[bold cyan]Processing image {image.id}",
                        )
                        filename = image.id
                        b64_data = image.image_base64

                        # Find the start of the actual base64 data
                        try:
                            comma_index = b64_data.find(",")
                            if comma_index != -1:
                                b64_string = b64_data[comma_index + 1 :]
                            else:
                                b64_string = b64_data
                                console.print(
                                    f"[yellow]Warning:[/] Could not find comma separator in base64 prefix for {filename}"
                                )

                            # Decode the base64 string
                            image_bytes = base64.b64decode(b64_string)

                            # Save the image bytes to a file
                            with open(filename, "wb") as f:
                                f.write(image_bytes)

                        except Exception as img_e:
                            console.print(
                                f"[bold red]Error processing image {filename}:[/] {img_e}"
                            )

                # Append the markdown content of the page
                all_markdown_parts.append(page.markdown)

        # Join the markdown parts from all pages
        final_markdown = "\n\n---\n\n".join(all_markdown_parts)

        # Save final_markdown to a file
        filename = "output.md"
        with open(filename, "w") as fd:
            fd.write(final_markdown)

        console.print(
            Panel(
                f"[bold green]Success![/] Output saved to [cyan]{filename}[/]",
                border_style="green",
                title="Processing Complete",
            )
        )

        # Show a preview of the markdown
        console.print("\n[bold]Preview of generated markdown:[/]")
        markdown_preview = (
            final_markdown[:500] + "..."
            if len(final_markdown) > 500
            else final_markdown
        )
        console.print(
            Syntax(markdown_preview, "markdown", theme="monokai", line_numbers=True)
        )

    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Error:[/] {str(e)}",
                border_style="red",
                title="Processing Failed",
            )
        )


if __name__ == "__main__":
    main()
