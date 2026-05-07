pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

echo "
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='demo').exists():
    User.objects.create_user(
        username='demo',
        email='demo@example.com',
        password='Demo123!'
    )
" | python manage.py shell