import boto3
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO

class S3DataBucket:

    def __init__(self):
        
        # loading the environmental variables
        load_dotenv(dotenv_path= "/app/.env")

        # define standard Bedrock configuration
        region_name = os.getenv("AWS_REGION")
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        self.file_path = "/app/data/medical_data.csv"
        # self.file_path = "../data/medical_data.csv"
        self.s3_key = "data/medical_data.csv"

        self.s3_client = boto3.client(
            service_name='s3',
            region_name=region_name
            )

    def s3_data_upload(self):

        self.s3_client.upload_file(self.file_path, self.bucket_name, self.s3_key)

        print(f"Uploaded file to s3 bucket {self.bucket_name}")

    def s3_get_data(self):

        # Download file content
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.s3_key)
        csv_content = response['Body'].read().decode('utf-8')

        # Load into pandas
        df = pd.read_csv(StringIO(csv_content))
        print(" === Fetched data from S3 Bucket === \n")
        print(" === Head of the dataframe === \n")
        print(df.head())
        print("\n === Columns of the dataframe === \n")
        print(df.columns)

        return df

if __name__=="__main__":

    s3_obj = S3DataBucket()

    # # calling s3_data_upload to upload data
    # s3_obj.s3_data_upload()

    # calling to get the data from s3 bucket
    df = s3_obj.s3_get_data()
    print(df.head())
