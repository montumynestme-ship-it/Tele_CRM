from django.contrib import admin
from .models import (
    CivilWorkItem,
    CompanyDetails,
    MaterialSpecification,
    PaymentPlan,
    Quotation,
    QuotationItem,
    QuotationSection,
)

admin.site.register(Quotation)
admin.site.register(QuotationSection)
admin.site.register(QuotationItem)
admin.site.register(PaymentPlan)
admin.site.register(MaterialSpecification)
admin.site.register(CivilWorkItem)
admin.site.register(CompanyDetails)
