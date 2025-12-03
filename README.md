## Meta Verilog Project

### Introduction
A structured Verilog/SystemVerilog project framework using Verilator for simulation and GTKWave for waveform visualization. This project provides a complete workflow for developing, simulating, and analyzing digital designs.

### Features
- **Verilator-based Simulation**: High-performance C++ simulation of Verilog/SystemVerilog designs
- **GTKWave Integration**: Waveform visualization and analysis
- **Automated Testbench Generation**: CSV-based testbench configuration
- **Flexible Build System**: Makefile-based build process with debug/release modes
- **Modular Architecture**: Separation of hardware (Verilog) and software (C++) components

### Project Structure
```
.
├── Makefile              # Build automation and project management
├── README.md             # Project documentation
├── bin                   # Compiled executables
├── build                 # Build artifacts and temporary files
│   ├── obj_dir           # Verilator-generated C++ files
│   └── wavefrom          # Generated waveform files
├── include               # Header files
│   ├── sim_main.h        # Simulation helper macros and utilities
│   └── top_module_name.h # Generated module name header
├── src                   # Source code
│   ├── csrc              # C++ source files
│   │   └── sim_main.cpp  # Main simulation driver
│   └── vsrc              # Verilog/SystemVerilog source files
│       └── top.v         # Top-level module example
├── testbench             # Testbench configuration
│   ├── csv2c.py          # Testbench CSV to C++ converter
│   └── testbench.csv     # Testbench configuration in CSV format
└── nvboard               # Optional NVBoard integration (if applicable)
```

### Prerequisites
Before using this project, ensure you have the following installed:
- Verilator (>= 4.000)
- GTKWave
- Python 3.x
- GNU Make
- C++ compiler (GCC or Clang)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/TangFengX/MetaVerilogProject.git
   cd MetaVerilogProject
   ```



2. Install required dependencies:
   ```bash
   # Ubuntu/Debian:
   sudo apt-get install verilator gtkwave python3 make g++
   
   # CentOS/RHEL/Fedora:
   sudo yum install verilator gtkwave python3 make gcc-c++
   
   # macOS:
   brew install verilator gtkwave python3
   ```


#### Build Targets
- `make run` *(default)*: Complete build, run simulation, and show waveform
- `make tb`: Generate testbench configuration from CSV
- `make toc`: Convert Verilog to C++ using Verilator
- `make mk`: Compile C++ files to executable
- `make sim`: Run simulation and open waveform viewer
- `make clean`: Remove all build artifacts
- `make lint`: Perform static code analysis on Verilog files


#### Testbench Configuration
The testbench is configured using `testbench/testbench.csv`. The CSV format includes:
- **Columns 1-3**: Time (ps), Pin name, Value
- **Columns 5+**: Configuration parameters (max stimulate time, clock settings, etc.)



### Configuration parameters
| Parameter | Description |
|-----------|-------------|
| t1 | Maximum stimulate time (ps) |
| t2 | Half clock cycle (ps) |
| t3 | Enable clock input (0/1) |
| t4 | Clock pin name |

### Customization
To use with your own Verilog design:
1. Replace `src/vsrc/top.v` with your top module
2. Update `TOPNAME` in Makefile to match your top module name
3. Modify `testbench/testbench.csv` to configure your testbench
4. Adjust `src/csrc/sim_main.cpp` if needed for custom initialization

### Contributing
Contributions are welcome! Please fork the repository and submit pull requests.
