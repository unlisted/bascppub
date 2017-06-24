from chalice import Chalice
from random import choice
from requests import get
import boto3
import botocore

app = Chalice(app_name='basicpub')
app.debug = True

STATUSES = [{"status_code": 0, "status_string": "OK"},
            {"status_code": 1, "status_string": "Not OK"},
            {"status_code": 2, "status_string": "Error"},
            {"status_code": 3, "status_string": "Unknown"}]

DEFAULT_BUCKET = 'basicpub'
S3 = boto3.resource('s3')


@app.route('/status', methods=['GET'])
def status():
    """Return random status"""
    return choice(STATUSES)


def remote_roll():
    """Use remote api to roll two dice and return sum"""
    url = "http://roll.diceapi.com/json/2d6"
    data = get(url=url).json()
    return data['dice'][0]['value'] + data['dice'][1]['value']


def get_setpoint():
    """return the current setpoint or None if not set"""
    bucket = DEFAULT_BUCKET
    setpoint_obj = S3.Object(bucket_name=bucket, key='setpoint')
    response = setpoint_obj.get()
    data = response['Body'].read()

    return int(data) if data != "" else None


def put_setpoint(value):
    """put setpoint value into s3 bucket"""
    bucket = DEFAULT_BUCKET
    S3.Object(bucket, 'setpoint').put(Body=value)


class CountActions:
    Reset, Increment, Get = range(3)


# TODO: Quick and dirty, but it works
def count(action):
    """Reset, Increment or Get S3 count object"""
    bucket = DEFAULT_BUCKET

    # create bucket if it doesn't exist
    try:
        S3.Object(bucket, 'count').load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            S3.Object(bucket_name=bucket, key='count').put(Body=str(0))
        else:
            raise

    count_obj = S3.Object(bucket_name=bucket, key='count')
    response = count_obj.get()
    data = response['Body'].read()

    if action == CountActions.Reset:
        value = str(0)
        S3.Object(bucket, 'count').put(Body=value)
    elif action == CountActions.Increment:
        value = str(int(data) + 1)
        S3.Object(bucket, 'count').put(Body=value)

    return data


def reset():
    """resets count and setpoint"""
    put_setpoint("")
    count(CountActions.Reset)


def play(point, setpoint):
    """return win, lose, push or next"""
    if setpoint is None:
        if point == 7 or point == 11:
            reset()
            return "win"
        elif point == 2 or point == 3 or point == 12:
            reset()
            return "lose"
        else:
            put_setpoint(str(point))
            count(CountActions.Increment)
            return "roll again"
    else:
        if point == 7:
            reset()
            return "lose"
        elif point == setpoint:
            reset()
            return "win"
        else:
            count(CountActions.Increment)

    return "roll again"


@app.route('/dice/roll', methods=['GET'])
def roll():
    """endpoint goes through roll iteration and returns response"""

    point = remote_roll()
    setpoint = get_setpoint()

    current_count = count(CountActions.Get)
    ret = play(point, setpoint)

    return {"count": current_count,
            "roll": point,
            "setpoint": setpoint,
            "result": ret}


@app.route('/dice/reset', methods=['GET'])
def handle_reset():
    """resets game state, sends response"""
    reset()
    current_count = count(CountActions.Get)
    setpoint = get_setpoint()
    return {"count": current_count,
            "roll": -1,
            "setpoint": setpoint,
            "result": "reset"}


@app.route('/send', methods=['POST'], content_types=['image/png'])
def handle_send():
    """Accepts png, stores in S3, returns resource URL"""
    request = app.current_request
    bucket = DEFAULT_BUCKET
    key = "test.png"
    ret = S3.Object(bucket, key).put(Body=request.raw_body, ACL='public-read')

    client = s3 = boto3.client('s3')
    url = '{}/{}/{}'.format(client.meta.endpoint_url, bucket, key)
    return {"url": url}
