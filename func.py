from parliament import Context
import logging
import json
import pickle
import numpy as np
 
model = None

def main(context: Context):
    """ 
    Serverless Function 
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    """
    r = context.request
    
    #
    # Debug output.
    #
    logging.warning(f'')
    logging.warning(f'')
    logging.warning(f'**************************************************************')
    logging.warning(f'************** main function called.')
    logging.warning(f'**************  context.request: {r}')
    logging.warning(f'**************  content_length: {r.content_length}')
    logging.warning(f'**************  get_data: {r.get_data()}')
    logging.warning(f'**************  type: {type(r.get_data())}')
    logging.warning(f'**************  headers: {r.headers}')

    #
    # Get the json data from Flask and convert it a python dictionary.
    #
    data = json.loads(r.get_data())
    logging.warning(f'**************  data: {data}')
    logging.warning(f'**************  type(data): {type(data)}')

    #
    # Load the model from storage.
    #
    global model
    
    if model == None:
        logging.warning(f'************** Loading model.')
        try:
            model = pickle.load(open("iris_rfc.pkl", "rb"))
            logging.warning(f'************** Iris model loaded.')

        except Exception as e:
            logging.warning(f'************** Load model failed!!!')
            model = None

    #
    # Prepare the data for use in a prediction.
    #

    #
    # Get the 4 parameters from the dictionary.
    #
    predict_request = [data['sl'],data['sw'],data['pl'], data['pw']] 
    
    #
    # Convert the json to an numpy array
    #
    predict_request = np.array(predict_request).reshape(1,-1)
    
    #
    # Call the model's predict function by passing in the numpy array.
    #
    y_hat = model.predict(predict_request)
    
    #
    # Return the prediction
    #
    output = {'y_hat': int(y_hat[0])}
    logging.warning(f'************** prediction: {output}')
    logging.warning(f'**************************************************************')
    logging.warning(f'')
    logging.warning(f'')
   
    return { "prediction": output['y_hat'] }, 200
