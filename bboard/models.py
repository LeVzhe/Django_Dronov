from django.db import models

class Bb(models.Model):
#verbose_name - параметр, для человеческого названия полей модели
    title = models.CharField(max_length=50, verbose_name='Toвар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

#человеческое название самой модели
    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-published']