# basicpub
Basic publishing service using Chalice framework

## API Status
API can be used by sending GET to /status endpoint.

https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/status

A random status is chosen from a list of dictionaries and returned to the caller. 

Random status was chosen over returning useful and real status information in order to preserve time to dedicate to the remaining two more interesting problems.
```
(chalice-demo) morgan@chair:~/work/ad/basicpub$ http https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/status
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 45
Content-Type: application/json
Date: Sat, 24 Jun 2017 13:40:18 GMT
Via: 1.1 1a3d70af1a1100f9b3da94cb72651784.cloudfront.net (CloudFront)
X-Amz-Cf-Id: 2LqXiwOfZgM591_sHFjPbnqPHZjZlVNkKfjCy9tG0gjiAqnMCfuSPA==
X-Amzn-Trace-Id: sampled=0;root=1-594e6bc0-5398df6ea77a661050bf6087
X-Cache: Miss from cloudfront
x-amzn-RequestId: a854278c-58e2-11e7-bbb7-d94a01a4b900

{
    "status_code": 1, 
    "status_string": "Not OK"
}
```
## Transform publicly available data into something fun.
Play Street Dice

https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/dice/reset

https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/dice/roll

API supports two functions, reset and roll which can be executed by sending GET to /reset and /roll respectively. 

Game state is maintained in two S3 keys, count and setpoint. Count stores the number of rolls and setpoint stores the current setpoint. Reset will reset the currently running game by setting count to zero and setting set to empty string.

Roll works by calling the dice rolling API at http://roll.diceapi.com/json/2d6. This endpoint returns the results of rolling two six sided die. Roll sums the values and returns a JSON object containing the following fields
* count - number of rolls so far (not including last roll)
* roll - value of the current roll
* setpoint - value of the current setpoint
* result - win, lose, roll again, reset

Game loosly follows the rules of Street Dice (craps) which can be found here

https://wizardofodds.com/games/street-dice/

Game state is defined simply in two S3 keys for the sake of quickly producing a working game. With more time available for design I would have liked to address the following items.
* properly serialize game state (use Python 3 for byte type support)
* support multiuser by generating and returning gameID and storing game state for each gameID
* keep metrics (win/loss streaks, etc..)
* lazy initialize state (currently reset must be called before roll on fresh deploy)

```
(chalice-demo) morgan@chair:~/work/ad/basicpub$ http https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/dice/reset
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 63
Content-Type: application/json
Date: Sat, 24 Jun 2017 14:01:45 GMT
Via: 1.1 4470b111fbbc064d9b2edf2f1eff705e.cloudfront.net (CloudFront)
X-Amz-Cf-Id: tmjZuQB8WuG59RX1OXkuIHnOTm6nqcbg5UPRl2R2pYpbdGWb_vD2AA==
X-Amzn-Trace-Id: sampled=0;root=1-594e70c8-a643545e00d75fce20be18c4
X-Cache: Miss from cloudfront
x-amzn-RequestId: a7d0987a-58e5-11e7-b4bd-77938095466c

{
    "count": "0", 
    "result": "reset", 
    "roll": -1, 
    "setpoint": null
}

(chalice-demo) morgan@chair:~/work/ad/basicpub$ http https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/dice/roll
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 60
Content-Type: application/json
Date: Sat, 24 Jun 2017 14:02:01 GMT
Via: 1.1 76c6a47dca1edcb3bf573679a8c13b40.cloudfront.net (CloudFront)
X-Amz-Cf-Id: C8CzXq4VAd6WUursnBHrGYDKtVYHiWDFJL6zayYQyu8WCPM8E_edkQ==
X-Amzn-Trace-Id: sampled=0;root=1-594e70d8-afae06cf92104fcbf9251479
X-Cache: Miss from cloudfront
x-amzn-RequestId: b1540cfb-58e5-11e7-9e16-2b7924135912

{
    "count": "0", 
    "result": "win", 
    "roll": 7, 
    "setpoint": null
}
```
## Upload a PNG image to S3

https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/dice/reset

A png image can be uploaded and stored on S3 by sending POST to the /send endpoint and including the raw data in the request body.

The function which handles /send uses boto3 api to store the data in an S3 bucket and returns the resource url in a JSON object.

For the sake of simplicity the uploaded file is always stored under the same key. A better approach may have been to either generate key names or accecpt key names from the client

```
(chalice-demo) morgan@chair:~/work/ad/basicpub$ http POST https://v9dqfziqk4.execute-api.us-east-2.amazonaws.com/dev/send @/home/morgan/sources/CppCoreGuidelines/param-passing-advanced.png
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 63
Content-Type: application/json
Date: Sat, 24 Jun 2017 14:33:50 GMT
Via: 1.1 0ae737265831ce30da6ba6dcf15e3d61.cloudfront.net (CloudFront)
X-Amz-Cf-Id: PV_TiF1l-j55oO5OSHueWMhpo2Tkxf9rRIgwew_vh49SE1MbPkQ4yA==
X-Amzn-Trace-Id: sampled=0;root=1-594e784e-4348ee54be3b89bc53f9b2a3
X-Cache: Miss from cloudfront
x-amzn-RequestId: 23e178ad-58ea-11e7-80ff-217bc3da301a

{
    "url": "https://s3.us-east-2.amazonaws.com/basicpub/test.png"
}
```

## A note about credentials
In order to get the API to work correctly I had to generate an IAM policy which allows all actions on the S3 service. It's not ideal from a security perspective but it allows the API to function. The policy is stored in .chalice/policy.json. To use this policy chalice must be deployed as follows
```chalice deploy --no-autogen-policy```

