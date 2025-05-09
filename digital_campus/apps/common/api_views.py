"""
users/api_views.py

API views for the users app.
Currently supports:
- Course detail lookup by name (case-insensitive)

Author: Your Name or Team
Last updated: 2025-05-02
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Course
from .serializers import CourseSerializer


class CourseDetailView(APIView):
    """
    Returns course detail for a given course name.
    The lookup is case-insensitive.
    """

    def get(self, request, name):
        try:
            course = Course.objects.get(name__iexact=name)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
