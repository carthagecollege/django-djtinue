from django import forms
from django.contrib import admin
from django.utils import timezone
from django.core.urlresolvers import reverse

from djtinue.enrichment.models import Course, Registration

from datetime import timedelta


class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = (
        'title', 'course_number', 'credits', 'room', 'active'
    )
    ordering = ['active','title','course_number']


class OrderInline(admin.TabularInline):
    model = Registration.order.through
    max_num = 1
    exclude = ('order',)
    readonly_fields = [
        'cc_name','cc_4_digits','total','status','transid'
    ]
    can_delete = False

    def cc_name(self, instance):
        return instance.order.cc_name
    cc_name.short_description = 'Name on card'

    def cc_4_digits(self, instance):
        return "x{}".format(instance.order.cc_4_digits)
    cc_4_digits.short_description = 'Last 4 digits on card'

    def total(self, instance):
        return instance.order.total
    total.short_description = 'Total'

    def status(self, instance):
        return instance.order.status
    status.short_description = 'Status'

    def transid(self, instance):
        return instance.order.transid
    transid.short_description = 'Transaction ID'


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(label="Personal Email", required=False)
    phone = forms.CharField(label="Cell Phone", required=False)

    class Meta:
        model = Registration
        fields = '__all__'


class RegistrationAdmin(admin.ModelAdmin):
    model = Registration
    form =  RegistrationForm
    list_display = (
        'first_name', 'print_last_name', 'email','created_at','xdate'
    )
    fields = (
        'first_name', 'second_name', 'last_name', 'previous_name',
        'address1', 'city', 'state', 'postal_code',
        'phone', 'phone_home', 'phone_work',
        'email_work', 'email', 'social_security_number',
        'date_of_birth', 'attended_before', 'collegeid',
        'verify', 'courses'
    )
    search_fields = ('last_name', 'email','social_security_number')
    ordering = ['-created_at','last_name']
    raw_id_fields = ("order",)
    exclude = ('order',)
    inlines = [
        OrderInline,
    ]

    class Media:
        css = {
            'all': (
                '/static/djtinue/css/admin.css',
            )
        }
        #js = ('https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js',)

    def get_queryset(self, request):
        """
        only show registrations that were exported less than 21 days ago
        """
        now = timezone.now()
        ids = []
        qs = super(RegistrationAdmin, self).get_queryset(request)
        for reg in qs:
            #obj = reg.order.all()
            obj = reg.order.filter(status="approved")
            if len(obj) >= 1:
                '''
                order = obj[0]
                if order.export_date:
                    if order.export_date + timedelta(days=21) > now:
                        ids.append(reg.id)
                else:
                    ids.append(reg.id)
                '''
                # the above time restriction was not working for lynn
                # so we ignore it for now
                ids.append(reg.id)
        return qs.filter(pk__in=ids)

    def xdate(self, instance):
        order = instance.order.all()[0]
        return order.export_date
    xdate.short_description = 'Export Date'

    def print_last_name(self, obj):
        return u'<a href="{}">{}</a>'.format(
            reverse("registration_print", args=(obj.id,)),
            obj.last_name
        )
    print_last_name.allow_tags = True
    print_last_name.short_description = 'Last Name (print)'


admin.site.register(Course, CourseAdmin)
admin.site.register(Registration, RegistrationAdmin)
