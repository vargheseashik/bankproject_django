from .models import Account
from django.shortcuts import redirect
from django.contrib import messages

def account_created_validator(func):

    def wrapper(request,*args,**kwargs):
        try:
            account=Account.objects.get(user=request.user)
            status=account.active_status
            if status=="Active":
                messages.error(request,"Account Already Exists!")
                return redirect("index")
            else:
                return func(request,*args,**kwargs)
        except:
            return func(request, *args, **kwargs)

    return wrapper