
# To trace and anslyse case.py

case:
	@echo "*** tracing case ***\n" && python3 trace.py case.py
	@echo "*** anslysing case ***\n" && python3 analyse.py

clean:
	rm -rf __pycache__ && rm -f \
	trace_result.txt coverage.txt analyse_result.txt

.PHONY : case clean
