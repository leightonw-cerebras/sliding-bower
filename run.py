#!/usr/bin/env cs_python

import argparse
import csv
import json
import struct
import time
import numpy as np

from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='the test name')
    parser.add_argument("--cmaddr", help="IP:port for CS system")
    
    args = parser.parse_args()
    name = args.name
    cmaddr = args.cmaddr
    
    # Parse the compile metadata
    with open(f"{name}/out.json", encoding="utf-8") as json_file:
        compile_data = json.load(json_file)
    
    kernel_width = int(compile_data["params"]["kernel_width"])
    num_elems = int(compile_data["params"]["num_elems"])
    
    print()
    print("Run parameters:")
    print("Kernel width = ", kernel_width)
    print("Elems per vector = ", num_elems)
    
    # Construct a runner using SdkRuntime
    runner = SdkRuntime(name, cmaddr=cmaddr)
    
    # Grab symbols from ELF files for copying data on/ off device
    arr0_symbol = runner.get_id("arr0")
    dot_products_symbol = runner.get_id("dot_products")
    
    # Set type and order of the memcpys
    memcpy_dtype = MemcpyDataType.MEMCPY_32BIT
    memcpy_order = MemcpyOrder.ROW_MAJOR
    
    # Input data
    rng = np.random.default_rng()
    arr0_in_data = rng.random(size=kernel_width*num_elems, dtype=np.float32)
    
    input_vectors = arr0_in_data.reshape(kernel_width, num_elems)
    print("\nDot products: ")
    for pe in range(kernel_width): 
        print("PE ", pe, " vector: ", input_vectors[pe]);
    print()

    # Load and run the program
    print("Starting run...")
    runner.load()
    runner.run()
    
    # Copy data to arr0 in device
    print("Copy data...")
    runner.memcpy_h2d(arr0_symbol, arr0_in_data, 0, 0, kernel_width, 1, num_elems,
                      streaming=False, data_type=memcpy_dtype,
                      order=memcpy_order, nonblock=False)
    
    print("Launch kernel...")
    runner.launch("main_fn", nonblock=False)
    
    # Copy back data in arr1 from device
    dot_products = np.zeros([kernel_width*kernel_width], dtype=np.float32)
    runner.memcpy_d2h(dot_products, dot_products_symbol, 0, 0, kernel_width, 1, kernel_width,
                      streaming=False, data_type=memcpy_dtype,
                      order=memcpy_order, nonblock=True)
    print("Copied back dot products.")

    # Stop the program
    runner.stop()

    dot_products = dot_products.reshape(kernel_width, kernel_width)

    print("\nDot products: ")
    for pe in range(kernel_width): 
        print("PE ", pe, ": ", dot_products[pe]);
    
    print("SUCCESS!")
    
if __name__ == "__main__":
    main()
