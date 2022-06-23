import datetime
import time
import boto3
import os



def get_from_timestamp():
   # UTC:実行日(JST)の前日
   today = datetime.date.today()
   # UTC:開始日(JST)の前日15時
   yesterday = datetime.datetime.combine(today - datetime.timedelta(days = 1), datetime.time(15, 0, 0))
   # UNIX時刻に変換
   timestamp = time.mktime(yesterday.timetuple())
   return int(timestamp)

def get_to_timestamp(from_ts):
   # 開始日時から23時間59分59秒後
   return from_ts + (60 * 60 * 24) - 1

def s3Export(LogGroup,  Destination, DestinationPreix):

   from_ts = get_from_timestamp()
   to_ts = get_to_timestamp(from_ts)
      
   # CloudWatchLogsをS3へエクスポート
   dstr = str(datetime.date.today())
   client = boto3.client('logs')
   responce = client.create_export_task(
       logGroupName        = LogGroup,
       fromTime            = from_ts * 1000,
       to                  = to_ts * 1000,
       destination         = Destination,
       destinationPrefix   = DestinationPreix
   )
   return responce


def lambda_handler(event, context):
   ap = 'ap01'
   d = str(datetime.date.today())
   log_list = ['-bwf', '-windows-event', '-windows-iis']
   
   print('AP01のログをエクスポート：')
   for log in log_list:
      print(ap+':start')
      s3Export('ada-'+ap+log, 'ada-log-ap'+log, d + '/'+ap)
      print(ap+':end')
      print('=')

