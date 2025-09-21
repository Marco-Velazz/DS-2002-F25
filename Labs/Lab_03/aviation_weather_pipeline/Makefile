.PHONY: all fetch analyze clean

# Default target
all: analyze

fetch:
	@echo "Starting fetch: downloading METAR data into raw_metars/..."
	./fetch_metars.sh
	@echo "Finished fetch: data saved in raw_metars/."

analyze: fetch
	@echo "Starting analyze: processing JSON into weather_report.csv..."
	./analyze_data.sh
	@echo "Finished analyze: results are in weather_report.csv."
	@echo "Pipeline completed successfully!"

clean:
	@echo "Cleaning up generated files..."
	rm -rf raw_metars weather_report.csv
	@echo "Cleanup complete."
