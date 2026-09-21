# Alternativa a scripts/build.py para Linux/macOS/MSYS2 con g++.
CXX ?= g++
FLAGS = -std=c++17 -Wall -Wextra -Wpedantic -Wshadow -Wconversion -O1 -g
build/tests: cpp/tests.cpp cpp/segment_tree.hpp cpp/trace_recorder.hpp
	mkdir -p build && $(CXX) $(FLAGS) cpp/tests.cpp -o $@
build/tests_san: cpp/tests.cpp cpp/segment_tree.hpp
	mkdir -p build && $(CXX) $(FLAGS) -fsanitize=address,undefined cpp/tests.cpp -o $@
build/demo_trace: cpp/demo_trace.cpp cpp/segment_tree.hpp cpp/trace_recorder.hpp
	mkdir -p build && $(CXX) $(FLAGS) cpp/demo_trace.cpp -o $@
test: build/tests build/tests_san
	./build/tests && ./build/tests_san
trace: build/demo_trace
	./build/demo_trace trace/trace_demo.json
