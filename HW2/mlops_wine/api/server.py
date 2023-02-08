import pickle
from io import BytesIO

import psycopg2
import settings
from api.parsers import Removing_Parser, Train_Parser
from api.validators import get_model_fix_rules, get_model_predict_rules
from flask import Flask, request
from flask_restx import Api, Resource
from models import Model
from services import Dataset, ModelsStorage, db, get_list_models

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
        return {"models": storage.get_models()}, 201


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
        params_api = api.payload["params"]

        try:
            list_m = get_list_models()
        except Exception as e:
            return {"status": "Failed", "error": str(e)}, 408

        try:
            p = eval(params_api)
        except Exception as e:
            return {"status": "Failed", "error": str(e)}, 401

        if model_name not in list_m:
            return {'status': 'Failed', "error": "Name already exists"}, 403

        try:
            model = Model(type_m=model_type, model_args=p)
            bio = BytesIO()
            pickle.dump(model, bio)

            db.engine.execution_options(autocommit=True).execute(
                """
                INSERT INTO public.models ("Name", "type", "Params", "weights")
                VALUES (%s, %s, %s, %s);
                """,
                (
                    model_name,
                    model_type,
                    params_api,
                    psycopg2.Binary(bio.getvalue())
                ))

            db.engine.dispose()
            return {'status': 'ok'}, 201
        except Exception as e:
            return {'status': 'Failed', "error": str(e)}, 406


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
        try:
            _model_list = get_list_models()
        except Exception:
            return {'status': 'Failed'}, 408

        if Removing_Parser.parse_args()["name"] in _model_list:
            db.engine.execution_options(autocommit=True).execute(
                f"""
                DELETE
                FROM public.models
                WHERE "modelName" = '{Removing_Parser.parse_args()["name"]}';
                """).fetchone()
            db.engine.dispose()
            return {"status": 'ok'}, 201
        else:
            return {
                "status": "Failed",
                "message": "Model with a given name does not exist"
            }, 404


@api.route("/model/train")
class Model_Train(Resource):
    @api.expect(Train_Parser)
    @api.doc(
        responses={201: "Success",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   406: "Error while training model; See description for more info",
                   408: "Failed to reach DB"
                   })
    def post(self):
        try:
            _model_list = get_list_models()
        except Exception:
            return {'status': 'Failed', 'message': Exception}, 408
        if Train_Parser.parse_args()["name"] in _model_list:
            try:
                _mRaw_list = db.engine.execution_options(autocommit=True).execute(
                    f"""
                    SELECT weights
                    FROM public.models
                    WHERE "Name" = '{Train_Parser.parse_args()["name"]}';
                    """
                ).fetchone()
                db.engine.dispose()
                _model = pickle.loads(_mRaw_list[0])
                _model.train()
                _w = BytesIO()
                pickle.dump(_model, _w)
                db.engine.execution_options(autocommit=True).execute(
                    f"""
                    UPDATE public.models
                    SET
                        "Trained" = True,
                        "train_acc" = {round(_model.score()["train_accuracy"], 20)},
                        "test_acc" = {round(_model.score()["validation_accuracy"], 20)},
                        "weights" = %s,
                        "Date" = now()
                    WHERE "Name" = '{Train_Parser.parse_args()["name"]}';
                    """,
                    (psycopg2.Binary(_w.read()))
                )
                db.engine.dispose()
                return {'status': "ok"}, 201
            except Exception:
                raise
                return {
                    'status': 'Failed'
                }, 406
        else:
            return {
                "status": "Failed",
            }, 404


@api.route("/models/test")
class Model_Test(Resource):
    @api.expect(Train_Parser)
    @api.doc(
        responses={201: "Success",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   406: "Error while training model; See description for more info",
                   408: "Failed to reach DB"
                   })
    def get(self):
        _name_file = Train_Parser.parse_args()["name"]
        _path_file = Train_Parser.parse_args()["path"]

        _mRaw_list = db.engine.execution_options(autocommit=True).execute(
            f"""
            SELECT weights
            FROM public.models
            WHERE "modelName" = '{_name_file}';
            """
        ).fetchone()
        db.engine.dispose()
        _model = pickle.loads(_mRaw_list[0])

        try:
            _model.test(_path_file)
            return {'status': 'OK'}, 201

        except Exception:
            return {'status': 'Failed', }, 406


@api.route("/models/predict")
class predict_model(Resource):
    @api.expect(model_fix)
    @api.doc(
        responses={201: "Success",
                   400: "Bad Request",
                   401: "Unauthorized",
                   403: "Forbidden",
                   404: "Not Found",
                   406: "Error while training model; See description for more info",
                   408: "Failed to reach DB"
                   })
    def post(self):
        _name = api.payload["name"]
        params = api.payload
        params = params.pop('name')

        try:
            _model_list = get_list_models()
        except Exception:
            return {"status": "Failed",
                    "message": "Error"}, 408

        if _name in _model_list:
            try:
                row_model = db.engine.execution_options(autocommit=True).execute(
                    f"""
                    SELECT weights FROM public.models
                    WHERE "Name" = '{_name}'
                    """
                ).fetchone()
                db.engine.dispose()
                _model_list = pickle.loads(row_model[0])
                return {"result": _model_list.predict(params)}, 201
            except Exception:
                return {"status": "Failed",
                        "message": "Error"}, 407
        else:
            return {"status": "Failed",
                    "message": "models does not exist"}, 404


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
