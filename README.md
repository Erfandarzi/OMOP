

![complex-radiotherapy-data-model](https://github.com/user-attachments/assets/1fbfc9ae-a830-4bf9-b809-6eaa8796d5e3)

# Radiotherapy Data Integration into OMOP CDM

## Project Overview

This project aims to extend the Observational Medical Outcomes Partnership (OMOP) Common Data Model (CDM) to incorporate radiotherapy (RT) data from DICOM files. The goal is to standardize RT data representation within the OMOP framework, facilitating large-scale analysis and research in radiation oncology.

## Current State

We have developed a Python script that serves as a foundation for extracting RT data from DICOM files and structuring it in a format compatible with our proposed OMOP CDM extension. The script currently:

1. Reads DICOM files (including RT-specific files like RTPLAN, RTSTRUCT, and RTDOSE)
2. Extracts relevant information into two main structures: `rt_occurrences` and `rt_features`
3. Converts these structures into pandas DataFrames
4. Optionally saves the results to CSV files

## Project Structure

```
/
├── DICOM.py              # Main Python script for DICOM processing
├── requirements.txt      # Python dependencies
├── sample_output/        # Directory containing sample output CSV files
└── README.md             # This file
```

## How to Use

1. Ensure you have Python 3.7+ installed.
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Update the `directory` variable in `DICOM.py` to point to your DICOM files.
4. Run the script:
   ```
   python DICOM.py
   ```

## Current Limitations

- The script does not yet map extracted data to OMOP concepts.
- Integration with existing OMOP tables is not implemented.
- The full range of RT-specific data is not captured, especially for complex objects like RTPLAN and RTSTRUCT.
- Data is not loaded into an actual OMOP CDM database structure.

## Next Steps

1. Enhance data extraction for all RT modalities
2. Develop OMOP concept mapping for RT-specific data
3. Implement integration with existing OMOP tables
4. Extend OMOP vocabulary for RT concepts
5. Develop database integration for inserting data into OMOP CDM structure
6. Implement data validation and error handling
7. Create comprehensive documentation and testing suite

## Contributing

This project is part of a collaborative effort to standardize RT data within the OMOP framework. 

