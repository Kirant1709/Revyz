from django.shortcuts import render
from app1.models import Student
from app1.serializers import StudentSerializer
from app1.pagination import MyPagination
from rest_framework import generics


import os
import io
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, StreamingHttpResponse
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter

# Create your views here.

#Api 1: to list all students
class StudentAPIView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = MyPagination
    search_fields = ('=location','tech_skills')


#API2: to create a student and generate its resume and upload it to s3

class StudentCreateAPIView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer  

    def post(self, request, *args, **kwargs):
            serializer = StudentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                # Create a response object with appropriate content type
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="resume.pdf"'

                # Create a PDF document
                doc = SimpleDocTemplate(response, pagesize=letter)
                pdf_buffer = io.BytesIO()

                # Content for the PDF
                content = []

                # Extract data from the validated serializer
                resume_data = serializer.validated_data
                content.append(f"Name: {resume_data['name']}")
                content.append(f"phone number: {resume_data['phone_number']}")
                content.append(f"email: {resume_data['email']}")
                content.append(f"tech_skills: {resume_data['tech_skills']}")
                # Add more fields as needed

                # Build the PDF document
                table = Table([content])
                doc.build([table])

                # Save the PDF to S3
                try:
                    s3 = boto3.client(
                        's3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME
                    )
                    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                    file_name = f"resumes/{serializer.validated_data['name']}_resume.pdf"
                    s3.upload_fileobj(pdf_buffer, bucket_name, file_name)
        

                    return Response({"message": "Student resume PDF generated and saved to S3."}, status=201)
                except NoCredentialsError:
                    return Response({"message": "AWS credentials not available."}, status=400)
            return Response(serializer.errors, status=400)
    

#API3: to fetch Student resume
class StudentResumeView(APIView):
    def get(self, request, name, format=None):
        s3 = boto3.client('s3')
        bucket_name = 'studresume'
        
        key = f'{name}'

        try:
            response = s3.get_object(Bucket=bucket_name, Key=key)
            pdf_content = response['Body'].read()

            response = StreamingHttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{key}"'
            return response
        except Exception as e:
            return Response({'error': 'PDF not found'}, status=404)
        


        