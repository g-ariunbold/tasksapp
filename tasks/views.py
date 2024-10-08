from django.contrib.auth.models import Group, User
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .serializers import (GroupSerializer, UserSerializer, CategorySerializer,
                          StatusSerializer, TagSerializer, TaskSerializer,)
from .models import Category, Status, Tag, Task, TaskAssignment

class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.created_by == request.user

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

class TaskFilter(filters.FilterSet):
    created_by = filters.NumberFilter(field_name='created_by', lookup_expr='exact')
    class Meta:
        model = Task
        fields = {
            'name': ['exact', 'icontains'],
            'is_completed': ['exact'],
            'created_at': ['lt', 'gt', 'exact'],
            'created_by': ['exact'],
        }

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.none()
    serializer_class = TaskSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaskFilter
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if user.is_superuser:
            queryset = Task.objects.all().order_by('-id')
        else:
            queryset = Task.objects.filter(Q(created_by=user) | Q(taskassignment__user=user)).order_by('-id')
        return queryset

    def perform_create(self, serializer):
        try:
            self._check_for_assigned_user_ids(self.request.user, serializer.validated_data)
        except PermissionDenied as e:
            raise PermissionDenied(e)
        serializer.save()

    def perform_update(self, serializer):
        try:
            self._check_for_assigned_user_ids(self.request.user, serializer.validated_data)
        except PermissionDenied as e:
            raise PermissionDenied(e)
        serializer.save()

    # def perform_destroy(self, instance):
    #     if not self.request.user.is_staff:
    #         raise PermissionDenied("Only admin users can delete tasks.")
    #     instance.delete()
    
    def _check_for_assigned_user_ids(self, user, validated_data):
        if not user.is_staff and 'assigned_user_ids' in validated_data:
            raise PermissionDenied("Only admin users can assign tasks to other users.")