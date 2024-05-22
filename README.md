Commands
--------

- compile command: `cslc layout.csl --arch=wse2 --fabric-dims=15,3 --fabric-offsets=4,1 -o out --params=kernel_width:6,num_elems:20 --memcpy --channels=1`

- run command: `cs_python run.py --name out`

Parameters
----------

- `kernel_width` is number of PEs in the program, of size `kernel_width x 1`

- `num_elems` is number of elements per vector

Operation
---------

Each PE begins with a vector of size `num_elems`. Each PE sends its vector to its eastern
neighbor, where the receiving PE computes the dot product of its vector with the received
vector. The received vector is then sent onward to the next neighbor, until all vectors
have passed through all PEs. The easternmost PE sends its vector to the westernmost PE.

Each PE stores the result of a dot product with a received vector in an array,
with index corresponding to the x-coordinate of the PE from which the vector originated.
i.e., on PE 2, `dot_products[1]` will contain the dot product of the vector on PE 2 and
the vector originating from PE 1. `dot_products[2]` on PE 1 will contain the same value.

The program uses three colors to route the data. Colors 0 and 1 are used to implement
a checkerboard pattern for sending vectors westward, and color 2 is used to send vectors
from the easternmost PE to the westernmost PE.

For four PEs, the routing is as follows:

```
 PE: 0 --- 1 --- 2 --- 3

 0:  .> - >.     .> - >.
     ^     v     ^     v

 1:        .> - >.      
           ^     v      

 2:  .< - <.< - <.< - <.
     v                 ^
```

For eight PEs, the routing is as follows:
```
 PE: 0 --- 1 --- 2 --- 3 --- 4 --- 5 --- 6 --- 7

 0:  .> - >.     .> - >.     .> - >.     .> - >.
     ^     v     ^     v     ^     v     ^     v

 1:        .> - >.     .> - >.     .> - >.
           ^     v     ^     v     ^     v

 2:  .< - <.< - <.< - <.< - <.< - <.< - <.< - <.
     v                                         ^
```
