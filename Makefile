TOPNAME = top
VERILATOR = verilator
TIMESTAMP = $(shell date +%Y%m%d_%H%M%S)





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
WAVEFROM = $(shell pwd)/wavefrom


#file
TESTBENCH_FILE=$(TESTBENCH)/testbench.csv
SIM_CONFIG_FILE=$(INCLUDE)/sim_config.h
TESTBENCH_TOOL=$(TESTBENCH)/csv2c.py
PIN_BIND_CONFIG_FILE=$(PIN)/top.nxdc
WAVEFROM_FILE = $(WAVEFROM)/wavefrom_$(TIMESTAMP).fst
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


VERILATOR_FLAGS += --trace-fst  --cc --top-module $(TOPNAME) --Mdir $(OBJ_DIR) --exe
CFLAGS+= -DWAVEFILE="\\\"$(WAVEFROM_FILE)\\\"" -Wall -O2 $(addprefix -I ,$(INCLUDES))
LDFLAGS += $(NVBOARD_ARCHIVE) -lSDL2 -lSDL2_image -lSDL2_ttf -lz
MAKE_FLAGS+= -f $(OBJ_DIR)/V$(TOPNAME).mk -C $(OBJ_DIR) CXXFLAGS="$(CFLAGS)"  LDLIBS="$(LDFLAGS)" -j $(CORES)

.PHONY: all toc sim clean cleanlib tb bind 


$(EXECUTABLE): $(OBJ_DIR)/V$(TOPNAME).mk $(SIM_CONFIG_FILE) $(PIN_BIND_CONFIG_CPP_FILE)  $(NVBOARD_ARCHIVE) $(CSRC) $(VSRC) $(wildcard $(INCLUDE)/*.h)#build exe with auto-generated .mk file
	@mkdir -p $(BIN)
	@make $(MAKE_FLAGS)
	@mv $(OBJ_DIR)/V$(TOPNAME) $(BIN)

toc:$(OBJ_DIR)/V$(TOPNAME).mk
$(OBJ_DIR)/V$(TOPNAME).mk : $(VERILOG_FILES)
	@mkdir -p $(BUILD)
	@mkdir -p $(OBJ_DIR)
	@$(VERILATOR) $(VERILATOR_FLAGS) $(VERILOG_FILES) $(CPP_FILES)



clean:
	@rm $(BUILD) -rf
	@rm $(BIN) -rf 
	@rm $(NVBOARD_ARCHIVE) -rf

cleanlib:
	@make nvboard-clean
cleanwave:
	@rm $(WAVEFROM) -rf
cleanall:clean cleanlib cleanwave

lint:#analyze verilog code
	@$(VERILATOR) --lint-only -Wall $(VERILOG_FILES)


tb:$(SIM_CONFIG_FILE)
$(SIM_CONFIG_FILE): $(TESTBENCH_FILE) $(TESTBENCH_TOOL)
	@rm $(SIM_CONFIG_FILE) -rf
	@python $(TESTBENCH_TOOL) $(TESTBENCH_FILE) $(SIM_CONFIG_FILE)

bind:$(PIN_BIND_CONFIG_CPP_FILE)
$(PIN_BIND_CONFIG_CPP_FILE):$(PIN_BIND_CONFIG_FILE)
	@touch $(PIN_BIND_CONFIG_CPP_FILE)
	@python $(AUTO_PIN_BIND_SCRIPT) $(PIN_BIND_CONFIG_FILE) $(PIN_BIND_CONFIG_CPP_FILE)

run:$(EXECUTABLE)
	@mkdir -p $(WAVEFROM)
	@$(BIN)/V$(TOPNAME)


genbind:$(shell pwd)/pin/top.nxdclite
	@python $(shell pwd)/pin/gen_tool.py




