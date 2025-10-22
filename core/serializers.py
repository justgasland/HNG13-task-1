from rest_framework import serializers
from .models import AnalyzedString


class AnalyzedStringSerializer(serializers.ModelSerializer):
    """
    Serializer for AnalyzedString model
    Returns data in the exact format required by the spec
    """
    id = serializers.CharField(source='sha256_hash', read_only=True)
    properties = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyzedString
        fields = ['id', 'value', 'properties', 'created_at']
        read_only_fields = ['created_at']
    
    def get_properties(self, obj):
        """
        Format properties as per spec requirements
        """
        return {
            'length': obj.length,
            'is_palindrome': obj.is_palindrome,
            'unique_characters': obj.unique_characters,
            'word_count': obj.word_count,
            'sha256_hash': obj.sha256_hash,
            'character_frequency_map': obj.character_frequency_map
        }


class StringInputSerializer(serializers.Serializer):
    """
    Serializer for validating POST request input
    """
    value = serializers.CharField(required=True, allow_blank=False)
    
    def validate_value(self, value):
        """
        Validate that value is a string
        """
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be a string")
        return value