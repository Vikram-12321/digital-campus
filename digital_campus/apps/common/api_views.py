"""
users/api_views.py

API views for the users app.
Currently supports:
- Course detail lookup by name (case-insensitive)

Author: Vikram Bhojanala
Last updated: 2025-05-09
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.request import Request

from .models import Course
from .serializers import CourseSerializer


class CourseDetailView(APIView):
    """
    Retrieve course details by name (case-insensitive).

    Example:
        GET /api/courses/MAT137/
    """

    def get(self, request: Request, name: str) -> Response:
        name = name.strip()
        course = get_object_or_404(Course, name__iexact=name)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
