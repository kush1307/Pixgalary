from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    topic = models.CharField(max_length=25)

    def __str__(self):
        return self.topic


class Pins(models.Model):
    # category = models.ForeignKey(Category, related_name="category", on_delete=models.DO_NOTHING)
    category = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='all_photos')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class SavePin(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    pin = models.ForeignKey(Pins, related_name='pin', on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.pin.id} - {self.user}"


class Board(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100)
    pins = models.ManyToManyField(Pins, related_name='pins', blank=True)
    category = models.ManyToManyField(Category)
    image1 = models.ImageField(upload_to='all_photos', blank=True)
    image2 = models.ImageField(upload_to='all_photos', blank=True)
    image3 = models.ImageField(upload_to='all_photos', blank=True)
    image4 = models.ImageField(upload_to='all_photos', blank=True)

    def __str__(self):
        return self.title


