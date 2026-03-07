TOPNAME = top
VERILATOR = verilator
TIMESTAMP = $(shell date +%Y%m%d_%H%M%S)
.DEFAULT_GOAL:=all
b?=0






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
WAVEFROM = $(PWD)/wavefrom



TESTBENCH_FILE=$(TESTBENCH)/testbench$(b).csv
SIM_CONFIG_FILE=$(INCLUDE)/sim_config.h
TESTBENCH_TOOL=$(TESTBENCH)/csv2c.py
PIN_BIND_CONFIG_FILE=$(PIN)/top.nxdc
WAVEFROM_FILE = $(WAVEFROM)/wavefrom_$(TIMESTAMP).fst
AUTO_PIN_BIND_SCRIPT = $(NVBOARD_HOME)/scripts/auto_pin_bind.py
PIN_BIND_CONFIG_CPP_FILE = $(CSRC)/auto_bind.cpp
NVBOARD_MAKEFILE = $(NVBOARD_HOME)/scripts/nvboard.mk
EXECUTABLE = $(BIN)/V$(TOPNAME)

VERILOG_FILES := $(wildcard $(VSRC)/*.v $(VSRC)/*.sv)
CPP_FILES := $(wildcard $(CSRC)/*.c $(CSRC)/*.cc $(CSRC)/*.cpp)

ifeq ($(b),1)
	INCLUDES = $(INCLUDE) $(OBJ_DIR) $(NVBOARD_HOME)/usr/include
	include $(NVBOARD_HOME)/scripts/nvboard.mk
	D_NVBOARD = -DNVBOARD
	
else
	INCLUDES = $(INCLUDE) $(OBJ_DIR) 
	D_NVBOARD = 
	CPP_FILES := $(filter-out $(CSRC)/auto_bind.cpp, $(CPP_FILES))
endif

all:$(EXECUTABLE)


INCLUDES_FILE :=$(wildcard $(INCLUDE)/*.h)










#硬件配置
CORES=$(shell nproc)


VERILATOR_FLAGS += --trace-fst  --cc --top-module $(TOPNAME) --Mdir $(OBJ_DIR) --exe




CFLAGS+= -DWAVEFILE="\\\"$(WAVEFROM_FILE)\\\"" $(D_NVBOARD) -Wall -O2 $(addprefix -I ,$(INCLUDES))
LDFLAGS += $(NVBOARD_ARCHIVE) -lSDL2 -lSDL2_image -lSDL2_ttf -lz
MAKE_FLAGS+= -f $(OBJ_DIR)/V$(TOPNAME).mk -C $(OBJ_DIR) CXXFLAGS="$(CFLAGS)"  LDLIBS="$(LDFLAGS)" -j $(CORES)



.PHONY: all toc sim clean cleanlib tb bind 


$(EXECUTABLE): $(OBJ_DIR)/V$(TOPNAME).mk  $(CPP_FILES) $(INCLUDES_FILE) $(NVBOARD_ARCHIVE)
	@echo "b=$(b)\n,$(CPP_FILES)"
	@mkdir -p $(BIN)
	@make $(MAKE_FLAGS)
	@mv $(OBJ_DIR)/V$(TOPNAME) $(BIN)

toc:$(OBJ_DIR)/V$(TOPNAME).mk
$(OBJ_DIR)/V$(TOPNAME).mk : $(VERILOG_FILES) 
	@mkdir -p $(BUILD)
	@mkdir -p $(OBJ_DIR)
	@$(VERILATOR) $(VERILATOR_FLAGS) $(VERILOG_FILES) $(CPP_FILES)






LATEST_FST := $(shell ls $(WAVEFROM)/*.fst 2>/dev/null | sort | tail -n 1)
sim:$(EXECUTABLE)
	@gtkwave $(LATEST_FST)

run:$(EXECUTABLE)
	@mkdir -p $(WAVEFROM)
	$(EXECUTABLE)

vcd:
	@LATEST_FST=$$(ls $(WAVEFROM)/*.fst 2>/dev/null | sort | tail -n 1); \
	fst2vcd "$$LATEST_FST" > "$${LATEST_FST%.fst}.vcd" 2>/dev/null || true
	


clean:
	@rm $(BUILD) -rf
	@rm $(BIN) -rf 


cleanlib:
	@rm $(NVBOARD_BUILD_DIR) -rf
cleanwave:
	@rm $(WAVEFROM) -rf

cleanall:clean cleanlib cleanwave

lint:
	@$(VERILATOR) --lint-only -Wall $(VERILOG_FILES)


tb:$(SIM_CONFIG_FILE)

$(SIM_CONFIG_FILE): $(TESTBENCH_FILE) $(TESTBENCH_TOOL)
	@rm $(SIM_CONFIG_FILE) -rf
	@python $(TESTBENCH_TOOL) $(TESTBENCH_FILE) $(SIM_CONFIG_FILE)

bind:$(PIN_BIND_CONFIG_CPP_FILE)
$(PIN_BIND_CONFIG_CPP_FILE):$(PIN_BIND_CONFIG_FILE) $(shell pwd)/pin/top.nxdclite $(shell pwd)/pin/gen_tool.py $(shell pwd)/pin/pins
	@touch $(PIN_BIND_CONFIG_CPP_FILE)
	@python $(AUTO_PIN_BIND_SCRIPT) $(PIN_BIND_CONFIG_FILE) $(PIN_BIND_CONFIG_CPP_FILE)



genbind:$(shell pwd)/pin/top.nxdclite
	@python $(shell pwd)/pin/gen_tool.py




