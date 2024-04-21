from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Device, DeviceLocation
from .utils import get_redis_connection
import redis

@api_view(['GET'])
def latest_device_info(request, device_id):
    try:
        r = get_redis_connection()
        deviceid=device_id.strip('{}')
        if not r:
            return Response({'error': 'Failed to connect to Redis'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        device_info_bytes = r.hgetall(deviceid)
        if not device_info_bytes:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # Convert bytes keys to strings
        device_info = {key.decode('utf-8'): value.decode('utf-8') for key, value in device_info_bytes.items()}

        return Response(device_info)

    except redis.exceptions.ConnectionError as e:
        return Response({'error': f'Redis connection error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({'error': f'Unexpected error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def device_location(request, device_id):
    try:
        deviceid=device_id.strip('{}')
        # Attempt to retrieve the device and its start/end locations
        device = Device.objects.get(device_id=deviceid)
        start_location = DeviceLocation.objects.filter(device=device).order_by('timestamp').first()
        end_location = DeviceLocation.objects.filter(device=device).order_by('timestamp').last()
        
        # Prepare response data with start and end locations
        if start_location and end_location:
            response_data = {
                'start_location': (start_location.latitude, start_location.longitude),
                'end_location': (end_location.latitude, end_location.longitude)
            }
            return Response(response_data)
        else:
            return Response({'error': 'Start or end location not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except DeviceLocation.DoesNotExist:
        return Response({'error': 'Device locations not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # Handle other unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def device_location_points(request, device_id, start_time, end_time):
    try:
        deviceid=device_id.strip('{}')
        start_time=start_time.strip('{}')
        end_time=end_time.strip('{}')
        # Attempt to retrieve the device object by device_id
        device = Device.objects.get(device_id=deviceid)
        
        # Attempt to retrieve location points within the specified time range
        location_points = DeviceLocation.objects.filter(device=device, timestamp__range=(start_time, end_time))
        
        # Prepare response data with location points
        response_data = [
            {'latitude': point.latitude, 'longitude': point.longitude, 'timestamp': point.timestamp}
            for point in location_points
        ]
        
        return Response(response_data)
    
    except Device.DoesNotExist:
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
    
    except DeviceLocation.DoesNotExist:
        return Response({'error': 'Location points not found for the device within the specified time range'},
                        status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # Handle any other unexpected errors
        return Response({'error': f'Unexpected error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

