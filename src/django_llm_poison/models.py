from django.db import models


class MarkovModel(models.Model):
    hash = models.CharField(max_length=255, primary_key=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hash
