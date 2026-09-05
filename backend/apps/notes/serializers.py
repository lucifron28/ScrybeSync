from rest_framework import serializers
from .models import Category, Note


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        name = attrs.get('name')
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if name and user and user.is_authenticated:
            qs = Category.objects.filter(user=user, name=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'name': 'A category with this name already exists for this user.'})
        return attrs


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_category(self, value):
        if value is None:
            return value
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if value.user != request.user:
                raise serializers.ValidationError("Category does not belong to the authenticated user.")
        return value