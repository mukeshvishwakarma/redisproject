import redis
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response


def get_redis_connection():
    try:
        return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    except redis.exceptions.ConnectionError as e:
        # Handle Redis connection error
        return Response({'error': f'Redis connection error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)