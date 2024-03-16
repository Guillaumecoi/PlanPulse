from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework import status, permissions
from .serializers import CreateCourseSerializer
from .models.models import Course


class CreateCourseView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        serializer = CreateCourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)