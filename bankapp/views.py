from django.shortcuts import render,redirect
from .forms import UserRegistrationForm,LoginForm,AccountCreationForm,TransactionCreateForm
from django.views.generic import TemplateView
from .models import CustomUser,Account,Transactions
from django.contrib.auth import authenticate,login as djangologin,logout as djangologout
from django.utils.decorators import method_decorator
from .decorators import account_created_validator
from django.http import JsonResponse
# Create your views here.
class Registration(TemplateView):
     model=CustomUser
     form_class=UserRegistrationForm
     template_name = "registration.html"
     context={}
     def get(self,request,*args,**kwargs):
         self.context["form"]=self.form_class
         return render(request,self.template_name,self.context)

     def post(self, request, *args, **kwargs):
         form = self.form_class(request.POST)
         if form.is_valid():
             form.save()
             return render(request, "login.html")
         else:
             self.context["form"]=form
             return render(request, self.template_name, self.context)


class LoginView(TemplateView):
    model = CustomUser
    form_class = LoginForm
    template_name = "login.html"
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["form"] = self.form_class
        return render(request, self.template_name, self.context)
    def post(self, request, *args, **kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user=self.model.objects.get(username=username)
            if (user.username==username)&(user.password==password):
                djangologin(request, user)
                print("success")
                return redirect("index")
            else:
                print("Failed")
                return render(request, self.template_name, self.context)

def index(request):
    context={}
    try:
     # check for login account status= active
        account = Account.objects.get(user=request.user)
        status = account.active_status
        print(status)
        flag = True if status == "Active" else False
        context["flag"] = flag
        return render(request, "home.html", context)
    except:
        return render(request,"home.html",context)

def logout(request):
    djangologout(request)
    return redirect("login")

@method_decorator(account_created_validator,name="dispatch")

class AccountCreateView(TemplateView):
    model=Account
    template_name = "createaccount.html"
    form_class=AccountCreationForm
    context={}
    def get(self,request,*args,**kwargs):
        account_number=""
        account=self.model.objects.all().last()
        if account:
            lastacno=int(account.account_number)
            accno=1+lastacno
            account_number=accno
            pass
        else:
            account_number=1000
        self.context["form"]=self.form_class(initial={"account_number":account_number,"user":request.user})
        return render(request, self.template_name, self.context)
    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return render(request,"home.html")


class GetUserMixin(object):
    def get_user(self, account_num):
        return Account.objects.get(account_number=account_num)

class TransactionsView(TemplateView, GetUserMixin):
    model = Transactions
    template_name = "transactions.html"
    form_class = TransactionCreateForm
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["form"] = self.form_class(initial={"user": request.user})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            to_account_number = form.cleaned_data.get("to_account_number")  # lakshmi
            amount = form.cleaned_data.get("amount")
            account = self.get_user(to_account_number)
            remarks = form.cleaned_data.get("remarks")
            account.balance += float(amount)
            account.save()
            cur_acct = Account.objects.get(user=request.user)
            cur_acct.balance -= float(amount)
            cur_acct.save()
            transaction = Transactions(user=request.user, amount=amount, to_account_number=to_account_number,
                                       remarks=remarks)
            transaction.save()
            return redirect("history")

        else:
            self.context["form"] = form
            return render(request, self.template_name, self.context)

class BalanceEnq(TemplateView):
    def get(self, request, *args, **kwargs):
        account = Account.objects.get(user=request.user)
        balance = account.balance
        #return render(request, "balance.html", {"balance": balance})
        return JsonResponse({"balance": balance})

class TransactionHistory(TemplateView):
    def get(self, request, *args, **kwargs):
        debit_transactions = Transactions.objects.filter(user=request.user)
        #fetching loggedin user account
        l_user = Account.objects.get(user=request.user)
        credit_transactions = Transactions.objects.filter(to_account_number=l_user.account_number )
        return render(request, "transactionhistory.html",{"dtransactions":debit_transactions,"ctransactions":credit_transactions})