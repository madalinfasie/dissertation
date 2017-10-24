from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail, BadHeaderError

from .forms import SentUsMailForm


def contact(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        send_form = SentUsMailForm(request.POST)

        # check whether it's valid:
        if send_form.is_valid():
            subject = send_form.cleaned_data['subject']
            message = send_form.cleaned_data['message']
            sender = send_form.cleaned_data['email']
            recipients = ['blitznews@zesoft.ro']
            if subject and message and sender:
                try:
                    send_mail(subject, message, sender, recipients)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return HttpResponseRedirect('/contact/thankyou/')

    # if a GET (or any other method) we'll create a blank form
    else:
        send_form = SentUsMailForm()

    return render(request, 'contact/contact.html', {'send_form': send_form})