import os
from PIL import Image


def get_images_from_subfolders(main_folder):
    images = []
    for root, dirs, files in os.walk(main_folder):
        for file in files:
            if file.lower().endswith(('count_graphs.png')):
                images.append(os.path.join(root, file))
    return images


def create_collage(images, images_per_row, collage_width, output_file):
    # Assuming all images are of the same size (1000x500 in this case)
    img_width, img_height = 1000, 500
    collage_height = ((len(images) + images_per_row - 1) // images_per_row) * img_height

    collage_image = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))

    for index, img_path in enumerate(images):
        img = Image.open(img_path)
        x = (index % images_per_row) * img_width
        y = (index // images_per_row) * img_height
        collage_image.paste(img, (x, y))

    collage_image.save(output_file)
    print(f'Collage saved as {output_file}')


def create_collages_in_batches(main_folder, images_per_batch, images_per_row, collage_width):
    images = get_images_from_subfolders(main_folder)
    for i in range(0, len(images), images_per_batch):
        batch_images = images[i:i + images_per_batch]
        output_file = f'collage_{i // images_per_batch + 1}.png'
        create_collage(batch_images, images_per_row, collage_width, output_file)


def main():
    main_folder = 'output_data/'
    images_per_batch = 50  # Number of images per collage
    images_per_row = 5  # Number of images per row
    collage_width = 5000  # Collage width in pixels (5 images per row * 1000 px width per image)

    create_collages_in_batches(main_folder, images_per_batch, images_per_row, collage_width)


if __name__ == '__main__':
    main()
