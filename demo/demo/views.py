from django.shortcuts import render_to_response

def iframe(request):
    return render_to_response('index.html', {'request': request})
