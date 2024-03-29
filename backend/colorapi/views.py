from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, renderers
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from .apps import ColorapiConfig
import base64
from io import BytesIO
from PIL import Image, ImageOps
import requests, json
import random

class GeneratePaletteAPI(APIView):
    colorMats = {
        '':
        [1,1,1,
         1,1,1,
         1,1,1],
        # Red-Blind
        'Protanopia':   
        [0.567,0.433,0.000,
        0.558,0.442,0.000,
        0.000,0.242,0.758],
        # Green-Blind
        'Deuteranopia': 
        [0.625,0.375,0.000,
        0.700,0.300,0.000,
        0.000,0.300,0.700],
        # Blue-Blind
        'Tritanopia':   
        [0.950,0.050,0.000,
        0.000,0.433,0.567,
        0.000,0.475,0.525],
        # Monochromacy
        'Achromatopsia':
        [0.299,0.587,0.114,
        0.299,0.587,0.114,
        0.299,0.587,0.114],
        }
    
    def apply_color_matrix(self, color, colorBlindnessType):
        matrix = self.colorMats.get(colorBlindnessType)
        r = round(color[0] * matrix[0] + color[1] * matrix[1] + color[2] * matrix[2])
        g = round(color[0] * matrix[3] + color[1] * matrix[4] + color[2] * matrix[5])
        b = round(color[0] * matrix[6] + color[1] * matrix[7] + color[2] * matrix[8])
        return [r, g, b]

    def post(self, request):
        try:
            url = "http://colormind.io/api/"
            list_url = "http://colormind.io/list/"
            
            response = requests.get(list_url)
            data = request.data
            colorBlindnessType = request.query_params.get('colorType', None)
            print(colorBlindnessType)


            # model is the color model specified in the request data. 
            # input_colors is a list of colors provided in the request data. 
            #model = data.get('model', 'default')

            if response.status_code == 200:
                models = response.json().get('result', [])
                model = random.choice(models)
            input_colors = data.get('input', [])

            payload = {
                'model': model,
                'input': input_colors if input_colors else ["N"] * 5  # Replace 5 with your desired number of colors
            }

            response = requests.post(url, data=json.dumps(payload))

            if response.status_code == 200:
                result = response.json().get('result', [])
                
                palette = []
                paletteWithType = []
                
                for idx, color in enumerate(result):
                    if idx < len(input_colors) and input_colors[idx] != "N":
                        locked_color = self.apply_color_matrix(input_colors[idx], colorBlindnessType)
                        paletteWithType.append({'rgb': locked_color, 'isLocked': True}) 
                        palette.append({'rgb': input_colors[idx], 'isLocked': True})
                    else:
                        transformed_color = self.apply_color_matrix(color, colorBlindnessType)
                        palette.append({'rgb': color, 'isLocked': False})
                        paletteWithType.append({'rgb': transformed_color, 'isLocked': False})


                return Response({'palette': palette, 'paletteWithType': paletteWithType, 'colorType': colorBlindnessType}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to generate palette', 'status_code': response.status_code}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ColorRecognitionAPI(APIView):
    def post(self, request):
        try:
            # Load the color recognition model
            color_model = ColorapiConfig.model 

            if not request:
                return Response({'error': 'Image file is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Process the uploaded image
            img = Image.open(request)

            img_array = np.array(img)
            resized_array = img_array

            # Extract RGB values from the processed image
            red_channel = resized_array[:, :, 0]
            green_channel = resized_array[:, :, 1]
            blue_channel = resized_array[:, :, 2]

            # Create a DataFrame from RGB values
            image_df = pd.DataFrame({'red': red_channel.ravel(),
                                     'green': green_channel.ravel(),
                                     'blue': blue_channel.ravel()})

            # Make predictions using the color model
            predictions = color_model.predict(image_df)

            predicted = np.argmax(predictions, axis=1)
            predicted = pd.DataFrame(predicted, columns=['label']).to_json()

            return Response(predicted, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Color recognition failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignificantColorsAPI(APIView):
    def post(self, request):
        try:
            img = Image.open(request)

            img_array = np.array(img)
            reshaped_array = img_array.reshape((-1, 3))

            # Perform k-means clustering to find dominant colors
            num_colors = 5  # You can adjust this based on the number of colors you want in the palette
            kmeans = KMeans(n_clusters=num_colors, random_state=42)
            kmeans.fit(reshaped_array)
            dominant_colors = kmeans.cluster_centers_.astype(int)

            return Response({'palette': dominant_colors.tolist()}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Color recognition failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class SimulationAPI(APIView):

    colorMats = {
        # Red-Blind
        'Protanopia':   
        [0.567,0.433,0.000,
        0.558,0.442,0.000,
        0.000,0.242,0.758],
        # Green-Blind
        'Deuteranopia': 
        [0.625,0.375,0.000,
        0.700,0.300,0.000,
        0.000,0.300,0.700],
        # Blue-Blind
        'Tritanopia':   
        [0.950,0.050,0.000,
        0.000,0.433,0.567,
        0.000,0.475,0.525],
        # Monochromacy
        'Achromatopsia':
        [0.299,0.587,0.114,
        0.299,0.587,0.114,
        0.299,0.587,0.114],
        }
    
    def simulate_colorblindness(self, red, green, blue, color_matrix):

        # Apply the protanomaly matrix to the original RGB values
        new_rgb_values = np.dot(np.array(color_matrix).reshape((3,3)), [red, green, blue])

        # Extract the simulated RGB values
        new_red, new_green, new_blue = new_rgb_values

        return new_red, new_green, new_blue
    
    def post(self, request):
        try:
            
            simulationType = request.query_params.get('simulateType')
            img = Image.open(request.FILES.get('image'))

            img_array = np.array(img)

            # Extract RGB values from the processed image
            red_channel = img_array[:, :, 0]
            green_channel = img_array[:, :, 1]
            blue_channel = img_array[:, :, 2]

            for i in range(img_array.shape[0]):
                for j in range(img_array.shape[1]):
                    # Get the original RGB values
                    red = img_array[i, j, 0]
                    green = img_array[i, j, 1]
                    blue = img_array[i, j, 2]
                        
                    # Choose a color matrix based on the type of colorblindness
                    color_matrix = self.colorMats.get(simulationType)

                    # Update RGB values
                    new_red, new_green, new_blue = self.simulate_colorblindness(red, green, blue, color_matrix)

                    # Update RGB values of the pixel
                    img_array[i, j, 0] = new_red
                    img_array[i, j, 1] = new_green
                    img_array[i, j, 2] = new_blue
                
                modified_img_array = np.stack([red_channel, green_channel, blue_channel], axis=-1)
                modified_img = Image.fromarray(modified_img_array)

                compressed_buffer = BytesIO()

                # Resize the image to a reasonable size
                modified_img = ImageOps.exif_transpose(modified_img)
                modified_img.thumbnail((800, 800))

                # Save the compressed image to the buffer
                modified_img.save(compressed_buffer, format="JPEG", quality=85)

                # Get the base64-encoded string of the compressed image
                img_str = base64.b64encode(compressed_buffer.getvalue()).decode("utf-8")

            return Response({'simulationType': simulationType, 'modifiedImage': img_str}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': f'Color recognition failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)