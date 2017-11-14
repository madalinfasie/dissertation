from django.shortcuts import render

from .forms import UserSummaryForm
from summarymodule.get_summary import get_summary


def index(request):
	summary = ''
	if request.method == 'POST':
		form = UserSummaryForm(request.POST)
		if form.is_valid():
			
			if form.cleaned_data['sentences_number']:
				summary = get_summary(form.cleaned_data['text'], form.cleaned_data['sentences_number'])
			else:
				summary = get_summary(form.cleaned_data['text'], 3)
			return render(request, 'usersummaryapp/usersummary.html', {'nbar':'usersummary', 'form': form, 'summary': summary})
	else:
		form = UserSummaryForm()

	return render(request, 'usersummaryapp/usersummary.html', {'nbar':'usersummary', 'form': form})
