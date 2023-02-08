import pandas as pd
import settings
from api.parsers import Removing_Parser, Test_Parser, Train_Parser
from api.validators import get_model_fix_rules, get_model_predict_rules
from flask import Flask, request
from flask_restx import Api, Resource
from models import Model
from services import Dataset, ModelsStorage, read_models_list

model_dict = {}  # TODO: Move to storage

app = Flask(__name__)
api = Api(app)
dataset = Dataset(settings.DATASET_PATH)
storage = ModelsStorage()


class ParamsInputting:
    NAME_MODEL = 'name_model'
    TYPE_MODEL = 'type_model'
    PARAMS_MODEL = 'params_model'
    PATH = 'path'


model_fix = api.model("input_model", get_model_fix_rules())
model_predict = api.model("input_predict", get_model_predict_rules(dataset.df))


@api.route("/models/list")
class Model_List(Resource):
    @api.doc(responses={201: "Success"})
    def get(self):
        return {"models": read_models_list()}, 201


@api.route("/models/add")
class Model_Add(Resource):
    @api.expect(model_fix)
    @api.doc(
        responses={201: "Success",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   408: "Too much models"
                   })
    def post(self):
        model_name = api.payload[ParamsInputting.NAME_MODEL]
        model_type = api.payload[ParamsInputting.TYPE_MODEL]
        try:
            eval(api.payload[ParamsInputting.PARAMS_MODEL])
        except Exception:
            return {
                "status": "Fail",
                "message": "Params error. Not that type of error"
            }, 401

        if storage.models_count() >= settings.MAX_MODELS:
            return {
                "status": "Fail",
                "message": "Max_num: delete previous version"
            }, 408

        if storage.model_is_exists(model_name):
            return {
                "status": "Failed",
                "message": "Model with a given name already exists"
            }, 403

        try:
            model = Model(model_type)
            ModelsStorage().save_model(model, model_name=model_name)
            return {"status": "Ok", }, 201
        except Exception:
            return {"status": "oopsss..smth more happened", }, 402


@api.route("/models/remove")
class Model_Remove(Resource):
    @api.expect(Removing_Parser)
    @api.doc(
        responses={201: "Success",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   })
    def delete(self):
        model_name = Removing_Parser.parse_args()["name"]
        res = ModelsStorage().delete_model(model_name)
        if res is False:
            return {
                "status": "Failed",
                "message": "Model with a given name does not exist"
            }, 404

        return {
            "status": "Ok",
            "message": "Model delected"
        }, 201


@api.route("/models/train")
class Model_Train(Resource):
    @api.expect(Train_Parser)
    @api.doc(
        responses={201: "Success",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   408: "Too much models"
                   })
    def get(self):
        model_name = Train_Parser.parse_args()['name']
        data_path = Train_Parser.parse_args()['path']

        if not storage.model_is_exists(model_name):
            return {
                "status": "Failed",
                "message": "Model with a given name does not exist!"
            }, 404

        try:
            model = storage.load_model(model_name)
            model.fit(data_path)
            train_score = model.train_score
            return {
                "status": "Ok",
                "message": "Train score {}".format(train_score)
            }, 201
        except Exception:
            return {
                "status": "Failed",
                "message": getattr(Exception, "message", repr(Exception))
            }, 406


class Model_Test(Resource):
    @api.expect(Test_Parser)
    @api.doc(
        responses={201: "Success",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   408: "Too much models"
                   })
    def get(self):
        model_name = Train_Parser.parse_args()['name']
        data_path = Train_Parser.parse_args()['path']
        if not storage.model_is_exists(model_name):
            return {
                "status": "Failed",
                "message": "Model with a given name does not exist!"
            }, 404

        try:
            model = storage.load_model(model_name)
            model.test(data_path)
            test_score = model.test_score
            return {
                "status": "ok",
                "message": "Test score {}".format(test_score)
            }, 201
        except Exception:
            return {
                "status": "Failed",
                "message": getattr(Exception, "message", repr(Exception))
            }, 406


@api.route("/models/predict")
class Predict(Resource):
    @api.expect(model_predict)
    @api.doc(
        responses={200: "Success",
                   400: "Bad Request",
                   404: "Model not found",
                   500: "Internal Server Error"}
    )
    def post(self):
        model_name = api.payload["name"]
        params = api.payload
        params.pop("name")
        try:
            if storage.model_is_exists(model_name):
                model = storage.load_model(model_name)
                data = pd.DataFrame(params, index=[0])
                data = data.astype(float)
                y_pred = model.predict(data)
                return {"result": f"Predicted value: {y_pred[0]}"}, 200
            return {"message": "Model not found"}, 404
        except Exception as e:
            return {"message": str(e)}, 500


@app.route('/retrain', methods=['POST'])
class Retrain(Resource):
    def retrain_model(self):
        data = request.get_json()
        model_name = data['model_name']
        if not storage.model_is_exists(model_name):
            return {'message': 'Error: Model not found'}, 400

        model_dict[model_name].retrain()
        return {'message': 'Model retrained successfully'}, 200


class Server:
    def __init__(self):
        self.app = app
        self.api = api

    def serve(self,
              host=settings.APP_HOST,
              port=settings.APP_PORT,
              debug=settings.DEBUG):
        self.app.run(host=host, port=port, debug=debug)
