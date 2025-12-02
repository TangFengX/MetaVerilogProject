TOPNAME = top
VERILATOR = verilator
WAVEFROM_NAME = wavefrom.fst
#路径
PWD=$(shell pwd)

BUILD=$(PWD)/build




BIN=$(PWD)/bin
CSRC=$(PWD)/src/csrc
VSRC=$(PWD)/src/vsrc
TOP_MODULE_FILE=$(if $(wildcard $(VSRC)/$(TOPNAME).v),$(VSRC)/$(TOPNAME).v,(if $(wildcard $(VSRC)/$(TOPNAME).sv),$(VSRC)/$(TOPNAME).sv,))

OBJ_DIR=$(BUILD)/obj_dir
INCLUDE = $(PWD)/include

INCLUDES = $(INCLUDE) $(OBJ_DIR)


VERILOG_FILES := $(wildcard $(VSRC)/*.v $(VSRC)/*.sv)
CPP_FILES := $(wildcard $(CSRC)/*.c $(CSRC)/*.cc $(CSRC)/*.cpp)
pcpp:
	@echo $(CPP_FILES)


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








toc:
	@echo "verilog ----verilator----> cpp"
	@rm  $(OBJ_DIR)/* -rf
	@echo "#include \"V$(TOPNAME).h\"" > $(INCLUDE)/top_module_name.h
	@mkdir -p $(BUILD)
	@mkdir -p $(OBJ_DIR)
	@$(VERILATOR) $(VERILATOR_CFLAGS) $(VERILOG_FILES) $(CPP_FILES)

mk:
	@echo "cpp ----g++----> exe"
	@mkdir -p $(BIN)
	@make -f $(OBJ_DIR)/V$(TOPNAME).mk -C $(OBJ_DIR) CXXFLAGS="$(FLAGS)" $(MAKE_FLAGS)
	@mv $(OBJ_DIR)/V$(TOPNAME) $(BIN)

sim:
	@echo "show wavefrom in gtkwave"
	@mkdir -p $(WAVEFROM)
	@$(BIN)/V$(TOPNAME)
	@gtkwave $(WAVEFROM_FILE)

run:
	@make toc
	@make mk
	@make sim


clean:
	@rm $(BUILD) -rf
	@rm $(BIN) -rf 

lint:
	@$(VERILATOR) --lint-only -Wall $(VERILOG_FILES)



