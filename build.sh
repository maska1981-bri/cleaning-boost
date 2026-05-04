pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='demo').exists() or User.objects.create_superuser('demo', 'demo@example.com', 'Demo123!')" | python manage.py shell