from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import Category, Status, Tag, Task, TaskAssignment


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'sub_category', 'user']

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data.pop('user', None)
        return super().create(validated_data)


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    is_completed = serializers.BooleanField(required=False, allow_null=True)
    status = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=False, allow_null=True)
    sub_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), required=False, allow_null=True)
    task_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False, allow_null=True
    )
    class Meta:
        model = Task
        fields = ['id',
                  'name',
                  'description',
                  'is_completed',
                  'status',
                  'due_date',
                  'created_at',
                  'updated_at',
                  'sub_task',
                  'task_category',
                  'tags']

    def create(self, validated_data):
        new_task = super().create(validated_data)
        user = self.context['request'].user
        task_assignment = TaskAssignment.objects.create(task=new_task, user=user, created_by=user)
        
        return new_task
