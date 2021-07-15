from parliament import Context
import logging
import json
import pickle
import numpy as np
 
model = None

def main(context: Context):
    """    Serverless Function 
    Args:
        context (Context): The context parameter contains the Flask request object and any
    CloudEvent received with the request.

    Returns:
        [tuple]: (prediction dict, http status)
    """
    #
    # Load the model from storage. Globals are used to prevent the model
    # from being loaded more than once.
    #
    global model
    
    if model == None:
        logging.info(f'Loading model.')
        try:
            model = pickle.load(open("iris_rfc.pkl", "rb"))
            logging.info(f'Iris model loaded.')
        except Exception as e:
            logging.warning(f'Load model failed!!!')
            model = None
    #
    # Get the json data from Flask and convert it to a python dictionary.
    #
    r = context.request
    data = json.loads(r.get_data())
    
    #
    # Prepare the data for use in a prediction. Get the 4 prediction parameters from the dictionary
    # and convert them to a flattened numpy array. The format is often model dependent.
    #
    predict_request = np.array([data['sl'],data['sw'],data['pl'], data['pw']]).reshape(1,-1)
    
    #
    # Call the model's predict function by passing in the numpy array and 
    # return the prediction and an OK status.
    #
    try:
        y_hat = model.predict(predict_request)
        output = {'y_hat': int(y_hat[0])}
        return { "prediction": output['y_hat'] }, 200
    except:
        logging.warning(f'Bad data or prediction')
        return { "no": "content" }, 204
