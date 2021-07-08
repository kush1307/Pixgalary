from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        img.save(self.image.path, format="JPEG", quality=70)

    def get_absolute_url(self):
        return reverse('pin-detail', kwargs={'pk': self.pk})


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

    def get_absolute_url(self):
        return reverse('board-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image1.path)
        img.save(self.image1.path, format="JPEG", quality=70)

        img = Image.open(self.image2.path)
        img.save(self.image2.path, format="JPEG", quality=70)

        img = Image.open(self.image3.path)
        img.save(self.image3.path, format="JPEG", quality=70)

        img = Image.open(self.image4.path)
        img.save(self.image4.path, format="JPEG", quality=70)


class Comment(models.Model):
    pins = models.ForeignKey(Pins, related_name="comments", on_delete=models.CASCADE)
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pins.title} <-> {self.name}"
