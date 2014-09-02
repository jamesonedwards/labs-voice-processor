from django.db import models
import datetime

'''
For file upload reference, see: 
http://stackoverflow.com/questions/5871730/need-a-minimal-django-file-upload-example
'''

'''
def get_original_file_path(instance, filename):
    return '/'.join([settings.VOICE_FILES_DIR, instance.unique_id, filename])

def get_altered_file_path(instance):
    return '/'.join([settings.VOICE_FILES_DIR, instance.unique_id, 'altered.mp3'])
'''

# Create your models here.
class Message(models.Model):
    unique_id = models.CharField('Unique ID', max_length=200)
    name = models.CharField('Name', max_length=200)
    email = models.CharField('Email', max_length=200)
    original_file = models.CharField('Path to original file', max_length=200)
    altered_file = models.CharField('Path to altered file', max_length=200)
    # original_file = models.FileField(upload_to=get_original_file_path)
    # altered_file = models.FileField(upload_to=get_altered_file_path)
    text = models.TextField('Transcribed Text')
    date_created = models.DateTimeField('Date Created', default=datetime.datetime.now, blank=True)

    def __unicode__(self):
        # TODO: Once transcription is in place, change this to display the text field.
        return self.altered_file
