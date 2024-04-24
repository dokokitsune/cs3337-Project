from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from .models import MainMenu, Comment
from .forms import BookForm, CommentForm
from .models import Book


from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


from django.contrib.auth.decorators import login_required


def index(request):
    return render(request,
                  'bookMng/index.html',
                  {
                      'item_list': MainMenu.objects.all()
                  })


@login_required(login_url=reverse_lazy('login'))
def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            #form.save()
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request,
                  'bookMng/postbook.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'submitted': submitted
                  })


@login_required(login_url=reverse_lazy('login'))
def displaybooks(request):
    books = Book.objects.all()
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books
                  })


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)


@login_required(login_url=reverse_lazy('login'))
def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)
    book.pic_path = book.picture.url[14:]
    return render(request,
                  'bookMng/book_detail.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book
                  })


@login_required(login_url=reverse_lazy('login'))
def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'books': books
                  })


@login_required(login_url=reverse_lazy('login'))
def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    return render(request,
                  'bookMng/book_delete.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book
                  })

@login_required(login_url=reverse_lazy('login'))
def add_comment(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.book = book
            form.save()
            return redirect('displaycom', book_id=book_id)
    else:
        form = CommentForm()
    return render(request,
                  'bookMng/add_comment.html',
                  {
                      'item_list': MainMenu.objects.all(), 'form': form, 'book': book})

@login_required(login_url=reverse_lazy('login'))
def displaycom(request, book_id):
    book = Book.objects.get(id=book_id)
    comments = Comment.objects.filter(book=book)
    return render(request,
                  'bookMng/displaycom.html',
                  {
                      'item_list': MainMenu.objects.all(), 'book': book, 'comments': comments})

def add_to_cart(request, book_id):
    book = Book.objects.get(id=book_id)

    if 'cart' not in request.session:
        request.session['cart'] = {}

    cart = request.session['cart']

    if str(book_id) in cart:
        cart[str(book_id)]['quantity'] += 1
    else:
        cart[str(book_id)] = {
            'quantity': 1,
            'price': float(book.price)
        }

    request.session.modified = True

    return redirect('cart')



def remove_from_cart(request, book_id):
    if 'cart' in request.session:
        cart = request.session['cart']
        if str(book_id) in cart:
            del cart[str(book_id)]
            request.session.modified = True

    return redirect('cart')


def cart(request):
    cart_items = []
    total_price = 0

    if 'cart' in request.session:
        cart = request.session['cart']
        book_ids = cart.keys()
        books = Book.objects.filter(id__in=book_ids)

        for book in books:
            quantity = cart[str(book.id)]['quantity']
            total_price += book.price * quantity
            cart_items.append({'book': book, 'quantity': quantity})

    return render(request, 'bookMng/cart.html',
                  {'cart_items': cart_items, 'total_price': total_price,
                   'item_list': MainMenu.objects.all()})
