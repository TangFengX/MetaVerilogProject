## Meta Verilog Project
# Introduction
A structure of verilog project. Using Verilator and GTKwave to stimulate.
# Structure
```
.
├── Makefile
├── README.md
├── bin
├── build
│   ├── obj_dir
│   └── wavefrom
├── include
│   └── top_module_name.h
└── src
    ├── csrc
    │   └── sim_main.cpp
    └── vsrc
        └── top.v
```
# Usage
`make run`:convert `.v` or `.sv` compile,run and show the wave in gtkwave.
`make clean`:clean all temp files, executable and wavefrom files generate while building 
`make lint`:Apply static code analysis on verilog