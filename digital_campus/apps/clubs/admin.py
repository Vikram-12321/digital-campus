from django.contrib import admin
from django.utils.html import format_html
from django import forms

from .models import Club, ClubMembership
from .forms import ClubMembershipForm


class ClubMembershipInline(admin.TabularInline):
    form = ClubMembershipForm
    model = ClubMembership
    extra = 1
    autocomplete_fields = []
    raw_id_fields = ['profile']
    fields = ('profile', 'role', 'status')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'profile':
            kwargs['widget'] = forms.Select(attrs={
                'style': 'width: 300px; height: 200px;'
            })
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    inlines = [ClubMembershipInline]
    list_display = ('name', 'display_owners', 'member_count', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('name', 'clubmembership__profile__user__username',)

    class Media:
        css = {
            'all': ('admin/css/clubs.css',)
        }

    def display_owners(self, obj):
        owners = obj.club_membership_set.filter(role='owner').select_related('profile__user')
        return format_html('<br>'.join([m.profile.user.username for m in owners]))
    display_owners.short_description = 'Owners'

    def member_count(self, obj):
        return obj.club_membership_set.count()
    member_count.short_description = 'Members'


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    form = ClubMembershipForm 
    raw_id_fields = []
    autocomplete_fields = []
    list_display = ('club', 'profile', 'role', 'status', 'joined_at')

    list_filter = ('club', 'role', 'status')
    list_editable = ('role', 'status')
    search_fields = ('club__name', 'profile__user__username',)
    date_hierarchy = 'joined_at'

    def profile_user(self, obj):
        return obj.profile.user.username
    profile_user.short_description = 'User'
    profile_user.admin_order_field = 'profile__user__username'
