from parliament import Context
import logging
import json
import pickle
import numpy as np
 
def main(context: Context):
    """ 
    Serverless Function 
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    
    Testing:
    Call the Iris predictor with 4 input parameters.
    curl -X POST -H "Content-Type: application/json" --data '{"sl": 5.1, "sw": 3.5, "pl": 1.4, "pw": 0.2}' 127.0.0.1:8081 (should predict = 0)
    curl -X POST -H "Content-Type: application/json" --data '{"sl": 5.9, "sw": 3.0, "pl": 5.1, "pw": 1.8}' 127.0.0.1:8081 (should predict = 2)
    """
    model = None

    r = context.request
    logging.warning(f'************** Called function: context.request: {r}')
    logging.warning(f'************** Called function: content_length: {r.content_length}')
    logging.warning(f'************** Called function: get_data: {r.get_data()}')
    logging.warning(f'************** Called function: type: {type(r.get_data())}')
    logging.warning(f'************** Called function: headers: {r.headers}')

    # Get the data from Flask.
    data = json.loads(r.get_data())
    logging.warning(f'************** Called function: data: {data}')
    logging.warning(f'************** Called function: type(data): {type(data)}')

    logging.warning(f'************** Loading model.')
    try:
        model = pickle.load(open("iris.pkl", "rb"))
        logging.warning(f'************** Iris model loaded.')

    except Exception as e:
        logging.warning('Load model failed!!!')
        model = None

    # Convert the json to an numpy array
    predict_request = [data['sl'],data['sw'],data['pl'], data['pw']] 
    predict_request = np.array(predict_request).reshape(1,-1)
    
    # Pass in the np array to make a prediction.
    y_hat = model.predict(predict_request)
    
    # Return the prediction
    output = {'y_hat': int(y_hat[0])}
    logging.warning(f'************** prediction: {output}')

    return { "prediction": output['y_hat'] }, 200
