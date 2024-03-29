from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description",)
    search_fields = ("title",)
    list_filter = ("title",)
    empty_value_display = "-пусто-"
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
