TOPNAME = top
VERILATOR = verilator



#path
PWD=$(shell pwd)
NVBOARD_HOME=$(PWD)/nvboard
BUILD=$(PWD)/build
PIN=$(PWD)/pin
BIN=$(PWD)/bin
CSRC=$(PWD)/src/csrc
VSRC=$(PWD)/src/vsrc
OBJ_DIR=$(BUILD)/obj_dir
INCLUDE = $(PWD)/include
TESTBENCH=$(PWD)/testbench
WAVEFROM = $(BUILD)/wavefrom


#file
TESTBENCH_FILE=$(TESTBENCH)/testbench.csv
SIM_CONFIG_FILE=$(INCLUDE)/sim_config.h
TESTBENCH_TOOL=$(TESTBENCH)/csv2c.py
PIN_BIND_CONFIG_FILE=$(PIN)/top.nxdc
WAVEFROM_FILE = $(WAVEFROM)/wavefrom.fst
AUTO_PIN_BIND_SCRIPT = $(NVBOARD_HOME)/scripts/auto_pin_bind.py
PIN_BIND_CONFIG_CPP_FILE = $(CSRC)/auto_bind.cpp
NVBOARD_MAKEFILE = $(NVBOARD_HOME)/scripts/nvboard.mk
EXECUTABLE = $(BIN)/V$(TOPNAME)

#source file
TOP_MODULE_FILE=$(if $(wildcard $(VSRC)/$(TOPNAME).v),$(VSRC)/$(TOPNAME).v,(if $(wildcard $(VSRC)/$(TOPNAME).sv),$(VSRC)/$(TOPNAME).sv,))
VERILOG_FILES := $(wildcard $(VSRC)/*.v $(VSRC)/*.sv)
CPP_FILES := $(wildcard $(CSRC)/*.c $(CSRC)/*.cc $(CSRC)/*.cpp)



all:$(EXECUTABLE)
#include nvboard makefile
include $(NVBOARD_HOME)/scripts/nvboard.mk


INCLUDES = $(INCLUDE) $(OBJ_DIR) $(NVBOARD_HOME)/usr/include






#硬件配置
CORES=$(shell nproc)

#verilator选项
VERILATOR_CFLAGS += --trace-fst  
VERILATOR_CFLAGS += --cc
VERILATOR_CFLAGS += --top-module $(TOPNAME)
VERILATOR_CFLAGS += --Mdir $(OBJ_DIR)
VERILATOR_CFLAGS += --exe


#make选项
MAKE_FLAGS+= -j $(CORES)
FLAGS+= -DWAVEFILE="\\\"$(WAVEFROM_FILE)\\\""
FLAGS+= -Wall
FLAGS+= -O2
FLAGS+= $(addprefix -I ,$(INCLUDES))


.PHONY: all toc sim clean cleanlib tb bind 


$(EXECUTABLE): $(OBJ_DIR)/V$(TOPNAME).mk $(SIM_CONFIG_FILE) $(PIN_BIND_CONFIG_CPP_FILE)  $(NVBOARD_ARCHIVE)#build exe with auto-generated .mk file
	@echo "cpp ----g++----> exe"
	@mkdir -p $(BIN)
	@make -f $(OBJ_DIR)/V$(TOPNAME).mk -C $(OBJ_DIR) CXXFLAGS="$(FLAGS)" $(MAKE_FLAGS) LDLIBS="$(NVBOARD_ARCHIVE) -lSDL2 -lSDL2_image -lSDL2_ttf -lz $(LDLIBS)"
	@mv $(OBJ_DIR)/V$(TOPNAME) $(BIN)

toc:$(OBJ_DIR)/V$(TOPNAME).mk 
$(OBJ_DIR)/V$(TOPNAME).mk :  #use verilator to generate .cpp and .h
	@echo "verilog ----verilator----> cpp"
	@echo "#include \"V$(TOPNAME).h\"" > $(INCLUDE)/top_module_name.h
	@mkdir -p $(BUILD)
	@mkdir -p $(OBJ_DIR)
	@$(VERILATOR) $(VERILATOR_CFLAGS) $(VERILOG_FILES) $(CPP_FILES)

sim:#stimulate and use gtkwave to display wavefrom
	@echo "show wavefrom in gtkwave"
	@mkdir -p $(WAVEFROM)
	@$(BIN)/V$(TOPNAME)
	@gtkwave $(WAVEFROM_FILE)

clean:
	@rm $(BUILD) -rf
	@rm $(BIN) -rf 
	@rm $(NVBOARD_ARCHIVE) 

cleanlib:
	@make nvboard-clean

cleanall:clean cleanlib
lint:#analyze verilog code
	@$(VERILATOR) --lint-only -Wall $(VERILOG_FILES)


tb:$(SIM_CONFIG_FILE)
$(SIM_CONFIG_FILE):#read testbench, generate sim_config.h
	@python --version
	@rm $(SIM_CONFIG_FILE)
	@python $(TESTBENCH_TOOL) $(TESTBENCH_FILE) $(SIM_CONFIG_FILE)

bind:$(PIN_BIND_CONFIG_CPP_FILE)
$(PIN_BIND_CONFIG_CPP_FILE):
	@touch $(PIN_BIND_CONFIG_CPP_FILE)
	@python --version
	@python $(AUTO_PIN_BIND_SCRIPT) $(PIN_BIND_CONFIG_FILE) $(PIN_BIND_CONFIG_CPP_FILE)

run:$(BIN)
	@$(BIN)/V$(TOPNAME)



COMMANDS = gcc g++ python gtkwave verilator

SDL2_HEADERS = SDL2/SDL.h SDL2/SDL_image.h SDL2/SDL_ttf.h

LINK_TEST_LIBS = -lSDL2 -lSDL2_image -lSDL2_ttf

define check_command
	@echo "-> Checking command: $1 ..."
	@if command -v $1 > /dev/null 2>&1; then \
		echo "  ✓ '$1' exists"; \
	else \
		echo "ERROR: Command '$1' not found"; \
		exit 1; \
	fi
endef

define check_header
	@echo "-> Checking header: $1 ..."
	@if ! test -f /usr/include/$1 && ! test -f /usr/local/include/$1 && ! test -f /usr/include/x86_64-linux-gnu/$1; then \
		echo "ERROR: Header '$1' not found in standard include paths"; \
		echo "  Try: sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev"; \
		exit 1; \
	fi
	@echo "  ✓ '$1' exists"
endef

define check_python_module
	@echo "-> Checking Python module: $1 ..."
	@if ! python3 -c "import $1" 2>/dev/null; then \
		echo "ERROR: Python module '$1' not found"; \
		echo "  Try: pip install $1"; \
		exit 1; \
	fi
	@echo "  ✓ Python module '$1' exists"
endef

define check_library
	@echo "-> Checking library: $1 ..."
	@if ! echo "int main() { return 0; }" | gcc -x c - -o /dev/null -l$1 2>/dev/null; then \
		echo "ERROR: Library '$1' not found or cannot be linked"; \
		echo "  Try: sudo apt-get install lib$1-dev"; \
		exit 1; \
	fi
	@echo "  ✓ Library '$1' can be linked"
endef

define check_verilator_version
	@echo "-> Checking Verilator version ..."
	@if ! verilator --version 2>/dev/null | grep -q "Verilator"; then \
		echo "ERROR: Verilator not working properly"; \
		exit 1; \
	fi
	@verilator --version 2>/dev/null | head -1
	@echo "  ✓ Verilator is working"
endef

define install_suggestion
	@case "$1" in \
		gcc|g++) echo "    sudo apt-get install gcc g++" ;; \
		python) echo "    sudo apt-get install python3" ;; \
		gtkwave) echo "    sudo apt-get install gtkwave" ;; \
		verilator) echo "    sudo apt-get install verilator" ;; \
		*) echo "    Please check your package manager for '$1'" ;; \
	esac
endef

check: check_commands check_libs check_python_modules check_libraries check_verilator
check_commands:
	@echo "=== Checking required commands ==="
	@$(call check_command,gcc)
	@$(call check_command,g++)
	@$(call check_command,python)
	@$(call check_command,gtkwave)
	@$(call check_command,verilator)

check_libs:
	@echo ""
	@echo "=== Checking SDL2 headers ==="
	@$(call check_header,SDL2/SDL.h)
	@$(call check_header,SDL2/SDL_image.h)
	@$(call check_header,SDL2/SDL_ttf.h)

check_python_modules:
	@echo ""
	@echo "=== Checking Python modules ==="
	@$(call check_python_module,sys)
	@$(call check_python_module,csv)
	@$(call check_python_module,re)
	@$(call check_python_module,os)
	@$(call check_python_module,collections)

check_libraries:
	@echo ""
	@echo "=== Checking libraries ==="
	@$(call check_library,SDL2)
	@$(call check_library,SDL2_image)
	@$(call check_library,SDL2_ttf)
	@$(call check_library,z)

check_verilator:
	@echo ""
	@echo "=== Checking Verilator ==="
	@$(call check_verilator_version)

check_all: check
	@echo ""
	@echo "========================================"
	@echo "All checks passed! Environment is ready."
	@echo "========================================"
