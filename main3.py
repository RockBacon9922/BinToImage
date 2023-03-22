import argparse
import math
import struct

import numpy as np
from PIL import Image


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Hexdump utility that writes output to a PNG file')
    parser.add_argument('input_file', help='Input file to hexdump')
    parser.add_argument(
        '-o', '--output', help='Output PNG file', required=True)
    parser.add_argument('-c', '--columns', type=int, default=16,
                        help='Number of columns per row (default: 16)')
    parser.add_argument('-s', '--start', type=int, default=0,
                        help='Starting offset (default: 0)')
    parser.add_argument('-e', '--end', type=int, default=-1,
                        help='Ending offset (default: end of file)')
    args = parser.parse_args()
    return args


def load_file(input_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    return data


def hexdump(data, columns, start_offset, end_offset):
    offset_format = '08X'
    ascii_format = ''.join(
        [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])
    result = []
    for i in range(0, len(data), columns):
        chunk = data[i:i+columns]
        hex_chunk = ' '.join([f"{byte:02X}" for byte in chunk])
        printable_chunk = ''.join([f"{ascii_format[byte]}" for byte in chunk])
        offset = start_offset + i
        if end_offset > 0:
            if offset >= end_offset:
                break
            chunk_length = min(len(chunk), end_offset - offset)
            hex_chunk = hex_chunk[:chunk_length*3-1]
            printable_chunk = printable_chunk[:chunk_length]
        result.append(
            f"{offset_format % offset}  {hex_chunk:<48}  {printable_chunk}")
    return result


def draw_image(data, width, height, output_file):
    colors = np.empty((256, 3), dtype=np.uint8)
    for i in range(256):
        colors[i] = struct.pack(
            'BBB', *(colormap[i] >> j & 0xff for j in (16, 8, 0)))
    img = Image.frombytes('RGB', (width, height),
                          bytes(colors[data].flatten()))
    img.save(output_file)


def main():
    args = parse_arguments()
    data = load_file(args.input_file)
    columns = args.columns
    start_offset = args.start
    end_offset = args.end if args.end > 0 else len(data)
    output_file = args.output
    hexdump_lines = hexdump(data, columns, start_offset, end_offset)
    image_file = draw_image(data, columns*8, len(hexdump_lines), output_file)
    print(f"Hexdump written to {output_file}")


if __name__ == '__main__':
    main()
