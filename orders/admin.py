from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem, PaymentSettings


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('card_number',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['book']
    extra = 0
    readonly_fields = ('book', 'quantity', 'price')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_info', 'status_badge', 'total_amount', 'address', 'landmark',
        'payment_screenshot_icon', 'created_at', 'action_buttons'
    )
    list_filter = ('status', 'created_at', 'payment_screenshot')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name', 'address', 'landmark')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    readonly_fields = (
        'user', 'status', 'total_amount', 'address', 'landmark',
        'payment_screenshot_display', 'created_at', 'updated_at'
    )
    actions = [
        'mark_as_confirmed_preparing',
        'mark_as_awaiting_delivery',
        'mark_as_delivered',
        'mark_as_cancelled',
        'export_as_csv',
    ]
    fieldsets = (
        ('Buyurtma maʼlumotlari', {
            'fields': ('user', 'status', 'total_amount', 'address', 'landmark', 'created_at', 'updated_at')
        }),
        ("To'lov maʼlumotlari", {
            'fields': ('payment_screenshot', 'payment_screenshot_display')
        }),
    )

    def user_info(self, obj):
        return format_html(
            '<b>{}</b><br><span class="text-muted">{}</span>',
            obj.user.first_name or '', obj.user.phone
        )
    user_info.short_description = 'Foydalanuvchi'

    def status_badge(self, obj):
        color = {
            'pending': 'secondary',
            'awaiting_confirmation': 'warning',
            'confirmed_preparing': 'primary',
            'awaiting_delivery': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
        }.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>', color, obj.get_status_display()
        )
    status_badge.short_description = 'Holat'

    def payment_screenshot_icon(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<a href="#" onclick="return showScreenshot(\'{}\')">'
                '<i class="fas fa-image fa-lg text-success"></i>'
                '</a>',
                obj.payment_screenshot.url
            )
        return format_html('<span class="text-muted">Yoʻq</span>')
    payment_screenshot_icon.short_description = "To'lov skrini"

    def payment_screenshot_display(self, obj):
        if obj.payment_screenshot:
            return format_html('<img src="{}" width="300" />', obj.payment_screenshot.url)
        return format_html('<span class="text-muted">Yoʻq</span>')
    payment_screenshot_display.short_description = "To'lov skrini (katta)"

    def action_buttons(self, obj):
        if obj.status == 'awaiting_confirmation':
            return format_html(
                '<a href="{}" class="btn btn-success btn-sm me-1">Tasdiqlash</a>'
                '<a href="{}" class="btn btn-danger btn-sm">Bekor qilish</a>',
                reverse('orders:order_confirm', args=[obj.id]),
                reverse('orders:order_cancel', args=[obj.id])
            )
        elif obj.status == 'confirmed_preparing':
            return format_html(
                '<a href="{}" class="btn btn-info btn-sm">Yetkazib berishga tayyor</a>',
                reverse('orders:order_awaiting_delivery', args=[obj.id])
            )
        elif obj.status == 'awaiting_delivery':
            return format_html(
                '<a href="{}" class="btn btn-primary btn-sm">Yetkazib berilgan</a>',
                reverse('orders:order_delivered', args=[obj.id])
            )
        elif obj.status == 'delivered':
            return format_html('<span class="badge bg-success">Yetkazib berilgan</span>')
        elif obj.status == 'cancelled':
            return format_html('<span class="badge bg-danger">Bekor qilingan</span>')
        return ''
    action_buttons.short_description = "Amallar"

    def mark_as_confirmed_preparing(self, request, queryset):
        updated = queryset.update(status='confirmed_preparing')
        self.message_user(request, f"{updated} ta buyurtma 'Tasdiqlangan, yetkazib berishga tayyorlanmoqda' holatiga o'tkazildi.")
    mark_as_confirmed_preparing.short_description = "Tasdiqlangan, yetkazib berishga tayyorlanmoqda"

    def mark_as_awaiting_delivery(self, request, queryset):
        updated = queryset.update(status='awaiting_delivery')
        self.message_user(request, f"{updated} ta buyurtma 'Yetkazib berilishi kutilmoqda' holatiga o'tkazildi.")
    mark_as_awaiting_delivery.short_description = "Yetkazib berilishi kutilmoqda"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f"{updated} ta buyurtma 'Yetkazib berilgan' holatiga o'tkazildi.")
    mark_as_delivered.short_description = "Yetkazib berilgan"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} ta buyurtma 'Bekor qilindi' holatiga o'tkazildi.")
    mark_as_cancelled.short_description = "Bekor qilish"

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=buyurtmalar.csv'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Foydalanuvchi', 'Telefon', 'Holat', 'Jami summa', 'Manzil', "Mo'ljal", 'Yaratilgan'])
        for order in queryset:
            writer.writerow([
                order.id,
                order.user.first_name,
                order.user.phone,
                order.get_status_display(),
                order.total_amount,
                order.address,
                order.landmark,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response
    export_as_csv.short_description = "Tanlanganlarni CSVga eksport qilish"

    class Media:
        css = {
            'all': (
                'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
            )
        }
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js',
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['modal_html'] = """
            <div id=\"screenshotModal\" style=\"display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7);\">
                <div style=\"position: relative; background-color: #fff; margin: 5% auto; padding: 20px; width: 80%; max-width: 800px; border-radius: 5px;\">
                    <div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;\">
                        <h5 style=\"margin: 0;\">To'lov skrini</h5>
                        <button onclick=\"hideScreenshot()\" style=\"background: none; border: none; font-size: 20px; cursor: pointer;\">&times;</button>
                    </div>
                    <div style=\"text-align: center;\">
                        <img id=\"screenshotImage\" src=\"\" style=\"max-width: 100%; max-height: 70vh;\">
                    </div>
                </div>
            </div>
            <script>
                function showScreenshot(url) {
                    document.getElementById('screenshotImage').src = url;
                    document.getElementById('screenshotModal').style.display = 'block';
                    return false;
                }
                function hideScreenshot() {
                    document.getElementById('screenshotModal').style.display = 'none';
                }
                document.getElementById('screenshotModal').addEventListener('click', function(e) {
                    if (e.target === this) {
                        hideScreenshot();
                    }
                });
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape') {
                        hideScreenshot();
                    }
                });
            </script>
        """
        return super().changelist_view(request, extra_context=extra_context)
