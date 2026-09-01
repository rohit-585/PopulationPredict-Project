from django.db import models


from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

from django.db import models

class MapSelection(models.Model):
    state = models.CharField(max_length=100)
    primary = models.CharField(max_length=100)
    secondary = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.state} - {self.primary} vs {self.secondary}"
