from django import forms

class MessageForm(forms.Form):
    original_file = forms.FileField(
                                    label='Select a file',
                                    help_text='max. 42 megabytes'
                                    )
    creepify = forms.ChoiceField(choices=[
                                          ('yes','Yes'),
                                          ('no','No')
                                          ],
                                 widget=forms.RadioSelect(),
                                 label="Creepify?"
                                 )
