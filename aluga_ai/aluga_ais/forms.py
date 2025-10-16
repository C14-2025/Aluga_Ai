from django import forms
from .models import Topic,Entry

class TopicForm(forms.ModelForm):
    """Form for creating and editing topics."""
    
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}  # No label for the text field
        
class EntryForm(forms.ModelForm):
    """Form for creating and editing entries."""
    
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': ''}  # No label for the text field
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}  # Textarea with 80 columns