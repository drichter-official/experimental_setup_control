import os
import pygame
from PIL import Image, ImageDraw
import numpy as np

def transparent_polygon_editor(folder_path):
    """
    Allow the user to select polygon regions to make transparent in images within a folder.
    """
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Initialize Pygame
    pygame.init()

    # Process each image in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Process common image formats
            image_path = os.path.join(folder_path, filename)
            try:
                # Open the image and ensure it has an alpha channel (RGBA mode)
                image = Image.open(image_path).convert("RGBA")
                width, height = image.size

                # Convert the image to a NumPy array for manipulation
                img_array = np.array(image)

                # Create a Pygame window with the size of the image
                screen = pygame.display.set_mode((width, height))
                pygame.display.set_caption(f"Editing {filename}")

                # Load the image into Pygame
                mode = image.mode
                size = image.size
                data = image.tobytes()

                pygame_image = pygame.image.fromstring(data, size, mode)

                # Main loop for this image
                done = False
                polygons = []  # List to store polygons
                current_polygon = []  # Points in the current polygon

                while not done:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                if current_polygon:
                                    # Finish current polygon
                                    polygons.append(current_polygon.copy())
                                    current_polygon = []
                            elif event.key == pygame.K_s:
                                # Save and move to next image
                                done = True
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:  # Left click
                                pos = pygame.mouse.get_pos()
                                current_polygon.append(pos)
                            elif event.button == 3:  # Right click
                                if current_polygon:
                                    # Finish current polygon
                                    polygons.append(current_polygon.copy())
                                    current_polygon = []

                    # Draw the image
                    screen.blit(pygame_image, (0, 0))

                    # Draw current polygon
                    if current_polygon:
                        if len(current_polygon) > 1:
                            pygame.draw.lines(screen, (255, 0, 0), False, current_polygon, 2)
                        for point in current_polygon:
                            pygame.draw.circle(screen, (255, 0, 0), point, 3)

                    # Draw finished polygons
                    for poly in polygons:
                        if len(poly) > 2:
                            pygame.draw.polygon(screen, (0, 255, 0), poly, 2)
                        else:
                            pygame.draw.lines(screen, (0, 255, 0), False, poly, 2)

                    pygame.display.flip()

                # After done editing, apply polygons to image

                # Create a mask
                mask = Image.new('L', (width, height), 0)
                mask_draw = ImageDraw.Draw(mask)

                for poly in polygons:
                    mask_draw.polygon(poly, fill=255)

                # Convert mask to numpy array
                mask_array = np.array(mask)

                # Set alpha channel of img_array to 0 where mask is 255
                img_array[mask_array == 255, 3] = 0

                # Convert back to image
                new_image = Image.fromarray(img_array)

                # Save the modified image
                new_filename = f"{filename}"
                new_image_path = os.path.join(folder_path, new_filename)
                new_image.save(new_image_path)
                print(f"Processed and saved {new_filename}")

                # Close the Pygame window
                pygame.display.quit()

            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    pygame.quit()

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder containing images: ")
    transparent_polygon_editor(folder_path)
