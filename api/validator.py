from flask import (
    jsonify,
)

REQUIRED_FIELD_MISSING = '{0} is a required field'

def requiredFieldsMissing(requiredFields, request):
    for field in requiredFields:

        if field not in request.form or not request.form[field]:
            return jsonify(status=401, message=REQUIRED_FIELD_MISSING.format({field}))

    return None
