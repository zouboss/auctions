from django import forms
from .models import AuctionListing,Bid,Comment

class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Titre de l\'enchère'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description de l\'enchère'}),
            'starting_bid': forms.NumberInput(attrs={'placeholder': 'Prix de départ'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'URL de l\'image'}),
            'category': forms.TextInput(attrs={'placeholder': 'Catégorie'}),
        }

class BidForm(forms.ModelForm):
    bid_amount = forms.DecimalField(
        label="Montant de l'enchère",
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={"placeholder": "Entrez votre enchère"})
    )

    class Meta:
        model = Bid
        fields = ['bid_amount']


class CommentForm(forms.ModelForm):
    comment_text = forms.CharField(
        label="Commentaire",
        widget=forms.Textarea(attrs={"placeholder": "Ajoutez un commentaire", "rows": 3})
    )

    class Meta:
        model = Comment
        fields = ['comment_text']