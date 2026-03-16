# media/views.py
import io
import os

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from .models import Photo


def _resize_image(uploaded_file, max_px=1920):
    img = Image.open(uploaded_file)
    if img.mode in ('RGBA', 'LA'):
        # Paste onto white background to handle transparency (PIL defaults to black)
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85, optimize=True)
    buf.seek(0)
    name = os.path.splitext(uploaded_file.name)[0] + '.jpg'
    return InMemoryUploadedFile(buf, 'ImageField', name, 'image/jpeg', buf.getbuffer().nbytes, None)


@permission_required('media.add_photo')
def add_photo(request, object_type, object_id):
    if request.method != 'POST':
        return HttpResponse(status=405)

    print(f"Attempting to add photo for {object_type} {object_id}")
    print(f"Files in request: {request.FILES}")

    try:
        # Split into app_label and model_name
        app_label, model_name = object_type.split('.')
        model = apps.get_model(app_label, model_name)
        obj = get_object_or_404(model, id=object_id)

        # Create the photo
        photo = Photo.objects.create(
            image=_resize_image(request.FILES['file']),
            customer=request.user.customer,
            content_type=ContentType.objects.get_for_model(model),
            object_id=object_id
        )

        # Add to M2M relationship if it exists
        if hasattr(obj, 'photos'):
            obj.photos.add(photo)

        # Return just the photo HTML snippet
        return TemplateResponse(request, 'media/photo_snippet.html', {
            'photo': photo,
            'object_type': object_type,
            'object_id': object_id
        })

    except Http404:
        raise
    except Exception as e:
        print(f"Error in add_photo: {type(e)} - {str(e)}")
        return HttpResponse(str(e), status=500)


@permission_required('media.view_photo')
def get_photos(request, object_type, object_id):
    model = apps.get_model(object_type)
    obj = get_object_or_404(model, id=object_id)

    return TemplateResponse(request, 'media/photos.html', {
        'photos': obj.photos.order_by('-uploaded_at'),
        'object_type': object_type,
        'object_id': object_id
    })

@permission_required('media.view_photo')
def get_photos_edit(request, object_type, object_id):
    model = apps.get_model(object_type)
    obj = get_object_or_404(model, id=object_id)
    return TemplateResponse(request, 'media/photos_edit.html', {
        'photos': obj.photos.order_by('-uploaded_at'),
        'object_type': object_type,
        'object_id': object_id,
    })


@csrf_exempt
@permission_required('media.delete_photo')
def delete_photo(request, photo_id):
    if request.method != 'DELETE':
        return HttpResponse(status=405)

    photo = get_object_or_404(Photo, id=photo_id)

    # Capture everything needed before deletion
    content_type = photo.content_type
    object_id = photo.object_id
    object_type = f'{content_type.app_label}.{content_type.model}'
    model = content_type.model_class()

    perm = f'{content_type.app_label}.change_{content_type.model}'
    if not request.user.has_perm(perm):
        return HttpResponse(status=403)

    photo.delete()

    response = HttpResponse(status=200)
    response['HX-Trigger'] = 'photoDeleted'
    return response
