import pydicom
import os
import pandas as pd
from zipfile import ZipFile
import hashlib
from prettytable import PrettyTable

# Define OMOP concept IDs (these would normally come from a standardized vocabulary)
CONCEPT_IDS = {
    'RTPLAN': 1000,
    'RTDOSE': 1001,
    'RTSTRUCT': 1002,
    'RTIMAGE': 1003,
    'CT': 1004,
    'MR': 1005,
    'BEAM': 1006,
    'DOSE': 1007,
    'STRUCTURE': 1008,
    'GY': 1009,
    'MM': 1010,
}

def read_dicom_file(file_path):
    if file_path.endswith('.zip'):
        with ZipFile(file_path, 'r') as zip_file:
            file_name = zip_file.namelist()[0]  # Assume single file in zip
            with zip_file.open(file_name) as dicom_file:
                return pydicom.dcmread(dicom_file)
    else:
        return pydicom.dcmread(file_path)

def generate_id(input_string):
    return int(hashlib.md5(input_string.encode()).hexdigest(), 16) % (10 ** 8)

def extract_rt_occurrence(dicom_data):
    return {
        'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
        'person_id': generate_id(dicom_data.PatientID),
        'visit_occurrence_id': generate_id(f"{dicom_data.PatientID}_{dicom_data.StudyDate}"),
        'rt_concept_id': CONCEPT_IDS.get(dicom_data.Modality, 0),
        'rt_start_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
        'rt_end_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
        'rt_type_concept_id': 0,  # This would come from a standardized vocabulary
        'rt_source_value': dicom_data.Modality,
    }

def extract_rt_plan(dicom_data):
    features = []
    if hasattr(dicom_data, 'BeamSequence'):
        for beam in dicom_data.BeamSequence:
            features.append({
                'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_{beam.BeamNumber}"),
                'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                'feature_concept_id': CONCEPT_IDS['BEAM'],
                'value_as_number': beam.NumberOfControlPoints,
                'value_as_string': getattr(beam, 'BeamName', 'Unknown'),
                'value_as_concept_id': 0,  # This would come from a standardized vocabulary
                'unit_concept_id': None,
                'feature_date': dicom_data.StudyDate,
                'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
                'feature_type_concept_id': 0,  # This would come from a standardized vocabulary
            })
    return features

def extract_rt_dose(dicom_data):
    return [{
        'rt_feature_id': generate_id(dicom_data.SOPInstanceUID),
        'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
        'feature_concept_id': CONCEPT_IDS['DOSE'],
        'value_as_number': getattr(dicom_data, 'DoseGridScaling', None),
        'value_as_string': f"Dose Units: {getattr(dicom_data, 'DoseUnits', 'Unknown')}",
        'value_as_concept_id': 0,  # This would come from a standardized vocabulary
        'unit_concept_id': CONCEPT_IDS['GY'],
        'feature_date': dicom_data.StudyDate,
        'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
        'feature_type_concept_id': 0,  # This would come from a standardized vocabulary
    }]

def extract_rt_struct(dicom_data):
    features = []
    if hasattr(dicom_data, 'StructureSetROISequence'):
        for roi in dicom_data.StructureSetROISequence:
            features.append({
                'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_{roi.ROINumber}"),
                'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                'feature_concept_id': CONCEPT_IDS['STRUCTURE'],
                'value_as_string': roi.ROIName,
                'value_as_concept_id': 0,  # This would come from a standardized vocabulary
                'unit_concept_id': None,
                'feature_date': dicom_data.StudyDate,
                'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
                'feature_type_concept_id': 0,  # This would come from a standardized vocabulary
            })
    return features

def extract_rt_image(dicom_data):
    return [{
        'rt_feature_id': generate_id(dicom_data.SOPInstanceUID),
        'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
        'feature_concept_id': CONCEPT_IDS[dicom_data.Modality],
        'value_as_number': getattr(dicom_data, 'SliceThickness', None),
        'value_as_string': f"Slice Thickness: {getattr(dicom_data, 'SliceThickness', 'Unknown')}",
        'value_as_concept_id': 0,  # This would come from a standardized vocabulary
        'unit_concept_id': CONCEPT_IDS['MM'],
        'feature_date': dicom_data.StudyDate,
        'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
        'feature_type_concept_id': 0,  # This would come from a standardized vocabulary
    }]

def process_dicom_files(directory):
    rt_occurrences = []
    rt_features = []

    for filename in os.listdir(directory):
        if filename.endswith('.IMA') or filename.endswith('.zip'):
            file_path = os.path.join(directory, filename)
            try:
                dicom_data = read_dicom_file(file_path)
                
                rt_occurrences.append(extract_rt_occurrence(dicom_data))
                
                if dicom_data.Modality == 'RTPLAN':
                    rt_features.extend(extract_rt_plan(dicom_data))
                elif dicom_data.Modality == 'RTDOSE':
                    rt_features.extend(extract_rt_dose(dicom_data))
                elif dicom_data.Modality == 'RTSTRUCT':
                    rt_features.extend(extract_rt_struct(dicom_data))
                elif dicom_data.Modality in ['CT', 'MR', 'RTIMAGE']:
                    rt_features.extend(extract_rt_image(dicom_data))
                
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")

    return rt_occurrences, rt_features

# Main execution
directory = '../'
rt_occurrences, rt_features = process_dicom_files(directory)

# Convert to DataFrames
rt_occurrences_df = pd.DataFrame(rt_occurrences)
rt_features_df = pd.DataFrame(rt_features)

print(rt_occurrences_df)
print(rt_features_df)

# Save to CSV
rt_occurrences_df.to_csv('rt_occurrences.csv', index=False)
rt_features_df.to_csv('rt_features.csv', index=False)

# After creating the DataFrames:
rt_occurrences_df = pd.DataFrame(rt_occurrences)
rt_features_df = pd.DataFrame(rt_features)

# Function to create a pretty table from a dataframe
def dataframe_to_pretty_table(df, title):
    table = PrettyTable()
    table.title = title
    table.field_names = df.columns
    for row in df.itertuples(index=False):
        table.add_row(row)
    return table

# Create pretty tables
occurrences_table = dataframe_to_pretty_table(rt_occurrences_df, "RT Occurrences")
features_table = dataframe_to_pretty_table(rt_features_df, "RT Features")

# Print tables
print(occurrences_table)
print("\n")
print(features_table)
