from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone 
from django.shortcuts import get_object_or_404
from ..models import App_Data
from ..serializer import AppDataSerializer
from ..utils.sanitize import no_html_validator
from ..permissions.authentication import LoginTokenAuthentication
from ..utils.pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated

SANITIZE_FIELDS=["title","url_test","description"]

class AppDataAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

#===========================================GET/GET BY ID================================#
    def get(self, request, id=None):
        if not request.user or not request.user.is_authenticated:
            return Response({"error":"You are logged out please login first"},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            if id:
                app_data= get_object_or_404(App_Data, id=id)
                serializer = AppDataSerializer(app_data)
                return Response({"success": True, "data":serializer.data},status=status.HTTP_200_OK)
            
            queryset = App_Data.objects.all().order_by("-id")

            paginator=CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

            serializer = AppDataSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        except Exception as e:
            return Response({"error":f"Something went wrong:{str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#=========================================POST=====================================#
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response(
            {"error": "You are logged out please login first"},
            status=status.HTTP_401_UNAUTHORIZED
        )

        data = request.data.copy()

        # Sanitize fields
        for field in SANITIZE_FIELDS:
            if field in data and data[field]:
                try:
                    data[field] = no_html_validator(data[field])
                except Exception as e:
                    return Response(
                    {"error": f"Invalid input in {field}: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = AppDataSerializer(data=data)

            if serializer.is_valid():
                serializer.save(created_by=request.user, updated_by=request.user)
                return Response(
            {
                "success": True,
                "message": "Data created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#=============================================PATCH============================#
    def patch(self, request, id):
        if not request.user or not request.user.is_authenticated:
            return Response(
            {"error": "You are logged out please login first"},
            status=status.HTTP_401_UNAUTHORIZED
        )

        try:
                app_data = App_Data.objects.get(id=id)
        except App_Data.DoesNotExist:
            return Response(
            {"error": "Data not found to update"},
            status=status.HTTP_404_NOT_FOUND
        )

        data = request.data.copy()

       # sanitize safely
        for field in SANITIZE_FIELDS:
            if field in data and data[field]:
                try:
                   data[field] = no_html_validator(data[field])
                except Exception as e:
                    return Response(
                    {"error": f"Invalid input in {field}: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = AppDataSerializer(app_data, data=data, partial=True)

        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(
            {
                "success": True,
                "message": "Data updated successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#===========================================DELETE======================================#
    def delete(self, request, id):
        if not request.user or not request.user.is_authenticated:
            return Response({"error":"You are logged out please login first"},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            app_data = App_Data.objects.get(id=id)
        except App_Data.DoesNotExist:
            return Response({"error":"Data not found to delete"},status=status.HTTP_404_NOT_FOUND)
        
        app_data.is_active=False
        app_data.updated_by=request.user
        app_data.updated_at=timezone.now()
        app_data.save()
        return Response({"success":True, "message":"Data deleted successfully"}, status=status.HTTP_200_OK)
    
    