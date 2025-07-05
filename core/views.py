from django.shortcuts import render
from .models import RecentActivity
from master.models import UserCustom

def recent_activity_view(request):
    activities = RecentActivity.objects.order_by('-timestamp')[:50]  # last 50 activities

    # 1️⃣ Extract user_ids from activities
    user_ids = [activity.user_id for activity in activities if activity.user_id]

    # 2️⃣ Fetch usernames in one query
    users = UserCustom.objects.filter(id__in=user_ids).values('id', 'username')
    user_dict = {user['id']: user['username'] for user in users}

    # 3️⃣ Annotate each activity with username
    for activity in activities:
        activity.username = user_dict.get(activity.user_id, "Unknown")

    return render(request, 'core/recent_activity.html', {
        'activities': activities,
    })
