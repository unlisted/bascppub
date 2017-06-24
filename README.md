# basicpub
Basic publishing service using Chalice framework

## API Status
A random status is chosen from a list of dictionaries and returned to the caller. API can be used by sending GET to /status endpoint.

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
