### For Covid 19 LabCorp Results Processing HL7 - SFTP
import re
import time
import pandas as pd
import pysftp
from sqlalchemy import *
from sqlalchemy.sql import func
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert as pg_insert
import hl7
import io
import json
import numpy as np
from . import  db
from .models import LabCorpFile, LabCorpFileDetail, LabCorpOrderDetails
import uuid

sftp_host = 'sftp.clutch.health'
sftp_port = '22'
sftp_user = 'labcorp'
sftp_password = 'dd15fa1d7377a67f23a6715878480f95'
sftp_dir = '/sftp/incoming'

def time_now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def to_date(dt):
    try:
        date = datetime.strptime(dt, '%Y%m%d')
        return date
    except:
        return None

def get_pname(seg):
    try:
        name = str(seg[5])
        name = name.replace("^", " ")
    except:
        name = None
    return name

def get_paddress(seg):
    try:
        address = str(seg[11]).replace("^", ",")
        address = address.split(',')
        address = str(address[:4]).replace("[", "").replace("]", "")
    except:
        address  = None
    return address

def hl72JSON(h, source):
    json_=[]
    msh_10 = h.segment('MSH')[10];
    msgdt = str(h.segment('MSH')[7]);
    msgdt = to_date(msgdt[:8])
    _segments = [];
    segIndex = 1;
    segDic = {};
    segARR = []
    try:
        pname = get_pname(h.segment('PID'))
    except:
        pname = None
    try:
        paddress = get_paddress(h.segment('PID'))
    except:
        paddress = None
    for seg in h:
        segName = str(seg[0])
        segVal = str(seg)
        fieldIndex = 1
        fieldCount = 1
        _fields = []
        seg.pop(0)
        if(segName == 'MSH'):
            fieldDoc = {'_id':'MSH_1','Val': seg.separator}
            _fields.append(fieldDoc)
            fieldCount += 1
            fieldIndex += 1
        for field in seg:
            fieldName = segName+'_'+str(fieldIndex)
            fieldVal = str(field)
            hasRepetitions = False;
            if fieldVal:
                fieldDoc = {'_id': fieldName,'Val': fieldVal}
                if ('~' in fieldVal and fieldName != 'MSH_2'):
                    hasRepetitions = True;
                    _repfields = []
                    repFields = fieldVal.split('~');
                    repIndex = 1;
                    for repField in repFields:
                        if repField:
                            repFieldVal = str(repField);
                            fieldName = segName+'_'+str(fieldIndex)
                            fieldDoc = {'_id': fieldName,'Val': repFieldVal, 'Rep': repIndex}
                            _repfields.append(fieldDoc)

                            if('^' in repFieldVal):
                                repFieldComps = repFieldVal.split('^');
                                comIndex = 1;
                                for repFieldComp in repFieldComps:
                                    repFieldCompVal = str(repFieldComp);
                                    comName = segName+'_'+str(fieldIndex)+'_'+str(comIndex)
                                    if repFieldCompVal:
                                        fieldDoc = {'_id': comName,'Val': repFieldCompVal, 'Rep': repIndex}
                                        _repfields.append(fieldDoc)
                                    comIndex += 1
                        repIndex += 1;
                    fieldDoc = {'_id': fieldName,'Val': fieldVal, 'Repetitions': _repfields}
                _fields.append(fieldDoc)
                fieldCount += 1
                if (hasRepetitions == False and len(field) > 1 and fieldName != 'MSH_2'):
                    comIndex = 1
                    for component in field:
                        comName = segName+'_'+str(fieldIndex)+'_'+str(comIndex)
                        comVal = str(component)
                        if comVal:
                            fieldDoc = {'_id': comName,'Val': comVal}
                            _fields.append(fieldDoc)
                        comIndex += 1
            fieldIndex += 1
        if segName in segDic:
            segDic[segName] = segDic[segName] + 1;
        else:
            segDic[segName] = 1;
        segDoc ={'_id': segName, 'Rep': segDic[segName], 'Seq': segIndex, 'Val': segVal, 'FC': fieldIndex-1, 'VF': fieldCount-1, 'Fields': _fields}
        _segments.append(segDoc)
        segIndex += 1
    json_segments = [json.dumps(x) for x in _segments]
    guid = str(uuid.uuid4())
    hl7doc = ('{ "id": "%s", "guid": "%s", "date": "%s", "name": "%s", "address": "%s", "segments": %s, "source":["%s"] }') % (msh_10, guid, msgdt, pname, paddress, json_segments, source)
    hl7doc = cleanup_json(hl7doc)
    hl7js = json.dumps(hl7doc, indent=4, sort_keys=True)
    return hl7js

def cleanup_json(thisjson):
    clean_json = re.sub(r':\s*{', ': {', thisjson)
    clean_json = re.sub(r'}\n,', '},', clean_json)
    clean_json = re.sub(r',(\s*)}', r'\1}', clean_json)
    clean_json = thisjson.replace("'", "\\").replace("\\","")
    return clean_json

def readHL7(infile):
    json_list = []
    Messages = infile.splitlines()
    hl7_string=''
    for message in Messages[1:]:
        hl7_string += message + '\r'
    for message in [hl7_string]:
        h = hl7.parse(message)
        doc = hl72JSON(h, Messages[0])
        newjson = json.loads(doc)
    return newjson

def list_get(l, i):
    try:
        return l[i]
    except IndexError:
        return None

def replace_values_in_string(text, args_dict):
    if text != None:
        replaced = args_dict[text]
        return replaced
    else:
        return 'No Value Supplied'

def hl7_json_to_dataframe(newJson):
    columns = {
            "FC":"dfsegmentsfc",
            "Rep":"dfsegmentsrep",
            "Seq":"dfsegmentsseq",
            "VF":"dfsegmentsvf",
            "Val":"dfsegmentsval",
            "_id":"dfsegmentsid",
            "source":"file_name",
            "name":"dfsname"
            }
    try:
        result_json = json.loads(newJson)
        result = pd.DataFrame.from_dict(result_json['segments'])
        result['dfsaddress'] = result_json['address']
        result['dfsdate'] = result_json['date']
        result['dfsid'] = result_json['id']
        result['guid'] = result_json['guid']
        result['dfsname'] = result_json['name']
        result['source'] = result_json['source'][0]
        result = result.rename(columns=columns)
        temp_result = result.explode('Fields')
        temp_result = temp_result['Fields'].apply(pd.Series).rename(columns = {'_id':'dfsegmentsfieldsid','Val':'dfsegmentsfieldsval','Repetitions':'dfsegmentsrep'})
        result = result.merge(temp_result.drop(columns=['dfsegmentsrep']), how="inner", left_index=True, right_index=True).drop(columns=['Fields'])
        result['created_by_fk'] = 1
        result['changed_by_fk'] = 1
        result = result.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        result = result[['dfsid','guid','file_name','dfsdate','dfsname','dfsaddress','dfsegmentsfc','dfsegmentsrep','dfsegmentsseq','dfsegmentsvf','dfsegmentsval','dfsegmentsfieldsid','dfsegmentsfieldsval','created_by_fk','changed_by_fk']]
        result_labcorp_file_detail = result.to_dict(orient='records')
        db.session.bulk_insert_mappings(LabCorpFileDetail, result_labcorp_file_detail)
        db.session.commit()
        print('Inserted result into LabCorpFileDetail')
    except Exception as e:
        print('Fatal error inserting into labcorp message header detail table', e)
        db.session.rollback()
        return str(e)
    try:
        result['dfsegmentsfieldsid'] = result['dfsegmentsfieldsid'].astype(str) + '_' + result['dfsegmentsrep'].astype(str)
        result = result.pivot(index=['file_name','guid','dfsaddress','dfsdate','dfsid','dfsname'], columns='dfsegmentsfieldsid', values='dfsegmentsfieldsval').reset_index()
        result = result.to_dict(orient='records')[0]
        result = [{
                'guid':result.get('guid'),
                'file_name':result.get('file_name'),
        	'patient_id':'No Value Supplied' if result.get('PID_2_1') is None else result.get('PID_2_1'),
        	'patient_id_2':'No Value Supplied' if result.get('PID_4_1') is None else result.get('PID_4_1'),
        	'control_number':'No Value Supplied' if list_get(result.get('OBR_2_1').split('^'), 0) is None else list_get(result.get('OBR_2_1').split('^'), 0),
        	'alt_control_number':'No Value Supplied' if result.get('OBR_18_1') is None else result.get('OBR_18_1'),
        	'last_name':'No Value Supplied' if result.get('PID_5_1') is None else list_get(result.get('PID_5_1').split('^'), 0),
        	'middle_name':'No Value Supplied' if list_get(result.get('PID_5_1').split('^'), 2) is None else list_get(result.get('PID_5_1').split('^'), 2),
        	'first_name':'No Value Supplied' if result.get('PID_5_1') is None else list_get(result.get('PID_5_1').split('^'), 1),
        	'date_of_birth':result.get('PID_7_1'),
        	'patient_phone':'No Value Supplied' if result.get('PID_13_1') is None else result.get('PID_13_1'),
                'sex':replace_values_in_string(result.get('PID_8_1'), {'M':'Male','F':'Female','U':'Unknown'}),
        	'race':'No Value Supplied' if result.get('PID_10_1') is None else result.get('PID_10_1'),
        	'ethnicity':'No Value Supplied' if result.get('PID_22_1') is None else result.get('PID_22_1'),
        	'lab_test':'No Value Supplied' if result.get('OBR_4_1') is None else list_get(result.get('OBR_4_1').split('^'), 1),
        	'lab_test_code':'No Value Supplied' if result.get('OBR_4_1') is None else list_get(result.get('OBR_4_1').split('^'), 0),
        	'result':'No Value Supplied' if result.get('OBX_5_1') is None else result.get('OBX_5_1'),
        	'specimen_number':'No Value Supplied' if result.get('PID_3_1') is None else result.get('PID_3_1'),
        	'collection_date_and_time':datetime.strptime(result.get('OBR_7_1'), '%Y%m%d%H%M'),
        	'reported_date_and_time':datetime.strptime(result.get('OBR_22_1'), '%Y%m%d%H%M'),
        	'clinical_info':'No Value Supplied' if result.get('OBR_13_1') is None else result.get('OBR_13_1'),
                'fasting':replace_values_in_string(list_get(result.get('PID_18_1').split('^'), 6), {'Y':True, 'N':False}),
        	'total_volume':'No Value Supplied' if result.get('OBR_9_1') is None else result.get('OBR_9_1'),
        	'specimen_source':'No Value Supplied' if result.get('OBR_15_1') is None else result.get('OBR_15_1'),
                'abnormal_flag':replace_values_in_string(result.get('OBX_8_1'), {'L':'Below Normal','H':'Above High Normal','LL':'Alert Low','<':'Panic Low','A':'Abnormal','AA':'Critical Abnormal','S':'Susceptible','R':'Resistant','I':'Intermediate','NEG':'Negative','POS':'Positive'}),
        	'collection_units': 'No Value Supplied' if result.get('OBX_6_1') is None else result.get('OBX_6_1'),
        	'reference_range':'No Value Supplied' if result.get('OBX_7_1') is None else result.get('OBX_7_1'),
                'test_status':replace_values_in_string(result.get('OBX_11_1'), {'P':'Preliminary','X':'Canceled','F':'Complete','C':'Corrected Result','I':'Incomplete'}),
        	'lab':'No Value Supplied' if result.get('OBX_15_1') is None else result.get('OBX_15_1'),
        	'patient_note':'No Value Supplied' if result.get('NTE_3_1') is None else result.get('NTE_3_1'),
        	'observation_note_1':'No Value Supplied' if result.get('NTE_3_2') is None else result.get('NTE_3_2'),
        	'observation_note_2':'No Value Supplied' if result.get('NTE_3_3') is None else result.get('NTE_3_3'),
                'specimen_status':replace_values_in_string(list_get(result.get('PID_18_1').split('^'), 5), {'P':'Preliminary','F':'Final'}),
        	'ordering_provider_last_name':'No Value Supplied' if result.get('ORC_12_1') is None else list_get(result.get('ORC_12_1').split('^'), 2),
        	'ordering_provider_first_name':'No Value Supplied' if result.get('ORC_12_1') is None else list_get(result.get('ORC_12_1').split('^'), 1),
        	'provider_npi':'No Value Supplied' if result.get('ORC_12_1') is None else list_get(result.get('ORC_12_1').split('^'), 0),
        	'facility_id':'No Value Supplied' if  result.get('ZPS_2_1') is None else result.get('ZPS_2_1'),
        	'facility_name':'No Value Supplied' if result.get('ZPS_3_1') is None else result.get('ZPS_3_1'),
        	'facility_street':'No Value Supplied' if result.get('ZPS_4_1') is None else list_get(result.get('ZPS_4_1').split('^'), 0),
        	'facility_city':'No Value Supplied' if result.get('ZPS_4_1') is None else list_get(result.get('ZPS_4_1').split('^'), 2),
        	'facility_state':'No Value Supplied' if result.get('ZPS_4_1') is None else list_get(result.get('ZPS_4_1').split('^'), 3),
        	'facility_zip':'No Value Supplied' if result.get('ZPS_4_1') is None else list_get(result.get('ZPS_4_1').split('^'), 4),
        	'facility_phone':'No Value Supplied' if  result.get('ZPS_5_1') is None else result.get('ZPS_5_1'),
        	'facility_director_prefix':'No Value Supplied' if result.get('ZPS_7_1') is None else list_get(result.get('ZPS_7_1').split('^'), 0),
        	'facility_director_last_name':'No Value Supplied' if result.get('ZPS_7_1') is None else list_get(result.get('ZPS_7_1').split('^'), 1),
        	'facility_director_first_name':'No Value Supplied' if result.get('ZPS_7_1') is None else list_get(result.get('ZPS_7_1').split('^'), 2),
        	'data':'No Value Supplied' if result.get('ZEF_2_1') is None else result.get('ZEF_2_1'),
                'created_by_fk':1,
                'changed_by_fk':1
                }]
        db.session.bulk_insert_mappings(LabCorpOrderDetails, result)
        db.session.commit()
        print('Inserted result into LabCorpOrderDetails')
       # print(LabCorpOrderDetails.match_labtest_user(requisition_number=result.get('OBR_2_1'), first_name=list_get(result.get('PID_5_1').split('^'), 1), last_name=list_get(result.get('PID_5_1').split('^'), 0), date_of_birth=result.get('PID_7_1')))
        return True
    except Exception as e:
        print('Could not insert to order details table', e)
        db.session.rollback()
        return str(e)

def file_exists(processed):
    print('Checking if file has been processed')
    processed_files = [r.file_name for r in db.session.query(LabCorpFile.file_name).filter(LabCorpFile.process_success==True).distinct()]
    insert_file_names = list(set(processed)-set(processed_files))
    return insert_file_names

def insert_processed_record(file_name, message_number, process_success, raw_hl7, processed_hl7, error):
    try:
        update_session = LabCorpFile(file_name=file_name,message_number=message_number,process_success=process_success,raw_hl7=raw_hl7,processed_hl7=processed_hl7,error=error)
        #upsert_session = {'process_success':process_success}
        #print(pg_insert(LabCorpFile).values(**update_session.__dict__))
        #statement = pg_insert(LabCorpFile).values(**update_session.__dict__).on_conflict_do_update(index_elements=[LabCorpFile.file_name], set_=upsert_session)#set_=update_session.props_dict())
        #statement = pg_insert(LabCorpFile).values(update_session).on_conflict_do_update(constraint='file_name', set)
        #db.session.execute(statement)
        db.session.add(update_session)
        db.session.commit()
        print('LabCorpFile log created: {}, processing success: {}'.format(file_name, process_success))
    except Exception as e:
        print('LabCorpFile Insert failed. Record may already exist in the database.', e)
        db.session.rollback()
        try:
            print('Updating LabCorpFile process_success:{}'.format(process_success))
            update_session = LabCorpFile.process_success = process_success
            db.session.commit()
        except Exception as e:
            print('LabCorpFile update failed', e)
            db.session.rollback()

def fetch_file_as_bytesIO(sftp, path):
    with sftp.open(path, mode='rb') as file:
        file_size = file.stat().st_size
        file.prefetch(file_size)
        file.set_pipelined()
        return io.BytesIO(file.read(file_size))

def processNTE(line_tracker,line):
    if not line_tracker:
        return line
    else:
        df = pd.DataFrame.from_dict(line_tracker, orient='index')
        df = df.rename(columns={0: "NTE", 1: "NTE_1",2:"NTE_2",3:"NTE_3"})
        df['NTE_1'] = df['NTE_1'].astype(int)
        df = df.sort_values(by=['NTE_1']).reset_index()
        df = df.groupby(['NTE'], sort=True, as_index = True)['NTE_3'].apply('<br>'.join)
        return (str('NTE|1|L|') + str(df[0])).replace('\r\n','')

def files_to_process():
    processed = []
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:
        with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_password,cnopts=cnopts) as sftp:
            print("Connection succesfully established ... ")
            sftp.cwd(sftp_dir)
            directory_structure = sftp.listdir_attr()
            for attr in directory_structure:
                if attr.filename.endswith('.DAT') or attr.filename.endswith('.dat'):
                    processed.append(attr.filename)
        insert_file_names = file_exists(processed=processed)
        print('Files to process', len(insert_file_names))
        return insert_file_names
    except Exception as e:
        print("Fatal error fetching new files from SFTP:", e)
        return []

# If there are new files to process then process them else fail
def format_hl7_files(insert_file_names):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    if len(insert_file_names) > 0:
        with pysftp.Connection(host=sftp_host, username=sftp_user, password=sftp_password,cnopts=cnopts) as sftp:
            print("Connection succesfully established... ")
            sftp.cwd(sftp_dir)
            directory_structure = sftp.listdir_attr()
            for i in insert_file_names:
                try:
                    print('___________________________________________________________')
                    print('Processing', i)
                    data = fetch_file_as_bytesIO(sftp, path=i)
                    messages = {}
                    temp_message = ''
                    count = 0
                    for lines in data:
                        lines = lines.decode('utf8')
                        #lines = lines.replace('"','"')#.replace('\r\n','\n')
                        if lines.startswith('MSH'):
                            count += 1
                            messages[count] = temp_message
                        messages[count] += lines
                except Exception as e:
                    print(i,e)
                    pass
                for j in messages:
                    print('Formatting message number {0} from {1}'.format(j, i))
                    line_tracker = {}
                    message = ''
                    message_from_dict = messages[j].split('\r\n')
                    for line in message_from_dict:
                        if not line.startswith('NTE'):
                            data_line = processNTE(line_tracker, line)
                            if data_line.startswith('NTE|1|L|'):
                                note_line = processNTE(line_tracker, line)
                                line_tracker = {}
                                message += (note_line.replace('"',"'") + '\r\n')
                                #print(note_line)
                                #print(note_line.replace('"','\\"'))
                                #print(note_line.replace('"',"'"))
                            message += (line + '\r\n')
                        else:
                            lines = line.split('|')
                            line_tracker[line] = lines
                    try:
                        infile = str(i + '\r\n') + str(message)
                        print('Formatted HL7:', i)
                        hl7_json = readHL7(infile)
                        print('Converted HL7 to JSON:', i)
                        hl7_dataframe_to_sql = hl7_json_to_dataframe(hl7_json)
                        if hl7_dataframe_to_sql == True:
                            print('Temporary result saved to database')
                            insert_processed_record(i, message_number = j, process_success = 1, raw_hl7 = message, processed_hl7 = hl7_json, error = hl7_dataframe_to_sql)
                            if j == 1:
                                #sftp.rename('/sftp/results/incoming' + '/' + i, '/sftp/results/incoming/processed' + '/' + i)
                                print('Moved', sftp_dir + '/' + i, '--->', sftp_dir+'/processed' + '/' + i)
                        else:
                            insert_processed_record(i, message_number = j, process_success = 0, raw_hl7 = message, processed_hl7 = hl7_json, error = hl7_dataframe_to_sql)
                            print('Failed to write temporary result to database')
                    except Exception as e:
                        print('Failed to format HL7:', i, e)
                        insert_processed_record(i, message_number = j, process_success = 0, raw_hl7 = None, processed_hl7 = None, error =  str(e))
                        return False
                return True
    else:
        print('No new files to process')
