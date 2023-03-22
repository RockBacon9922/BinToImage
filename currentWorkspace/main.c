
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lodepng.h"

// Function to round a value to the nearest multiple of a given factor
int round_to_nearest(int value, int factor)
{
    return ((value + (factor / 2)) / factor) * factor;
}

int main(int argc, char *argv[])
{
    if (argc != 5)
    {
        printf("Usage: %s binary_file colour_depth width height\n", argv[0]);
        return 1;
    }

    const char *filename = argv[1];
    int colour_depth = atoi(argv[2]);
    int width = atoi(argv[3]);
    int height = atoi(argv[4]);

    FILE *file = fopen(filename, "rb");
    if (!file)
    {
        printf("Error: Could not open file %s\n", filename);
        return 1;
    }

    // Skip the header of the binary file
    fseek(file, 54, SEEK_SET);

    // Allocate memory for the image data
    unsigned char *image_data = (unsigned char *)malloc(width * height * 3 * sizeof(unsigned char));
    if (!image_data)
    {
        printf("Error: Could not allocate memory\n");
        fclose(file);
        return 1;
    }

    // Read the image data from the binary file
    fread(image_data, sizeof(unsigned char), width * height * 3, file);

    // Convert the binary data to pixel colours
    for (int i = 0; i < width * height * 3; i += 3)
    {
        // Get the RGB values from the binary data
        int red = image_data[i];
        int green = image_data[i + 1];
        int blue = image_data[i + 2];

        // Round the values to the nearest colour within the colour depth
        red = round_to_nearest(red, 256 / colour_depth);
        green = round_to_nearest(green, 256 / colour_depth);
        blue = round_to_nearest(blue, 256 / colour_depth);

        // Set the pixel colour
        int pixel_index = i / 3;
        image_data[pixel_index * 4] = red;
        image_data[pixel_index * 4 + 1] = green;
        image_data[pixel_index * 4 + 2] = blue;
        image_data[pixel_index * 4 + 3] = 255; // Alpha channel (fully opaque)
    }

    // Create the output image using LodePNG library
    unsigned error = lodepng_encode32_file("output.png", image_data, width, height);
    if (error)
    {
        printf("Error %u: %s\n", error, lodepng_error_text(error));
        free(image_data);
        return 1;
    }

    // Free memory
    free(image_data);

    printf("Image saved as output.png\n");

    return 0;
}