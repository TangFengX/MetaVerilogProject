TOPNAME = top
VERILATOR = verilator
WAVEFROM_NAME = wavefrom.fst
PWD=$(shell pwd)
BUILD=$(PWD)/build


TESTBENCH=$(PWD)/testbench
TESTBENCH_FILE=$(TESTBENCH)/testbench.csv
SIM_CONFIG_FILE=$(INCLUDE)/sim_config.h
TESTBENCH_TOOL=$(TESTBENCH)/csv2c.py
TARGET=$(BIN)/V$(TOPNAME)

BIN=$(PWD)/bin
CSRC=$(PWD)/src/csrc
VSRC=$(PWD)/src/vsrc
TOP_MODULE_FILE=$(if $(wildcard $(VSRC)/$(TOPNAME).v),$(VSRC)/$(TOPNAME).v,(if $(wildcard $(VSRC)/$(TOPNAME).sv),$(VSRC)/$(TOPNAME).sv,))

OBJ_DIR=$(BUILD)/obj_dir
INCLUDE = $(PWD)/include

INCLUDES = $(INCLUDE) $(OBJ_DIR)


VERILOG_FILES := $(wildcard $(VSRC)/*.v $(VSRC)/*.sv)
CPP_FILES := $(wildcard $(CSRC)/*.c $(CSRC)/*.cc $(CSRC)/*.cpp)


WAVEFROM = $(BUILD)/wavefrom
WAVEFROM_FILE = $(WAVEFROM)/$(WAVEFROM_NAME)

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


mk:$(TARGET)


toc:$(OBJ_DIR)/V$(TOPNAME).mk
$(OBJ_DIR)/V$(TOPNAME).mk: $(SIM_CONFIG_FILE)
	@echo "verilog ----verilator----> cpp"
	@rm  $(OBJ_DIR)/* -rf
	@echo "#include \"V$(TOPNAME).h\"" > $(INCLUDE)/top_module_name.h
	@mkdir -p $(BUILD)
	@mkdir -p $(OBJ_DIR)
	@$(VERILATOR) $(VERILATOR_CFLAGS) $(VERILOG_FILES) $(CPP_FILES)

$(TARGET): $(OBJ_DIR)/V$(TOPNAME).mk
	@echo "cpp ----g++----> exe"
	@mkdir -p $(BIN)
	@make -f $(OBJ_DIR)/V$(TOPNAME).mk -C $(OBJ_DIR) CXXFLAGS="$(FLAGS)" $(MAKE_FLAGS)
	@mv $(OBJ_DIR)/V$(TOPNAME) $(BIN)

sim:$(TARGET)
	@echo "show wavefrom in gtkwave"
	@mkdir -p $(WAVEFROM)
	@$(BIN)/V$(TOPNAME)
	@gtkwave $(WAVEFROM_FILE)

run:sim
	


clean:
	@rm $(BUILD) -rf
	@rm $(BIN) -rf 

lint:
	@$(VERILATOR) --lint-only -Wall $(VERILOG_FILES)
tb:$(SIM_CONFIG_FILE)
$(SIM_CONFIG_FILE): 
	@python --version
	@rm $(SIM_CONFIG_FILE) -f
	@python $(TESTBENCH_TOOL) $(TESTBENCH_FILE) $(SIM_CONFIG_FILE)



