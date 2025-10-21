from rest_framework import serializers
from .models import String


class StringSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='sha256_hash', read_only=True)
    properties = serializers.SerializerMethodField()
    
    class Meta:
        model = String
        fields = ['id', 'value', 'properties', 'created_at']
        read_only_fields = ['created_at']
    
    def get_properties(self, obj):
        return {
            'length': obj.length,
            'is_palindrome': obj.is_palindrome,
            'unique_characters': obj.unique_characters,
            'word_count': obj.word_count,
            'sha256_hash': obj.sha256_hash,
            'character_frequency_map': obj.char_frequency
        }