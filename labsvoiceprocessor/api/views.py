# Create your views here.

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from api.models import Message
from api.forms import MessageForm
from django.core import serializers
import uuid
from labsvoiceprocessor import settings
from libs import ApiResponse
import os
import subprocess

# import logging
# from django.template import response

'''
Reference:
http://stackoverflow.com/questions/11813620/django-store-inmemoryuploadedfile-on-the-disk
'''

def testupload(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            __uploadhelper(request)
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('api.views.testupload'))
    else:
        form = MessageForm()  # An empty, unbound form
    # Load documents for the list page
    messages = Message.objects.all()
    # Render list page with the documents and the form
    return render_to_response(
                              'api/testupload.html',
                              {'messages': messages, 'form': form},
                              context_instance=RequestContext(request))


def listfiles(request):
    try:
        # Load documents for the list page
        messages = Message.objects.all()
        # Return the file list as JSON.
        return HttpResponse(serializers.serialize('json', messages), mimetype="application/json")
    except Exception as ex:
        # Respond with error as JSON.
        return HttpResponse(ApiResponse.from_exception(ex).to_json(), mimetype="application/json")


def savefile(request):
    try:
        # Handle file upload
        if request.method == 'POST':
            newMsg = __uploadhelper(request)
            # Return success message as JSON.
            return HttpResponse(ApiResponse(success=True, message=newMsg.altered_file).to_json(), mimetype="application/json")
        else:
            raise Exception('Must use HTTP POST method!')
    except Exception as ex:
        # Respond with error as JSON.
        return HttpResponse(ApiResponse.from_exception(ex).to_json(), mimetype="application/json")


def __uploadhelper(request):
    if request.FILES is None or request.FILES['original_file'] is None:
        raise Exception('No file sent.')
    # Get uploaded file.
    origFile = request.FILES['original_file']
    # Apply reverse reverb (aka "creepify")?
    soxCreepify = True if request.POST['creepify'] == 'yes' else False
    # Check that this is a wav file.
    if origFile.content_type not in settings.ALLOWABLE_INPUT_FILE_TYPES:
        raise Exception('You can only upload WAV files!')
    # TODO: Eventually, extract file extention and check for a list of supported file types.
    # Create unique user path.
    fileRoot = settings.MEDIA_ROOT + settings.VOICE_FILES_DIR
    urlRoot = settings.MEDIA_URL + settings.VOICE_FILES_DIR
    uniqueId = str(uuid.uuid4())
    userDir = os.path.join(fileRoot, uniqueId)
    userUrl = '/'.join([urlRoot, uniqueId])
    os.makedirs(userDir)
    # origFilePath = os.path.join(userDir, origFile.name) # Removed the input file name since it will be passed to a shell script command.
    origFilePath = os.path.join(userDir, settings.ORIG_FILE_NAME)
    origFileUrl = '/'.join([userUrl, settings.ORIG_FILE_NAME])
    # Save uploaded file.                
    __handle_uploaded_file(origFile, origFilePath)
    # Now generate altered file.
    altFilePath = os.path.join(userDir, settings.ALT_FILE_NAME)
    altFileUrl = '/'.join([userUrl, settings.ALT_FILE_NAME])
    # Temp files.
    soxTmpFilePath = os.path.join(userDir, 'tmp.wav')
    soxTmpFileRevPath = os.path.join(userDir, 'tmprev.wav')
    if soxCreepify:
        # Example: sox original.wav tmp.wav norm vad gain -7 pitch -600 overdrive 20 pad .25; sox tmp.wav tmprev.wav reverse reverb -w reverse; sox -m tmp.wav tmprev.wav altered.mp3
        # First create temp file with standard voice mods.
        soxCmd = ' '.join([settings.SOX_PATH, origFilePath, soxTmpFilePath, 'norm vad gain', settings.SOX_GAIN, 'pitch', settings.SOX_PITCH, 'overdrive', settings.SOX_OVERDRIVE, 'pad', settings.SOX_PAD])
        subprocess.call(soxCmd, shell=True)
        # Then add the reverse reverb (two shell commands).
        soxCmd = ' '.join([settings.SOX_PATH, soxTmpFilePath, soxTmpFileRevPath, 'reverse reverb -w reverse'])
        subprocess.call(soxCmd, shell=True)
        soxCmd = ' '.join([settings.SOX_PATH, '-m', soxTmpFilePath, soxTmpFileRevPath, altFilePath])
        subprocess.call(soxCmd, shell=True)
        # Then delete the temp files.
        os.remove(soxTmpFilePath)
        os.remove(soxTmpFileRevPath)
    else:
        # Example: sox original.wav altered.wav norm vad gain -7 pitch -600 overdrive 20 pad .25
        soxCmd = ' '.join([settings.SOX_PATH, origFilePath, altFilePath, 'norm vad gain', settings.SOX_GAIN, 'pitch', settings.SOX_PITCH, 'overdrive', settings.SOX_OVERDRIVE, 'pad', settings.SOX_PAD])
        subprocess.call(soxCmd, shell=True)
    newMsg = Message(
                     unique_id=uniqueId,
                     original_file=origFileUrl,
                     altered_file=altFileUrl
                    )
    newMsg.save()
    # Return the Message object that you just created.
    return newMsg


def __handle_uploaded_file(f, destPath):
    with open(destPath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


