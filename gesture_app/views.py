from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import mediapipe as mp
import numpy as np
import base64
import time
from django.shortcuts import render
import json

def index(request):
    return render(request, 'index.html')


# Gesture Recognition Setup
mp_tasks = mp.tasks
BaseOptions = mp_tasks.BaseOptions
GestureRecognizer = mp_tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp_tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp_tasks.vision.RunningMode


latest_result = None

def print_result(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='/Users/omarqandil/Desktop/Trial 1000/exported_model/gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

recognizer = GestureRecognizer.create_from_options(options)

@csrf_exempt
def process_frame(request):
    global latest_result
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON from request body
            frame_data = data['frame']
            frame_data = frame_data.split(',')[1]  # Remove the Base64 header
            frame_bytes = base64.b64decode(frame_data)  # Decode Base64
            frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)  # Convert to NumPy array
            frame = cv2.imdecode(frame_np, flags=1)  # Decode image

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
            h, w, c = frame_rgb.shape
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            frame_timestamp_ms = int(time.time() * 1000)
            recognizer.recognize_async(mp_image, frame_timestamp_ms)

            result_text = "No gesture detected"
            if latest_result is not None:
                if latest_result.gestures:
                    result_text = f"Result: {latest_result.gestures[0][0].category_name}"

            return JsonResponse({'result': result_text})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Frame data missing'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


