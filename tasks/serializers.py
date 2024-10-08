from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import Category, Status, Tag, Task, TaskAssignment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


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

class TaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = ['id', 'user', 'assigned_at']
        read_only_fields = ['assigned_at']

class TaskSerializer(serializers.ModelSerializer):
    assigned_users = TaskAssignmentSerializer(
        source='taskassignment_set', many=True, read_only=True)
    assigned_user_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'is_completed', 'status', 'due_date', 'created_at',
                  'updated_at', 'sub_task', 'task_category', 'tags', 'assigned_users', 'assigned_user_ids']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        assigned_user_ids = validated_data.pop('assigned_user_ids', [])
        task = Task.objects.create(**validated_data)
        self._create_task_assignments(task, assigned_user_ids)
        return task

    def update(self, instance, validated_data):
        assigned_user_ids = validated_data.pop('assigned_user_ids', None)
        task = super().update(instance, validated_data)
        if assigned_user_ids is not None:
            TaskAssignment.objects.filter(task=task).delete()
            self._create_task_assignments(task, assigned_user_ids)
        return task
    def _create_task_assignments(self, task, user_ids):
        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            TaskAssignment.objects.create(
                task=task, user=user, created_by=self.context['request'].user)