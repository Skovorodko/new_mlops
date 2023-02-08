from flask_restx import fields


def get_model_fix_rules() -> dict:
    return {
        "name_model": fields.String(
            required=True,
            title="Name of the model",
            desctpion="Name of the model must be unique",
        ),
        "type_model": fields.String(
            required=True,
            title="Type of the model",
            description="Type of the model must be Ridge or LinearRegression",
        ),
        "params_model": fields.String(
            required=True,
            title="Params of the model",
            description="Params of the model must be a dictionary",
            default="{}"
        )
    }


def get_model_predict_rules(df) -> dict:
    rules = {
        'name_model': fields.String(
            title="Name of the model",
            required=True,
            default="name_model",
        ),
    }
    for i in range(10):
        rules[df.columns[i]] = fields.Float(
            title=df.columns[i],
            required=True,
            default=0
        )

    return rules
