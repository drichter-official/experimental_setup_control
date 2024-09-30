import os
from PIL import Image

def mask_to_transparent(folder_path):
    """
    Apply a mask to make the left half of all images in the folder transparent.

    Parameters:
    folder_path (str): The path to the folder containing the images to process.
    """
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Process each image in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Process common image formats
            image_path = os.path.join(folder_path, filename)
            try:
                # Open the image
                image = Image.open(image_path).convert("RGBA")  # Ensure the image has an alpha channel
                width, height = image.size

                # Create a transparent mask for the left half
                pixels = image.load()  # Access the pixel data

                for x in range(width // 2):
                    for y in range(height):
                        # Set the alpha value to 0 for full transparency
                        r, g, b, a = pixels[x, y]
                        pixels[x, y] = (r, g, b, 0)

                # Save the modified image
                new_filename = f"masked_{filename}"
                new_image_path = os.path.join(folder_path, new_filename)
                image.save(new_image_path)
                print(f"Processed and saved {new_filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

# Example usage:
# mask_left_half_to_transparent('/path/to/your/images')
