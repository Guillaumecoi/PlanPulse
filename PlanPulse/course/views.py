from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateCourseSerializer
from .models.models import Course


class CreateCourseView(APIView):
    serializer_class = CreateCourseSerializer

    def post(self, request):
        if not self.request.user.is_authenticated:
            return Response({"error": "You must be logged in to create a course"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateCourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    