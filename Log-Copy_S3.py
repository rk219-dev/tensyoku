import json
import urllib.parse
import boto3
import datetime

datetime_now = datetime.datetime.now()
date_now = datetime_now.date()
date_1d = date_now - datetime.timedelta(days=1)
h_date = date_1d.strftime('%Y-%m-%d')   # '-'区切りの日付（実行日の前日）
s_date = date_1d.strftime('%Y/%m/%d/')  # "/"区切りの日付（実行日の前日）]
print('日付(-)：'+ h_date)
print('日付(/)：'+ s_date)

# AWSのアカウントID
aws_id = '▲▲▲▲'

# <CloudWatchにて収集しているログ>
FOLDER_cw = h_date + '/'
# </CloudWatchにて収集しているログ>

# <AWS WAFのログ>
FOLDER_WAF = s_date
# </AWS WAFのログ>

# <ALBのログ>
alb_list = ['alb-production/', 'alb-staging/']
###FOLDER_ALB = 'AWSLogs/' + aws_id + '/elasticloadbalancing/ap-northeast-1/' + s_date
# </ALBのログ>

# <VPCのログ>
vpc_num = 4 # VPCの数
FOLDER_VPC_LIST = []
cnt = 1
while cnt <= vpc_num:
    FOLDER_VPC = 'vpc-0' + str(cnt) + '/AWSLogs/' + aws_id + '/vpcflowlogs/ap-northeast-1/' + s_date
    FOLDER_VPC_LIST.append(FOLDER_VPC)
    cnt += 1
# </VPCのログ>

# <CloudTrailのログ>
region_list = ['ap-northeast-1/', 'ap-northeast-3/']
# </CloudTrailのログ>

s3 = boto3.client('s3')

# S3オブジェクトのコピー関数
def s3Copy(BUCKET_NAME,FOLDER_NAME):
    print('■開始')
    
    # 全てのオブジェクトを取得する
    next_token = ''
    print('■while突入')
    while True:
        if next_token == '':
            print('if')
            response = s3.list_objects_v2(Bucket=BUCKET_NAME,Prefix=FOLDER_NAME)
        else:
            print('else')
            response = s3.list_objects_v2(Bucket=BUCKET_NAME,Prefix=FOLDER_NAME, ContinuationToken=next_token)
        # バケット内が"空"の場合は何もせず、次のバケットを見に行く
        if not response['KeyCount']:
            print('■■バケット空')
            pass
        # バケット内にオブジェクトがあればコピーを実行する
        else:
            print('■■バケットあり')
            print('■■for突入')
            for content in response['Contents']:
                keyn = content['Key'] ## コピー元のキー名
                c_keyn = h_date + '-dr/' + keyn ## コピー先のプレフィックス名
                print('---')
                print('■■■コピー元のキー名：' + keyn)
                print('■■■コピー先のプレフィックス名：' + c_keyn)
                print(' _ ')
                # コピーの実行
                print('■■■■コピーの実行')
                res = s3.copy_object(
                    Bucket=BUCKET_NAME + '-dr',
                    Key=c_keyn,
                    CopySource={
                        'Bucket': BUCKET_NAME,
                        'Key': keyn
                    }
                )
                print('■■■■コピーの終了')
            print('■■for脱出')
            
        print('■オブジェクトがまだある場合、処理を続行')
        if 'NextContinuationToken' in response:
            print('■■続行')
            next_token = response['NextContinuationToken']
        # オブジェクトがもうない場合、処理を終了
        else:
            print('■■終了')
            break
    print('■終了')

def lambda_handler(event, context):
    print('<BWFのログ>')
    s3Copy('▲▲▲▲-ap-bwf',FOLDER_cw)
    
    print('<WindowsEventのログ>')
    s3Copy('▲▲▲▲-ap-windows-event',FOLDER_cw)
    
    print('<IISのログ>')
    s3Copy('▲▲▲▲-ap-windows-iis',FOLDER_cw)
    
    print('<DBのログ>')
    s3Copy('▲▲▲▲-db',FOLDER_cw)
    
    print('<FSのログ>')
    s3Copy('▲▲▲▲-fs-audit',FOLDER_cw)
    
    print('<VPNのログ>')
    s3Copy('▲▲▲▲-vpn-connection',FOLDER_cw)
    
    print('<WAFのログ>')
    s3Copy('▲▲▲▲-waf',FOLDER_WAF)
    
    print('<ALBのログ>')
    for al in alb_list:
        FOLDER_ALB = al + 'AWSLogs/' + aws_id + '/elasticloadbalancing/ap-northeast-1/' + s_date
        s3Copy('▲▲▲▲-alb-access',FOLDER_ALB)
    
    print('<VPCのログ>')
    for fvl in FOLDER_VPC_LIST:
        s3Copy('▲▲▲▲-vpc-reject',fvl)
    
    print('<CloudTrailのログ>')
    for rl in region_list:
        ct = 'AWSLogs/' + aws_id + '/CloudTrail/' + rl + s_date
        ctd = 'AWSLogs/' + aws_id + '/CloudTrail-Digest/' + rl + s_date
        s3Copy('▲▲▲▲-cloudtrail',ct)
        s3Copy('▲▲▲▲-cloudtrail',ctd)
