from django.db import models


class AnalyzedString(models.Model):
    """Model to store analyzed strings and their computed properties"""
    
    # The actual string value
    value = models.TextField(unique=True)
    
    # SHA-256 hash serves as the unique identifier
    sha256_hash = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Computed properties
    length = models.IntegerField()
    is_palindrome = models.BooleanField(db_index=True)
    unique_characters = models.IntegerField()
    word_count = models.IntegerField(db_index=True)
    character_frequency_map = models.JSONField()
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analyzed_strings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sha256_hash']),
            models.Index(fields=['is_palindrome']),
            models.Index(fields=['word_count']),
            models.Index(fields=['length']),
        ]
    
    def __str__(self):
        return f"{self.value[:50]}... (hash: {self.sha256_hash[:8]})"