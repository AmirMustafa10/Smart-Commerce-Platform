from django.contrib.auth import get_user_model
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q, F, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from core.models import (
    StoreManagerRequiredMixin,
    ShipperRequiredMixin,
    TenantQuerySetMixin,
)
from orders.models import Order, OrderItem
from products.models import Product

CustomUser = get_user_model()


class ManagerDashboardView(
    LoginRequiredMixin, TenantQuerySetMixin, StoreManagerRequiredMixin, TemplateView
):
    """
    KPI dashboard for store owners/managers.

    Provides:
    - total_orders_today    : int
    - revenue_this_month    : Decimal (DELIVERED orders only)
    - orders_by_status      : dict {status: count}
    - top_products          : list of {name, total_qty}
    - sales_last_7_days     : list of {date: 'YYYY-MM-DD', total: float} — Chart.js ready
    - pending_orders_count     : int
    - delivered_orders_today_count: int
    - unsettled_cash: Decimal
    - average_order_value: Decimal
    - low_stock_products          : list of products
    - recent_activities          : list of activities
    """

    template_name = "dashboards/manager_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        store = self.request.user.store
        today = timezone.localdate()
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # ------------------------------------------------------------------
        # Base querysets (single definition → reused, keeps queries DRY)
        # ------------------------------------------------------------------
        base_orders = Order.objects.filter(store=self.request.user.store)

        # items only Actail DELIVERED
        base_items = OrderItem.objects.filter(
            order__in=base_orders, order__status=Order.Status.DELIVERED
        )

        # ------------------------------------------------------------------
        # 1. Total orders created today
        # ------------------------------------------------------------------
        context["total_orders_today"] = base_orders.filter(
            created_at__date=today
        ).count()

        # ------------------------------------------------------------------
        # 2. Revenue this month (DELIVERED orders only)
        # ------------------------------------------------------------------
        revenue = base_orders.filter(
            status=Order.Status.DELIVERED,
            created_at__gte=month_start,
        ).aggregate(total=Sum("total_amount"))["total"]
        context["revenue_this_month"] = revenue or 0

        # ------------------------------------------------------------------
        # 3. Orders grouped by status — single query, converted to dict
        # ------------------------------------------------------------------
        status_counts = {
            status_key: 0 for status_key, status_label in Order.Status.choices
        }

        status_rows = (
            base_orders.values("status").annotate(count=Count("id")).order_by("status")
        )

        for row in status_rows:
            if row["status"] in status_counts:
                status_counts[row["status"]] = row["count"]

        context["orders_by_status"] = status_counts

        # ------------------------------------------------------------------
        # 4. Top 5 best-selling products (by total quantity sold)
        #    Joins OrderItem → Product in a single aggregate query.
        # ------------------------------------------------------------------
        context["top_products"] = list(
            base_items.values(name=F("product__name"))
            .annotate(total_qty=Sum("quantity"))
            .order_by("-total_qty")[:5]
        )

        # ------------------------------------------------------------------
        # 5. Sales trend for the last 7 days — Chart.js ready
        #    Uses TruncDate for a single GROUP BY day aggregate.
        # ------------------------------------------------------------------
        seven_days_ago = today - timedelta(days=6)

        # We fetch data from the database in a single daily query, grouping by the total amount of orders.
        raw_sales = (
            base_orders.filter(created_at__date__gte=seven_days_ago)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Sum("total_amount"))
            .order_by("day")
        )

        # Create a dictionary to iterate through each row in `raw_sales`; if a day has a `total_amount`, store that value,otherwise store zero (indicating nothing was sold that day).
        sales_map = {row["day"]: float(row["total"] or 0) for row in raw_sales}
        sales_list = []

        # We calculate the date of this lap (date from a week ago + number of days in the lap) to get each day of the week. Iftoday is the 12th, then the first lap is 12 + 0, the second is 12 + 1, so it's day 13, etc.
        for offset in range(7):
            current_date = seven_days_ago + timedelta(days=offset)

            formatted_date = current_date.strftime("%Y-%m-%d")

            # We ask the dictionary: "Was anything sold today?" If yes, get the figure; if no, set it to 0.0.
            daily_total = sales_map.get(current_date, 0.0)

            sales_list.append({"date": formatted_date, "total": daily_total})

        context["sales_last_7_days"] = sales_list

        # ------------------------------------------------------------------
        # 5. Number of pending orders
        # ------------------------------------------------------------------
        context["pending_orders_count"] = base_orders.filter(
            status=Order.Status.PENDING
        ).count()

        # ------------------------------------------------------------------
        # 6. Number of DELIVERED orders today
        # ------------------------------------------------------------------
        context["delivered_orders_today_count"] = base_orders.filter(
            status=Order.Status.DELIVERED,
            delivered_at__date=today,
        ).count()

        # ------------------------------------------------------------------
        # 7. Unsettled Cash (Cash held by Shippers)
        # ------------------------------------------------------------------
        unsettled_cash_query = base_orders.filter(
            status=Order.Status.DELIVERED,
            is_settled=False,
            payment_method=Order.PaymentMethod.COD,
        ).aggregate(total_cash=Sum("total_amount"))

        context["unsettled_cash"] = unsettled_cash_query["total_cash"] or 0.0

        # ------------------------------------------------------------------
        # 8. Average Order Value
        # ------------------------------------------------------------------
        aov_query = base_orders.filter(status=Order.Status.DELIVERED).aggregate(
            avg_value=Avg("total_amount")
        )

        avg_value = aov_query["avg_value"] or 0.0
        context["average_order_value"] = round(avg_value, 2)

        # ------------------------------------------------------------------
        # 9. Low Stock Alerts
        # ------------------------------------------------------------------
        context["low_stock_products"] = list(
            Product.objects.filter(
                store=self.request.user.store,
                stock_quantity__lte=5,
            )
            .values("name", "stock_quantity")
            .order_by("stock_quantity")[:10]
        )

        # ------------------------------------------------------------------
        # 10. recent_activities
        # ------------------------------------------------------------------
        context["recent_activities"] = list(
            base_orders.values(
                "id",
                "customer__name",
                "status",
                "updated_at",
            ).order_by("-updated_at")[:5]
        )

        return context


class ShipperDashboardView(
    LoginRequiredMixin, TenantQuerySetMixin, ShipperRequiredMixin, TemplateView
):
    """
    Daily settlement dashboard for delivery workers (shippers).

    Provides:
    - cash_collected_today  : Decimal — total CASH the shipper has collected today
    - Total Unsettled Cash  : Decimal — total CASH the shipper Unsettled
    - Active Deliveries: QuerySet — Orders shipped by the shipper (for list display).
    - delivered_orders_today: QuerySet — today's delivered orders (for the list view)
    """

    template_name = "dashboards/shipper_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shipper = self.request.user
        store = shipper.store
        today = timezone.localdate()

        # ------------------------------------------------------------------
        # Base queryset — scoped to this shipper's store, no soft-deleted
        # ------------------------------------------------------------------
        base = Order.objects.filter(
            store=store,
            shipper=shipper,
        )

        # ------------------------------------------------------------------
        # 1. Cash collected today
        # ------------------------------------------------------------------
        cash = base.filter(
            status=Order.Status.DELIVERED,
            payment_method=Order.PaymentMethod.COD,
            delivered_at__date=today,
        ).aggregate(total=Sum("total_amount"))["total"]
        context["cash_collected_today"] = cash or 0

        # ------------------------------------------------------------------
        # 2. Total Unsettled Cash
        # ------------------------------------------------------------------
        unsettled_cash_query = base.filter(
            status=Order.Status.DELIVERED,
            payment_method=Order.PaymentMethod.COD,
            is_settled=False,
        ).aggregate(total_cash=Sum("total_amount"))["total_cash"]
        context["unsettled_cash"] = unsettled_cash_query or 0

        # ------------------------------------------------------------------
        # 3. Active Deliveries
        # ------------------------------------------------------------------
        context["active_orders"] = (
            base.filter(
                status=Order.Status.SHIPPED,
            )
            .select_related("customer")
            .order_by("-updated_at")
        )

        # ------------------------------------------------------------------
        # 4. Delivered orders today
        # ------------------------------------------------------------------
        context["delivered_orders_today"] = (
            base.filter(
                status=Order.Status.DELIVERED,
                delivered_at__date=today,
            )
            .select_related("customer")
            .order_by("-updated_at")
        )

        return context
