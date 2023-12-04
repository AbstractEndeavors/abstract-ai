import pytesseract
from PIL import Image

# If you are on Windows, set the tesseract_cmd to your Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def image_to_text(image_path):
    # Open an image using PIL
    img = Image.open(image_path)

    # Use Tesseract to do OCR on the image
    text = pytesseract.image_to_string(img)

    return text

# Example usage
text_from_image = image_to_text('C:/Users/jrput/Pictures/Screenshot_from_2023-01-10_00-06-10.png')
print(text_from_image)
