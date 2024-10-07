import os
from PIL import Image
import numpy as np
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
                # Open the image and ensure it has an alpha channel (RGBA mode)
                image = Image.open(image_path).convert("RGBA")
                width, height = image.size

                # Convert the image to a NumPy array for fast manipulation
                img_array = np.array(image)

                # Set the alpha channel of the left half (x < width // 2) to 0 (transparent)
                img_array[:height, :width // 3, 3] = 0
                img_array[:height, 2 * (width // 3):, 3] = 0

                brightness = np.mean(img_array[:, :, :3], axis=2)

                # Set the alpha channel to 0 (transparent) for pixels with brightness below the threshold
                img_array[brightness < 3, 3] = 0
                # Convert back to an image
                new_image = Image.fromarray(img_array)

                # Save the modified image
                new_filename = f"{filename}"
                new_image_path = os.path.join(folder_path, new_filename)
                new_image.save(new_image_path)
                print(f"Processed and saved {new_filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    mask_to_transparent('/home/daniel/projects/experimental_setup_controller/data/40_imgs_marker/images')