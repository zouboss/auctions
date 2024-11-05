from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/", views.create_auction_listing, name="create_auction_listing"),
    path("", views.active_listings, name="active_listings"),
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("watchlist/", views.watchlist_view, name="watchlist_view"),

]
