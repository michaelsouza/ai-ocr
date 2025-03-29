import os
import argparse
from dotenv import load_dotenv
from mistralai import Mistral
import base64 # <-- Import the base64 library

# Load environment variables from .env file
load_dotenv()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process a PDF file from a URL using Mistral OCR and save the output to a file.")
    parser.add_argument("pdf_url", help="URL of the PDF file to process")
    args = parser.parse_args()

    pdf_url = args.pdf_url
    api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        print("Error: MISTRAL_API_KEY environment variable not set.")
        return

    client = Mistral(api_key=api_key)

    try:
        # Make the API call with the document URL
        print(f"Processing PDF from: {pdf_url}...") # Added status message
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": pdf_url},
            include_image_base64=True
        )

        all_markdown_parts = []

        # Process each page in the response
        for page in response.pages:
            print(f"Processing page {page.index}...") # Added status message
            # Process and save images for the current page
            for image in page.images:
                filename = image.id
                b64_data = image.image_base64

                # Find the start of the actual base64 data
                try:
                    comma_index = b64_data.find(',')
                    if comma_index != -1:
                        b64_string = b64_data[comma_index + 1:]
                    else:
                        # Handle cases where the prefix might be missing (though unlikely)
                        b64_string = b64_data
                        print(f"Warning: Could not find comma separator in base64 prefix for {filename}")

                    # Decode the base64 string
                    image_bytes = base64.b64decode(b64_string)

                    # Save the image bytes to a file
                    with open(filename, 'wb') as f:
                        f.write(image_bytes)
                    print(f"Saved image: {filename}") # Added status message

                except Exception as img_e:
                    print(f"Error processing image {filename}: {img_e}")

            # Append the markdown content of the page
            all_markdown_parts.append(page.markdown)

        # Join the markdown parts from all pages (add a separator like a newline)
        final_markdown = "\n\n---\n\n".join(all_markdown_parts) # Added a separator between pages

        # Print the final combined markdown to standard output
        print(final_markdown)
        print("\nMarkdown generation complete.") # Added status message
        
        # Save final_markdown to a file
        filename = "output.md"
        print(f"Saving output file to {filename}")
        with open(filename, "w") as fd:
            fd.write(final_markdown)


    except Exception as e:
        print(f"An error occurred during OCR processing: {e}")

if __name__ == "__main__":
    main()