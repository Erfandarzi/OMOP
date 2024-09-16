import pydicom
import os
from zipfile import ZipFile
from collections import defaultdict

def read_dicom_file(file_path):
    if file_path.endswith('.zip'):
        with ZipFile(file_path, 'r') as zip_file:
            file_name = zip_file.namelist()[0]  # Assume single file in zip
            with zip_file.open(file_name) as dicom_file:
                return pydicom.dcmread(dicom_file)
    else:
        return pydicom.dcmread(file_path)

def print_dicom_info(dicom_data):
    print(f"SOP Class: {dicom_data.SOPClassUID}")
    print(f"Modality: {getattr(dicom_data, 'Modality', 'N/A')}")
    print(f"Study Date: {getattr(dicom_data, 'StudyDate', 'N/A')}")
    print(f"Series Date: {getattr(dicom_data, 'SeriesDate', 'N/A')}")
    print(f"Manufacturer: {getattr(dicom_data, 'Manufacturer', 'N/A')}")
    print(f"Institution Name: {getattr(dicom_data, 'InstitutionName', 'N/A')}")
    print("\nAvailable Tags:")
    for elem in dicom_data:
        if elem.tag.is_private:
            print(f"  {elem.tag}: {elem.name} (Private)")
        else:
            print(f"  {elem.tag}: {elem.name}")
    print("\n")

def process_dicom_files(directory):
    tag_summary = defaultdict(int)

    for filename in os.listdir(directory):
        if filename.endswith('.IMA') or filename.endswith('.zip'):
            file_path = os.path.join(directory, filename)
            try:
                dicom_data = read_dicom_file(file_path)
                print(f"File: {filename}")
                print_dicom_info(dicom_data)
                
                # Count occurrences of each tag
                for elem in dicom_data:
                    tag_summary[elem.tag] += 1
                
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")

    print("Tag Summary:")
    for tag, count in sorted(tag_summary.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {pydicom.datadict.keyword_for_tag(tag)} (occurs in {count} files)")

# Main execution
directory = '../'
process_dicom_files(directory)