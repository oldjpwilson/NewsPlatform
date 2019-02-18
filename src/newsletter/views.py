from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.template import Context
from django.template.loader import get_template

from newsletter.models import SignUp
from newsletter.utils import Mailchimp


@login_required
def profile_update_email_preferences(request):
    if request.method == "POST":

        if 'subscribe' in request.POST:
            email = request.POST['email']
            email_qs = SignUp.objects.filter(
                user=request.user, subscribed=True)
            if email_qs.exists():
                messages.info(
                    request, 'We know you\'re excited! We\'ll keep you updated on the latest deals!')
                return redirect(reverse("edit-email-preferences"))
            else:
                signup = get_object_or_404(SignUp, user=request.user)
                signup.email = email
                signup.subscribed = True
                signup.save()
                try:
                    new_mailchimp = Mailchimp()
                    new_mailchimp.add_email(signup.email)
                except:
                    new_mailchimp.resubscribe(signup.email)
                messages.info(
                    request, 'Thanks for signing up!')
                return redirect(reverse("edit-email-preferences"))

        if 'unsubscribe' in request.POST:
            user_signup_qs = SignUp.objects.filter(user=request.user)
            if user_signup_qs.exists():
                new_mailchimp = Mailchimp()
                user_signup = user_signup_qs[0]
                user_signup.subscribed = False
                user_signup.save()
                new_mailchimp.unsubscribe(email=user_signup_qs[0].email)
                messages.info(
                    request, 'You will no longer receive emails from us.')
                return redirect(reverse("edit-email-preferences"))
            else:
                messages.info(
                    request, 'You are not subscribed to our email list.')
                return redirect(reverse("edit-email-preferences"))

    context = {
        "user": request.user,
        'display': 'edit_email_notifications',
    }

    return render(request, 'core/profile.html', context)
