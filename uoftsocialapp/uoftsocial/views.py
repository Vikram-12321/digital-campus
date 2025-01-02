from django.shortcuts import render
from dal import autocomplete

#Models
from posts.models import Post
from . models import Course

#Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from . serializer import ReactSerializer


class ReactView(APIView):

    serializer_class = ReactSerializer

    def get(self, request):
        output = [{"name":output.name
                   }
                   for output in Course.objects.all()]
        return Response(output)
    
    def post(self, request):
        serializer = ReactSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


def home(request):
    context = { 
        'posts': Post.objects.all() 
    }
    return render(request, 'uoftsocial/home.html', context)

def about(request):
    return render(request, 'uoftsocial/about.html')

def account(request):
    return render(request, 'uoftsocial/account.html')


class CourseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # If user not logged in or has no permission, return empty
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        
        qs = Course.objects.all()

        if self.q:  # typed text from user
            qs = qs.filter(name__icontains=self.q)
        return qs
    
