from django import forms

from .models import MaterialSpecification, Quotation


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            "quotation_number",
            "client_name",
            "client_phone",
            "client_email",
            "project_type",
            "project_location",
            "designer_name",
            "quotation_date",
            "expected_completion_date",
            "project_area_sqft",
            "design_theme",
            "execution_timeline",
            "scope_of_work",
            "exclusions",
            "payment_terms",
            "warranty_terms",
            "selected_package",
            "base_amount",
            "package_amount",
            "notes",
        ]
        widgets = {
            "quotation_date": forms.DateInput(attrs={"type": "date"}),
            "expected_completion_date": forms.DateInput(attrs={"type": "date"}),
            "base_amount": forms.HiddenInput(),
            "package_amount": forms.HiddenInput(),
            "selected_package": forms.HiddenInput(),
        }


class MaterialSpecificationForm(forms.ModelForm):
    class Meta:
        model = MaterialSpecification
        exclude = ("quotation",)
