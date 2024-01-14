import copy
import json
import logging
import subprocess
import os
import tarfile
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from odoo import models, fields, api
from odoo.http import request

_logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024*1024
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

class GdriveSetting(models.Model):
    """This model is to set up setting for google client

    Args:
        models (_type_): _description_
    """
    _name = "gdrive.settings"

    _description = "Google Drive Setting"

    name            = fields.Char()
    folder_name     = fields.Char()
    folder_code     = fields.Char()
    scopes          = fields.Char()
    datetime        = fields.Datetime()
    max_count       = fields.Integer()
    credential_json = fields.Text()
    token_json      = fields.Text()

    # db setting
    db_host = fields.Char()
    db_port = fields.Integer()
    db_user = fields.Char()
    db_password = fields.Char()
    db_name = fields.Char()

    backup_files = fields.One2many(comodel_name="gdrive.settings.file", inverse_name="gdrive_setting_id")

    def _get_authorization_url(self, redirect_uri: str) -> str:
        flow = InstalledAppFlow.from_client_config(json.loads(self.credential_json), scopes=self.scopes.split(","), redirect_uri=redirect_uri)
        return flow.authorization_url()

    def _get_drive(self):
        self.ensure_one()
        creds = self._get_token()
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.token_json = creds.to_json()
        return build("drive", "v3", credentials=creds)

    def _get_token(self)->Credentials:
        self.ensure_one()
        return Credentials.from_authorized_user_info(json.loads(self.token_json), self.scopes.split(","))

    def upload(self, filename: str, store_fname: str, parent_folder_code: str = ""):
        """To upload file

        Args:
            filename (str): Filename on google drive
            store_fname (str): Actual file path
            parent_folder_code (str): Parent directory's id

        Returns:
            _type_: _description_
        """
        drive = self._get_drive()
        body_data = {
            "name": filename
        }
        if parent_folder_code:
            body_data["parents"] =[parent_folder_code]
        file = MediaFileUpload(filename=store_fname, chunksize=CHUNK_SIZE)
        file = drive.files().create(body=body_data, media_body=file, fields="id, size").execute()
        return file.get('id'), file.get('size')

    def action_login_with_gmail(self):
        """Action button from UI

        Returns:
            _type_: _description_
        """
        res = copy.copy(self._context.get('params') or {
            "model": self._name,
            "view_type": "form"
        })
        res['id'] = self.id
        current_uri = request.httprequest.referrer + "#" + "&".join(f"{k}={v}" for k,v in res.items())
        res["current_uri"] = current_uri
        redirect_uri = f"{self.env['ir.config_parameter'].get_param('web.base.url')}/gdrive/login"
        auth_url, state = self._get_authorization_url(redirect_uri=redirect_uri)
        self.env['ir.config_parameter'].set_param(state, json.dumps(res))
        return {
            'type':'ir.actions.act_url',
            'url': auth_url,
            'target': 'self',
        }

    def action_create_folder(self):
        """Action button from UI
        """
        drive = self._get_drive()
        results = drive.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])
        folder_code = ""
        for item in items:
            if self.folder_name == item.get('name'):
                folder_code = item.get('id')
        body_data = {
            "name": self.folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if folder_code == "":
            file = (
                drive.files()
                .create(body=body_data, fields="id")
                .execute()
            )
            folder_code = file.get('id')
        self.folder_code = folder_code

    @classmethod
    def convert_to_tarfile(cls, src_file: str, filepath: str):
        with tarfile.open(filepath, 'w:gz') as tar:
            tar.add(src_file)

    def _generate_filename(self, now_time: datetime)->str:
        self.ensure_one()
        return f"{self.name}-{self.db_name}-{now_time}.sql"

    @api.model
    def schedule_backup(self):
        now_time = datetime.now()
        for record in self.search([]):
            if record.datetime < now_time:
                filename = record._generate_filename(now_time)
                filepath = f"/tmp/{filename}"

                tar_filename = f"{filename}.tar.gz"
                tar_filepath = f"{filepath}.tar.gz"
                try:
                    _logger.info("#gdrive_bk starting backup the database %s", record.name)
                    res = subprocess.call(f'''PGPASSWORD="{record.db_password}" pg_dump -d {record.db_name} -h {record.db_host} -p {record.db_port} -U {record.db_user} -f "{filepath}"''', shell=True)
                    _logger.info("#gdrive_bk done backup the database %s", record.name)
                    if res == 0:
                        _logger.info("#gdrive_bk start creating tar file")
                        self.convert_to_tarfile(filepath, tar_filepath)
                        _logger.info("#gdrive_bk done creating the tar file")
                        record.datetime = record.datetime + timedelta(days=1)
                        _logger.info("#gdrive_bk start uploading to google drive")
                        file_id, size = record.upload(filename=tar_filename, store_fname=tar_filepath, parent_folder_code=record.folder_code)
                        _logger.info("#gdrive_bk done uploading to google drive")
                        self.env["gdrive.settings.file"].create({
                            "gdrive_setting_id": record.id,
                            "date": fields.Date.context_today(self),
                            "parent_folder_code": record.folder_code,
                            "file_name": tar_filename,
                            "file_code": file_id,
                            "size": size
                        })
                        os.remove(filepath)
                        os.remove(tar_filepath)
                        _logger.info("#gdrive_bk successfully backup the database %s", record.name)
                    else:
                        _logger.error("#gdrive_bk failed to backup the database with status code : %s", res)
                except Exception as err:
                    raise err


class GdriveSettingFile(models.Model):
    """This model is to save file

    Args:
        models (_type_): _description_
    """
    _name = "gdrive.settings.file"
    _description = "Google Drive File"
    _order = "date DESC"

    gdrive_setting_id = fields.Many2one(comodel_name="gdrive.settings")
    date = fields.Date(index=True)
    parent_folder_code = fields.Char()
    backup_count = fields.Integer(related="gdrive_setting_id.max_count")
    file_name = fields.Char()
    file_code = fields.Char()
    size = fields.Integer()

    def unlink(self):
        for record in self:
            drive = record.gdrive_setting_id._get_drive()
            try:
                drive.files().delete(fileId=record.file_code).execute()
            except HttpError as err:
                if err.status_code != 404:
                    raise err
        return super().unlink()

    @api.model
    def schedule_delete(self):
        count = 0
        _logger.info("#gdrive_bk schedule delete started")
        today = fields.Date.context_today(self)
        for record in self.search([]):
            if record.date < today - timedelta(days=record.backup_count):
                record.unlink()
                count+=1
        _logger.info("#gdrive_bk done schedule delete : %s count", count)

