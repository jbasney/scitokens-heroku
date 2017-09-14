from flask import Flask, jsonify
import json
from datetime import datetime
app = Flask(__name__)
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import base64
import binascii


def bytes_from_long(data):
    """
    Create a base64 encoded string for an integer
    """
    return base64.urlsafe_b64encode(cryptography.utils.int_to_bytes(data)).decode('ascii')

@app.route('/')
def homepage():

    return """
    <h1>Hello from SciTokens!</h1>
    """.format()

# Oauth well known    
@app.route('/.well-known/openid-configuration')
def OpenIDConfiguration():
    # We need more to be compliant with the RFC
    configuration = {
        "issuer": "https://demo.scitokens.org",
        "jwks_uri": "https://demo.scitokens.org/oauth2/certs"
    }
    return jsonify(configuration)
    

# jwks_uri 
@app.route('/oauth2/certs')
def Certs():
    """
    Provide the "keys"
    """
    
    # Read in the private key environment variable
    private_key = serialization.load_pem_private_key(
        base64.b64decode(os.environ['PRIVATE_KEY']),
        password=None,
        backend=default_backend()
    )
    
    # Get the public numbers
    public_key = private_key.public_key()
    numbers = public_key.public_numbers()
    
    # Hash the public "n", and use it for the Key ID (kid)
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(bytes_from_long(numbers.n))
    kid = binascii.hexlify(digest.finalize())
    
    keys = {'keys': [
        {
            "alg": "RS256",
            "n": bytes_from_long(numbers.n),
            "e": bytes_from_long(numbers.e),
            "kty": "RSA",
            "use": "sig",
            "kid": kid
        }
    ]}
    return jsonify(keys)



if __name__ == '__main__':
    # Given the private key in the ENV PRIVATE_KEY, calculate the public key
    
    app.run(debug=True, use_reloader=True)
