from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Survey, Choice
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import generic
from .forms import SurveyForm, ChoiceFormSet
from django.forms import formset_factory



class IndexView(generic.ListView):
    template_name = 'survey/index.html'
    model = Survey
    # instead of using object_list
    context_object_name = 'question_list'

    def get_queryset(self):
        return Survey.objects.all()


class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Survey
    template_name = 'survey/create.html'
    form_class = SurveyForm
    success_url = 'survey/index/'

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['form'] = SurveyForm(self.request.POST)
            context['formset'] = ChoiceFormSet(self.request.POST)
        else:
            context['form'] = SurveyForm()
            context['formset'] = ChoiceFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form = context['form']
        formset = context['formset']
        if all([form.is_valid(), formset.is_valid()]):
            form.instance.owner = self.request.user
            question = form.save()
            for inline_form in formset:
                if inline_form.cleaned_data:
                    choice = inline_form.save(commit=False)
                    choice.question = question
                    choice.save()
            return HttpResponseRedirect(reverse('survey:index',))


class DetailView(generic.DetailView):
    model = Survey
    template_name = 'survey/detail.html'

def vote(request, question_id):
    survey = get_object_or_404(Survey, pk=question_id)

    selected_choice = survey.choice_set.get(pk=request.POST['choice'])

    selected_choice.votes += 1
    selected_choice.save()
    return HttpResponseRedirect(reverse('survey:results', args=(survey.id,)))

class ResultsView(generic.DetailView):
    model = Survey
    template_name = 'survey/results.html'
