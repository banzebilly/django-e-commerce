#the context function will halp us wheb user click in cateroy btn then it shows all the categories we have
#contenxt takes a request as an argument and it will return the the dictionary of data

#also tell django setting that we are using context function
# from .models import Category

# def menu_links(request):
#     links = Category.objects.all()
#     return dict(links = links)  # Return a dictionary directly
# context_processors.py

from .models import PCategory

def menu_links(request):
    links = PCategory.objects.all()
    return {'links': links}
