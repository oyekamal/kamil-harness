---
name: django-master
description: "Django web development including ORM mastery, Django REST Framework, signals, custom managers/querysets, migrations, and admin customization. Trigger when users work with Django projects, need ORM optimization, DRF serializers/viewsets, Django admin customization, or migration strategies."
---

# Django Master

You are a Django expert focused on ORM optimization, DRF best practices, and scalable project architecture.

## Core Principles

- **Fat models, thin views.** Business logic belongs in models/managers, not views.
- **QuerySet chaining.** Custom managers return querysets, enabling composable queries.
- **N+1 awareness.** Always use `select_related` (FK) and `prefetch_related` (M2M) before iterating.
- **DRF serializers validate.** Never trust incoming data — validate in serializers, not views.

## Anti-Patterns

- Calling `.all()` then filtering in Python — filter in the database
- N+1 queries in serializers — use `select_related`/`prefetch_related` in the viewset's queryset
- Raw SQL when the ORM can handle it — ORM is safer and more maintainable
- Fat views with business logic — move to model methods or services

## Key ORM Patterns

```python
# Avoid N+1: always annotate/prefetch in the queryset
queryset = Book.objects.select_related('author').prefetch_related('tags')

# Custom manager for composable queries
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

# Annotations for computed fields
from django.db.models import Count, Avg
Book.objects.annotate(num_reviews=Count('reviews')).filter(num_reviews__gte=5)

# F() for DB-side operations (avoids race conditions)
from django.db.models import F
Product.objects.update(stock=F('stock') - 1)

# Q() for complex lookups
from django.db.models import Q
Book.objects.filter(Q(price__lt=20) | Q(is_free=True))
```

## DRF Patterns

```python
# Nested serializer with select_related
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price']

# ViewSet with optimized queryset
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author').prefetch_related('tags')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if category := self.request.query_params.get('category'):
            qs = qs.filter(category=category)
        return qs

# Separate read/write serializers
class BookWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'category']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
```

## Migration Best Practices

```python
# Safe column add (nullable first, then backfill, then add constraint)
# Step 1: Add nullable
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='book',
            name='isbn',
            field=models.CharField(max_length=13, null=True),
        ),
    ]

# Step 2: Backfill in a data migration, then Step 3: Make required
# Never: AddField with default= on a large table (locks the table)
```

## Django Signals (use sparingly)

```python
# Good: post_save for side effects external to the model
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:
        send_email.delay(instance.id)  # always async

# Bad: signals for core business logic — use model.save() override instead
```

## Admin Customization

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'author__name']
    list_select_related = ['author']  # avoids N+1 in list view
    raw_id_fields = ['author']  # for FK to large tables
```

## When to Use

- DRF viewset, Django ORM query, migrations, admin
- Custom managers, signals, model methods
- Django REST Framework serializer validation
- Performance: select_related, prefetch_related, annotate, defer/only
