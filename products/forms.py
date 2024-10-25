from django import forms

class ContactForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter here'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter here'}))
    subject = forms.ChoiceField(choices=[
        ('', 'Select Subject **'),
        ('Delivery & Orders', 'Delivery & Orders'),
        ('Diet & Exercise', 'Diet & Exercise'),
        ('Marketing & Press', 'Marketing & Press'),
        ('Share Your Success', 'Share Your Success'),
        ('Wholesale And Returns', 'Wholesale And Returns'),
    ], required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter here'}), required=True)