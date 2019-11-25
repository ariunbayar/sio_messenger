from django import forms


class ProfileForm(forms.Form):

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=254)
    image = forms.FileField(required=False)

    def __init__(self, profile, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not profile.image:
            self.fields['image'].required = True
