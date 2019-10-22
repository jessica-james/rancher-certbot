import requests
import os
import subprocess
import ast


def get_rancher_projects (environment_names):
    session = requests.Session()

    response = session.get(f'{rancher_url}/projects/', auth=rancher_auth, verify=verify_ssl)
    environments = environment_names

    projects = {}
    for project in response.json()["data"]:
        projects[project["name"]] = project["id"]

    envDict = {env: projects[env] for env in environments if env in projects.keys()}
    return envDict


def create_new_certs (domains, projects):
    domain_dict = dict(zip([domain for domain in domain_names], projects))
    for domain in domains:
        certbot_path = "/usr/local/bin/certbot"
        certbot_command = f'certonly -n --agree-tos --email crate-support@cisco.com --dns-route53 -d {domain}.{domain_dict[domain]}.{tld}'
        subprocess.call(f'{certbot_path} {certbot_command}', shell=True)



def upload_certs (projects):
    session = requests.Session()
    cert_folder = "/etc/letsencrypt/live/"

    domain_dict = dict(zip([domain for domain in domain_names], projects))

    for item, value in domain_dict.items():
        api_path = f"{rancher_url}projects/{projects[value]}/certificates"
        cert_path = open(f"{cert_folder}{item}.{value}.{tld}/cert.pem", "r")
        chain_path = open(f"{cert_folder}{item}.{value}.{tld}/chain.pem", "r")
        key_path = open(f"{cert_folder}{item}.{value}.{tld}/privkey.pem", "r")
        body = {
            "type"       : "certificate",
            "name"       : f"{item}.{value}.{tld}",
            "cert"       : f"{cert_path.read()}",
            "certChain"  : f"{chain_path.read()}",
            "key"        : f"{key_path.read()}",
            "created"    : 'null',
            "description": 'null',
            "removed"    : 'null',
            "uuid"       : 'null'
        }
        response = session.post(api_path, auth=rancher_auth, verify=verify_ssl, data=body)
        print(response.status_code)


if __name__ == '__main__':
    # Set Variables from Environment
    rancher_access_key = os.environ["RANCHER_ACCESS_KEY"]
    rancher_secret_key = os.environ["RANCHER_SECRET_KEY"]
    rancher_url = os.environ["RANCHER_URL"]
    env_names = ast.literal_eval(os.environ["ENVIRONMENT_NAMES"])
    tld = os.environ["TLD"]
    domain_names = ast.literal_eval(os.environ["DOMAINS"])
    # Create rancher session
    verify_ssl = True
    rancher_auth = (rancher_access_key, rancher_secret_key)
    projects = get_rancher_projects(env_names)
    # Create Certificates
    create_new_certs(domain_names, projects)
    #Upload Certs
    upload_certs(projects)

