from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from .serializers import (GroupSerializer, UserSerializer, CategorySerializer,
                          StatusSerializer, TagSerializer, TaskSerializer,)
from .models import Category, Status, Tag, Task, TaskAssignment


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all().order_by('-id')
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticated]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if user.is_superuser:
            queryset = Task.objects.all().order_by('-id')
        else:
            queryset = Task.objects.filter(taskassignment__user=user).order_by('-id')

        return queryset