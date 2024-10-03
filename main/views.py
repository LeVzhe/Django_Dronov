from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from main.forms import (AIFormSet, BbForm, GuestCommentForm, ProfileEditForm,
                        RegisterForm, SearchForm, UserCommentForm)
from main.models import AdvUser, Bb, Comment, SubRubric
from main.utilities import signer


def index(request):
    bbs = Bb.objects.filter(is_active=True).select_related("rubric")[:10]
    context = {"bbs": bbs}
    return render(request, "main/index.html", context)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, "main/activation_failed.html")
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = "main/activation_done_earlier.html"
    else:
        template = "main/activation_done.html"
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


def other_page(request, page):
    try:
        template = get_template("main/" + page + ".html")
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


@login_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {"bbs": bbs}
    return render(request, "main/profile.html", context)


class ProfileDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = "main/profile_delete.html"
    success_url = reverse_lazy("main:index")
    success_message = "Пользователь удален"

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class RegisterView(CreateView):
    model = AdvUser
    template_name = "main/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("main:register_done")


class RegisterDoneView(TemplateView):
    template_name = "main/register_done.html"


class PassworEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = "main/password_edit.html"
    success_url = reverse_lazy("main:profile")
    success_message = "Пароль пользователя изменен"


class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = "main/profile_edit.html"
    form_class = ProfileEditForm
    success_url = reverse_lazy("main:profile")
    success_message = "Данные пользователя изменены"

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BBLoginView(LoginView):
    template_name = "main/login.html"


class BBLogoutiew(LogoutView):
    pass


def rubric_bbs(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ""

    form = SearchForm(initial={"keyword": keyword})
    paginator = Paginator(bbs, 2)
    if "page" in request.GET:
        page_num = request.GET["page"]
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {
        "rubric": rubric,
        "page": page,
        "bbs": page.object_list,
        "form": form,
    }
    return render(request, "main/rubric_bbs.html", context)


def bb_detail(request, rubric_pk, pk):
    bb = Bb.objects.get(pk=pk)
    initial = {"bb": bb.pk}
    if request.user.is_authenticated:
        initial["author"] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == "POST":
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, "Комментарий добавлен")
            return redirect(request.get_full_path_info())
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, "Комментарий не добавлен")
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    context = {"bb": bb, "ais": ais, "comments": comments, "form": form}
    return render(request, "main/bb_detail.html", context)


@login_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    comments = Comment.objects.filter(bb=pk, is_active=True)

    ais = bb.additionalimage_set.all()
    context = {
        "bb": bb,
        "ais": ais,
        "comments": comments,
    }
    return render(request, "main/profile_bb_detail.html", context)


@login_required
def profile_bb_add(request):
    if request.method == "POST":
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, "Объявление добавлено")
                return redirect("main:profile")
    else:
        form = BbForm(
            initial={
                "author": request.user.pk,
            }
        )
        formset = AIFormSet()

    context = {"form": form, "formset": formset}
    return render(request, "main/profile_bb_add.html", context)


@login_required
def profile_bb_edit(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == "POST":
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(
                    request, messages.SUCCESS, "Объявление исправленно"
                )
                return redirect("main:profile")
    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {
        "form": form,
        "formset": formset,
    }
    return render(request, "main/profile_bb_edit.html", context)


@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == "POST":
        bb.delete()
        messages.add_message(request, messages.SUCCESS, "Объявление удалено")
        return redirect("main:profile")
    else:
        context = {"bb": bb}
        return render(request, "main/profile_bb_delete.html", context)
