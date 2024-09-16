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

CONCEPT_IDS = {
    # Modalities
    'RTPLAN': 1000,
    'RTDOSE': 1001,
    'RTSTRUCT': 1002,
    'RTIMAGE': 1003,
    'CT': 1004,
    'MR': 1005,

    # General concepts
    'BEAM': 1006,
    'DOSE': 1007,
    'STRUCTURE': 1008,
    'GY': 1009,
    'MM': 1010,
    'FRACTION': 1011,

    # RT Plan specific
    'PLAN_LABEL': 1012,
    'PLAN_NAME': 1013,
    'PLAN_DESCRIPTION': 1014,
    'PLAN_DATE': 1015,
    'PLAN_TIME': 1016,
    'PLAN_INTENT': 1017,
    'PLAN_GEOMETRY': 1018,
    'PRESCRIPTION_DESCRIPTION': 1019,
    'NUMBER_OF_FRACTIONS_PLANNED': 1020,

    # Dose specific
    'DOSE_TYPE': 1021,
    'DOSE_SUMMARY_TYPE': 1022,
    'DOSE_GRID_SCALING': 1023,
    'DOSE_UNITS': 1024,

    # Structure Set specific
    'STRUCTURE_SET_LABEL': 1025,
    'STRUCTURE_SET_NAME': 1026,
    'STRUCTURE_SET_DESCRIPTION': 1027,
    'STRUCTURE_SET_DATE': 1028,
    'STRUCTURE_SET_TIME': 1029,
    'ROI_NAME': 1030,
    'ROI_DESCRIPTION': 1031,
    'ROI_VOLUME': 1032,

    # Treatment specific
    'TREATMENT_MACHINE': 1033,
    'TREATMENT_DATE': 1034,
    'TREATMENT_TIME': 1035,
    'CURRENT_TREATMENT_STATUS': 1036,
    'TREATMENT_POSITION': 1037,

    # Image specific
    'IMAGE_TYPE': 1038,
    'PIXEL_SPACING': 1039,
    'SLICE_THICKNESS': 1040,
    'IMAGE_POSITION_PATIENT': 1041,
    'IMAGE_ORIENTATION_PATIENT': 1042,
    'PATIENT_POSITION': 1043,
    'RT_IMAGE_PLANE': 1044,
    'RT_IMAGE_POSITION': 1045,
    'IMAGE_PLANE_PIXEL_SPACING': 1046,

    # Machine and setup specific
    'GANTRY_ANGLE': 1047,
    'PATIENT_SUPPORT_ANGLE': 1048,
    'TABLE_TOP_VERTICAL_POSITION': 1049,
    'TABLE_TOP_LONGITUDINAL_POSITION': 1050,
    'TABLE_TOP_LATERAL_POSITION': 1051,
    'TABLE_TOP_PITCH_ANGLE': 1052,
    'TABLE_TOP_ROLL_ANGLE': 1053,
    'SAD': 1054,  # Source to Axis Distance
    'SID': 1055,  # Source to Image Distance

    # Beam specific
    'BEAM_NUMBER': 1056,
    'BEAM_NAME': 1057,
    'BEAM_DESCRIPTION': 1058,
    'RADIATION_TYPE': 1059,
    'BEAM_TYPE': 1060,
    'BEAM_DOSE': 1061,
    'BEAM_MU': 1062,
    'NUMBER_OF_CONTROL_POINTS': 1063,

    # DVH specific
    'DVH_TYPE': 1064,
    'DVH_DOSE_UNITS': 1065,
    'DVH_VOLUME_UNITS': 1066,
    'DVH_MINIMUM_DOSE': 1067,
    'DVH_MAXIMUM_DOSE': 1068,
    'DVH_MEAN_DOSE': 1069,

    # Patient specific
    'PATIENT_NAME': 1070,
    'PATIENT_ID': 1071,
    'PATIENT_BIRTH_DATE': 1072,
    'PATIENT_SEX': 1073,
    'PATIENT_AGE': 1074,
    'PATIENT_SIZE': 1075,
    'PATIENT_WEIGHT': 1076,

    # Study specific
    'STUDY_INSTANCE_UID': 1077,
    'STUDY_DATE': 1078,
    'STUDY_TIME': 1079,
    'STUDY_DESCRIPTION': 1080,

    # Series specific
    'SERIES_INSTANCE_UID': 1081,
    'SERIES_NUMBER': 1082,
    'SERIES_DESCRIPTION': 1083,

    # Equipment specific
    'MANUFACTURER': 1084,
    'MANUFACTURER_MODEL_NAME': 1085,
    'SOFTWARE_VERSIONS': 1086,

    # Institution specific
    'INSTITUTION_NAME': 1087,
    'INSTITUTIONAL_DEPARTMENT_NAME': 1088,

    # Physician specific
    'REFERRING_PHYSICIAN_NAME': 1089,
    'OPERATORS_NAME': 1090,

    # Approval status
    'APPROVAL_STATUS': 1091,
    'REVIEW_DATE': 1092,
    'REVIEW_TIME': 1093,
    'REVIEWER_NAME': 1094,
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
    
    # List of attributes to extract from RT Plan
    rt_plan_attributes = [
        ('RTPlanLabel', 'PLAN_LABEL'),
        ('RTPlanName', 'PLAN_NAME'),
        ('RTPlanDescription', 'PLAN_DESCRIPTION'),
        ('RTPlanDate', 'PLAN_DATE'),
        ('RTPlanTime', 'PLAN_TIME'),
        ('PlanIntent', 'PLAN_INTENT'),
        ('RTPlanGeometry', 'PLAN_GEOMETRY'),
        ('PrescriptionDescription', 'PRESCRIPTION_DESCRIPTION'),
        ('NumberOfFractionsPlanned', 'NUMBER_OF_FRACTIONS_PLANNED'),
    ]
    
    for dicom_attr, concept_name in rt_plan_attributes:
        if hasattr(dicom_data, dicom_attr):
            value = getattr(dicom_data, dicom_attr)
            features.append({
                'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_{concept_name}"),
                'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                'feature_concept_id': CONCEPT_IDS[concept_name],
                'value_as_string': str(value),
                'value_as_number': value if isinstance(value, (int, float)) else None,
                'feature_date': dicom_data.StudyDate,
                'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
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
    
    # Extract Structure Set information
    struct_set_attributes = [
        ('StructureSetLabel', 'STRUCTURE_SET_LABEL'),
        ('StructureSetName', 'STRUCTURE_SET_NAME'),
        ('StructureSetDescription', 'STRUCTURE_SET_DESCRIPTION'),
        ('StructureSetDate', 'STRUCTURE_SET_DATE'),
        ('StructureSetTime', 'STRUCTURE_SET_TIME'),
    ]
    
    for dicom_attr, concept_name in struct_set_attributes:
        if hasattr(dicom_data, dicom_attr):
            value = getattr(dicom_data, dicom_attr)
            features.append({
                'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_{concept_name}"),
                'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                'feature_concept_id': CONCEPT_IDS[concept_name],
                'value_as_string': str(value),
                'feature_date': dicom_data.StudyDate,
                'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
            })
    
    # Extract ROI information
    if hasattr(dicom_data, 'StructureSetROISequence'):
        for roi in dicom_data.StructureSetROISequence:
            roi_number = roi.ROINumber
            roi_name = roi.ROIName
            roi_description = getattr(roi, 'ROIDescription', '')
            
            features.extend([
                {
                    'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_ROI_{roi_number}_NAME"),
                    'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                    'feature_concept_id': CONCEPT_IDS['ROI_NAME'],
                    'value_as_string': roi_name,
                    'feature_date': dicom_data.StudyDate,
                    'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
                },
                {
                    'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_ROI_{roi_number}_DESCRIPTION"),
                    'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                    'feature_concept_id': CONCEPT_IDS['ROI_DESCRIPTION'],
                    'value_as_string': roi_description,
                    'feature_date': dicom_data.StudyDate,
                    'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
                }
            ])
    
    # Extract ROI Contour information (if available)
    if hasattr(dicom_data, 'ROIContourSequence'):
        for roi_contour in dicom_data.ROIContourSequence:
            if hasattr(roi_contour, 'ContourSequence'):
                roi_number = roi_contour.ReferencedROINumber
                contour_count = len(roi_contour.ContourSequence)
                features.append({
                    'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_ROI_{roi_number}_CONTOUR_COUNT"),
                    'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                    'feature_concept_id': CONCEPT_IDS['ROI_VOLUME'],  # Using ROI_VOLUME as a proxy for contour information
                    'value_as_number': contour_count,
                    'value_as_string': f"Number of contours: {contour_count}",
                    'feature_date': dicom_data.StudyDate,
                    'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
                })
    
    return features

def extract_rt_image(dicom_data):
    features = []
    
    # Extract general image information
    image_attributes = [
        ('ImageType', 'IMAGE_TYPE'),
        ('PixelSpacing', 'PIXEL_SPACING'),
        ('SliceThickness', 'SLICE_THICKNESS'),
        ('ImagePositionPatient', 'IMAGE_POSITION_PATIENT'),
        ('ImageOrientationPatient', 'IMAGE_ORIENTATION_PATIENT'),
        ('PatientPosition', 'PATIENT_POSITION'),
        ('RTImagePlane', 'RT_IMAGE_PLANE'),
        ('RTImagePosition', 'RT_IMAGE_POSITION'),
        ('ImagePlanePixelSpacing', 'IMAGE_PLANE_PIXEL_SPACING'),
    ]
    
    for dicom_attr, concept_name in image_attributes:
        if hasattr(dicom_data, dicom_attr):
            value = getattr(dicom_data, dicom_attr)
            features.append({
                'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_{concept_name}"),
                'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                'feature_concept_id': CONCEPT_IDS[concept_name],
                'value_as_string': str(value),
                'value_as_number': value[0] if isinstance(value, (list, tuple)) and len(value) > 0 else None,
                'feature_date': dicom_data.StudyDate,
                'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
            })
    
    # Extract machine and setup information
    setup_attributes = [
        ('GantryAngle', 'GANTRY_ANGLE'),
        ('PatientSupportAngle', 'PATIENT_SUPPORT_ANGLE'),
        ('TableTopVerticalPosition', 'TABLE_TOP_VERTICAL_POSITION'),
        ('TableTopLongitudinalPosition', 'TABLE_TOP_LONGITUDINAL_POSITION'),
        ('TableTopLateralPosition', 'TABLE_TOP_LATERAL_POSITION'),
        ('TableTopPitchAngle', 'TABLE_TOP_PITCH_ANGLE'),
        ('TableTopRollAngle', 'TABLE_TOP_ROLL_ANGLE'),
        ('RadiationMachineSAD', 'SAD'),
        ('RTImageSID', 'SID'),
    ]
    
    for dicom_attr, concept_name in setup_attributes:
        if hasattr(dicom_data, dicom_attr):
            value = getattr(dicom_data, dicom_attr)
            features.append({
                'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_{concept_name}"),
                'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                'feature_concept_id': CONCEPT_IDS[concept_name],
                'value_as_number': float(value) if value is not None else None,
                'value_as_string': str(value),
                'feature_date': dicom_data.StudyDate,
                'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
            })
    
    # Extract exposure information
    if hasattr(dicom_data, 'ExposureSequence'):
        for i, exposure in enumerate(dicom_data.ExposureSequence):
            if hasattr(exposure, 'KVP'):
                features.append({
                    'rt_feature_id': generate_id(f"{dicom_data.SOPInstanceUID}_KVP_{i}"),
                    'rt_occurrence_id': generate_id(dicom_data.SOPInstanceUID),
                    'feature_concept_id': CONCEPT_IDS['KVP'],
                    'value_as_number': float(exposure.KVP),
                    'value_as_string': f"KVP: {exposure.KVP}",
                    'feature_date': dicom_data.StudyDate,
                    'feature_datetime': f"{dicom_data.StudyDate}{getattr(dicom_data, 'StudyTime', '')}",
                })
    
    return features

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
