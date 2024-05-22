#!/bin/bash
cslc layout.csl --arch=wse2 --fabric-dims=15,3 --fabric-offsets=4,1 -o out \
                --params=kernel_width:6,num_elems:20 --memcpy --channels=1
cs_python run.py --name out
