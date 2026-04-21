"""
Management command: seed_test_data
===================================

Populates the database with realistic dummy data so the admin changelist
has meaningful content for testing every smart-filter kind.

Usage::

    python manage.py seed_test_data          # 200 tasks (default)
    python manage.py seed_test_data --tasks 500
    python manage.py seed_test_data --flush   # wipe existing data first
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from test_app.models import Category, Task

User = get_user_model()

# ── Seed constants ──────────────────────────────────────────────────────

CATEGORY_NAMES = [
    "Backend",
    "Frontend",
    "DevOps",
    "Design",
    "QA",
    "Security",
    "Documentation",
    "Infrastructure",
    "Mobile",
    "Data Science",
]

FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Eve",
    "Frank", "Grace", "Hector", "Ivy", "Jack",
]

TASK_TITLES = [
    "Set up CI/CD pipeline",
    "Fix login page redirect loop",
    "Implement dark-mode toggle",
    "Write unit tests for payment module",
    "Optimise database indexes",
    "Upgrade Django to latest LTS",
    "Add CSV export to admin",
    "Review pull request #142",
    "Migrate legacy API v1 endpoints",
    "Create onboarding documentation",
    "Add rate-limiting middleware",
    "Design new dashboard wireframes",
    "Investigate memory leak in worker",
    "Build email notification service",
    "Refactor permissions module",
    "Containerise staging environment",
    "Add search to admin changelist",
    "Implement two-factor authentication",
    "Benchmark serialiser performance",
    "Automate SSL certificate renewal",
    "Create feature-flag system",
    "Fix timezone handling in reports",
    "Set up error tracking with Sentry",
    "Write API documentation",
    "Implement WebSocket notifications",
    "Add drag-and-drop file upload",
    "Audit third-party dependencies",
    "Create database backup strategy",
    "Fix mobile responsive layout",
    "Implement audit logging",
]


class Command(BaseCommand):
    help = "Seed the database with sample Categories, Users, and Tasks."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tasks",
            type=int,
            default=200,
            help="Number of Task records to create (default: 200).",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            default=False,
            help="Delete all existing test data before seeding.",
        )

    def handle(self, *args, **options):
        task_count: int = options["tasks"]
        flush: bool = options["flush"]

        if flush:
            self.stdout.write("Flushing existing data...")
            Task.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING("  done."))

        # ── Categories ──────────────────────────────────────────────
        categories = []
        for name in CATEGORY_NAMES:
            cat, created = Category.objects.get_or_create(name=name)
            categories.append(cat)
            if created:
                self.stdout.write(f"  + Category: {cat}")

        # ── Users (non-superuser staff) ─────────────────────────────
        users = list(User.objects.filter(is_staff=True))
        for first in FIRST_NAMES:
            username = first.lower()
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="testpass123",
                    first_name=first,
                    last_name="Tester",
                    is_staff=True,
                )
                users.append(user)
                self.stdout.write(f"  + User: {user.username}")

        if not users:
            # fallback: ensure at least one user exists
            users = list(User.objects.all()[:1])

        # ── Superuser (for admin login) ─────────────────────────────
        if not User.objects.filter(is_superuser=True).exists():
            su = User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin",
            )
            self.stdout.write(self.style.SUCCESS(
                f"  * Superuser created: {su.username} / admin"
            ))

        # ── Tasks ───────────────────────────────────────────────────
        statuses = [s.value for s in Task.Status]
        priorities = [p.value for p in Task.Priority]
        today = date.today()
        bulk = []

        for i in range(task_count):
            due = today + timedelta(days=random.randint(-30, 90)) if random.random() > 0.15 else None
            bulk.append(
                Task(
                    title=f"{random.choice(TASK_TITLES)} #{i + 1}",
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    category=random.choice(categories) if random.random() > 0.1 else None,
                    assignee=random.choice(users) if random.random() > 0.2 else None,
                    score=round(random.uniform(0, 100), 1) if random.random() > 0.25 else None,
                    is_active=random.random() > 0.3,
                    due_date=due,
                )
            )

        Task.objects.bulk_create(bulk)
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Seeded {task_count} tasks, "
            f"{len(categories)} categories, "
            f"{len(users)} users."
        ))
