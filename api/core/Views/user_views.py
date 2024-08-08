# core/views/user_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.serializers import UserSerializer, ProfileSerializer, GroupSerializer
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Profile
from core.models.historyc_models import OperationLog
from core.serializers import UserSerializer, ProfileSerializer
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from ..middleware import OperationLogMiddleware
from ..check_manager import IsManager


class CreateUserView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            group_name = request.data.get('group', 'customers')
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            profile_data = {'user': user.id}
            profile_serializer = ProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
            refresh = RefreshToken.for_user(user)
            
            # Update request body to include the new object's ID
            request.body_data['object_id'] = user.id
            
            return Response({
                'id': user.id,
                'user': serializer.data,
                'profile': profile_serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, format=None):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

class GroupListView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'id': user.id,
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk, format=None):
        request.data['model'] = 'user'
        request.data['operation'] = 'UPDATE'
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'id': user.id,
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        content_type = ContentType.objects.get(model='user')
        
        # Log the delete operation before deleting the user
        OperationLog.objects.create(
            user=request.user,
            action="DELETE",
            content_type=content_type,
            object_id=user.id,
            object_repr=f"user {user.id}",
            change_message=f"User {request.user} performed DELETE on user {user.id}"
        )
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
