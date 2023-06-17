from load_model import saved_model

from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import json


app = Flask(__name__)

# Loading crop recommendation model
crop_recommendation_model = saved_model

# Loading crop data into a dataframe
crop_data = pd.read_csv('fertiliser-application-stage.csv')





def crop_prediction(N, P, K, temperature, humidity, ph, rainfall):
    data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    data = pd.DataFrame(data, columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    my_prediction = crop_recommendation_model.predict(data)
    final_prediction = my_prediction[0]

    return final_prediction


def fertilizer_recommendation(crop_name, dataframe):
    crop_row = dataframe[dataframe['CROP TYPE'] == crop_name]
    if not crop_row.empty:
        crop_ferts = crop_row.values.tolist()[0]
    else:
        crop_ferts = "Crop not found in the dataframe."

    return crop_ferts, crop_name


@app.route('/api/crop-recommendation', methods=['GET'])
def get_crop_recommendation():
    # Get user input from request data or query parameters
    data = request.get_json() or request.args
    print('request data', data)
    # Extract user input data
    N = float(data.get('N', 0))
    P = float(data.get('P', 0))
    K = float(data.get('K', 0))
    temperature = float(data.get('temperature', 0))
    humidity = float(data.get('humidity', 0))
    ph = float(data.get('ph', 0))
    rainfall = float(data.get('rainfall', 0))

    # Perform crop prediction
    crop_name = crop_prediction(N, P, K, temperature, humidity, ph, rainfall).upper()

    # Retrieve fertilizer recommendation for the predicted crop
    crop_fert, _ = fertilizer_recommendation(crop_name, crop_data)

    response = {
        'recommended_crop': crop_name,
        'recommended_fertilizers': crop_fert[1:3],
        'pre_planting_fertilizer': crop_fert[1],
        'top_dressing_fertilizer': crop_fert[2]
    }

    data = json.dumps(response)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

