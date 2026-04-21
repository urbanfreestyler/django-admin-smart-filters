"""
Admin configuration that wires up SmartFilterAdminMixin on every model,
demonstrating each built-in filter kind.
"""

from django.contrib import admin

from django_admin_smart_filters.admin import SmartFilterAdminMixin
from django_admin_smart_filters.builder import Filter
from django_admin_smart_filters.declarations import DropdownFilter

from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Task)
class TaskAdmin(SmartFilterAdminMixin, admin.ModelAdmin):
    """
    Showcases all six built-in filter kinds provided by the package.

    Filters rendered in the changelist sidebar:
      • status      → dropdown
      • priority    → multi_select
      • due_date    → date_range
      • score       → numeric_range
      • is_active   → boolean_toggle
      • assignee    → autocomplete  (uses Django User search_fields)
    """

    # -- Standard ModelAdmin config --
    list_display = (
        "title",
        "status",
        "priority",
        "category",
        "assignee",
        "score",
        "is_active",
        "due_date",
        "created_at",
    )
    list_display_links = ("title",)
    list_per_page = 25
    search_fields = ("title",)
    autocomplete_fields = ("category",)
    raw_id_fields = ("assignee",)
    ordering = ("-created_at",)

    # -- Smart filter declarations (fluent builder style) --
    smart_filters = [
        # Class-style declaration
        DropdownFilter("status"),
        # Fluent-builder declarations
        Filter.field("priority").multi_select(),
        Filter.field("due_date").date_range(),
        Filter.field("score").numeric_range(),
        Filter.field("is_active").boolean_toggle(),
        Filter.field("assignee").autocomplete(),
    ]
