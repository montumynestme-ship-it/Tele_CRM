from django.contrib.auth import get_user_model
from crm_api.models import Lead, LeadImport

User = get_user_model()

def global_context(request):
    """
    Provides global data to all templates, such as the list of salespeople and imported leads.
    """
    if request.user.is_authenticated:
        # Fetching all users who can be assigned leads
        salespeople = User.objects.all() 
        # Fetching latest 100 unconverted imports for the selector
        unconverted_imports = LeadImport.objects.filter(is_converted=False).order_by('-timestamp')[:100]
        
        return {
            'global_salespeople': salespeople,
            'global_unconverted_imports': unconverted_imports
        }
    return {}
