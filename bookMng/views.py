from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from .models import MainMenu, Comment
from .forms import BookForm, CommentForm
from .models import Book

from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required



@login_required
def favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user = request.user

    if user in book.favorites.all():
        # Book is already a favorite, remove it
        book.favorites.remove(user)
    else:
        # Add the book to favorites
        book.favorites.add(user)

    return redirect('book_detail', book_id=book.id)


@login_required
def my_favorites(request):
    user = request.user
    favorite_books = user.favorite_books.all()
    return render(request, 'bookMng/my_favorites.html', {'favorite_books': favorite_books, 'item_list': MainMenu.objects.all()})

def index(request):
    return render(request, "bookMng/index.html", {"item_list": MainMenu.objects.all()})


def about_us(request):
    return render(
        request, "bookMng/about_us.html", {"item_list": MainMenu.objects.all()}
    )


@login_required(login_url=reverse_lazy("login"))
def postbook(request):
    submitted = False
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            # form.save()
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()

            form.save_m2m()

            return HttpResponseRedirect("/postbook?submitted=True")
    else:
        form = BookForm()
        if "submitted" in request.GET:
            submitted = True
    return render(
        request,
        "bookMng/postbook.html",
        {"form": form, "item_list": MainMenu.objects.all(), "submitted": submitted},
    )


@login_required(login_url=reverse_lazy("login"))
def displaybooks(request):
    books = Book.objects.all()
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(
        request,
        "bookMng/displaybooks.html",
        {"item_list": MainMenu.objects.all(), "books": books},
    )


class Register(CreateView):
    template_name = "registration/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("register-success")

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)


@login_required(login_url=reverse_lazy("login"))
def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)
    book.pic_path = book.picture.url[14:]
    return render(
        request,
        "bookMng/book_detail.html",
        {"item_list": MainMenu.objects.all(), "book": book},
    )


@login_required(login_url=reverse_lazy("login"))
def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(
        request,
        "bookMng/mybooks.html",
        {"item_list": MainMenu.objects.all(), "books": books},
    )


@login_required(login_url=reverse_lazy("login"))
def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()

    return render(
        request,
        "bookMng/book_delete.html",
        {"item_list": MainMenu.objects.all(), "book": book},
    )


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

def update_cart(request):
    if request.method == 'POST':
        shopping_cart = request.session.get('cart', {})

        for book_id, item in shopping_cart.items():
            quantity = int(request.POST.get(f'quantity_{book_id}', item['quantity']))
            shopping_cart[book_id]['quantity'] = quantity

        request.session['cart'] = shopping_cart
        request.session.modified = True

    return redirect('cart')


def checkout(request):
    cart_items = []
    total_price = 0

    if 'cart' in request.session:
        shopping_cart = request.session['cart']
        book_ids = shopping_cart.keys()
        books = Book.objects.filter(id__in=book_ids)

        for book in books:
            quantity = shopping_cart[str(book.id)]['quantity']
            total_price += book.price * quantity
            cart_items.append({'book': book, 'quantity': quantity, 'total_price': book.price * quantity})

    if request.method == 'POST':
        del request.session['cart']
        return redirect('order_success')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'bookMng/checkout.html', context)


def order_success(request):
    return render(request, 'bookMng/order_success.html')


def cancel_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('index')


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
                   'item_list': MainMenu.objects.all(),
                   'is_cart_empty': not cart_items})



def search_book(request):
    if request.method == 'POST':
        searched_book = request.POST.get('search-item')

        if searched_book:
            books = Book.objects.filter(name__icontains=searched_book)

            for b in books:
                b.pic_path = b.picture.url[14:]
        else:
            books = Book.objects.none()

        return render(request,
                      'bookMng/display_search_results.html',
                      {
                          'item_list': MainMenu.objects.all(),
                          'books': books
                      })
