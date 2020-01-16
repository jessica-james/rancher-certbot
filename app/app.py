import ast
import os
import re
import requests
import subprocess


class CertAutomation:

    def __init__(self, rancher_url, rancher_auth, verify_ssl, environment, domain, certbot_path="/usr/local/bin/certbot", cert_folder="/etc/letsencrypt/live", email="jamchapp@cisco.com"):
        projects = {}
        self.auth = rancher_auth
        self.verify = verify_ssl
        static_session = requests.Session()
        static_response = static_session.get(f'{rancher_url}/projects/', auth=self.auth, verify=self.verify)
        for project in static_response.json()["data"]:
            projects[project["name"]] = project["id"]
        self.email = email
        self.rancher_url = rancher_url
        self.certbot_path = certbot_path
        self.cert_folder = cert_folder
        self.domain = domain
        self.certbot_command = f'certonly -n --agree-tos --email {self.email} --dns-route53 -d {self.domain}'
        self.environment = environment
        self.envId = projects[environment]
        self.api_path = f"{rancher_url}projects/{self.envId}/certificates"
        self.working_directory = f"{self.cert_folder}/{self.domain}"
        self.cert_path = f"{self.working_directory}/cert.pem"
        self.chain_path = f"{self.working_directory}/chain.pem"
        self.key_path = f"{self.working_directory}/privkey.pem"
        self.body = {}

    def createNewCert(self):
        subprocess.call(f'{self.certbot_path} {self.certbot_command}', shell=True)

    def uploadCert(self):
        self.session = requests.Session()
        with open(self.cert_path, "r") as cert, open(self.chain_path, "r") as chain, open(self.key_path, "r") as key:
            self.body = {
                "type"       : "certificate",
                "name"       : {self.domain},
                "cert"       : f"{cert.read()}",
                "certChain"  : f"{chain.read()}",
                "key"        : f"{key.read()}",
                "created"    : 'null',
                "description": 'null',
                "removed"    : 'null',
                "uuid"       : 'null'
            }
            response = self.session.post(self.api_path, auth=self.auth, verify=self.verify, data=self.body)
            return response.status_code


if __name__ == '__main__':
    rancher_access_key = os.environ["RANCHER_ACCESS_KEY"]
    rancher_secret_key = os.environ["RANCHER_SECRET_KEY"]
    rancher_url = os.environ["RANCHER_URL"]
    verify_ssl = True
    rancher_auth = (rancher_access_key, rancher_secret_key)
    for domain in ast.literal_eval(os.environ["DOMAINS"]):
        regex = re.compile('((?<=[.])[a-zA-Z-]+)')
        match = regex.search(domain)
        environment = match.group(1)
        certificate = CertAutomation(rancher_url, rancher_auth, verify_ssl, environment, domain)
        certificate.createNewCert()
        certificate.uploadCert()




