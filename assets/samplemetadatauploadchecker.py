import numpy as np
import pandas as pd
import openpyxl
import json
import io
import base64

class SampleMetadataUploadChecker:
    '''
    for all of these, if they return true, there is a problem
    '''

    def __init__(self,content_string,header_address):
        self.content_string=content_string
        with open(header_address,'r') as f:
            self.header_json=json.load(f)
        
    def create_workbook(self):
        decoded=base64.b64decode(self.content_string)
        self.workbook=openpyxl.load_workbook(io.BytesIO(decoded))

    def lacks_sheetname(self):
        return ('sample_sheet' not in self.workbook.sheetnames)

    def create_dataframe(self):
        decoded=base64.b64decode(self.content_string)
        self.dataframe=pd.read_excel(
            io.BytesIO(decoded),
            sheet_name='sample_sheet',
            skiprows=1
        )

    def headers_malformed(self):
        total_header_set=set()
        for temp_archetype in self.header_json.keys():
            total_header_set=total_header_set.union(self.header_json[temp_archetype])
        presented_columns=set(self.dataframe.columns)
        malformed_columns=presented_columns.difference(total_header_set)
        if len(malformed_columns)>0:
            return malformed_columns
        else:
            return False

    def contains_underscore(self):
        return np.any(
            self.sample_df.stack().astype(str).str.contains('_').values
        )

    def contains_no_sample_rows(self):
        if len(self.sample_df.index)==0:
            return True
        else:
            return False

if __name__=="__main__":

    sample_excel_address='/home/rictuar/Downloads/PRESENTATION.xlsx'

    my_SampleMetadataUploadChecker=SampleMetadataUploadChecker(
        content_string,
        header_address
    )
    my_SampleMetadataUploadChecker.create_workbook()
    my_SampleMetadataUploadChecker.lacks_sheetname()
    my_SampleMetadataUploadChecker.create_dataframe()
    my_SampleMetadataUploadChecker.headers_malformed()
    my_SampleMetadataUploadChecker.contains_underscore()
    my_SampleMetadataUploadChecker.contains_no_sample_rows()
