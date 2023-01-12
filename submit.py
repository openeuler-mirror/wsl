# coding=utf-8
import os
import json
import time
import requests
from azure.storage.blob import BlobClient
from string import Template
import argparse
import sys
import datetime
from typing import Optional
import humanize
import datetime
import logging

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fmter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
ch.setFormatter(fmt=fmter)
logger.addHandler(ch)

class SubmitPackage(object):
    def __init__(self, tenantId: str, clientId: str, clientSecret: str) -> None:
        self.baseurl = tokenResource = "https://manage.devcenter.microsoft.com"
        tokenRequestBody = "grant_type=client_credentials&client_id={}&client_secret={}&resource={}".format(clientId, clientSecret, tokenResource)
        tokenHeaders = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        tokenResponse = requests.post("https://login.microsoftonline.com/{}/oauth2/token".format(tenantId), data=tokenRequestBody, headers=tokenHeaders)
        
        logger.info('get access token status: {} {}'.format(tokenResponse.status_code, tokenResponse.reason))
        tokenJson = tokenResponse.json()
        self._acess_token = tokenJson["access_token"]
        self._init = True

    def make_submit_body(self, metapath: str, templatepath: str):
        with open(metapath, encoding='utf-8') as meta:
            metadata = json.loads(meta.read())
            metadata['year'] = datetime.date.today().year
        with open(templatepath, encoding='utf-8') as template:
            content = ''.join(template.readlines())
            t = Template(content)
            config = t.substitute(metadata)
        return json.loads(config)

    def get_app_info(self, release: str):
        if not self._init:
            sys.exit(1)
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}

        appResponse = requests.get("{}/v1.0/my/applications".format(self.baseurl), headers=headers)

        logger.info('get app info status: {} {}'.format(appResponse.status_code, appResponse.reason))
        logger.info(appResponse.headers["MS-CorrelationId"])  # Log correlation ID
        data = appResponse.json()
        for app in data['value']:
            if app['primaryName'] == 'openEuler {}'.format(release):
                return app
        raise ValueError("no {} found".format(release))

    def delete_exist_submission(self, submissionToRemove: str):
        if not self._init:
            sys.exit(1)
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}

        deleteSubmissionResponse = requests.delete("{}/v1.0/my/{}".format(self.baseurl, submissionToRemove), headers=headers)

        logger.info('delete pending submit status: {} {}'.format(deleteSubmissionResponse.status_code, deleteSubmissionResponse.reason))
        logger.info(deleteSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID

    def create_submit(self, applicationId: str, appSubmissionRequestJson, zipFilePath: str):
        headers = {"Authorization": "Bearer " + self._acess_token,
                "Content-type": "application/json",
                "User-Agent": "Python"}

        # Create submission
        createSubmissionResponse = requests.post("{}/v1.0/my/applications/{}/submissions".format(self.baseurl, applicationId), headers=headers)

        logger.info('create submission status: {} {}'.format(createSubmissionResponse.status_code, createSubmissionResponse.reason))
        logger.info(createSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID

        submissionJsonObject = createSubmissionResponse.json()
        if createSubmissionResponse.status_code >= 400:
            logger.error(submissionJsonObject)
            sys.exit(1) 
        submissionId = submissionJsonObject["id"]
        fileUploadUrl = submissionJsonObject["fileUploadUrl"]

        if len(submissionJsonObject['applicationPackages']) > 0:
            for package in submissionJsonObject['applicationPackages']:
                logger.info('package {} {} {} will be replaced'.format(package['fileName'], package['fileStatus'], package['version']))
                package['fileStatus'] = 'PendingDelete'

        appSubmissionRequestJson['applicationPackages'].extend(submissionJsonObject['applicationPackages'])

        # Update submission
        updateSubmissionResponse = requests.put("{}/v1.0/my/applications/{}/submissions/{}".format(self.baseurl, applicationId, submissionId), json.dumps(appSubmissionRequestJson).encode('utf-8'), headers=headers)
        logger.info('update submission status: {} {}'.format(updateSubmissionResponse.status_code, updateSubmissionResponse.reason))
        logger.info(updateSubmissionResponse.headers["MS-CorrelationId"])  # Log correlation ID

        updateSubmissionObject = updateSubmissionResponse.json()
        if updateSubmissionResponse.status_code >= 400:
            logger.error(updateSubmissionObject)
            sys.exit(1)

        size = os.stat(zipFilePath).st_size
        logger.info("begin to upload zip file({}): {} to {}".format(humanize.naturalsize(size), zipFilePath, fileUploadUrl))
        # Upload images and packages in a zip file.
        blob_client = BlobClient.from_blob_url(fileUploadUrl)
        with open(zipFilePath, "rb") as data:
            blob_client.upload_blob(data, blob_type="BlockBlob", progress_hook=progress, length=size)

        logger.info("upload end")
        # Commit submission
        commitResponse = requests.post("{}/v1.0/my/applications/{}/submissions/{}/commit".format(self.baseurl, applicationId, submissionId), headers=headers)

        logger.info('commit submission status: {} {}'.format(commitResponse.status_code, commitResponse.reason))
        logger.info(commitResponse.headers["MS-CorrelationId"])  # Log correlation ID
        commitResponseObject = commitResponse.json()
        if commitResponse.status_code >= 400:
            logger.error(commitResponseObject)
            sys.exit(1)

        # Pull submission status until commit process is completed
        getSubmissionStatusResponse = requests.get("{}/v1.0/my/applications/{}/submissions/{}/status".format(self.baseurl, applicationId, submissionId), headers=headers)
        submissionJsonObject = getSubmissionStatusResponse.json()
        while submissionJsonObject["status"] == "CommitStarted":
            time.sleep(60)
            getSubmissionStatusResponse = requests.get("{}/v1.0/my/applications/{}/submissions/{}/status".format(self.baseurl, applicationId, submissionId), headers=headers)
            submissionJsonObject = getSubmissionStatusResponse.json()
            logger.info('get commit status: {}'.format(submissionJsonObject["status"]))

        exitCode = 0
        logger.info('get commit status finished, final status: {}'.format(submissionJsonObject["status"]))
        if submissionJsonObject['statusDetails']["errors"]:
            logger.error(submissionJsonObject)
            exitCode = 1

        return exitCode

def progress(current: int, total: Optional[int]):
    t = total if total else '0'
    logger.info('{}/{}'.format(humanize.naturalsize(current), humanize.naturalsize(t)))

def init_parser():
    parser = argparse.ArgumentParser(
        prog = 'submit.py',
        description= 'automate create a UWP app submission',
    )

    parser.add_argument('-c', '--client_id', help="azure AD applicaion client id")
    parser.add_argument('-t', '--tenant_id', help="azure AD user id")
    parser.add_argument('-k', '--client_secret', help="azure AD application key secret")
    parser.add_argument('-r', '--release', help="release number")
    parser.add_argument('-m', '--meta', help="meta data file for submission request template, default to ./meta/{RELEASE}/meta.json")
    parser.add_argument('--template', default="template.json", help="submission request template, default to ./template.json")
    parser.add_argument('-f', '--zipfile', help="zip file path which contains intro images name as `release` and a appxupload bundle")
    return parser

if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()

    if not args.client_id or not args.tenant_id or not args.client_secret or not args.release or not args.zipfile:
        parser.print_help()
        sys.exit(1)

    if not args.meta:
        args.meta = 'meta/{}/meta.json'.format(args.release)
    
    sp = SubmitPackage(args.tenant_id, args.client_id, args.client_secret)
    
    data = sp.get_app_info(args.release)

    if data and "pendingApplicationSubmission" in data :
        submissionToRemove = data["pendingApplicationSubmission"]["resourceLocation"]
        sp.delete_exist_submission(submissionToRemove)

    requestBody = sp.make_submit_body(args.meta, args.template)
    sys.exit(sp.create_submit(data['id'], requestBody, args.zipfile))
    