from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Category, Listing, Comment, Bid
from datetime import datetime

from .models import User




def index(request):
    activeListing = Listing.objects.filter(Active=True)

    return render(request, "auctions/index.html",{
        "listings":activeListing,
        "categories": Category.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

def create_listing(request):
    categories = Category.objects.all();
    if request.method == "POST":
        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y, %I:%M %p")
        title = request.POST["title"]
        description = request.POST["description"]
        bid = request.POST["bid"]
        image = request.POST["url"]
        category = request.POST["category"]
        current_user = request.user

        price = Bid(
            bids=float(bid), 
            user=current_user
        )
        price.save()

        categoryName = Category.objects.get(category_name=category)

        listing = Listing(
            title=title,
            description=description,
            image=image,
            price=price,
            lister=current_user,
            category=categoryName,
            time=formatted_date
        )

        listing.save()
    
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html", {
            "categories": categories,
        });

def categoryList(request):

    if request.method == "POST":
        categoryName = request.POST['category']
        selection = Category.objects.get(category_name=categoryName)
        activeListing = Listing.objects.filter(Active=True, category=selection)

        return render(request, "auctions/index.html",{
        "listings":activeListing,
        "categories": Category.objects.all(),
    })

def listings(request, id):
        listingData = Listing.objects.get(pk=id)
        check_owner = request.user.username == listingData.lister.username
        isWatchlist = request.user in listingData.watchlist.all()
        comments = Comment.objects.filter(listing=listingData)
        return render(request, "auctions/listings.html", {
        "listing": listingData,
        "isWatchlist": isWatchlist,
        "comments": comments,
        "check_owner": check_owner  
    });

def addtoWatchlist(request, id):
    listingdetails = Listing.objects.get(pk=id)
    user = request.user
    listingdetails.watchlist.add(user)
    return HttpResponseRedirect(reverse("listings", args=(id, )))

def removefromWatchlist(request, id):
    listingdetails = Listing.objects.get(pk=id)
    user = request.user
    listingdetails.watchlist.remove(user)
    return HttpResponseRedirect(reverse("listings", args=(id, )))

def watchlist(request):
    user = request.user
    
    listings = user.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })

def comment(request, id):
    user = request.user
    listing = Listing.objects.get(pk=id)
    comment = request.POST['comment']

    newComment = Comment(
        author=user,
        listing=listing,
        comment=comment
    )

    newComment.save()

    return HttpResponseRedirect(reverse("listings", args=(id, )))

def addBid(request, id):
    bidvalue = request.POST['bid']
    listing = Listing.objects.get(pk=id)  
    isWatchlist = request.user in listing.watchlist.all()
    check_owner = request.user.username == listing.lister.username

    comments = Comment.objects.filter(listing=listing)

    if float(bidvalue) > listing.price.bids:  
        new_bid = Bid(
            bids=bidvalue,
            user=request.user
        )
        new_bid.save()
        listing.price = new_bid
        listing.save()

        return render(request, "auctions/listings.html", {
            "listing": listing,
            "update": True,
            "message": "Bid Successful! 😁",
            "isWatchlist": isWatchlist,
            "comments":comments,
            "check_owner": check_owner
        })
    
    else:
        return render(request, "auctions/listings.html", {
            "listing": listing,
            "update": False,
            "message": "Bid unsuccessful 😑. You have bidded less than the given amount",
            "isWatchlist": isWatchlist,
            "comments":comments,
            "check_owner": check_owner
        })
    
def closeListing(request, id):
    listing = Listing.objects.get(pk=id)
    listing.Active = False
    listing.save()
    comments = Comment.objects.filter(listing=listing)
    isWatchlist = request.user in listing.watchlist.all()
    check_owner = request.user.username == listing.lister.username

    return render(request, "auctions/listings.html", {
        "listing": listing,
        "isWatchlist": isWatchlist,
        "comments": comments,
        "check_owner": check_owner,
        "update": True,
        "message": "Your Auction is closed! 😊"  
    });


