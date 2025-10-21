from django.db import models


class String(models.Model):

    id=models.AutoField(primary_key=True)

    value=models.TextField()

    created_at=models.DateTimeField(auto_now_add=True)
    
    length=models.IntegerField()
    is_palindrome=models.BooleanField()
    word_count=models.IntegerField()
    sha256_hash=models.CharField(max_length=64, unique=True)
    
    unique_characters = models.IntegerField() 
    char_frequency=models.JSONField()

    def __str__(self):
        return self.value
    
    class Meta:
        db_table = 'strings'

# Create your models here.
