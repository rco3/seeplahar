# media/views.py
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt

from .models import Photo


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
            image=request.FILES['file'],  # Dropzone uses 'file'
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

    except Exception as e:
        print(f"Error in add_photo: {type(e)} - {str(e)}")
        return HttpResponse(str(e), status=500)


@permission_required('media.view_photo')
def get_photos(request, object_type, object_id):
    model = apps.get_model(object_type)
    obj = get_object_or_404(model, id=object_id)

    return TemplateResponse(request, 'media/photos.html', {
        'photos': obj.photos.all(),
        'object_type': object_type,
        'object_id': object_id
    })

@permission_required('media.delete_photo')
def delete_photo(request, photo_id):
    if request.method != 'DELETE':
        return HttpResponse(status=405)

    photo = get_object_or_404(Photo, id=photo_id)

    # Check if user has permission to modify the related object
    content_type = photo.content_type
    perm = f'{content_type.app_label}.change_{content_type.model}'
    print(perm)
    if not request.user.has_perm(perm):
        print("What you talking bout, Willis?")
        return HttpResponse(status=403)

    photo.delete()
    return HttpResponse(status=204)  # 204 No Content