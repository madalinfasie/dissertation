from datetime import datetime, timedelta

from django.db.models import F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchQuery
from django.contrib.auth.decorators import login_required

from .models import BlogArticles, UserBlogs
from .forms import AddBlogForm


def index(request):

    # lista stirilor votate -- o folosesc ca sa imi dau seama ce este disabled si ce e enabled
    if request.user.is_anonymous:
        voted_up_list = []
        voted_down_list = []
    else:
        # iau id-urile stirilor care au fost votate pozitiv/negativ de userul care este conectat in momentul asta
        voted_up_list = UserBlogs.objects.filter(vote=1, id_user_id=request.user).values_list('id_blog_id', flat=True)
        voted_down_list = UserBlogs.objects.filter(vote=-1, id_user_id=request.user).values_list('id_blog_id', flat=True)


    blog = BlogArticles.objects.all()
    if request.GET.get('textbox_search'):
        vector = SearchVector('blog_title') + \
                 SearchVector('blog_description') + \
                 SearchVector('blog_text')

        blog_list = BlogArticles.objects.annotate(search=vector).filter(
            search=SearchQuery(request.GET.get('textbox_search'))).order_by('-create_date', 'blog_title').distinct('create_date', 'blog_title')
        # Paginator {
        page = request.GET.get('page',1)
        paginator = Paginator(blog_list, 10)
        try:
            blog = paginator.page(page)
        except PageNotAnInteger:
            blog = paginator.page(1)
        except EmptyPage:
            blog = paginator.page(paginator.num_pages)
        # }
        return render(request, 'blog/blog.html', {'blog': blog})
    else:
        blog_list = BlogArticles.objects.all().order_by('-create_date')[:100]
    
        # Paginator {
        page = request.GET.get('page',1)
        paginator = Paginator(blog_list, 10)
        try:
            blog = paginator.page(page)
        except PageNotAnInteger:
            blog = paginator.page(1)
        except EmptyPage:
            blog = paginator.page(paginator.num_pages)


    # render the page
    return render(request, 'blog/blog.html', {'blog': blog,
                                              'voted_up_list': voted_up_list,
                                              'voted_down_list': voted_down_list,
                                              'nbar': 'blog'})


@login_required
def add_blog(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        add_form = AddBlogForm(request.POST or None, request.FILES or None)

        # check whether it's valid:
        if add_form.is_valid():
            entry = add_form.save(commit=False)
            entry.author = request.user
            entry.save()
            return HttpResponseRedirect('/blog/')

    # if a GET (or any other method) we'll create a blank form
    else:
        add_form = AddBlogForm()

    return render(request, 'blog/add_blog.html', {'add_form': add_form, 'nbar': 'blog'})


@login_required
def edit_blog(request, id=None):
    blog = get_object_or_404(BlogArticles, id=id)
    # create a form instance and populate it with data from the request:
    edit_form = AddBlogForm(request.POST or None, request.FILES or None, instance=blog)
    # check whether it's valid:
    if edit_form.is_valid():
        entry = edit_form.save(commit=False)
        entry.save()
        return HttpResponseRedirect('/blog/user/posts/')

    return render(request, 'blog/add_blog.html', {'add_form': edit_form,
                                                  'blog': blog,
                                                  "blog_title": blog.blog_title,
                                                  "blog_description":blog.blog_description,
                                                  "blog_text": blog.blog_text,
                                                  "blog_image": blog.blog_image, 'nbar': 'blog'})


@login_required
def delete_blog(request, id=None):
    blog = get_object_or_404(BlogArticles, id=id)
    blog.visible = False
    blog.save()
    return HttpResponseRedirect('/blog/user/posts/')


@login_required
def user_blogs(request):
    # get user's blogs ordered desc by create_date
    blog_list = BlogArticles.objects.filter(visible=True ,author=request.user).order_by('-create_date')[:100]
    # Paginator {
    page = request.GET.get('page', 1)
    paginator = Paginator(blog_list, 10)
    try:
        blog = paginator.page(page)
    except PageNotAnInteger:
        blog = paginator.page(1)
    except EmptyPage:
        blog = paginator.page(paginator.num_pages)
    # }

    # make the search {
    if request.GET.get('textbox_search'):
        if ('textbox_search' in request.GET) and request.GET['textbox_search'].strip():
            query_string = request.GET['textbox_search']
            entry_query = get_query(query_string, ['blog_title', 'blog_description', 'blog_text'])

            if query_string == '':
                blog = BlogArticles.objects.all().order_by('-blog_title')
            else:
                blog = BlogArticles.objects.filter(entry_query).order_by('-blog_title')
        return render(request, 'blog/user_blogs.html', {'blog': blog, 'nbar': 'blog'})
    # }
    return render(request, 'blog/user_blogs.html',{'blog': blog, 'nbar': 'blog'})


@login_required
def blogupvote(request, blog_id):
    user = request.user
    blog = BlogArticles.objects.get(pk=blog_id)
    try:
        userblogs = UserBlogs.objects.get(id_user=user, id_blog=blog)
    except:
        userblogs = None

    if userblogs is None:
        # adaug votul
        blog.vote_up += 1
        blog.save()
        # daca userul nu a votat stirea respectiva niciodata, se creaza inregistrare noua in UserNews
        userblogs_add = UserBlogs(id_user=user, id_blog=blog, vote=1)
        userblogs_add.save()
        return HttpResponseRedirect('/blog/')
    if userblogs.vote == -1:
        # daca userul a mai adaugat in trecut un vot, dar s-a razgandit si il schimba, atunci il anulez si incrementez
        # votul opus
        # IN VARIANTA ASTA USERUL NU ARE POSIBILITATEA DE A ANULA DEFINITIV VOTUL
        blog.vote_down += 1
        blog.vote_up += 1
        blog.save()
        # schimb data la care s-a inregistrat votul ultima data
        userblogs.last_date = datetime.now()
        userblogs.vote = 1
        userblogs.save()
        return HttpResponseRedirect('/blog/')

    return None


# ANALOG CA MAI SUS
@login_required
def blogdownvote(request, blog_id):
    user = request.user
    blog = BlogArticles.objects.get(pk=blog_id)
    try:
        userblogs = UserBlogs.objects.get(id_user=user, id_blog=blog)
    except:
        userblogs = None

    if userblogs is None:
        blog.vote_down -= 1
        blog.save()
        userblogs_add = UserBlogs(id_user = user, id_blog = blog, vote = -1)
        userblogs_add.save()
        return HttpResponseRedirect('/blog/')

    if userblogs.vote == 1:
        blog.vote_up -= 1
        blog.vote_down -= 1
        blog.save()
        userblogs.last_date = datetime.now()
        userblogs.vote = -1
        userblogs.save()
        return HttpResponseRedirect('/blog/')

    return None

