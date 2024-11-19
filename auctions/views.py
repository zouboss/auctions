from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from .models import User
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AuctionListingForm,BidForm,CommentForm
from .models import AuctionListing, Bid,Comment,Watchlist,Category


def index(request):
    return render(request, "auctions/active_listings.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("active_listings"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("active_listings"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("active_listings"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_auction_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.active = True
            listing.save()
            return redirect('active_listings')  # Redirige vers la page d'accueil ou une page de confirmation
    else:
        form = AuctionListingForm()

    return render(request, 'auctions/create_listing.html', {'form': form})

def active_listings(request):
    listings = AuctionListing.objects.filter(active=True)  # Récupère uniquement les annonces actives
    return render(request, 'auctions/active_listings.html', {'listings': listings})


def listing_detail(request, listing_id):
    auction = get_object_or_404(AuctionListing, id=listing_id)
    is_in_watchlist = request.user.is_authenticated and Watchlist.objects.filter(user=request.user, auction=auction).exists()
    current_price = auction.current_bid or auction.starting_bid
    comments = auction.comments.all()

    # Ajouter ou retirer de la watchlist
    if request.method == "POST" and 'watchlist' in request.POST:
        if is_in_watchlist:
            Watchlist.objects.filter(user=request.user, auction=auction).delete()
        else:
            Watchlist.objects.create(user=request.user, auction=auction)
        return redirect('listing_detail', listing_id=listing_id)

    # Gestion de l'enchère
    if request.method == "POST" and 'bid' in request.POST:
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            bid_amount = bid_form.cleaned_data['bid_amount']
            if bid_amount > current_price:
                Bid.objects.create(auction=auction, bidder=request.user, bid_amount=bid_amount)
                auction.current_bid = bid_amount
                auction.save()
                messages.success(request, "Votre enchère a été placée.")
            else:
                messages.error(request, "L'enchère doit être supérieure au prix actuel")
            return redirect('listing_detail', listing_id=listing_id)

    # Ajout de commentaire
    if request.method == "POST" and 'comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            Comment.objects.create(auction=auction, commenter=request.user, comment_text=comment_form.cleaned_data['comment_text'])
            return redirect('listing_detail', listing_id=listing_id)

    # Fermer l'enchère si c'est le propriétaire
    if request.method == "POST" and request.user == auction.owner and 'close_auction' in request.POST:
        highest_bid = auction.bids.order_by('-bid_amount').first()
        if highest_bid:
            auction.winner = highest_bid.bidder  # Définit le gagnant de l'enchère
            messages.success(request, f"L'enchère est fermée ! {highest_bid.bidder.username} a remporté l'enchère.")
        else:
            messages.info(request, "L'enchère a été fermée sans gagnant.")

        auction.active = False
        auction.save()
        return redirect('listing_detail', listing_id=listing_id)

    bid_form = BidForm()
    comment_form = CommentForm()

    return render(request, "auctions/listing_detail.html", {
        "auction": auction,
        "is_in_watchlist": is_in_watchlist,
        "current_price": current_price,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "comments": comments,
    })

@login_required
def watchlist_view(request):
    # Récupère toutes les annonces de la Watchlist de l'utilisateur
    watchlist_items = Watchlist.objects.filter(user=request.user)

    # Gestion de la suppression de l'annonce de la Watchlist
    if request.method == "POST":
        auction_id = request.POST.get("remove_auction")
        Watchlist.objects.filter(user=request.user, auction_id=auction_id).delete()
        return redirect("watchlist_view")

    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })


def filter_by_category(request):
    # Récupérer toutes les catégories uniques déjà saisies par les utilisateurs
    categories = AuctionListing.objects.values_list('category', flat=True).distinct().exclude(category=None)

    selected_category = request.GET.get('category', None)  # Catégorie sélectionnée par l'utilisateur
    listings = AuctionListing.objects.filter(active=True)  # Filtrer les enchères actives par défaut

    if selected_category:
        listings = listings.filter(category=selected_category)  # Filtrer par catégorie sélectionnée

    return render(request, "auctions/filter_by_category.html", {
        "categories": categories,
        "listings": listings,
        "selected_category": selected_category,
    })