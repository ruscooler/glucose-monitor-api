echo "Waiting for the database..."
docker/wait-for-it.sh db:5432

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating a superuser..."
echo "from django.contrib.auth import get_user_model;\
  User = get_user_model();\
  User.objects.create_superuser('admin','admin@admin.com', 'admin')" |
  python manage.py shell

exec "$@"