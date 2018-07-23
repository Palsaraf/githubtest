#from django.db.models.query import order_by
import calendar
import timeit
from Pyro.EventService.Server import start
from tms.debitcard.cardSaveAndValidate import cardSaveAndValidate
from tms.debitcard.cardSaveAndValidate import debitcardcheckandfraudrules
import cPickle
from _mysql_exceptions import IntegrityError
from decimal import Decimal,ROUND_DOWN
from utils.usertype import Money
from operator import itemgetter
from time import ctime
from utils.db import mysqldbwrapper
import webbrowser
from dateutil.relativedelta import relativedelta
from django.template.context import Context as django_Context
from django.template import Template as django_Template
from Pyro.errors import ConnectionClosedError
from Pyro.errors import ProtocolError
from config import loanstatusconfig
from config import mailconfig
from config import migration_config
from config.sms import sms_config
from tms.collection import collection_config
from config.waterfall import cardconfig
from config.waterfall.cardconfig import SERVICE_CODE
from config.waterfall import xmlconfig
from config.waterfall.waterfallconfig import CUSTOMER_LEVEL_EXCLUSION_LIST
from config.waterfall.waterfallconfig import LOAN_LEVEL_EXCLUSION_LIST
from config.CashBack.CashBackConfig import cashbackTypeExplanation
from config.CashBack.CashBackConfig import END_STATUS
from config.queueconfig import END_STATUS_CPA
import datetime
import random
from collections import OrderedDict
from datetime import timedelta
from django.views.generic.detail import DetailView, View
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import Context
from django.utils import simplejson
from gcms import dbtmsapi, gcmauthapi
from gcms.dbtmsapi import execute_search
from gcms.dbtmsapi import execute_select
from gcms.dbtmsapi import generate_new_path
from gcms.dbtmsapi import getBusinessTypeFrmLoanID
from gcms.dbtmsapi import get_CustomerInfo
from gcms.dbtmsapi import get_prorata_calc_date
from gcms.dbtmsapi import get_SOACC_count
from gcms.dbtmsapi import get_Store_Info_frm_storeid
from gcms.dbtmsapi import get_all_BankAccount_Info
from gcms.dbtmsapi import req_encoded
from gcms.dbtmsapi import get_product_classification
from utils.db import mysqldbwrapper
from tms.paymentcalendar import paymentutils
from tms.LoanScheduleGenerator.schedule_for_loan import Schedule
from tms.tmsdata import increqconfig
import os
from projectpath import projectpaths
from tms.tmsapi.paydates import getPayCycle
from tms.RTIServices.rtiapi import LOC_sendStatementsToUE,LOC_paymentHoliday

PROJECTPATH = projectpaths.getProjectPath()

DBCONFIGPATH = os.path.join(PROJECTPATH,projectpaths.DBCONFIGPATH)

config_file_path =DBCONFIGPATH
#from gcms.dbtmsapi import get_amount_collected
from gcms.dbtmsapi import getPaidAmt, getPaidAmt_tran
from gcms.dbtmsapi import get_bankname
from gcms.dbtmsapi import get_customer_email_from_cust_id
from gcms.dbtmsapi import get_pay_frequency
from gcms.dbtmsapi import get_product_repay_freq
from gcms.dbtmsapi import get_refunded_transactions
from gcms.dbtmsapi import getallbankinfo
from gcms.dbtmsapi import getbankinfo
from gcms.dbtmsapi import getbankname_uk
from gcms.dbtmsapi import isPhone
from gcms.dbtmsapi import getLinkedTemplateInfo
from gcms.dbtmsapi import get_withdrawal_reason
from gcms.dbtmsapi import isOutStandingBalance
from gcms.dbtmsapi import get_account_close_dtls
from gcms.dbtmsapi import post_sms
from gcms.dbtmsapi import search_Bank_Info_Repo
from gcms.dbtmsapi import update_or_insert_Notice_Flags
from gcms.dbtmsapi import checkUnreturnedMoney
from gcms.dbtmsapi import overridePayCalRecords
from gcms.dbtmsapi import updatePaymentRecords
from gcms.dbtmsapi import checkCashBackPaid
from gcms.dbtmsapi import get_balance_dtls
from gcms.dbtmsapi import insertIntoTransOffTrans
from gcms.dbtmsapi import updateNoticeFlagsAndGCMDocs
from gcms.dbtmsapi import getToBeGeneratedList
from gcms.dbtmsapi import get_amount_dtls
from gcms.dbtmsapi import add_existing_card_info
from gcms.dbtmsapi import check_card_exists
from gcms.dbtmsapi import waive_future
from gcms.dbtmsapi import get_card_list_from_loan_id
from gcms.dbtmsapi import get_card_list_withbintail
from gcms.dbtmsapi import update_selected_card_from_loan_id
from gcms.dbtmsapi import isDailyRunStarted
from gcms.dbtmsapi import updateDeltaMatrix
from gcms.dbtmsapi import get_customer_name
from gcms.dbtmsapi import modify_Notice_Flags
from config.document_template.doctemp_config import DOCTYPE,mail_subject,EMAILDOC,SOACC_valid_statuses
from config.document_template.doctemp_config import SOACC_valid_statuses
from gcms.gcmauthapi import fetch_user_store_and_business_type
from gcms.dbtmsapi import get_document_names
from gcms.dbtmsapi import get_associatedloans
from gcms.dbtmsapi import update_associated_carddetails
from gcms.dbtmsapi import get_doc_names
from gcms.dbtmsapi import get_product_classification
from gcms.dbtmsapi import get_product_details_of_loan
from gcms.gcmauthapi import get_spl_privileges_by_usr_id
from gcms.gcmauthapi import get_user_privileges
from gcms.gcmauthapi import check_user_privilege_on_store_id
from gcms.gcmauthapi import to_identify_pdtinfo
from gcms.gcmcaseapi import add_gcm_case_comments
from gcms.gcmcaseapi import add_gcm_email
from gcms.gcmcaseapi import add_gcm_notes
from gcms.gcmcaseapi import add_gcm_notes_checks
from gcms.gcmcaseapi import lockLead
from gcms.gcmcaseapi import check_caseid_assigned
from gcms.gcmcaseapi import check_entry_gcm_user
from gcms.gcmcaseapi import check_file_name_exists
from gcms.gcmcaseapi import encode
from gcms.gcmcaseapi import fetch_curr_date
from gcms.gcmcaseapi import getAllNotes
from gcms.gcmcaseapi import get_all_gcm_documents
from gcms.gcmcaseapi import get_all_gcm_documents_view
from gcms.gcmcaseapi import get_case_id_by_entity_id
from gcms.gcmcaseapi import get_custid_from_loanid
from gcms.gcmcaseapi import get_store_cust_id_from_loan_id
from gcms.gcmcaseapi import get_customer_entity_id
from gcms.gcmcaseapi import get_end_status_cd_by_case_id
from gcms.gcmcaseapi import get_entity_id_by_case_id
from gcms.gcmcaseapi import get_generated_list
from gcms.gcmcaseapi import get_loan_entity_id
from gcms.gcmcaseapi import get_loan_status_by_loan_case_id
from gcms.gcmcaseapi import get_loan_status_by_loan_id
from gcms.gcmcaseapi import get_log_id_by_loan_id
from gcms.gcmcaseapi import get_logid_by_caseid
from gcms.gcmcaseapi import get_reason_code
from gcms.gcmcaseapi import get_related_customer_case_id
from gcms.gcmcaseapi import get_related_loan_case_id
from gcms.gcmcaseapi import insert_gcm_document
from gcms.gcmcaseapi import isEndStatus
from gcms.gcmcaseapi import updateCreditCheckStatus
from gcms.gcmcaseapi import updateGCMCase
from gcms.gcmcaseapi import trandbupdateGCMCase
from gcms.gcmcaseapi import update_gcm_case_log_review_time
from gcms.gcmcaseapi import update_gcm_notes
from gcms.gcmcaseapi import update_get_user_table_by_case_id
from gcms.gcmcaseapi import get_repaymentdate_payfreq_info
from gcms.gcmcaseapi import get_cashback_info_by_loan_id
from gcms.gcmcaseapi import get_cashbackcalci_info_by_loan_id
from gcms.gcmcaseapi import get_uncleared_cycleinfo_by_loan_id
from gcms.gcmcaseapi import get_uncleared_cycles_by_loan_id
from gcms.gcmcaseapi import get_feegrace_paytypes_by_loan_id
from gcms.gcmcaseapi import unlockLead
from gcms.gcmcaseapi import getoldstatusfromlog
from gcms.gcmqueueapi import connect_pyro
from gcms.gcmcaseapi import trandbadd_gcm_notes
from gcms.gcmcaseapi import traninsert_gcm_document
from gcms import gcmcaseapi
import os

from utils.db.trandb import TranDB
from tms.CashBack.cbfunc import get_cashbackamount_info_by_loan_id
from tms.auth.views import check_user_in_privilege_list
from tms.CashBack.cbfunc import discard
from tms.custdetail.xmlhandler import buildCVSRequest
from tms.debitcard.cardservice_CIM_1003 import getCardDetails
from tms.doc_template.api_documents import document_generation_method
from tms.doc_template.api_documents import document_invalid_method
from tms.doc_template.api_documents import document_send_method
from tms.doc_template.api_documents import generate_document
from tms.doc_template.api_documents import get_generated_file_detail
from tms.doc_template.api_documents import output_Dir
from tms.doc_template.api_documents import output_File
from tms.documents.thread import emailIndividualSend
from tms.paymentcalendar import dpfunc
from tms.paymentcalendar import pcfunc
from tms.paymentcalendar import pcfactory
from tms.paymentcalendar.paymentutils import prorata_cal,\
    update_future_waiver_date
from tms.paymentcalendar.paymentutils import amount_cal
from tms.paymentcalendar.paymentutils import update_paydate_in_payments_table
from tms.paymentcalendar.globalvars import GlobalVars
from config.paymentcalendar.pcconfig import LSS_DICT
from tms.pullengine import downpaymentschedulegenerator
from tms.pullengine import paymentschedulegenerator
from tms.pullengine.paymentschedulegenerator import  PaymentScheduleGenerator
from tms.pullengine.paymentschedule import delete_transaction
from tms.pullengine.paymentschedule import update_paydate
from tms.pullengine.paymentschedule import update_transactions
from tms.pullengine.paymentschedule import update_generatedby
from tms.pullengine.paymentschedule import computegeneratedby
from tms.LoanScheduleGenerator import schedule_for_loan
from tms.settings import MEDIA_ROOT
from tms.settings import MEDIA_ROOT_IMAGE
from tms.settings import MEDIA_ROOT_MAIL
from tms.settings import MEDIA_ROOT_CSV
from tms.settings import MEDIA_ROOT_INPUT

from tms.tmsapi import loan
from tms.tmsapi import paydates
from tms.tmsapi.decorator import login_required,maintenance_deco,maintenance_deco_popups
from tms.tmsdata.models import Account
from tms.tmsapi.decorator import maintenance_deco_popups
from tms.tmsapi import chargeBack
from tms.tmsapi.decorator import login_required
from tms.tmsapi.paydatesconfig import paydate_change_reasons

from tms.tmsdata.models import Address_Info
from tms.tmsdata.models import BankAccount_Info
from tms.tmsdata.models import Bank_Info
from tms.tmsdata.models import Bank_Info_Repo
from tms.tmsdata.models import Cheque
from tms.tmsdata.models import Customer
from tms.tmsdata.models import CustomerProducts
from tms.tmsdata.models import CustomerSecurityQuestion
from tms.tmsdata.models import Customer_Basic_Info
from tms.tmsdata.models import Direct_Deposit
from tms.tmsdata.models import Doc_kits
from tms.tmsdata.models import Downpayments
#from tms.tmsdata.models import DNC
from tms.tmsdata.models import Email_Info
from tms.tmsdata.models import Employer_Info_Repo
from tms.tmsdata.models import Employment_Info
from tms.tmsdata.models import Ext_Bureau_Info
from tms.tmsdata.models import Extra_Info
from tms.tmsdata.models import Fees
from tms.tmsdata.models import IP_Address
from tms.tmsdata.models import Image_Info
from tms.tmsdata.models import Loan
from tms.tmsdata.models import LoanLatest
from tms.tmsdata.models import Loan_Info
from tms.tmsdata.models import MasterQuestionList
from tms.tmsdata.models import Notice_Flags
from tms.tmsdata.models import PayDates
from tms.tmsdata.models import PaymentCalendar
from tms.tmsdata.models import Payments
from tms.tmsdata.models import Phone_Info
from tms.tmsdata.models import Prepaid_Card_Info
from tms.tmsdata.models import Prepayments
from tms.tmsdata.models import Product
from tms.tmsdata.models import Reference_Info
from tms.tmsdata.models import Store
from tms.tmsdata.models import Store_Info
from tms.tmsdata.models import Legal_Info
from tms.tmsdata.models import Transactions
from tms.tmsdata.models import Collection_Info
from tms.tmsdata.models import Charge_Back
from tms.tmsdata.models import FutureWaiver
from tms.tmsdata.models import Loan
from tms.tmsutils import returns
from tms.tmsutils.TMSQ import TMSQueue
from tms.tmsutils.immediatepull import imm_pull_tms
from tms.tmsutils.postcode_utils import AddressLookUp_Utils
from tms.tmsutils.postcode_utils import PostCodeLookUp_Utils
from utils.dates import dates
from tms.waterfall import request as sanityParser
from tms.waterfall.merchant.barclays import Barclays
from tms.waterfall.merchant.voicepay import VoicePay
from tms.waterfall.pedriver import getcarddata
from tms.waterfall.pedriver import getkeytranid
from config.paymentcalendar.pcconfig import LSS_DICT
from config.paymentcalendar import pcconfig
from config import queueconfig
from tms.tmsapi.chargeBack import freeze_loan
from tms.collection import collection_config

from utils.dates import dates
from utils.builder.xml.custombuilder import CustomXMLBuilder
from utils.dates.dates import toDate
from utils.dates.dates import toDateTime
from utils.globalKey import getKeyTranID
from utils.misc import customlogger
from utils.misc.customlogger import rotatinglogger
from utils.misc.customexception import CustomException,TMSCustomException
from utils.misc.customexception import FieldNotFound
from utils.misc.customexception import LoggedExceptions
from utils.parsers.requestparser import Request
from utils.poster.customposter import Poster
import line_reassessment
import urllib

from config.CASconfig import CAS_LENDER_MAP

import urllib2
import json
import re
import url_settings
from tmsapi.paydatesUtils import *

from utils.poster import sslv3
from tms.documents.docgenerator import inidividualGeneration
from tms.documents.docgenerator import individualSend
from config.waterfall.waterfallconfig import CUSTOMER_LEVEL_EXCLUSION_LIST
from config.waterfall.waterfallconfig import LOAN_LEVEL_EXCLUSION_LIST
from config.queueconfig import END_STATUS_CPA

import os
from projectpath import projectpaths


from django.core.paginator import Paginator, InvalidPage, EmptyPage

from tms.tmsdata.validator import EMP_PAYROLLFREQ

PROJECTPATH = projectpaths.getProjectPath()

DBCONFIGPATH = os.path.join(PROJECTPATH,projectpaths.DBCONFIGPATH)



logger = customlogger.basiclogger("cust_detail_views", "DEFAULT")
card_logger = customlogger.basiclogger('Card Details', "CARD")
card_access_logger = customlogger.basiclogger('show card number', "CARD_ACCESS")
sms_logger = customlogger.basiclogger("cust_detail_views", "SMS")
paycal_logger = customlogger.basiclogger("Paycal_logger", "PAYCAL")
sch_logger = customlogger.basiclogger("Schedule", "Schedule_Generator")
#loan_gen_logger_refactor = customlogger.basiclogger("cust_detail_views", "LOAN_GEN",format="custom")
imm_pull_logger = customlogger.basiclogger("cust_detail_views", "IMMEDIATE_PULL")
log = rotatinglogger('Document_Generation_Logger',section='DOC_GENERATION_ROTATING')
pdc_log = rotatinglogger('PDC_Fund_To',section = 'PDC_LOG_ROTATING')
CB_log = customlogger.basiclogger("CB_Updates", "ChargeBack")
cas_logger = customlogger.basiclogger("PAYDATES", "CAS_CONNECTION")
externalarrange_logger = customlogger.basiclogger("externalarrange", "EXTERNALARRANGE")
# waiver_logger = customlogger.basiclogger("Waivers", "WAIVERS")

externalarrange_logger.info("ReleSE 3 "+str(simplejson.__file__)+ "Dir"+str(dir(simplejson)))
gcm_notes = customlogger.basiclogger("gcm_notes", "DEFAULT")
config_file_path =DBCONFIGPATH
configfile = DBCONFIGPATH
bank_info_det=''
flag=''

from tms.doc_template import utils
from gcms.gcmcaseapi import get_log_id_by_loan_id
from gcms.gcmcaseapi import add_gcm_notes
#from gcms.gcmcaseapi import get_generated_list
from gcms.gcmcaseapi import get_generated_list_new
from gcms.gcmcaseapi import get_entity_id_by_case_id
from gcms.gcmcaseapi import update_gcm_document_status
from gcms.gcmcaseapi import get_latest_gcmlog_by_caseid
from gcms.gcmcaseapi import get_documents_by_kitid
from tms.tmsapi.paydatesconfig import bankHolidayList_EngAndWales,bankHolidayList_Scotland,bankHolidayList_NI
#from gcms.dbtmsapi import get_CustomerInfo
from libs import pdf_generator
from gcms.dbtmsapi import get_document_names
from gcms.dbtmsapi import get_associatedloans
from gcms.dbtmsapi import update_associated_carddetails
from gcms.dbtmsapi import get_doc_names
import os
from projectpath import projectpaths

PROJECTPATH = projectpaths.getProjectPath()

DBCONFIGPATH = os.path.join(PROJECTPATH,projectpaths.DBCONFIGPATH)

#sys.path.append(PROJECTPATH+'/utils/misc')
from utils.misc.customlogger import rotatinglogger
import traceback
#sys.path.append(PROJECTPATH+'/utils')
from utils.smtpmailer import smtpmailer
from utils.smtpmailer.smtpmailer import mail_send
from tms.tmsutils.aesencrypt import encrypt_data, decrypt_data
from tms.tmsapi.decorator import login_required
bank_info_det=''
#output_file_path=''
#@login_required
from copy import deepcopy
from tms.PdcClient.views import cardStatementFn
from tms.PdcClient.views import cardInfoFn
from tms.PdcClient.views import cardEnquiryFn
from utils.globalKey import getKeyTranID
from tms.zebitAPI.zebitservice import reportCustomerProfileChange
from tms.zebitAPI.zebitservice import reportBankAccountChange
from tms.zebitService.zebit_config import PHYSICAL_CARD_STATUS
from tms.zebitAPI.zebitapi import getStoreId
from tms.collection import collection_config
import base64
from tms.tmsapi import chargeBackCSVUpload
from gcms.dbtmsapi import update_card_reference
from tms.sms import common_sms
from tms.tmsdata.validator import PAYDATES_FREQ_MAP, EMP_PAYROLLFREQ
from tms.tmsapi import SMSUploaded
from tms.tmsapi.auto_fee_waiver_api import AutoWaiverAPI

from tms.RTIServices import rtiapi

from tms.RTIServices.rtiapi import reportprofileupdate
configfile = DBCONFIGPATH
log = rotatinglogger('Document_Generation_Logger',section='DOC_GENERATION_ROTATING')
IandE_log = customlogger.basiclogger('Income_expense_calc',section='INOCME_EXPENSE_CALC')
Manual_UE_log = customlogger.basiclogger('Manual_UE_scores',section='MANUAL_UE_SCORES')
pdc_log = rotatinglogger('PDC_Fund_To',section = 'PDC_LOG_ROTATING')
flag=''

def cust_detail(request):
    """
    This view displays the customer / loan information based on the respective
    Id passed through the search.
    """
    read=0
    username = request.session['username']
    menu = request.session['sessionmenu']
    request.session["start_status"]=""
    request.session["changed_state"]=""
    user_detail={}
    global bank_info_det
    bank_info_det=get_bankname()
    
    privilege_tup=get_user_privileges(str(username))
    if (request.GET.has_key('loanqueue') and request.GET.has_key('loan_id')) and ('Leads',) not in privilege_tup:
        request.session['priv_msg'] = "Sorry You are not Authorized to enjoy this \
                                          priviledge,please contact Admin"
        return HttpResponseRedirect('/auth/index')

    elif ((request.GET.has_key('cust_id') or request.GET.has_key('loan_id')) and not request.GET.has_key('loanqueue')) and ('Search',)  not in privilege_tup:
        request.session['priv_msg'] = "Sorry You are not Authorized to enjoy this \
                                           priviledge,please contact Admin"

        return HttpResponseRedirect('/auth/index')
    
    elif request.GET.has_key('loan_id'):
        loanid = request.GET['loan_id']
        store = Loan.objects.filter(loan_id = loanid)[0].store_id
        if store == migration_config.store_id:
            request.session['priv_msg'] = "Sorry. This loan has been migrated to LS 2.0."
            return HttpResponseRedirect('/auth/index')

    field=""
    menu_flag=0
    extra_list =""
    case_id=''
    before_booked_flag=0
    queue = 0
    if request.method == 'GET':
        if 'read' in request.GET:
            read=request.GET['read']
        if 'cust_id' in request.GET:
            cust_id = request.GET['cust_id']
            loan_id=get_loan_entity_id(cust_id)
            field=cust_id
            case_id=get_case_id_by_entity_id(loan_id,'LOAN')
            try:
                lockLead(case_id,username)
            except IntegrityError, e:
                logger.error(str(e))
                error_message = str(e)
#                return HttpResponseRedirect("/record/?locked=1&read=1&&loan_id=%s" % loan_id)
            except Exception, e:
                error_message = "Technical problem in locking the lead"
                request.session['priv_msg'] = error_message
                return HttpResponseRedirect('/auth/index')

        elif 'loan_id' in request.GET:
            loan_id = request.GET['loan_id']
            case_id=get_case_id_by_entity_id(loan_id,'LOAN')
            cust_id=get_customer_entity_id(loan_id)
            field=loan_id

            if 'loanqueue' in request.GET:
                queue = 1
                if not check_entry_gcm_user(case_id):
                     request.session['priv_msg'] = "Sorry You are not Authorized to enjoy this \
                                           privilege,please go via Queue "
                     return HttpResponseRedirect('/auth/index')
            else:
                pass
#                try:
#                    lockLead(case_id,username)
#                except IntegrityError, e:
#                    logger.error(str(e))
#                    error_message = str(e)
##                    return HttpResponseRedirect("/record/?locked=1&read=1&&loan_id=%s" % loan_id)
#                except Exception, e:
#                    error_message = "Technical problem in locking the lead"
#                    request.session['priv_msg'] = error_message
#                    return HttpResponseRedirect('/auth/index')
    # Code for Extra Info
    extra_list = Extra_Info.objects.filter(loan=loan_id)
    status_cd=get_loan_status_by_loan_id(loan_id)
 
    """
    Select Suplemetal UE segment to display Manual UE loan score iframe in TMS portal
    """
    Supl_UE_Segment = Loan.objects.get(loan_id = loan_id).supplementary_segment.upper() if Loan.objects.get(loan_id = loan_id).supplementary_segment else None
    
    product_classification = get_product_classification(loan_id)
    return render_to_response('custdetail/custdetail.html', \
        {"username":username, "menu":menu,"status_cd":status_cd,\
        'field':field,'read':read,'loanqueue':queue,\
        "menu_flag":menu_flag,'extra_list':extra_list,"range1":range(60),"before_booked_flag":before_booked_flag,\
        "user_detail":user_detail,'params':{"cust_id":cust_id,"loan_id":loan_id},'product_classification':product_classification,'Supl_UE_Segment':Supl_UE_Segment } )

cust_detail = login_required(cust_detail)


def LOC_wizard_popup(request):
    """
    This will pop-up a window through which new bank record could be added after getting its validation done by UE using TMS-UE RTI .
    This renders a popup where Customer's Bank information\
    can be viewed and also be edited.
    """    
    username= 'TMS UI'
    try:
        #import pdb; pdb.set_trace()
        if 'username' in request.session:
            username = request.session['username']


        if request.method=='GET':
            loan_id = request.GET['loan_id']
            cust_id = request.GET['cust_id']
        elif request.method=='POST':
            loan_id = request.POST['loan_id']
            cust_id = request.POST['cust_id']
        else:
            return HttpResponse('CUSTOMER ID is Missing check with Back End Team!')
        if request.method == 'POST':            
            if not request.POST['account_number']:
                return HttpResponse('account number is missing!')
            
            #for k in request.POST:
            #    if request.POST[k]=='None' or request.POST[k]=='':
            #        request.POST[k]= None
                    
            if request.POST['act_now']== 'validate':    # validation segment
                logger.info("inside validate")
                data_dict={'cust_id': cust_id, 'bank_acc_nbr': request.POST['account_number'], 'routing_number': request.POST['routing_number'], 'username':username}
                UE_resp = rtiapi.LOC_bankAcc_update(data_dict)
                if UE_resp in ['cust id is not available','Invalid XML response from UE','Internal Error','No Information Found'] or UE_resp in ('Unhandled Exception In Validating AccountNo'):
                    return HttpResponse("Technical Error. Contact Back End Team.")
                else:
                    return HttpResponse(UE_resp)

                    
            #import pdb; pdb.set_trace()
            if request.POST['act_now']== 'save':         # saving the changes in the DB
                curr_date= datetime.datetime.now()
                routing_nbr= request.POST['routing_number'] or None
                swift_code = request.POST['swift_code'] or None
                account_number= request.POST['account_number'] or None            # to be confirmed
                
                account_type= request.POST['account_type'] or 'SALARY'
                account_name= request.POST['account_name'] or None
                FPS_eligibility=0
                CHAPS_eligibility=0
                BACS_eligibility=0
                bank_name = request.POST['bank_name'] or None
                bank_addr = request.POST['bank_addr'] or None
                bank_postcode = request.POST['bank_postcode'] or None
                bank_phone = request.POST['bank_phone'] or None
                branch_name = request.POST['branch_name'] or None
                
                account_nbr = encrypt_data(account_number)
                
                if FPS_eligibility is None:
                    FPS_eligibility = 0
                    
                if CHAPS_eligibility is None:
                    CHAPS_eligibility = 0
                    
                if BACS_eligibility is None:
                    BACS_eligibility = 0
                    
                logger.info("customer id :: "+str(cust_id))
                tmsconn = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA') #check whether the account number is already present???????
                
                #query1= "select bank_account_id from BankAccount_Info where cust_id=%s and account_number='%s' and override_flag=0"%(cust_id, account_nbr)
                #logger.info("print query :: "+str(query1))
                #account_id= tmsconn.get_one_result(query1)
                
                #if account_id:          #the account_number is already present. We need to override it
                #some active account_number is already present. We need to override it
                query_to_override= "update BankAccount_Info set override_flag = 1, last_updated = now(), modified_by='TMS UI'\
                                    where cust_id=%s and override_flag=0"%(cust_id)
                tmsconn.execute(query_to_override)
                logger.info("overrided the existing active record")
                    
                # add it as a new account_number. (new record)
                if account_type.upper() not in ('SAVINGS','CURRENT','SALARY'):
                    account_type= 'SALARY'
                query_insert= " insert into BankAccount_Info values(NULL,%s,%s,%s,%s,%s,now(),NULL,%s,%s,NULL,%s)"
                args=(routing_nbr, account_name, account_nbr, account_type, swift_code, 0,username, cust_id)
                tmsconn.execute(query=query_insert, args=args)
                logger.info("Inserting a new active record")
                
                sql = "select * from Bank_Info_Repo where routing_no='%s'"%(routing_nbr)
                bakRepoDetails = tmsconn.get_one_result(sql)
                if bakRepoDetails:
                    if(branch_name != bakRepoDetails['branch_name'] or bank_phone != bakRepoDetails['branch_phone'] or \
                       bank_postcode != bakRepoDetails['branch_postcode'] or bank_addr != bakRepoDetails['branch_address'] or \
                        bank_name != bakRepoDetails['bank_name'] or FPS_eligibility != bakRepoDetails['FPS_eligibility'] or \
                        CHAPS_eligibility != bakRepoDetails['CHAPS_eligibility'] or BACS_eligibility != bakRepoDetails['BACS_eligibility']):
                        
                        sql = "update Bank_Info_Repo set override_flag=1,last_modified_dt=now(),modified_by='%s' where routing_no='%s'"%(username,routing_nbr)
                        tmsconn.execute(sql)
                        logger.info("overriding in Bank_Info_Repo")
                        
                        insQry = "insert into Bank_Info_Repo (routing_no,bank_name,branch_name,branch_address,branch_postcode,branch_phone,\
                        FPS_eligibility,BACS_eligibility,CHAPS_eligibility,create_dt,created_by) values (%s,%s,%s,%s,\
                        %s,%s,%s,%s,%s,now(),%s)"
                        args=(routing_nbr,bank_name,branch_name,bank_addr,bank_postcode,bank_phone,FPS_eligibility,BACS_eligibility,CHAPS_eligibility,username)
                        tmsconn.execute(query=insQry, args=args)
                        logger.info("Inserted a new record in Bank_Info_Repo")
                else:
                    insQry = "insert into Bank_Info_Repo (routing_no,bank_name,branch_name,branch_address,branch_postcode,branch_phone,\
                        FPS_eligibility,BACS_eligibility,CHAPS_eligibility,create_dt,created_by) values (%s,%s,%s,%s,\
                        %s,%s,%s,%s,%s,now(),%s)"
                    args=(routing_nbr,bank_name,branch_name,bank_addr,bank_postcode,bank_phone,FPS_eligibility,BACS_eligibility,CHAPS_eligibility,username)
                    tmsconn.execute(query=insQry, args=args)
                    logger.info("Inserted a new record in Bank_Info_Repo")

                '''
                    INFORM THE CHANGES TO UI
                '''
                try:
                    bankInfoDict = {}
                    bankInfoDict['SortCode']            = routing_nbr
                    bankInfoDict['BankAccountNumber']   = account_number
                    bankInfoDict['Bankaccount_updated'] = 1
                    updateTOUI = rtiapi.LOC_bank_profile_infoUpdate(loan_id,data=bankInfoDict,UI_flag=0,service_code='6102')
                    if updateTOUI is not True:
                        logger.info("Bank Information is not properly updated to UI")
                except Exception,e:
                    logger.debug("Error in Informing the status to UI for the Cust Id :: "+str(cust_id))
                    logger.debug("Logging Error ::"+str(e)+str(traceback.format_exc()))
                
            return HttpResponse("Banks Details has been added successfully")
    except Exception,e:
        logger.info("Logging ::"+str(traceback.format_exc())+str(e))
    
def bank_popup(request):
    """
    This will pop-up a window through which new bank record could be added.
    This renders apopup where Customer's Bank information\
    can be viewed and also edited.
    """
    if 'username' in request.session:
        username = request.session['username']
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('CUSTOMER ID is Missing check with Back End Team!')
    customer_id = Customer.objects.filter(cust_id=cust_id)
    account_type_dict={'SALARY':'Salary','SAVINGS':'Savings','CURRENT':'Current','OTHER':'Other'}
    if request.method == 'POST':
        curr_date=datetime.datetime.now()
        Trouting_number = request.POST['routing_number']
        Tswift_code = request.POST['swift_code']
        Taccount_number = request.POST['account_number']
        Taccount_type=request.POST['account_type']
        Taccount_name=request.POST['account_name']
        Tbranch_name=request.POST['branch_name']
        Tbranch_phone=request.POST['bank_phone']
        Tbranch_postcode=request.POST['bank_postcode']
        Tbranch_addr=request.POST['bank_addr']
        Tbank_name=request.POST['bank_name']
        TFPS_eligibility=request.POST['FPS_eligibility']
        TCHAPS_eligibility=request.POST['CHAPS_eligibility']
        TBACS_eligibility=request.POST['BACS_eligibility']

        if Tbranch_name=="None":
            Tbranch_name=eval(Tbranch_name)
        elif len(Tbranch_name)==0:
            Tbranch_name=None
        if Tbranch_phone=="None":
            Tbranch_phone=eval(Tbranch_phone)
        elif len(Tbranch_phone)==0:
            Tbranch_phone=None
        if  Tbranch_postcode == "None":
            Tbranch_postcode=eval(Tbranch_postcode)
        elif len(Tbranch_postcode)==0:
            Tbranch_postcode=None
        if Tbranch_addr=="None":
            Tbranch_addr=eval(Tbranch_addr)
        elif len(Tbranch_addr)==0:
            Tbranch_addr=None
        if Tbank_name=="None":
            Tbank_name=eval(Tbank_name)

        TBACS_eligibility=eval(TBACS_eligibility)
        TCHAPS_eligibility=eval(TCHAPS_eligibility)
        TFPS_eligibility=eval(TFPS_eligibility)

        bankinfo=BankAccount_Info.objects.filter(cust=cust_id,override_flag=0)[0]

        if (bankinfo.routing_number != Trouting_number) or \
            (bankinfo.account_number != Taccount_number) or \
            (bankinfo.account_type != Taccount_type) or \
            (bankinfo.swift_cd != Tswift_code) or\
            (bankinfo.account_name!=Taccount_name):
                BankAccount_Info.objects.filter(cust=customer_id[0],override_flag=0 ).update(override_flag=1,last_updated=curr_date)
                bankobj = BankAccount_Info(routing_number=Trouting_number,\
                    account_number=Taccount_number,swift_cd=Tswift_code,\
                    account_type=Taccount_type,\
                    account_name=Taccount_name,\
                    create_date=str(curr_date),\
                    created_by=username,\
                    last_updated=None,\
                    modified_by=None,
                    cust=customer_id[0],override_flag=0 )
                bankobj.save()
                bank_info_repo=Bank_Info_Repo.objects.filter(routing_no=Trouting_number)
                if bank_info_repo:
                    bank_info_repo=bank_info_repo[0]
                    if (bank_info_repo.branch_name != Tbranch_name or\
                        bank_info_repo.branch_phone != Tbranch_phone or \
                        bank_info_repo.branch_postcode != Tbranch_postcode or \
                        bank_info_repo.branch_address != Tbranch_addr or\
                        bank_info_repo.bank_name != Tbank_name or\
                        bank_info_repo.FPS_eligibility != TFPS_eligibility or\
                        bank_info_repo.CHAPS_eligibility != TCHAPS_eligibility or\
                        bank_info_repo.BACS_eligibility != TBACS_eligibility):

                            if (((bank_info_repo.branch_address is None) and (Tbranch_addr is not None)) or \
                                ((bank_info_repo.branch_postcode is None) and (Tbranch_postcode is not None)) or\
                                ((bank_info_repo.branch_phone is None) and (Tbranch_phone is not None)) or\
                                ((bank_info_repo.branch_name is None) and (Tbranch_name is not None))):
                                    Bank_Info_Repo.objects.filter(routing_no=Trouting_number).update(override_flag=1,last_modified_dt=curr_date)

                                    bank_info_record=Bank_Info_Repo(routing_no=Trouting_number,\
                                    bank_name=Tbank_name,branch_name=Tbranch_name,\
                                    branch_address=Tbranch_addr,branch_postcode=Tbranch_postcode,\
                                    branch_phone=Tbranch_phone,FPS_eligibility=TFPS_eligibility,\
                                    BACS_eligibility=TBACS_eligibility,CHAPS_eligibility=TCHAPS_eligibility,\
                                    create_dt=curr_date,created_by=username,last_modified_dt=None,modified_by=None,verified_source='Service',\
                                    verified_dt=curr_date,override_flag=0)
                                    bank_info_record.save()

                else:
                    bank_info_repo=None
                    bank_info_record=Bank_Info_Repo(routing_no=Trouting_number,\
                    bank_name=Tbank_name,branch_name=Tbranch_name,\
                    branch_address=Tbranch_addr,branch_postcode=Tbranch_postcode,\
                    branch_phone=Tbranch_phone,FPS_eligibility=TFPS_eligibility,\
                    BACS_eligibility=TBACS_eligibility,CHAPS_eligibility=TCHAPS_eligibility,\
                    create_dt=curr_date,created_by=username,last_modified_dt=None,verified_source='Service',\
                    verified_dt=curr_date,override_flag=0)
                    bank_info_record.save()

        #rtiapi.LOC_bank_profile_infoUpdate(loan_id,UI_flag=0,service_code='6102')
    return render_to_response("custdetail/bank_popup.html", \
    {'account_type_dict':account_type_dict,"cust_id":cust_id,"loan_id":loan_id})
bank_popup = maintenance_deco_popups(bank_popup)
def emp_popup(request):
    """
    This will pop-up a window through which new employee record could be added.
    """

    if request.method=='GET':
        cust_id = request.GET['cust_id']
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        cust_id = request.POST['cust_id']
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('CUSTOMER ID is Missing check with Back End Team!')

    username=request.session['username']

    verified_source=[['GOOGLE','Google'],['SWITCH BOARD','Switch Board'],['YAHOO','Yahoo'],['YELL','Yell'],['DATABASE','Database'],['OTHER','Other']]
    payroll=[["DIRECT DEPOSIT","Direct Deposit"],["PAY CHEQUE","Pay Cheque"],["CASH","Cash"],["OTHER","Other"]]
    payfreq = [[key,value["Value"]] for key,value in EMP_PAYROLLFREQ.iteritems()]
#    payfreq=[["FOUR-WEEKLY","Four-Weekly"],\
#            ["FIRST MONDAY OF EACH MONTH","First Monday of each month"],\
#            ["FIRST TUESDAY OF EACH MONTH","First Tuesday of each month"],\
#            ["FIRST WEDNESDAY OF EACH MONTH","First Wednesday of each month"],\
#            ["FIRST THURSDAY OF EACH MONTH","First Thursday of each month"],\
#            ["FIRST FRIDAY OF EACH MONTH","First Friday of each month"],
#            ["LAST WORKING DAY OF A MONTH","Last working day of a month"],\
#            ["LAST WORKING DAY BEFORE","Last Working Day Before"],\
#            ["LAST DAY OF MONTH","Last day of month"],\
#            ["A SPECIFIC DATE OF THE MONTH","A specific date of the month"],\
#            ["LAST MONDAY OF EACH MONTH","Last Monday of each month"],\
#             ["LAST TUESDAY OF EACH MONTH","Last Tuesday of each month"],\
#             ["LAST WEDNESDAY OF EACH MONTH","Last Wednesday of each month"],\
#             ["LAST THURSDAY OF EACH MONTH","Last Thursday of each month"],\
#             ["LAST FRIDAY OF EACH MONTH","Last Friday of each month"],\
#             ['WEEKLY',"Weekly"],\
#             ['TWICE IN A MONTH',"Twice in a month"]
#             ]
    
    emp_payroll_freqs = simplejson.dumps(EMP_PAYROLLFREQ)
    
    cust_county=Address_Info.objects.filter(cust=cust_id).latest('create_date').county
    if request.POST:
        curr_date=datetime.datetime.now()
        employerName = str(request.POST['employerName']) or None
        jobTitle = str(request.POST['jobTitle']) or None
        employerAddress = str(request.POST['employerAddress']) or None
#        monthlyIncome = float(request.POST['monthlyIncome']) or 0
        try:
            monthlyIncome = float(request.POST['monthlyIncome'])
        except ValueError:
            monthlyIncome=0
        try:
            monthlyExpense= float(request.POST['monthlyExpense'])
        except ValueError:
            monthlyExpense=0

        fieldToInformToUI = {}
        fieldToInformToUI['monthlyIncome'] = request.POST['monthlyIncome']
        fieldToInformToUI['payRollFreq'] = request.POST['payRollFreq']
        fieldToInformToUI['monthlyExpense'] = request.POST['monthlyExpense']
        fieldToInformToUI['phone1'] = request.POST['phone1']
        fieldToInformToUI['employerName'] = request.POST['employerName']
        fieldToInformToUI['datum1'] = request.POST['datum1']
        fieldToInformToUI['datum2'] = request.POST['datum2']
        fieldToInformToUI['datum3'] = request.POST['datum3']
        fieldToInformToUI['datum4'] = request.POST['datum4']



        phone1 = str(request.POST['phone1']) or None
        phone2 = str(request.POST['phone2']) or None
        phone3 = str(request.POST['phone3']) or None
        payRollType = str(request.POST['payRollType'])or None
        datum1 = str(request.POST['datum1']) or None
        payRollFreq = str(request.POST['payRollFreq']) or None
        datum2 = str(request.POST['datum2']) or None
        datum3 = str(request.POST['datum3']) or None
        datum4 = str(request.POST['datum4']) or None
        employerPostcode = str(request.POST['postcode']) or None
        v_source1=str(request.POST['v_source1']) or None
        v_source2=str(request.POST['v_source2']) or None
        v_source3=str(request.POST['v_source3']) or None

        if v_source1=='OTHER':
                verified_source1=request.POST['source1_text']
                v_source1="other_"+str(verified_source1)
        if v_source2=='OTHER':
                verified_source2=request.POST['source2_text']
                v_source2="other_"+str(verified_source2)
        if v_source3=='OTHER':
                verified_source3=request.POST['source3_text']
                v_source3="other_"+str(verified_source3)

        Employment_Info.objects.filter(cust=cust_id,override_flag=0).update(override_flag=1,last_updated=str(curr_date))
        emp_data=Employment_Info(employer_name=employerName,\
        employer_addr=employerAddress,\
        employer_postcode=employerPostcode,employer_phone1=phone1,\
        employer_phone2=phone2,employer_phone3=phone3,\
        verified_source1=v_source1,verified_source2=v_source2,\
        verified_source3=v_source3,start_dt=datum1,end_dt=datum2,\
        job_title=jobTitle,payroll_type=payRollType,pay_freq=payRollFreq,\
        monthly_income=monthlyIncome,monthly_expense=monthlyExpense,create_date=curr_date,created_by=username,\
        last_updated=None,modified_by=None,pay_date=datum3,\
        next_paydate=datum4,override_flag=0,cust_id=cust_id)
        emp_data.save()
        repo_data1=Employer_Info_Repo.objects.filter(employer_name=employerName,\
        employer_postcode=employerPostcode,employer_phone=phone1)
        if repo_data1:
           repo_record1=repo_data1.latest('employer_last_verified')
           if repo_record1.employer_verified_source ==v_source1:
               repo_data1.update(employer_last_verified=curr_date)
           else:
               if v_source1:
                   entry1=Employer_Info_Repo(employer_name=employerName,\
                   employer_address=employerAddress,\
                   employer_postcode=employerPostcode,\
                   employer_phone=phone1,\
                   employer_verified_source=v_source1,\
                   employer_last_verified=curr_date)
                   entry1.save()
        else:
                if phone1 is not None and v_source1 is not None :
                    emp_repo1=Employer_Info_Repo(employer_name=employerName,\
                    employer_address=employerAddress,employer_postcode=employerPostcode,\
                    employer_phone=phone1,employer_verified_source=v_source1,\
                    employer_last_verified=curr_date)
                    emp_repo1.save()

        repo_data2=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                          employer_postcode=employerPostcode,employer_phone=phone2,employer_verified_source=v_source2)
        if repo_data2:
            repo_data2.update(employer_last_verified=curr_date)
        else:
                if phone2 is not None and v_source2 is not None:
                    if phone2==phone1 and v_source2 !=v_source1:
                        emp_repo2=Employer_Info_Repo(employer_name=employerName,\
                        employer_address=employerAddress,employer_postcode=employerPostcode,\
                        employer_phone=phone2,employer_verified_source=v_source2,\
                        employer_last_verified=curr_date)
                        emp_repo2.save()
                    if phone2 !=phone1 :
                        emp_repo2=Employer_Info_Repo(employer_name=employerName,\
                        employer_address=employerAddress,employer_postcode=employerPostcode,\
                        employer_phone=phone2,employer_verified_source=v_source2,\
                        employer_last_verified=curr_date)
                        emp_repo2.save()
        repo_data3=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                          employer_postcode=employerPostcode,employer_phone=phone3,employer_verified_source=v_source3)
        if repo_data3:
            repo_data3.update(employer_last_verified=curr_date)
        else:
                if phone3 is not None and v_source3 is not None:
                    if (phone3 ==phone1 and v_source3 != v_source1) or (phone3 ==phone2 and v_source3 != v_source2):
                        emp_repo3=Employer_Info_Repo(employer_name=employerName,\
                        employer_address=employerAddress,employer_postcode=employerPostcode,\
                        employer_phone=phone3,employer_verified_source=v_source3,\
                        employer_last_verified=curr_date)
                        emp_repo3.save()
                    if phone3 !=phone2 and phone3 !=phone1:
                        emp_repo3=Employer_Info_Repo(employer_name=employerName,\
                        employer_address=employerAddress,employer_postcode=employerPostcode,\
                        employer_phone=phone3,employer_verified_source=v_source3,\
                        employer_last_verified=curr_date)
                        emp_repo3.save()
        product_classification = get_product_classification(loan_id)
        if product_classification in ('LOC','INTERIM','LOAN'):

            if fieldToInformToUI:
                keyList = fieldToInformToUI.keys()
                if 'datum3' in keyList:
                    fieldToInformToUI['paydate'] = fieldToInformToUI['datum3']
                    fieldToInformToUI.pop('datum3')
                    
                if 'datum4' in keyList:
                    fieldToInformToUI['next_paydate'] = fieldToInformToUI['datum4']
                    fieldToInformToUI.pop('datum4')
                

                if 'datum1' in keyList:
                    fieldToInformToUI['CustTimeAtEmployer'] = fieldToInformToUI['datum1']
                    fieldToInformToUI.pop('datum1')
                    fieldToInformToUI.pop('datum2')
                '''
                    stDate = datetime.datetime.strptime(fieldToInformToUI['datum1'],'%Y-%m-%d').date()
                
                    if fieldToInformToUI['datum2'] is None or fieldToInformToUI['datum2'] == '':
                        edDate = datetime.datetime.now().date()
                    else:
                        edDate = datetime.datetime.strptime(fieldToInformToUI['datum2'],'%Y-%m-%d').date()
                    fieldToInformToUI['CustTimeAtEmployer'] = (edDate - stDate).days
                    '''
                try:
                    rtiapi.LOC_bank_profile_infoUpdate(loan_id=loan_id,data=fieldToInformToUI,service_code='6103')
                    logger.info("Employer Information update is informed to UI for the Loan Id :: "+str(loan_id))
                except Exception,e:
                    logger.debug("Error in Update for Employer Information to UI for the loan Id :: "+str(loan_id))

                try:
                    rtiInfo = {}                    
                    rtiInfo['newIncome'] = request.POST['monthlyIncome']
                    if request.POST['monthlyExpense']:
                        rtiInfo['newExpenditure'] = request.POST['monthlyExpense']
                    if rtiInfo:
                        rtiInfo['loan_id']          = loan_id
                        logger.info("Sending New Income Expence Info to UE RTI API for the Loan Id :: "+str(loan_id) +"::" +str(rtiInfo))
                        rtiapi.LOC_ChangeIncomeAndExpenditure(rtiInfo)
                except Exception,e:
                    logger.debug("Error in Sending New Income Expence Info to UE RTI API for the Loan Id :: "+str(loan_id) + " :: " + str(e))
                    
            
    return render_to_response('custdetail/employment_popup.html',{'payfreq':payfreq,\
    'payroll':payroll,'cust_county':cust_county,'verified_source':verified_source,"cust_id":cust_id,\
    "loan_id":loan_id,'emp_payroll_freqs':emp_payroll_freqs})
emp_popup = maintenance_deco_popups(emp_popup)

def charge_back_module(request):
    username=request.session['username']
#    status=queueconfig.CB_CODES['CB_status']
    all_status=queueconfig.CB_CODES['CB_status']
    curr_date =  datetime.date.today()
    curr_date_time = datetime.datetime.now()
    selected_post='OPEN'
#    reasons=queueconfig.CB_CODES[selected_post]
    reason=queueconfig.CB_CODES['CB_REASON'][selected_post]
    merchantName = queueconfig.CB_CODES['MerchantName']
#    merchant_id = None

    nxt_status = queueconfig.CB_CODES['NXT_STATUS']
    init_reasons = queueconfig.CB_CODES['CB_REASONS']
    chk_ext_days = 0
    error_msg = None
    status="OPEN"
    key_id = getKeyTranID()
    if request.method == "POST":
        loan_id = request.POST['loan_id']
        if request.POST.has_key("save"):
            try:
                CB_log.info(str(key_id)+ " : Functionality for INSERTing into Charge_Back has started for LoanID :: %s" %(loan_id))
                count = request.POST["rec_count"]
                count = count.split("_")
                count.remove("")
                for node_num in count:
                    db = TranDB(section='TMS_DATA')
                    curs = db.getcursor()
                    cb_raised_on = datetime.datetime.strptime(request.POST['ch_raised'+node_num],"%Y-%m-%d")
                    reason = request.POST['ch_reason'+node_num]
                    cb_reason = request.POST['cb_reason'+node_num]
                    merchant_name = request.POST['ch_merch'+node_num]
                    cb_ref_id = request.POST['ch_ref_id'+node_num]
                    amt = Decimal(request.POST['ch_amt'+node_num])
                    tran_dt = datetime.datetime.strptime(request.POST['tran_dt'+node_num],"%Y-%m-%d")
                    CB_log.info(str(key_id)+ " : Request for processing LoanID : %s sent to ChargeBack" %(loan_id))
                    ch_flag,error_msg = chargeBack.base_chbk(loan_id,amt,tran_dt,merchant_name,cb_raised_on,username,status,
                                                             cb_ref_id=cb_ref_id,reason=reason,key_id=key_id,db = db,curs = curs,cb_reason=cb_reason)
                    if not ch_flag:
                        CB_log.debug(str(key_id)+ " : Failed to INSERT the transaction for LoanID :: %s" %(loan_id))
            except Exception:
                db.rollback()
                db.close()
                error_msg = "Internal error while processing the transaction. Try later"
        elif request.POST.has_key("update"):
            try:
                CB_log.info(str(key_id)+ " : UPDATE existing CB record functionality started for LoanID :: %s" %(loan_id))
                to_final_freeze = 1
                openflag = 0
                loan_to_freeze = 1
                cb_id_list = []
                status_dict = {}
                reason_dict = {}
                extended_days = {}
                cb_list = request.POST['upd_list'].split(',')
                if cb_list[0] != '':
                    for elem in cb_list:
                        val = elem.split('~')
                        cb_id_list.append(val[0])
                        status_dict[val[0]] = val[1]
                        reason_dict[val[0]] = val[2]
                        extended_days[val[0]] = val[3]
                    '''
                    Below query checks whether any Charge Back transaction is in OPEN / CONVERSED state.
                    If yes, no unfreeze logic takes place else, unfreeze logic is applied only if value of flag loan_to_freeze = 1.
                    '''
                    tmsconn = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
                    check_opencb = "select * from Charge_Back where loan_id = %s and override_flag =0 and charge_back_id not in (%s) \
                            and status in ('OPEN','CONVERSED') "%(loan_id,','.join (str(cbi) for cbi in cb_id_list))
                    res_check_opencb = tmsconn.get_all_results(check_opencb)
                    if res_check_opencb or [st for st in status_dict.values() if st in ('OPEN', 'CONVERSED')]:
                        openflag = 1
                    for elem in cb_id_list:
                        charge_back=Charge_Back.objects.filter(loan=loan_id,override_flag = 0)
                        curr_val = [cb_val for cb_val in charge_back if int(elem) == cb_val.charge_back_id]
                        if curr_val[0].status == status_dict[elem] and curr_val[0].reason == str(reason_dict[elem]):
                            continue
                        else:
                            if status_dict[elem] == 'SETTLED':
                                '''
                                If the customer or lender accepts the mistake then we make deal with customer and then unfreeze the loan.
                                '''
                                if (((reason_dict[elem].upper().split('_')[0]) == "CUSTOMER ACCEPTED") or
                                    ((reason_dict[elem].upper().split('_')[0]) == "LENDER ACCEPTED")):
                                    if not openflag and loan_to_freeze:
                                        try:
                                            sql="select freeze_flag,arrangement_type,product_classification,due_amt,status_sup_reason,delin_sup_reason,mpc_sup_reason from TMS_Data.Payments ps join TMS_Data.Loan ln using(loan_id) join TMS_Data.Product pr using(product_id) where loan_id='%s'"%(loan_id)
                                            fre_flag=tmsconn.get_one_result(sql)
                                            if fre_flag['freeze_flag']:
                                                #Fetches the earlier status from gcm_case_log table
                                                old_status,case_id = getoldstatusfromlog(loan_id)

                                                #Updates the tran DB with the older status obtained above
                                                trandbupdateGCMCase(case_id,0,0,status_cd = old_status,done_by = username,date_elem = curr_date_time)
                                                reason=pcconfig.FEE_UNSUP_REASON['SETLD']

                                                if fre_flag['product_classification']=='LOC':
#                                                     status_sup=delin_sup=mpc_sup=None
#                                                     if fre_flag['status_sup_reason'] in ('CHARGE BACK','CONVERSED with Customer'):
#                                                         status_sup=-1
#                                                     if fre_flag['delin_sup_reason'] in ('CHARGE BACK','CONVERSED with Customer'):
#                                                         delin_sup=-1
#                                                     if fre_flag['mpc_sup_reason'] in ('CHARGE BACK','CONVERSED with Customer'):
#                                                         mpc_sup=-1

                                                    if not fre_flag['due_amt'] or fre_flag['arrangement_type']:   #if already arrangement is set, simply unfreeze
                                                        to_final_freeze = pcfunc.manualsuppress(loan_id=loan_id,user=username,freeze_sup=-1,freeze_till_date=None,
                                                                    freeze_from_date=None,freeze_sup_reason=reason)
                                                    else:
                                                        #get the upcoming duedate and give communication freeze till due date-1
                                                        cfreason=pcconfig.ARR_REASON['CF']
                                                        cf_sql="select paydate,date_add(paydate,interval -1 day) as cf_date from PayDates where loan_id='%s' and payment_type='LNCYC' and override_flag=0 and paydate>=curdate() order by paydate limit 1"%(loan_id)
                                                        cf_res=tmsconn.get_one_result(cf_sql)
                                                        if cf_res['cf_date'] and cf_res['cf_date']>=curr_date:    #if comm_freeze date is get than or equal to cur date
                                                            payments_obj = pcfactory.getpmobj('TMS_DATA')
#                                                              freeze_msg = pcfunc.manualsuppress(loan_id=loan_id,user=username,freeze_sup=-1,freeze_till_date=None,
#                                                                     freeze_from_date=None,freeze_sup_reason=reason,)
                                                            to_final_freeze = payments_obj.generalsuppress(loan_id=loan_id,user=username,freeze_sup=-1,freeze_till_date=None,
                                                                                                           freeze_from_date=None,freeze_sup_reason=reason,status_sup=1,delin_sup=1,mpc_sup=1,arr_sup=1,fee_sup=1,\
                                                                                                           mpc_suppress_tilldate=cf_res['paydate'],delin_suppress_tilldate=cf_res['paydate'],status_suppress_tilldate=cf_res['paydate'],fees_suppress_tilldate=cf_res['paydate'],\
                                                                                                           arrangement_till_date=cf_res['cf_date'],arrangement_sup_reason=cfreason,status_sup_reason=cfreason,delin_sup_reason=cfreason,mpc_sup_reason=cfreason,accrual_sup_reason=cfreason)
                                                            payments_obj.db.commit()
                                                            payments_obj.db.close()
                                                        elif cf_res['cf_date'] and cf_res['cf_date']<curr_date: #comm_freeze date less than current day, simply unfreeze
                                                            to_final_freeze = pcfunc.manualsuppress(loan_id=loan_id,user=username,freeze_sup=-1,status_sup=-1,delin_sup=-1,mpc_sup=-1,freeze_till_date=None,
                                                                    freeze_from_date=None,freeze_sup_reason=reason)
                                                #don't do anything if u dont find any date
                                                else:
                                                    #Calls the unfreeze module. Updates payment table and customers schedule
                                                    to_final_freeze = factory(0,date=curr_date,loan_id=loan_id,reason=reason)

                                                if to_final_freeze:
                                                    loan_to_freeze = 0
                                                    CB_log.info(str(key_id)+ " : Successfully updated the defened CB for LoanID :: %s" %(loan_id))
                                                else:
                                                    CB_log.info(str(key_id)+ " : Failed to update the defened CB for LoanID :: %s" %(loan_id))
                                        except:
                                            to_final_freeze = 0
                                            CB_log.info(str(key_id)+ " : %s ChargeBack failed for LoanID :: %s and the error is \n"+str(traceback.format_exc()) %(status_dict[elem],loan_id))
                                elif reason_dict[elem].upper() in queueconfig.CB_CODES['EXCLUDE_ALERT_LIST']:
                                    error_msg = "Change the status to POTENTIAL FRAUD, if not CHANGED"
                                    pass

                            elif status_dict[elem] == 'CONVERSED':
                                '''
                                If customer contacted with in 7 days from freeze date, and requested for an extension then we extend
                                the freeze date to a maximum of 7 days. If failed to get back then mail the loan gets moved to recoveries.
                                '''
                                conn = mysqldbwrapper.MySQLWrapper(configfile, 'TMS_DATA')
                                fzdates = conn.get_one_result(query="select freeze_from_date,freeze_till_date,mpc_suppress_tilldate,delin_suppress_tilldate,status_suppress_tilldate,product_classification from TMS_Data.Payments ps join TMS_Data.Loan ln using(loan_id) join TMS_Data.Product pr using(product_id) where loan_id=%s",args=loan_id)
#______________________________________R5 changes______________________________________
                                mpc_suppress_tilldate=None
                                delin_suppress_tilldate=None
                                status_suppress_tilldate=None
                                status_sup=delin_sup=mpc_sup=None
                                delin_sup_reason=mpc_sup_reason=status_sup_reason=None
#____________________________________________________________________________________________--
                                if fzdates['freeze_till_date'] and fzdates['freeze_from_date']:
                                    dfdate = (fzdates['freeze_till_date'] - fzdates['freeze_from_date']).days
                                if dfdate <= 7 and extended_days[elem]>0:
                                    Ext_dt = fzdates['freeze_till_date'] + timedelta(days=int(extended_days[elem]))

                                    if fzdates['product_classification'] =='LOC':
                                        if not fzdates['mpc_suppress_tilldate'] or fzdates['mpc_suppress_tilldate'] and fzdates['mpc_suppress_tilldate']<Ext_dt:
                                            mpc_suppress_tilldate=Ext_dt
                                            mpc_sup=1
                                            mpc_sup_reason='CONVERSED with Customer'
                                        if not fzdates['delin_suppress_tilldate'] or fzdates['delin_suppress_tilldate'] and fzdates['delin_suppress_tilldate']<Ext_dt:
                                            delin_suppress_tilldate=Ext_dt
                                            delin_sup=1
                                            delin_sup_reason='CONVERSED with Customer'
                                        if not fzdates['status_suppress_tilldate'] or fzdates['status_suppress_tilldate'] and fzdates['status_suppress_tilldate']<Ext_dt:
                                            status_suppress_tilldate=Ext_dt
                                            status_sup=1
                                            status_sup_reason='CONVERSED with Customer'
                                    freeze_msg = pcfunc.manualsuppress(loan_id=loan_id,user=username,freeze_sup=1,freeze_till_date=Ext_dt,status_sup=status_sup,delin_sup=delin_sup,mpc_sup=mpc_sup,
                                                                       mpc_suppress_tilldate=mpc_suppress_tilldate,freeze_from_date=fzdates['freeze_from_date'],delin_suppress_tilldate=delin_suppress_tilldate,
                                                                       status_suppress_tilldate=status_suppress_tilldate,freeze_sup_reason='CONVERSED with Customer',
                                                                       delin_sup_reason=delin_sup_reason,mpc_sup_reason=mpc_sup_reason,status_sup_reason=status_sup_reason)
                                    if "successfully" in freeze_msg:
                                        update_cb = "update TMS_Data.Charge_Back set extended_till_date=%s where charge_back_id=%s and override_flag=0"
                                        conn.execute(query=update_cb,args=(Ext_dt,elem))
                                    else:
                                        error_msg = "Internal Error in Extending the Date for Customer. Contact Backend Team"
                                if reason_dict[elem].upper() in queueconfig.CB_CODES['EXCLUDE_ALERT_LIST']:
                                    error_msg = "Change the status to SETTLED, after setting a PAYMENT PLAN"
                            if to_final_freeze:
                                '''
                                Inserts into chargeback table the latest updated status of charge back transaction under LOAN.
                                '''
                                current_dt = datetime.datetime.now()
                                chargeBack.insertIntoChargeBack(loan_id,curr_val[0].order_id,curr_val[0].match_flag,curr_val[0].cb_raised_on,curr_val[0].cb_amount,curr_val[0].tran_dt,
                                            curr_val[0].merchant_name,status_dict[elem],reason_dict[elem],username,cur_date=current_dt,
                                            cb_transaction_id=curr_val[0].cb_transaction_id,transaction_id=curr_val[0].
                                            transaction_id,cb_id=curr_val[0].charge_back_id,cb_reason=curr_val[0].cb_reason, DCA_Name = curr_val[0].dca_name)
                                CB_log.info(str(key_id)+ " : %s ChargeBack based on CC input for LoanID :: %s" %(status_dict[elem],loan_id))
                            else:
                                error_msg = "Internal Error while closing chargeback. Contact Backend Team"
            except Exception:
                error_msg = "Internal error while updating the transaction. Try later"
    else:
        loan_id = request.GET['loan_id']
    view_conn = mysqldbwrapper.MySQLWrapper(configfile,'TMS_DATA')
    view_ch_query = "select * from TMS_Data.Charge_Back where loan_id=%s and override_flag=0"
    view_chbk_args = loan_id
    fzdates2 = view_conn.get_one_result(query="select freeze_from_date,freeze_till_date, freeze_sup_reason from TMS_Data.Payments where loan_id=%s",args=loan_id)
    freeze_dt = fzdates2['freeze_till_date']
    if fzdates2['freeze_till_date'] and fzdates2['freeze_from_date'] and fzdates2['freeze_sup_reason'] in ("CHARGE BACK","CONVERSED with Customer"):
        dfdate2 = (fzdates2['freeze_till_date'] - fzdates2['freeze_from_date']).days - 7
        if dfdate2 > 0:
            chk_ext_days = 1
        else:
            chk_ext_days = 0
    else:
        chk_ext_days = 0
    charge_back = view_conn.get_all_results(query=view_ch_query, args=view_chbk_args)
#    transactions = view_conn.get_all_results(query=view_tran_query, args=view_tran_args)
    open_reasons = queueconfig.CB_CODES['CB_REASON']['OPEN']
    conversed_reasons = queueconfig.CB_CODES['CB_REASON']['CONVERSED']
    settled_reasons = queueconfig.CB_CODES['CB_REASON']['SETTLED']
    defended_reasons = queueconfig.CB_CODES['CB_REASON']['DEFENDED']
    not_defended_reasons = queueconfig.CB_CODES['CB_REASON']['NOT DEFENDED']
#    open_reasons = queueconfig.CB_CODES['OPEN']
#    extended_reasons = queueconfig.CB_CODES['EXTENDED']
#    closed_reasons = queueconfig.CB_CODES['CLOSED']
    tran_par = []
    cb_tran = [elem['cb_transaction_id'] for elem in charge_back]
#    n = 0
#    for elem in transactions:
#        tran_par.append(elem)
#        if elem['transaction_id'] in cb_tran:
#            tran_par[n]['flag']='true'
#        else:
#            tran_par[n]['flag']=None
#        n = n+1
    payments=Payments.objects.filter(loan=loan_id)[0]
#    return render_to_response('custdetail/charge_back_rough.html',{"loan_id":loan_id,"charge_back":charge_back,'status':status,'payments':payments,\
#                'reasons':reasons,'selected_post':selected_post,'open_reasons':open_reasons,'extended_reasons':extended_reasons,\
#                'closed_reasons':closed_reasons,"transactions":tran_par,"cb_tran":cb_tran,"error_msg":error_msg,'merchantName':merchantName})
    return render_to_response('custdetail/charge_back_rough.html',{"loan_id":loan_id,"charge_back":charge_back,'all_status':all_status,'payments':payments,\
                'reason':reason,'selected_post':selected_post,'open_reasons':open_reasons,'settled_reasons':settled_reasons,\
                'conversed_reasons':conversed_reasons,'defended_reasons':defended_reasons,\
                'not_defended_reasons':not_defended_reasons,'transactions':tran_par,"cb_tran":cb_tran,"error_msg":error_msg,\
                'merchantName':merchantName,'nxt_status':nxt_status,'init_reasons':init_reasons,'chk_ext_days':chk_ext_days,'freeze_dt':freeze_dt})

def sup_popup(request):
    """
    This will pop-up a window through which supressing can be done.
    """
    suppress_dict = {}
    msg = ""
    error_msg = ""
    warn_msg = ""
    loan_id = ""
    cur_date = datetime.datetime.now()
    username=request.session['username']
    suppress_reasons={}
    suppress_records={}

    formDict = {}
    if request.is_ajax():
         if request.POST.has_key('selected'):             
             if request.POST['selected']=='Un-Suppress':             
                 suppress_reasons=['SELECT OR DO NOTHING','RETURNED','DID NOT APPLY FOR LOAN','CROSSED SUPPRESS TILL DATE','WITHDRAWAL']
             else:
                 suppress_reasons=['SELECT OR DO NOTHING','RECOVERIES','CARD LOST','LOST JOB','CARD EXPIRED',\
                'TRUST DEED','STATUTE-BARRED','SOLD','DISPUTE','DEBT RELIEF ORDER','IVA','POTENTIAL FRAUD','TERMINATED',\
                 'SALARY NOT CREDITED','CARD BLOCKED','NO BALANACE IN CARD','CARD  NOT IN USE','DEFAULTED','BANKRUPTCY'\
                 'FRAUD','WRITE OFF','DC CHARGE BACK','DEBT MANAGEMENT','CLOSED','RETURNED','CPA WITHDRAWAL','']
             return HttpResponse(simplejson.dumps({'suppress_reasons':suppress_reasons}))

    if request.method=='GET':
        if "loan_id" in request.GET:
            loan_id = request.GET['loan_id']
        if "message" in request.GET:
            msg = request.GET['message']
        if "error_msg" in request.GET:
            error_msg = request.GET['error_msg']
        if "warn_msg" in request.GET:
            warn_msg = request.GET['warn_msg']
    elif request.method=='POST':
        if "loan_id" in request.POST:
           loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    if loan_id == "":
        return HttpResponse('Loan ID is Missing check with Back End Team!')

#    sup_type = ['PrnSup','IntSup','FeesSup','waterfallSup']
    sup_type = ['waterfallSup']
    allow_suppress_waterfall = '1'
    if  datetime.datetime.now().time()>datetime.time(22,0):
        run_date=datetime.datetime.today().date()+datetime.timedelta(days=1)
        tmsconn = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        query1="select * from dailyrun where date_of_run= '%s' and script_name='UPDATE_SUPP' and prev_run_started_at is not NULL limit 1"%(run_date)
        result=tmsconn.get_one_result(query1)
        if result:
            allow_suppress_waterfall='0'
    for item in sup_type:
         suppress_records.update({item:{item:0,item+'TillDate':None,item+'Reason':None}})
         formDict.update({item:{item:0,item+'TillDate':None,item+'Reason':None}})

    tms_con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    sql = "select loan_id,generate_flag,accrual_sup_reason,suppress_flag,suppress_till_date,wat_sup_reason from Payments where loan_id = %s"%(loan_id)
    sup_result = tms_con.get_one_result(sql)

    if sup_result:
#        if sup_result['generate_flag'] in (4,5,6,7):
#           suppress_records['FeesSup']['FeesSup'] = 1
#           suppress_records['FeesSup']['FeesSupReason'] = sup_result['accrual_sup_reason']
#           suppress_records['FeesSup']['FeesSupTillDate'] = sup_result['fee_suppress_till_date']
#        else:
#           suppress_records['FeesSup']['FeesSup'] = -1
#           suppress_records['FeesSup']['FeesSupReason'] = sup_result['accrual_sup_reason']
#
#        if sup_result['generate_flag'] in (2,3,6,7):
#           suppress_records['IntSup']['IntSup'] = 1
#           suppress_records['IntSup']['IntSupReason'] = sup_result['accrual_sup_reason']
#        else:
#           suppress_records['IntSup']['IntSup'] = -1
#           suppress_records['IntSup']['IntSupReason'] = sup_result['accrual_sup_reason']
#
#        if sup_result['generate_flag'] in (1,3,5,7):
#           suppress_records['PrnSup']['PrnSup'] = 1
#           suppress_records['PrnSup']['PrnSupReason'] = sup_result['accrual_sup_reason']
#        else:
#           suppress_records['PrnSup']['PrnSup'] = -1
#           suppress_records['PrnSup']['PrnSupReason'] = sup_result['accrual_sup_reason']

        if sup_result['suppress_flag']==1:
           suppress_records['waterfallSup']['waterfallSup'] = 1
           suppress_records['waterfallSup']['waterfallSupReason'] = sup_result['wat_sup_reason']
           suppress_records['waterfallSup']['waterfallSupTillDate'] = sup_result['suppress_till_date']
        else:
           suppress_records['waterfallSup']['waterfallSup'] = -1
           suppress_records['waterfallSup']['waterfallSupReason'] = sup_result['wat_sup_reason']

    if request.method == 'POST':   

        for key,value in formDict.iteritems():

          if key in request.POST:
            if request.POST[key] == "Un-Suppress":
                formDict[key][key] = -1
                if key+'Reason' in request.POST and request.POST[key+'Reason'] != 'SELECT OR DO NOTHING':
                    formDict[key][key+'Reason'] = request.POST[key+'Reason']
            else:
                formDict[key][key] = 1
                if key+'Reason' in request.POST and request.POST[key+'Reason'] != 'SELECT OR DO NOTHING':
                    formDict[key][key+'Reason'] = request.POST[key+'Reason']
                if key+'TillDate' in request.POST:
                    if request.POST[key+'TillDate'] == '':
                       request.POST[key+'TillDate'] = None
                    else:
                       formDict[key][key+'TillDate'] = dates.toDate(request.POST[key+'TillDate'])


        if suppress_records == formDict:
            return HttpResponseRedirect('/info/sup_popup/?loan_id=%s&message=%s'%(loan_id,'No Changes Made'))

        for key,value in formDict.iteritems():
            suppress_dict.update(value)

#        rtmsg = pcfunc.manualsuppress(loan_id,prn_sup=suppress_dict['PrnSup'],
#                                                      int_sup=suppress_dict['IntSup'],
#                                                      fee_sup=suppress_dict['FeesSup'],
#                                                      fee_suppress_till_date=suppress_dict['FeesSupTillDate'],
#                                                      wat_sup=suppress_dict['waterfallSup'],
#                                                      wat_sup_tilldate=suppress_dict['waterfallSupTillDate'],
#                                                      wat_sup_reason=suppress_dict['waterfallSupReason'],
#                                                      accrual_sup_reason = suppress_dict['FeesSupReason'],
#                                                      user=username,date_elem=cur_date)
        rtmsg = pcfunc.manualsuppress(loan_id,wat_sup=suppress_dict['waterfallSup'],
                                                      wat_sup_tilldate=suppress_dict['waterfallSupTillDate'],
                                                      wat_sup_reason=suppress_dict['waterfallSupReason'],
                                                      user=username,date_elem=cur_date)

        if rtmsg == "Suppress/Un-Suppress updated successfully":
           msg = "Suppress/Un-Suppress informations updated successfully "
        else:
           error_msg = "Error has occured while updations"

        return HttpResponseRedirect('/info/sup_popup/?loan_id=%s&message=%s&error_msg=%s&warn_msg=%s'%(loan_id,msg,error_msg,warn_msg))
    else:
       if suppress_records['waterfallSup']['waterfallSup']== -1:
          suppress_reasons ={'RETURNED':'RETURNED','DID NOT APPLY FOR LOAN':'DID NOT APPLY FOR LOAN',\
                            'CROSSED SUPPRESS TILL DATE':'CROSSED SUPPRESS TILL DATE','WITHDRAWAL':'WITHDRAWAL'}
       else:
         suppress_reasons ={'RECOVERIES':'RECOVERIES','CARD LOST':'CARD LOST','LOST JOB':'LOST JOB','CARD EXPIRED':'CARD EXPIRED','SALARY NOT CREDITED':'SALARY NOT CREDITED','CARD BLOCKED':'CARD BLOCKED',\
         'NO BALANCE IN CARD':'NO BALANCE IN CARD','CARD NOT IN USE':'CARD NOT IN USE','FRAUD':'FRAUD','WRITE OFF':'WRITE OFF','DEBT MANAGEMENT':'DEBT MANAGEMENT',\
         'DEFAULTED':'DEFAULTED','BANKRUPTCY':'BANKRUPTCY','CLOSED':'CLOSED','POTENTIAL FRAUD':'POTENTIAL FRAUD','TERMINATED':'TERMINATED',
         'TRUST DEED':'TRUST DEED','DC CHARGE BACK':'DC CHARGE BACK','STATUTE-BARRED':'STATUTE-BARRED','SOLD':'SOLD','DISPUTE':'DISPUTE','DEBT RELIEF ORDER':'DEBT RELIEF ORDER','IVA':'IVA','CPA WITHDRAWAL':'CPA WITHDRAWAL'}
       return render_to_response('custdetail/supress_popup.html',
   {'loan_id':loan_id,'suppress_records':suppress_records,
   'message':msg,'error_msg':error_msg,'warn_msg':warn_msg,'suppress_reasons':suppress_reasons,'serv_date':cur_date.date().strftime("%Y-%m-%d"),'allow_suppress_waterfall':allow_suppress_waterfall})
sup_popup = maintenance_deco_popups(sup_popup)


def ref_popup(request):
    """
    This will pop-up a window through which new reference record could be added.
    """
    #print "I CAME TO POPUP"
    if request.method=='GET':
        customer_id = request.GET['cust_id']
    if request.method=='POST':
        customer_id = request.POST['cust_id']
        #print "YOU CLICKED UPDATE BUTTON"
        first_name = request.POST['first_name']or None
        middle_name = request.POST['middle_name']or None
        last_name = request.POST['last_name']or None
        address = request.POST['address']or None
        phone_no = request.POST['phone_no']or None
        dnc=request.POST['dnc1']or None
        ref_rel=request.POST['ref_relation1']or None
        ref_postcode=request.POST['postcode']or None
        if dnc is not None:
            if dnc=='0':
                dnc_value=False
            if dnc=='1':
                dnc_value=True
        else:
            dnc_value=False
        ref_info = Reference_Info(first_name=first_name, \
            middle_name=middle_name, last_name=last_name, \
            address=address, phone_no=phone_no,cust_id=customer_id,create_date=\
            datetime.datetime.now(),DNC_flag=dnc_value,ref_relation=ref_rel,\
            override_flag=False,postcode=ref_postcode)
        ref_info.save()
    if request.method=='GET':
        print "HI"
    return render_to_response('custdetail/reference_popup.html',{'cust_id':customer_id})
ref_popup = maintenance_deco_popups(ref_popup)
def fetch_all_bank_result(cust_id):
    results=get_all_BankAccount_Info(cust_id)
    complete_record=[]
    for result in results:
        account_record=[]
        bank_name_list=[]
        if result[1]:
            bank_detail=search_Bank_Info_Repo(result[1])
            account_record.append(decrypt_data(result[3]))
            account_record.append(result[1])
            account_record.append(result[5])
            account_record.append(bank_detail['bank_name'])
            account_record.append(bank_detail['branch_address'])
            account_record.append(bank_detail['branch_phone'])
            account_record.append(result[4])
            account_record.append(bank_detail['branch_postcode'])
            account_record.append(result[2])
            account_record.append(bank_detail['branch_name'])
            account_record.append(result[6])
            complete_record.append(account_record)
    return complete_record

def viewhistory(request):
    """
    This will pop-up a window through which past history details could be
    viewed.
    """
    loan_id = ""
    cust_id = ""
    if request.method=='GET':
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        cust_id = request.POST['cust_id']


    headerlist = []
    datalist = []
    address_info=""
    emp_info=""
    id=""
    Pemail_info=""
    Oemail_info=""
#    Hphone_info=""
#    Wphone_info=""
#    Mphone_info=""
#    Ophone_info=""
    Phone_details=""
    title=""
    info = []
    if request.GET:
        id = request.GET['id']
        if id == 'contact':
            headerlist=['Apartment No', 'Building No', 'Building Name', 'Home Status', 'Start Date', 'End Date', 'Street1' ,'Street2',
                        'locality', 'County', 'City', 'Town','Postcode','Country','Modified Date']
            info=Address_Info.objects.filter(cust=cust_id, override_flag=1).order_by("-create_date")
            Pemail_info = Email_Info.objects.filter(cust=cust_id,email_type='PERSONAL', override_flag=1).order_by("-create_date")
            Oemail_info = Email_Info.objects.filter(cust=cust_id,email_type='OFFICIAL', override_flag=1).order_by("-create_date")
            Phone_details=Phone_Info.objects.filter(cust=cust_id,override_flag=1).order_by("-last_updated")



            title="Contact Information"

        if id == 'bank':

            headerlist=['Account Number','Routing Number','Swift Code','Bank Name','Bank Address','Bank Phone','Account Type','Bank Postcode','Account Name','Branch Name','Modified Date']

            info=fetch_all_bank_result(cust_id)
            title="Bank Information"

        if id == 'emp':
            headerlist=['Employer\'s Name','Employer\'s Address','Employer\'s Postcode',\
                        'Phone Number1',' Verified Source1' ,\
                        'Phone Number2',' Verified Source2' ,\
                        'Phone Number3',' Verified Source3' ,\
                        'Start Date','End Date','Job Title','Monthly Income','Monthly Expense','Payroll Type',\
                        'Payroll Frequency','Pay Date','Next PayDate','Modified Date']
            info=Employment_Info.objects.filter(cust=cust_id,override_flag=1).order_by('-employment_id')
            title="Employer Information"

        elif id == 'ref':
            headerlist=['First Name','Middle Name','Last Name','Phone Number','Address','Reference Relation','Postcode',"Modified Date"]
            info = Reference_Info.objects.filter(cust=cust_id,override_flag=1).order_by("-create_date")

            title="Reference Information"

        elif id == 'chq':
            headerlist=['Cheque Number','Cheque Amount','Receive Date','Clear Date','Bounce Flag']
            info = Cheque.objects.all()
            title= 'Cheque/Direct Deposits'
        elif id=='customer':
            headerlist=["Prefix","First Name","Middle Name","Last Name","Suffix","Gender","DOB","National ID","Employment Status","Marital Status","Number of Dependents","Mother's Maiden Name","Modified Date"]
            info=Customer_Basic_Info.objects.filter(cust=cust_id,override_flag=1).order_by("-create_date")
            title= 'Customer Basic Information'
        elif id=='card':
            if request.method=="POST":
                loan_id = request.POST['loan_id']
            elif request.method=="GET":
                loan_id = request.GET['loan_id']
            sql_pri=Ext_Bureau_Info.objects.filter(loan=loan_id, override_flag=0).exclude(bureau_name="PDC").order_by("-create_dt")
            sql_sec=Ext_Bureau_Info.objects.filter(loan=loan_id, override_flag=0).exclude(bureau_name="PDC").order_by("-create_dt")
            if sql_pri:
                sql="select * from TMS_Data.Ext_Bureau_Info where loan_id='%s' and bureau_name!='PDC' and override_flag=1"%(loan_id)
            elif sql_sec and len(sql_sec)>1:
                sql="select * from TMS_Data.Ext_Bureau_Info where loan_id='%s' and bureau_name!='PDC' and override_flag=1 and ext_bureau_info_id!=%s"%(loan_id,sql_sec.ext_bureau_info_id)
            else:
                sql=''
            if sql:
                info = get_card_list_withbintail(loan_id,sql_ext=sql)
            else:
                info=()
#            info=Ext_Bureau_Info.objects.filter(loan=loan_id,\
#                    override_flag=1).exclude(bureau_name="PDC").order_by("-create_dt")
            title='Card Details'

    return render_to_response('custdetail/history.html', \
        {'sessionobject':request.session, 'headerlist':headerlist, \
        'info':info,'id':id,'Pemail_info':Pemail_info,'Oemail_info':Oemail_info,\
        'title':title,'Phone_details':Phone_details,'loan_id':loan_id,"cust_id":cust_id})

viewhistory = maintenance_deco_popups(viewhistory)
def personal_detail(request):
    """
    This renders iframe for Personal Detail where Customer's Personal information\
    can be viewed and also edited.
    """
    marital_status = [["SINGLE","Single"],["MARRIED","Married"],
                      ["DIVORCED","Divorced"],["SEPARATED","Separated"],["WIDOWED","Widowed"],
                    ["COMMON LAW/PARTNER","Common Law/Partner"],["LIVING TOGETHER","Living Together"],
                    ["OTHERS","Others"]]
    emp_stat=[['FULL TIME','Full Time Employment'],['PART TIME','Part Time'],
    ['DIRECTOR','Director'],['SUB-CONTRACTOR','Sub-contractor'],
    ['SELF-EMPLOYED','Self-Employed'],['TEMPORARY','Temporary'],['ON BENEFITS','On Benefits'],
    ['UNEMPLOYED','Unemployed'],['RETIRED','Retired'],['STUDENT','Student'],['HOME MAKER','Home Maker']]
    
    selected_ques=''
    answer_obj=''
    answer=''
    flag=0
    questionlist=[]
    selected_ques_id=''
    questions=MasterQuestionList.objects.all()
    cust_id=''
    loan_id=''
    captureUIField = {}
    if 'username' in request.session:
        username = request.session['username']
        
    if request.method=='GET':
        cust_id=request.GET['cust_id']
        loanid = request.GET['loan_id']
        customer_id = Customer.objects.filter(cust_id=str(cust_id))
        test_obj=CustomerSecurityQuestion.objects.filter(cust=cust_id)

        if test_obj:
            answer_obj=CustomerSecurityQuestion.objects.filter(cust=cust_id).latest('create_date')
        if answer_obj:
            flag=1
            answer=answer_obj.answer
            selected_ques_id=answer_obj.question_id
            selected_ques=MasterQuestionList.objects.filter(question_id=selected_ques_id)[0].question_text
            selected_ques_id=answer_obj.question_id
            for question in questions:
                if question.question_id !=answer_obj.question_id:
                    tuple1=((question.question_id),(question.question_text))
                    questionlist.append(tuple1)
        else:
            flag=0
            for question in questions:
                tuple1=((question.question_id),(question.question_text))
                questionlist.append(tuple1)
                selected_ques_id=''

    if request.method == 'POST':
        curr_date=datetime.datetime.now()
        cust_id=request.POST['cust_id']
        loanid = request.POST['loan_id']
        Tprefix= request.POST['prefix'] or None
        Tfirstname = request.POST['firstname'] or None
        Tmiddlename = request.POST['middlename'] or None
        Tlastname = request.POST['lastname'] or None
        Tsuffix = request.POST['suffix'] or None
        Tgender = request.POST['gender'] or None
        TDOB = request.POST['datum1'] or None
        Tnationalid = request.POST['nationalid'] or None
        Temploymentstatus = request.POST['employmentstatus'] or None
        Tmaritalstatus = request.POST['maritalstatus'] or None
        Tnoofdependents = request.POST['noofdependents']
        Tmaidname = request.POST['maidname'] or None
        question_id1=request.POST['security_question'] or None
        answer1=request.POST['answer'] or None
        updateUI = eval(request.POST['updateUI'])
        
        
        for val in updateUI.keys():
            if updateUI[val] == request.POST[val]:
                updateUI.pop(val)
            else:
                updateUI[val] = request.POST[val]
                
        logger.info("Personal Information Dict Need to UI :: "+str(updateUI))
        #only when questionid1 and answer1 is present in POST request
        if question_id1 and answer1:
            custsecurityques=CustomerSecurityQuestion.objects.filter(cust=cust_id,override_flag=0)
            #if records already present in the table CustomerSecurityQuestion, check and insert
            if custsecurityques:
                if(question_id1 !=custsecurityques[0].question_id) and (answer1!=custsecurityques[0].answer):
                    db_entry=CustomerSecurityQuestion(question_id=question_id1,answer=answer1,create_date=\
                    curr_date,override_flag=flag,cust_id=cust_id)
                    db_entry.save()
            #if records already not present in the table CustomerSecurityQuestion, just insert
            else:
                db_entry=CustomerSecurityQuestion(question_id=question_id1,answer=answer1,create_date=\
                curr_date,override_flag=flag,cust_id=cust_id)
                db_entry.save()


        personalinfo = Customer_Basic_Info.objects.filter(cust=cust_id,override_flag=0)[0]

        if  Tnoofdependents:
               Tnoofdependents= (int(Tnoofdependents))

        else:
            Tnoofdependents=None

        if personalinfo.no_of_dependents:
            no_of_dependents=(int(personalinfo.no_of_dependents))
        else:
            no_of_dependents=personalinfo.no_of_dependents
        #data coming into the db can be in uppercase
        emp_status1=personalinfo.emp_status
        marital_status1=personalinfo.marital_status
        if Temploymentstatus:
            Temploymentstatus_test=Temploymentstatus.lower()
        else:
            Temploymentstatus_test=Temploymentstatus
        if emp_status1:
            emp_status_test=emp_status1.lower()
        else:
            emp_status_test=emp_status1
        if Tmaritalstatus:
            Tmaritalstatus_test=Tmaritalstatus.lower()
        else:
            Tmaritalstatus_test=Tmaritalstatus
        if marital_status1:
            marital_status_test=marital_status1.lower()
        else:
            marital_status_test=marital_status1

        if (Tprefix != personalinfo.prefix) or \
            (Tfirstname != personalinfo.first_name) or \
            (Tmiddlename != personalinfo.middle_name) or \
            (Tlastname != personalinfo.last_name) or \
            (Tsuffix != personalinfo.suffix) or \
            (Tgender != personalinfo.gender) or \
            (Tnationalid != personalinfo.decrypt_national_id()) or \
            (Temploymentstatus_test != emp_status_test) or \
            (Tmaritalstatus_test != marital_status_test) or \
            (Tnoofdependents != no_of_dependents) or \
            (str(TDOB) != str(personalinfo.decrypt_dob())) or \
            (Tmaidname != personalinfo.mothers_maiden_name):

            personalinfoadd=1
#            set override_flag=1 in customer_basic_info
            Customer_Basic_Info.objects.filter(customer_basic_info_id=personalinfo.customer_basic_info_id).update(override_flag=1,last_updated=str(curr_date),modified_by=username)
            if (Tfirstname != personalinfo.first_name) or \
               (Tmiddlename != personalinfo.middle_name) or \
               (Tlastname != personalinfo.last_name):
                conn = TranDB(section="TMS_DATA")
                curs = conn.getcursor()
                try:
                    query = "update Waterfall_Loan_Latest set first_name = %s,\
                    middle_name = %s,last_name =%s,modified_date = %s,\
                    modified_by = %s where cust_id = %s"
                    args = (Tfirstname or None,Tmiddlename or None,Tlastname or None,curr_date,username,cust_id)
                    conn.processquery(query=query,curs=curs,args = args,fetch=False)
                    conn.commit()
                except:
                    conn.rollback()
                conn.close()

            # 1) inserting new entry into Customer_Basic_Info Table
            perinfo_object = Customer_Basic_Info(first_name=Tfirstname,middle_name=Tmiddlename,last_name=Tlastname,gender=Tgender,DOB=TDOB,national_id=Tnationalid, suffix=Tsuffix, prefix=Tprefix, no_of_dependents=Tnoofdependents,mothers_maiden_name=Tmaidname,DNC_flag=False, marital_status=Tmaritalstatus, emp_status=Temploymentstatus,create_date=str(curr_date),created_by=username,last_updated=None,modified_by=None,cust_id=int(cust_id))
            perinfo_object.save()
            # 2) Update the Customer_Latest table
            #CustomerLatest.objects.filter(cust_id=int(customer_id[0].cust_id)).update(first_name=Tfirstname,last_name=Tlastname,dob=TDOB)
            # 3) Update the Loan_Latest table
            ll = LoanLatest.objects.get(loan_id=loanid ,cust_id=int(cust_id))
            ll.first_name=Tfirstname
            ll.last_name=Tlastname
            ll.dob=TDOB
            ll.save(force_update_dob=True)

        else:
            personalinfoadd=0

        questions=MasterQuestionList.objects.all()
        questionlist=[]

        test_obj=CustomerSecurityQuestion.objects.filter(cust=cust_id)
        if test_obj:
            answer_obj=CustomerSecurityQuestion.objects.filter(cust=cust_id).latest('create_date')
            if answer_obj:
                answer=answer_obj.answer
                selected_ques_id=answer_obj.question_id
                selected_ques=MasterQuestionList.objects.filter(question_id=selected_ques_id)[0].question_text
                for question in questions:
                    if question.question_id !=answer_obj.question_id:
                     tuple1=((question.question_id),(question.question_text))
                     questionlist.append(tuple1)
        else:
                for question in questions:
                    tuple1=((question.question_id),(question.question_text))
                    questionlist.append(tuple1)
                    selected_ques_id=''
        product_classification = get_product_classification(loanid)
        logger.info("Product Classification :: "+str(product_classification))
        if product_classification in ('LOC','INTERIM','LOAN'):
            if updateUI:
                try:
                    logger.info("Sending updateUI Dict to RTI Service :: "+str(updateUI))
                    informToUI = rtiapi.LOC_bank_profile_infoUpdate(loanid,updateUI,service_code='6103')
                
                    if informToUI is not True:
                        logger.debug("Profile Information is not updated to UI Properly ::"+str(loanid))
                except Exception,e:
                    logger.debug("Error in Profile Information update to UI ::"+str(e)+str(traceback.format_exc()))
                
    prefix_all=[['MISS','Miss'],['MR','Mr'],['MRS','Mrs'],['MS','Ms'],['REV','Rev'],['DR','Dr'],['OTHER','Other']]
    personal_info = Customer_Basic_Info.objects.filter(cust=cust_id,override_flag=0)[0]
    
    #captureUIField['first_name']      = personal_info.first_name
    #captureUIField['last_name']       = personal_info.last_name
    captureUIField['maritalstatus']  = personal_info.marital_status
    captureUIField['noofdependents']= personal_info.no_of_dependents
    #captureUIField['DOB']             = personal_info.DOB
    captureUIField['prefix']          = personal_info.prefix
    captureUIField['employmentstatus']= personal_info.emp_status
    
    return render_to_response("custdetail/personal_detail_iframe.html", \
    {'personal_info':personal_info ,'marital_status':marital_status ,'emp_stat':emp_stat,\
    'questionlist':questionlist,'answer':answer,'selected_ques':selected_ques,\
    'selected_ques_id':selected_ques_id,"prefixlist":prefix_all,"loan_id":loanid,'cust_id':cust_id,'updateUI':captureUIField})
personal_detail = maintenance_deco_popups(personal_detail)
def get_time(input_time):
            #print "ip from UI ",input_time
            time=''
            hr=input_time.split(":")[0]
            temp=input_time.split(":")[1]
            min1=temp.split(" ")[0]
            meri=temp.split(" ")[1]
            if len(hr)==1:
                hr="0"+hr
            input_time=hr+":"+min1+" "+meri
            if input_time[-2:]=='pm':
                if input_time[0:2]=='12':
                    min=input_time[3:5]
                    time= "12"+":"+str(min)+":00"
                elif int(input_time[0:2])<12:
                    hour=int(input_time[0:2])+12
                    min=input_time[3:5]
                    time= str(hour)+":"+str(min)+":00"
            if input_time[-2:]=='am':
                if input_time[0:2]=='12':
                    min=input_time[3:5]
                    time= "00"+":"+str(min)+":00"
                elif int(input_time[0:2])<12:
                    hour=input_time[0:2]
                    min=input_time[3:5]
                    time= str(hour)+":"+str(min)+":00"
            return time

def format_time(time):
    formatted_time=''
    if (int(time[:2])) > 12:
        hr=(int(time[:2])) - 12
        min= time[3:5]
        meridiem='pm'
        if int(hr)>9:
            formatted_time=str(hr)+":"+min+" "+meridiem
        elif int(hr)<10:
            formatted_time="0"+str(hr)+":"+min+" "+meridiem
    elif time[:2]=='00':
        hr='12'
        min=time[3:5]
        meridiem='am'
        formatted_time=hr+":"+min+" "+meridiem
    elif (int(time[:2])) < 12:
        hr=time[:2]
        min=time[3:5]
        meridiem='am'
        formatted_time=hr+":"+min+" "+meridiem
    elif (int(time[:2])) == 12:
        hr='12'
        min=time[3:5]
        meridiem='am'
        formatted_time=hr+":"+min+" "+meridiem
    return formatted_time


@transaction.commit_on_success
def contact_info(request):
    """
    This renders iframe for Contact Info where Customer's Contact information\
    can be viewed and also edited.
    """
    curr_date=datetime.datetime.now()
    selected_home_status=''
    is_country=0
    Capt_no=""
    Cbuilding_no=""
    Cbuilding_name=""
    Cstreet1=""
    Cstreet2=""
    Ccounty=""
    Ccity=""
    Ccountry=""
    CpostCode=""
    Cstart_date=""
    Clocality=""
    Ctown=""
    Cend_date=""
    Chome_status=""
    Ccust_id=""
    mob_priority_no = None
    mob_flag = 0
    oth_flag = 0
    update_error = 0
    contactFieldToUpdate = {}
    if 'username' in request.session:
        username = request.session['username']
    home_status_list=[['OWNED','Owned'],['RENTAL','Rental'],['TENANT COUNCIL','Tenant council'],
    ['TENANT FURNISHED','Tenant Furnished'],['TENANT UNFURNISHED','Tenant Unfurnished'],
    ['LIVING WITH PARENTS','Living with Parents'],['OTHERS','Others']]

    countrylist=[['AFGHANISTAN','Afghanistan'],["ALBANIA","Albania"],["ALGERIA","Algeria"],
                  ['ANDORRA','Andorra'],['ANGOLA','Angola'],['ANTIGUA & DEPS','Antigua & Deps'],
                  ['ARGENTINA','Argentina'],['ARMENIA','Armenia'],['AUSTRALIA','Australia'],
                  ['AUSTRIA','Austria'],['AZERBAIJAN','Azerbaijan'],['BAHAMAS','Bahamas'],
                  ['BAHRAIN','Bahrain'],['BANGLADESH','Bangladesh'],['BARBADOS','Barbados'],
                  ['BELARUS','Belarus'],['BELGIUM','Belgium'],['BELIZE','Belize'],
                  ['BENIN','Benin'],['BHUTAN','Bhutan'],['BOLIVIA','Bolivia'],['BOSNIA','Bosnia'],
                  ['BOTSWANA','Botswana'],['BRAZIL','Brazil'],['BURKINA','Burkina'],
                  ['BURUNDI','Burundi'],['CAMBODIA','Cambodia'],['CAMEROON','Cameroon'],
                  ['CANADA','Canada'],['CAPE','Cape'],['CENTRAL AFRICAN REP','Central African Rep'],
                  ['CHAD','Chad'],['CHILE','Chile'],['CHINA','China'],['COLOMBIA','Colombia'],
                  ['COMOROS','Comoros'],['CONGO','Congo'],['COSTA RICA','Costa Rica'],
                  ['CROATIA','Croatia'],['CUBA','Cuba'],['CYPRUS','Cyprus'],
                  ['CZECH REPUBLIC','Czech Republic'],['DENMARK','Denmark'],['DJIBOUTI','Djibouti'],
                  ['DOMINICA','Dominica'],['DOMINICAN REPUBLIC','Dominican Republic'],
                  ['EAST TIMOR','East Timor'],['Ecuador','Ecuador'],['EGYPT','Egypt'],
                  ['EL SALVADOR','El Salvador'],['ENGLAND','England'],
                  ['EQUATORIAL GUINEA','Equatorial Guinea'],['ERITREA','Eritrea'],
                  ['ESTONIA','Estonia'],['ETHIOPIA','Ethiopia'],['FIJI','Fiji'],
                  ['FINLAND','Finland'],['FRANCE','France'],['GABON','Gabon'],
                  ['GHANA','Ghana'],['GREAT BRITAIN','Great Britain'],
                  ['GAMBIA','Gambia'],['GEORGIA','Georgia'],['GERMANY','Germany'],
                  ['GREECE','Greece'],['GRENADA','Grenada'],['GUATEMALA','Guatemala'],
                  ['GUINEA','Guinea'],['GUINEA-BISSAU','Guinea-Bissau'],
                  ['GUYANA','Guyana'],['HAITI','Haiti'],['HONDURAS','Honduras'],
                  ['HUNGARY','Hungary'],['ICELAND','Iceland'],['INDIA', 'India'],['INDONESIA','Indonesia'],
                  ['IRAN','Iran'],['IRAQ','Iraq'],["IRELAND","Ireland"],['ISRAEL','Israel'],
                  ['ITALY','Italy'],['IVORY COAST','Ivory Coast'],['JAMAICA','Jamaica'],
                  ['JAPAN','Japan'],['JORDAN','Jordan'],['KAZAKHSTAN','Kazakhstan'],
                  ['KENYA','Kenya'],['KIRIBATI','Kiribati'],['KOREA NORTH','Korea North'],
                  ['KOREA SOUTH','Korea South'],['KOSOVO','Kosovo'],['KUWAIT','Kuwait'],
                  ['KYRGYZSTAN','Kyrgyzstan'],['LAOS','Laos'],['LATVIA','Latvia'],
                  ['LEBANON','Lebanon'],['LESOTHO','Lesotho'],['LIBERIA','Liberia'],
                  ['LIBYA','Libya'],['LIECHTENSTEIN','Liechtenstein'],['LITHUANIA','Lithuania'],
                  ['LUXEMBOURG','Luxembourg'],['MACEDONIA','Macedonia'],['MADAGASCAR','Madagascar'],
                  ['MALAWI','Malawi'],['MALAYSIA','Malaysia'],['MALDIVES','Maldives'],
                  ['MALI','Mali'],['MALTA','Malta'],['MARSHALL ISLANDS','Marshall Islands'],
                  ['MAURITANIA','Mauritania'],['MAURITIUS','Mauritius'],['MEXICO','Mexico'],
                  ['MICRONESIA','Micronesia'],['MOLDOVA','Moldova'],['MONACO','Monaco'],
                  ['MONGOLIA','Mongolia'],['MONTENEGRO','Montenegro'],['MOROCCO','Morocco'],
                  ['MOZAMBIQUE','Mozambique'],['MYANMAR','Myanmar'],['NAMIBIA','Namibia'],
                  ['NAURU','Nauru'],['NEPAL','Nepal'],['NETHERLANDS','Netherlands'],
                  ['NEW ZEALAND','New Zealand'],['NICARAGUA','Nicaragua'],
                  ['NIGER','Niger'],['NIGERIA','Nigeria'],['NORWAY','Norway'],
                  ['OMAN','Oman'],['PAKISTAN','Pakistan'],['PALAU','Palau'],
                  ['PANAMA','Panama'],['PAPUA NEW GUINEA','Papua New Guinea'],
                  ['PARAGUAY','Paraguay'],['PERU','Peru'],['PHILIPPINES','Philippines'],
                  ['POLAND','Poland'],['PORTUGAL','Portugal'],['QATAR','Qatar'],
                  ['ROMANIA','Romania'],['RUSSIAN FEDERATION','Russian Federation'],
                  ['RWANDA','Rwanda'],['ST KITTS & NEVIS','St Kitts & Nevis'],
                  ['ST LUCIA','St Lucia'],['ST VINCENT & GR/DINES','St Vincent & Gr/dines'],
                  ['SAMOA','Samoa'],['SAN MARINO','San Marino'],['SAO TOME & PRINCIPE','Sao Tome & Principe'],
                  ['SAUDI ARABIA','Saudi Arabia'],['SCOTLAND','Scotland'],
                  ['SENEGAL','Senegal'],['SERBIA','Serbia'],['SEYCHELLES','Seychelles'],
                  ['SIERRA LEONE','Sierra Leone'],['SINGAPORE','Singapore'],
                  ['SLOVAKIA','Slovakia'],['SLOVENIA','Slovenia'],['SOLOMON ISLANDS','Solomon Islands'],
                  ['SOMALIA','Somalia'],['SOUTH AFRICA','South Africa'],['SPAIN','Spain'],
                  ['SRI LANKA','Sri Lanka'],['SUDAN','Sudan'],['SURINAME','Suriname'],
                  ['SWAZILAND','Swaziland'],['SWEDEN','Sweden'],['SWITZERLAND','Switzerland'],
                  ['SYRIA','Syria'],['TAIWAN','Taiwan'],['TAJIKISTAN','Tajikistan'],
                  ['TANZANIA','Tanzania'],['THAILAND','Thailand'],['TOGO','Togo'],
                  ['TUNISIA','Tunisia'],['TURKEY','Turkey'],['TURKMENISTAN','Turkmenistan'],
                  ['TUVALU','Tuvalu'],['UGANDA','Uganda'],['UKRAINE','Ukraine'],
                  ['UNITED ARAB EMIRATES','United Arab Emirates'],['UNITED KINGDOM','United Kingdom'],
                  ['UNITED STATES','United States'],['URUGUAY','Uruguay'],
                  ['UZBEKISTAN','Uzbekistan'],['VANUATU','Vanuatu'],['VATICAN CITY','Vatican City'],
                  ['VENEZUELA','Venezuela'],['VIETNAM','Vietnam'],['WALES','Wales'],
                  ['YEMEN','Yemen'],['ZAIRE','Zaire'],['ZAMBIA','Zambia'],['ZIMBABWE','Zimbabwe']]
    if request.method=='GET':
        cust_id = request.GET['cust_id']
        loanid= request.GET['loan_id']
        loan_info = Loan_Info.objects.filter(loan=loanid,override_flag=0).order_by("-create_dt")[0]
        ll = LoanLatest.objects.filter(loan_id=loanid ,cust_id=int(cust_id))[0]
        fund_to=loan_info.fund_to
        
    if request.method == 'POST':
        cust_id = request.POST['cust_id']
        loanid= request.POST['loan_id']
        fund_to=request.POST['fund_to']
        fieldToInformToUI = eval(request.POST['contactFieldToUpdate']) 
               
        lead_id = Loan.objects.filter(loan_id=loanid)[0].lead_id
        update_dict = {}
        zebit_update_flag = 0

        customer_id = Customer.objects.filter(cust_id=cust_id)
        phoneinfo = Phone_Info.objects.filter(cust=cust_id, override_flag=0)
        
        Mphoneinfo = phoneinfo.filter(phone_type='MOBILE')
        Hphoneinfo = phoneinfo.filter(phone_type='HOME')
        Wphoneinfo = phoneinfo.filter(phone_type='WORK')
        Ophoneinfo = phoneinfo.filter(phone_type='OTHER')

        Tapts =  request.POST['apts'] or None
        Tbuilding_no=request.POST['building_no'] or None
        Tbuilding_name=request.POST['building_name']or None
        Thome_status=request.POST['home_status']
        Tstart_date=request.POST['datum1']or None
        Tend_date=request.POST['datum2']or None
        Tstreet1= request.POST['street1'] or None
        Tstreet2 = request.POST['street2'] or None
        Tlocality=request.POST['locality'] or None
        Tcounty = request.POST['county'] or None
        Tcity = request.POST['city'] or None
        Ttown=request.POST['town'] or None
        Tpostcode = request.POST['postcode']or None
        Tcountry = request.POST['country'] or None

        Thomephone = request.POST['homephone'] or None
        Tworkphone = request.POST['workphone'] or None
        oth_priority_no = Tworkphone
        Tmobilephone = request.POST['mobilephone'] or None
        Thomephone = request.POST['homephone'] or None
        Totherphone = request.POST['otherphone'] or None

        '''
        Thomephone = request.POST['homephone'] or None
        if Thomephone is not None:
            ThomephoneST = request.POST['homephoneST'] or None
            ThomephoneET = request.POST['homephoneET'] or None
            Thphone_dnc =eval(request.POST['dnc_home_value']) or "0"
        else:
            ThomephoneST =  None
            ThomephoneET =  None
            Thphone_dnc =  "0"

        Tworkphone = request.POST['workphone'] or None
        oth_priority_no = Tworkphone
        if Tworkphone is not None:
            TworkphoneST = request.POST['workphoneST'] or None
            TworkphoneET = request.POST['workphoneET'] or None
            Twphone_dnc = eval(request.POST['dnc_work_value']) or "0"
        else:
            TworkphoneST =  None
            TworkphoneET =  None
            Twphone_dnc =  "0"

        Tmobilephone = request.POST['mobilephone'] or None
        if Tmobilephone is not None:
            TmobilephoneST = request.POST['mobilephoneST'] or None
            TmobilephoneET = request.POST['mobilephoneET'] or None
            Tmphone_dnc = eval(request.POST['dnc_mobile_value']) or "0"
        else:
            TmobilephoneST = None
            TmobilephoneET = None
            Tmphone_dnc = "0"
        Totherphone = request.POST['otherphone'] or None
        if Totherphone is not None:
            TotherphoneST = request.POST['otherphoneST'] or None
            TotherphoneET = request.POST['otherphoneET'] or None
            Tophone_dnc = eval(request.POST['dnc_other_value']) or "0"
        else:
            TotherphoneST = None
            TotherphoneET = None
            Tophone_dnc = "0"
        '''
        Tpersonalemail = request.POST['personalemail'] or None
        Tofficialemail = request.POST['officialemail'] or None

        if Tstart_date:
            Tstart_date = toDate(Tstart_date)
        if Tend_date:
            Tend_date = toDate(Tend_date)

        addressinfo = Address_Info.objects.filter(cust=cust_id, override_flag=0)
        if addressinfo:
            addressinfo = addressinfo[0]
        else:
            logger.info('Error::No Address found for cust_id'+str(cust_id)+'::'+str(traceback.format_exc()))
            #raise Exception, 'No address found!!'
            content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
            mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
            update_error = 1
            return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})
        if (Tapts != addressinfo.decrypt_apt_no()) or (Tstreet1 != addressinfo.street1) or \
            (Tstreet2 != addressinfo.street2) or \
            (Tbuilding_no !=addressinfo.decrypt_building_no() )or\
            (Tbuilding_name != addressinfo.decrypt_building_name())or\
            (Thome_status != addressinfo.home_status) or\
            (Tstart_date != addressinfo.start_date)or\
            (Tend_date != addressinfo.end_date) or\
            (Tlocality != addressinfo.locality) or \
            (Ttown != addressinfo.town) or\
            (Tcounty != addressinfo.county ) or \
            (Tcity != addressinfo.city ) or \
            (str(Tpostcode) != str(addressinfo.postCode) ) or \
            (Tcountry != addressinfo.country ):
            if (Tbuilding_no !=addressinfo.decrypt_building_no() )or\
                (Tstreet1 != addressinfo.street1) or \
                (Tcounty != addressinfo.county ) or \
                (Tcity != addressinfo.city ) or \
                (str(Tpostcode) != str(addressinfo.postCode)):
                zebit_update_flag = 1

            try:
                addressinfo.override_flag = 1
                addressinfo.last_updated = curr_date
                addressinfo.modified_by=username
                addressinfo.save()
                addressobj = Address_Info(apt_no=Tapts,building_no=Tbuilding_no,\
                building_name=Tbuilding_name,street1=Tstreet1,street2=Tstreet2,\
                county=Tcounty,city=Tcity,country=Tcountry, postCode=Tpostcode, \
                start_date=Tstart_date,locality=Tlocality, town=Ttown,\
                end_date=Tend_date,home_status=Thome_status,create_date=str(curr_date),created_by=username,\
                last_updated=None,modified_by=None,cust=customer_id[0])
                logger.info('::storing following values in the Address_Info table for cust id:: '+str(cust_id)+'::\n'+'apt_no='+str(Tapts)+'|building_no='+str(Tbuilding_no)+\
                '|building_name='+str(Tbuilding_name)+'\nstreet1='+str(Tstreet1)+'|street2='+str(Tstreet2)+\
                '|\ncounty='+str(Tcounty)+'|city='+str(Tcity)+'|country='+str(Tcountry)+'|postCode='+str(Tpostcode)+\
                '|\nstart_date='+str(Tstart_date)+'|locality='+str(Tlocality)+'|town='+str(Ttown)+\
                '|\nend_date='+str(Tend_date)+'|home_status='+str(Thome_status)+'|create_date='+str(curr_date)+'|created_by='+str(username)+\
                '|\nlast_updated=None'+'|modified_by=None'+'|cust='+str(customer_id[0]))
                addressobj.save()
                
            except Exception,e:
                    transaction.rollback()
                    logger.info('Error:: address info could not be updated ::For cust_id'+str(cust_id)+'::Error string:: '+str(e)+'::'+str(traceback.format_exc()))
                    content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                    mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                    update_error = 1
                    return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})


        emailinfo = Email_Info.objects.filter(cust=cust_id, override_flag=0)
        Pemailinfo = emailinfo.filter(email_type='PERSONAL')
        Oemailinfo = emailinfo.filter(email_type='OFFICIAL')
        if((str(Tpostcode) != str(addressinfo.postCode) ) ):
            try:
                ll = LoanLatest.objects.get(loan_id=loanid ,cust_id=int(cust_id))
                ll.postCode=Tpostcode
                ll.save()
            except Exception, e:
                transaction.rollback()
                logger.info('Error::Post code could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        '''
        if ThomephoneST:
            ThomephoneST=str(get_time(ThomephoneST))

        if ThomephoneET:
            ThomephoneET = str(get_time(ThomephoneET))

        if TworkphoneST:
            TworkphoneST = str(get_time(TworkphoneST))

        if TworkphoneET:
            TworkphoneET = str(get_time(TworkphoneET))

        if TmobilephoneST:
            TmobilephoneST = str(get_time(TmobilephoneST))

        if TmobilephoneET:
            TmobilephoneET = str(get_time(TmobilephoneET))

        if TotherphoneST:
            TotherphoneST = str(get_time(TotherphoneST))

        if TotherphoneET:
            TotherphoneET = str(get_time(TotherphoneET))
        '''



        if Pemailinfo:
            try:
                if (Tpersonalemail != Pemailinfo[0].email_address):
                    # 2) inserting new entry into Email_Info Table
                    Pemailinfo[0].override_flag = 1
                    Pemailinfo[0].last_updated = curr_date
                    Pemailinfo[0].modified_by=username
                    Pemailinfo[0].save()
                    
                    if Tpersonalemail:
                        emailobj1 = Email_Info(email_type='PERSONAL',email_address=Tpersonalemail,create_date=str(curr_date),created_by=username,DNC_flag=False,last_success_dt=None,last_failed_dt=None,failure_reason=None,cust=customer_id[0],last_updated=None,modified_by=None,override_flag=0)
                        emailobj1.save()
                        LoanLatest.objects.filter(loan_id=loanid ,cust_id=int(customer_id[0].cust_id)).update(personal_email=Tpersonalemail)
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Email_Info could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
        elif Tpersonalemail:
            try:
                emailobj1 = Email_Info(email_type='PERSONAL',email_address=Tpersonalemail,create_date=str(curr_date),created_by=username,DNC_flag=False,last_success_dt=None,last_failed_dt=None,failure_reason=None,cust=customer_id[0],last_updated=None,modified_by=None,override_flag=0)
                emailobj1.save()
                LoanLatest.objects.filter(loan_id=loanid ,cust_id=int(customer_id[0].cust_id)).update(personal_email=Tpersonalemail)
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Email_Info could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        if Oemailinfo:
            try:
                if (Tofficialemail != Oemailinfo[0].email_address) :
                    Oemailinfo[0].override_flag = 1
                    Oemailinfo[0].last_updated = curr_date
                    Oemailinfo[0].modified_by=username
                    Oemailinfo[0].save()

                    if Tofficialemail:
                        emailobj2 = Email_Info(email_type='OFFICIAL',email_address=Tofficialemail,create_date=str(curr_date),created_by=username,DNC_flag=False,last_success_dt=None,last_failed_dt=None,failure_reason=None,cust_id=int(customer_id[0].cust_id),last_updated=None,modified_by=None, override_flag=0)
                        emailobj2.save()
                        LoanLatest.objects.filter(loan_id=loanid ,cust_id=int(customer_id[0].cust_id)).update(official_email=Tofficialemail)
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Official email could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        elif Tofficialemail:
            try:
                emailobj2 = Email_Info(email_type='OFFICIAL',email_address=Tofficialemail,create_date=str(curr_date),created_by=username,DNC_flag=False,last_success_dt=None,last_failed_dt=None,failure_reason=None,cust_id=int(customer_id[0].cust_id),last_updated=None,modified_by=None,override_flag=0)
                emailobj2.save()
                LoanLatest.objects.filter(loan_id=loanid ,cust_id=int(customer_id[0].cust_id)).update(official_email=Tofficialemail)
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Official email could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        if Mphoneinfo:
            try:
                MP = Mphoneinfo[0]
                '''
                if  TmobilephoneST:
                    TmobilephoneST = datetime.time(int(TmobilephoneST.split(':')[0]),int(TmobilephoneST.split(':')[1]))
                if  TmobilephoneET:
                    TmobilephoneET = datetime.time(int(TmobilephoneET.split(':')[0]),int(TmobilephoneET.split(':')[1]))

                if Tmobilephone != MP.phone_number or  int(Tmphone_dnc) != MP.DNC_flag or \
                    TmobilephoneST != MP.contact_start_time or TmobilephoneET !=MP.contact_end_time:
                '''
                if Tmobilephone != MP.phone_number:
                    MP.override_flag = 1
                    MP.last_updated = curr_date
                    MP.modified_by=username
                    MP.save()
                    phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Tmobilephone,
                                    phone_type='MOBILE',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=TmobilephoneET,
                                    #contact_start_time=TmobilephoneST,
                                    #DNC_flag=int(Tmphone_dnc),
                                    override_flag=0
                                    )
                    phone1.save()
                    LoanLatest.objects.filter(loan_id=loanid ,cust_id=int(customer_id[0].cust_id)).update(mobile_number=Tmobilephone)
                    if Tmobilephone != MP.phone_number:
                        zebit_update_flag = 1
                    mob_priority_no = Tmobilephone
                    mob_flag = 1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Mobile number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        elif Tmobilephone:
            try:
                phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Tmobilephone,
                                    phone_type='MOBILE',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=TmobilephoneET,
                                    #contact_start_time=TmobilephoneST,
                                    #DNC_flag=int(Tmphone_dnc),
                                    override_flag=0
                                    )
                phone1.save()
                LoanLatest.objects.filter(loan_id=loanid ,cust_id=int(customer_id[0].cust_id)).update(mobile_number=Tmobilephone)
                mob_priority_no = Tmobilephone
                mob_flag =1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Mobile number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        if Wphoneinfo:
            try:
                WP = Wphoneinfo[0]
                '''
                if  TworkphoneST:
                    TworkphoneST = datetime.time(int(TworkphoneST.split(':')[0]),int(TworkphoneST.split(':')[1]))
                if  TworkphoneET:
                    TworkphoneET = datetime.time(int(TworkphoneET.split(':')[0]),int(TworkphoneET.split(':')[1]))

                if Tworkphone != WP.phone_number or  int(Twphone_dnc) != WP.DNC_flag or \
                    TworkphoneST != WP.contact_start_time or TworkphoneET !=WP.contact_end_time:
                '''
                if Tworkphone != WP.phone_number:
                    WP.last_updated = curr_date
                    WP.modified_by=username
                    WP.override_flag = 1
                    WP.save()
                    phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Tworkphone,
                                    phone_type='WORK',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=TworkphoneET,
                                    #contact_start_time=TworkphoneST,
                                    #DNC_flag=int(Twphone_dnc),
                                    override_flag=0
                                    )
                    phone1.save()

                    oth_priority_no = Tworkphone
                    oth_flag = 1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Work phone number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        elif Tworkphone:
            try:
                phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Tworkphone,
                                    phone_type='WORK',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=TworkphoneET,
                                    #contact_start_time=TworkphoneST,
                                    #DNC_flag=int(Twphone_dnc),
                                    override_flag=0
                                    )
                phone1.save()
                oth_priority_no = Tworkphone
                oth_flag = 1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Work phone number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        if Hphoneinfo:
            try:
                HP = Hphoneinfo[0]
                '''
                if  ThomephoneST:
                    ThomephoneST = datetime.time(int(ThomephoneST.split(':')[0]),int(ThomephoneST.split(':')[1]))
                if  ThomephoneET:
                    ThomephoneET = datetime.time(int(ThomephoneET.split(':')[0]),int(ThomephoneET.split(':')[1]))

                if Thomephone != HP.phone_number or  int(Thphone_dnc) != HP.DNC_flag or \
                    ThomephoneST != HP.contact_start_time or ThomephoneET !=HP.contact_end_time:
                '''
                if Thomephone != HP.phone_number:
                    HP.last_updated = curr_date
                    HP.modified_by=username
                    HP.override_flag = 1
                    HP.save()
                    phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Thomephone,
                                    phone_type='HOME',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=ThomephoneET,
                                    #contact_start_time=ThomephoneST,
                                    #DNC_flag=int(Thphone_dnc),
                                    override_flag=0
                                    )
                    phone1.save()
                    if Thomephone != HP.phone_number:
                        zebit_update_flag = 1
                    if not oth_priority_no:
                        oth_priority_no = Thomephone
                        oth_flag = 1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Home phone number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        elif Thomephone:
            try:
                phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Thomephone,
                                    phone_type='HOME',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=ThomephoneET,
                                    #contact_start_time=ThomephoneST,
                                    #DNC_flag=int(Thphone_dnc),
                                    override_flag=0
                                    )
                phone1.save()
                if not oth_priority_no:
                    oth_priority_no = Thomephone
                    oth_flag = 1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Home phone number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        if Ophoneinfo:
            try:
                OP = Ophoneinfo[0]
                '''
                if  TotherphoneST:
                    TotherphoneST = datetime.time(int(TotherphoneST.split(':')[0]),int(TotherphoneST.split(':')[1]))
                if  TotherphoneET:
                    TotherphoneET = datetime.time(int(TotherphoneET.split(':')[0]),int(TotherphoneET.split(':')[1]))

                if Totherphone != OP.phone_number or  int(Tophone_dnc) != OP.DNC_flag or \
                    TotherphoneST != OP.contact_start_time or TotherphoneET !=OP.contact_end_time:
                '''
                if Totherphone != OP.phone_number:
                    OP.last_updated = curr_date
                    OP.modified_by=username
                    OP.override_flag = 1
                    OP.save()
                    phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Totherphone,
                                    phone_type='OTHER',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=TotherphoneET,
                                    #contact_start_time=TotherphoneST,
                                    #DNC_flag=int(Tophone_dnc),
                                    override_flag=0
                                    )
                    phone1.save()
                    if not oth_priority_no:
                        oth_priority_no = Totherphone
                        oth_flag = 1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Other phone number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})

        elif Totherphone:
            try:
                phone1 = Phone_Info(cust=customer_id[0],
                                    phone_number=Totherphone,
                                    phone_type='OTHER',
                                    create_date=curr_date,
                                    created_by=request.session['username'],
                                    #contact_end_time=TotherphoneET,
                                    #contact_start_time=TotherphoneST,
                                    #DNC_flag=int(Tophone_dnc),
                                    override_flag=0
                                    )
                phone1.save()
                if not oth_priority_no:
                    oth_priority_no = Totherphone
                    oth_flag = 1
            except Exception,e:
                transaction.rollback()
                logger.info('Error::Other phone number could not be updated for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})
        store = Loan.objects.filter(loan_id = loanid)[0].store_id
        
        product_classification = get_product_classification(loanid)
        if product_classification in ('LOC','INTERIM','LOAN'):        
            for val in fieldToInformToUI.keys():
                if fieldToInformToUI[val] == request.POST[val]:
                    fieldToInformToUI.pop(val)
                else:
                    fieldToInformToUI[val] = request.POST[val]
                    
            if fieldToInformToUI:
                keyList = fieldToInformToUI.keys()
                if 'datum1' in keyList:
                    fieldToInformToUI['Length_at_address'] = fieldToInformToUI['datum1']
                    fieldToInformToUI.pop('datum1')
                if 'datum2' in keyList:
                    fieldToInformToUI.pop('datum2')
                    '''
                    stDate = datetime.datetime.strptime(fieldToInformToUI['datum1'],'%Y-%m-%d').date()
                
                    if fieldToInformToUI['datum2'] is None or fieldToInformToUI['datum2'] == '':
                        edDate = datetime.datetime.now().date()
                    else:
                        edDate = datetime.datetime.strptime(fieldToInformToUI['datum2'],'%Y-%m-%d').date()
                     '''
                rtiapi.LOC_bank_profile_infoUpdate(loan_id=loanid,data=fieldToInformToUI,service_code='6103')
                
        if zebit_update_flag and store=='ZEBIT':
            update_dict ={'building_num':Tbuilding_no,\
                    'street':Tstreet1,'county':Tcounty,'city':Tcity,\
                    'postalcode':Tpostcode,'mobile_phone':Tmobilephone,\
                    'home_telephone':Thomephone}
            reportCustomerProfileChange(lead_id,update_dict)
    transaction.commit()
    try:
        conn = TranDB(section="TMS_DATA")
        curs = conn.getcursor()
        if mob_flag:
            if mob_priority_no:
                priority_no = mob_priority_no
            else:
                priority_no = Tworkphone or Thomephone or Totherphone or None
            query = "update Waterfall_Loan_Latest set phone_number = '%s',modified_date = '%s',\
                    modified_by = '%s' where cust_id = '%s'"\
                    %(priority_no,curr_date,username,cust_id)
            conn.processquery(query=query,curs=curs,fetch=False)
            conn.commit()
        elif oth_flag and not Tmobilephone:
            if oth_priority_no:
                priority_no = oth_priority_no
            else:
                priority_no = Thomephone or Totherphone or None
            query = "update Waterfall_Loan_Latest set phone_number = '%s',modified_date = '%s',\
                    modified_by = '%s' where cust_id = '%s'"\
                    %(priority_no,curr_date,username,cust_id)
            conn.processquery(query=query,curs=curs,fetch=False)
            conn.commit()
    except Exception, e:
        log.error("Error in updating Waterfall_Loan_Latest"+str(e))
        conn.rollback()
    conn.close()
    customer_id = Customer.objects.filter(cust_id=cust_id)
    phoneinfo = Phone_Info.objects.filter(cust=cust_id, override_flag=0)

    Mphoneinfo = phoneinfo.filter(phone_type='MOBILE')
    Hphoneinfo = phoneinfo.filter(phone_type='HOME')
    Wphoneinfo = phoneinfo.filter(phone_type='WORK')
    Ophoneinfo = phoneinfo.filter(phone_type='OTHER')


    # Update and Inserting the record if country is not in the country list.
    '''
    address_info = Address_Info.objects.filter(cust=cust_id,override_flag=0)[0]
    count_list=[]

    if address_info:
        for key,country in countrylist:
            if key == address_info.country:
                is_country = 1
                break
        if is_country == 0:
            # Store the values in other variables
            Capt_no=address_info.decrypt_apt_no()
            Cbuilding_no=address_info.decrypt_building_no()
            Cbuilding_name=address_info.decrypt_building_name()
            Cstreet1=address_info.street1
            Cstreet2=address_info.street2
            Ccounty=address_info.county
            Ccity=address_info.city
            Ccountry=address_info.country
            Cpostcode=address_info.postCode
            Cstart_date=address_info.start_date
            Clocality=address_info.locality
            Ctown=address_info.town
            Cend_date=address_info.end_date
            Chome_status=address_info.home_status

#            # Update the existing record
            address_info.override_flag = 1
            address_info.last_updated = curr_date
            address_info.modified_by=username
            address_info.save()
#            # Restore the old record with UNITED KINGDOM as country
            addressobj1 = Address_Info(apt_no=Capt_no,building_no=Cbuilding_no,\
                building_name=Cbuilding_name,street1=Cstreet1,street2=Cstreet2,\
                county=Ccounty,city=Ccity,country='UNITED KINGDOM', postCode=Cpostcode, \
                start_date=Cstart_date,locality=Clocality, town=Ctown,\
                end_date=Cend_date,home_status=Chome_status,create_date=str(curr_date),\
                override_flag=False,last_updated=None,modified_by=None,cust=customer_id[0])
            addressobj1.save()
    '''
    try:
        address_info = Address_Info.objects.filter(cust=cust_id,override_flag=0)[0]
    except Exception,e:
                address_info = ''
                logger.info('Error::No Address found for cust_id::'+str(cust_id)+' ::Error string::'+str(e)+'::\n'+str(traceback.format_exc()))
                content = "Please find the below traceback for this error::\n"+str(traceback.format_exc())
                mail_send(0,mailconfig.to, 'Error in updating user\'s contact details(cust_id::'+str(cust_id)+')',content,hst=1)
                update_error = 1
                return render_to_response("custdetail/contact_info_iframe.html",{'update_error':update_error,})


    Pemail_info = Email_Info.objects.filter(cust=cust_id, email_type='PERSONAL', override_flag=0)
    Oemail_info = Email_Info.objects.filter(cust=cust_id, email_type='OFFICIAL', override_flag=0)

    Mphone_info =  Phone_Info.objects.filter(cust=cust_id, phone_type='MOBILE', override_flag=0)
    Hphone_info = Phone_Info.objects.filter(cust=cust_id, phone_type='HOME', override_flag=0)
    Wphone_info = Phone_Info.objects.filter(cust=cust_id, phone_type='WORK', override_flag=0)
    Ophone_info = Phone_Info.objects.filter(cust=cust_id, phone_type='OTHER', override_flag=0)
    home_st=None
    home_end=None
    work_st=None
    work_end=None
    mobile_st=None
    mobile_end=None
    other_st=None
    other_end=None
    if Hphone_info:
        Hphone_info = Hphone_info[0]
        '''
        if Hphone_info.contact_start_time!=None:
            home_st=format_time(str(Hphone_info.contact_start_time))
        if Hphone_info.contact_end_time!=None:
            home_end=format_time(str(Hphone_info.contact_end_time))
        '''
    if Wphone_info:
        Wphone_info= Wphone_info[0]
        '''
        if Wphone_info.contact_start_time!=None:
            work_st =format_time(str(Wphone_info.contact_start_time))
        if Wphone_info.contact_end_time!=None:
            work_end =format_time(str(Wphone_info.contact_end_time))
        '''
    if Mphone_info:
        Mphone_info = Mphone_info[0]
        '''
        if Mphone_info.contact_start_time!=None:
            mobile_st =format_time(str(Mphone_info.contact_start_time))
        if Mphone_info.contact_end_time!=None:
            mobile_end =format_time(str(Mphone_info.contact_end_time))
        '''
    if Ophone_info:
        Ophone_info = Ophone_info[0]
        '''
        if Ophone_info.contact_start_time!=None:
            other_st =format_time(str(Ophone_info.contact_start_time))
        if Ophone_info.contact_end_time!=None:
            other_end =format_time(str(Ophone_info.contact_end_time))
        '''
    
    contactFieldToUpdate['building_no'] = address_info.decrypt_building_no()
    contactFieldToUpdate['county'] = address_info.county
    contactFieldToUpdate['home_status'] = address_info.home_status
    contactFieldToUpdate['postcode'] = address_info.postCode
    contactFieldToUpdate['datum1'] = str(address_info.start_date)
    contactFieldToUpdate['datum2'] = str(address_info.end_date)
    contactFieldToUpdate['street1'] = address_info.street1
    contactFieldToUpdate['city'] = address_info.city
    contactFieldToUpdate['personalemail'] = Pemail_info[0].email_address
    
    if Hphone_info:
        contactFieldToUpdate['homephone'] = Hphone_info.phone_number
        
    logger.info('logging mobile number dict :: '+str(Mphone_info))
    if Mphone_info:
        contactFieldToUpdate['mobilephone'] = Mphone_info.phone_number

    logger.info("Contact Information Dict :: "+str(contactFieldToUpdate))

    return render_to_response("custdetail/contact_info_iframe.html",\
    {'address_info':address_info,'countrylist':countrylist,'fieldInformToUI':contactFieldToUpdate,\
        'Pemail_info':Pemail_info,'Oemail_info':Oemail_info,\
        'Mphone_info':Mphone_info,'Hphone_info':Hphone_info,\
        'Wphone_info':Wphone_info,'Ophone_info':Ophone_info,\
        "loan_id":loanid,'selected_home_status':selected_home_status,\
        'cust_id':cust_id, 'fund_to':fund_to,'home_status_list':home_status_list,\
        'update_error':update_error})
        #'home_st':home_st,'home_end':home_end,'other_st':other_st,'other_end':other_end,
        #'work_st':work_st, 'work_end':work_end,'mobile_st':mobile_st,'mobile_end':mobile_end

contact_info = maintenance_deco_popups(contact_info)

def bank_info(request):
    """
    This renders iframe for Bank Info where Customer's Bank information\
    can be viewed and also edited.
    """
    if 'username' in request.session:
        username = request.session['username']
    account_type_dict={'SALARY':'Salary','SAVINGS':'Savings','CURRENT':'Current','OTHER':'Other'}
    curr_date=datetime.datetime.now()
    if request.method=='GET':
        cust_id = request.GET['cust_id']
        customer_id = Customer.objects.filter(cust_id=cust_id)
        loan_id= request.GET['loan_id']
    if request.method == 'POST':
        cust_id = request.POST['cust_id']
        loan_id= request.POST['loan_id']
        customer_id = Customer.objects.filter(cust_id=cust_id)
        Trouting_number = request.POST['routing_number']
        Tswift_code = request.POST['swift_code'] or None
        Taccount_number = request.POST['account_number']
        Taccount_type=request.POST['account_type'] or None
        Taccount_name=request.POST['account_name'] or None
        Tbranch_name=request.POST['branch_name']
        Tbranch_phone=request.POST['bank_phone']
        Tbranch_postcode=request.POST['bank_postcode']
        Tbranch_addr=request.POST['bank_addr']
        Tbank_name=request.POST['bank_name'] or None
        TFPS_eligibility=request.POST['FPS_eligibility']
        TCHAPS_eligibility=request.POST['CHAPS_eligibility']
        TBACS_eligibility=request.POST['BACS_eligibility']


        if Tbranch_name=="None":
            Tbranch_name=eval(Tbranch_name)
        elif len(Tbranch_name)==0:
            Tbranch_name=None
        if Tbranch_phone=="None":
            Tbranch_phone=eval(Tbranch_phone)
        elif len(Tbranch_phone)==0:
            Tbranch_phone=None
        if  Tbranch_postcode == "None":
            Tbranch_postcode=eval(Tbranch_postcode)
        elif len(Tbranch_postcode)==0:
            Tbranch_postcode=None
        if Tbranch_addr=="None":
            Tbranch_addr=eval(Tbranch_addr)
        elif len(Tbranch_addr)==0:
            Tbranch_addr=None
        if Tbank_name=="None":
            Tbank_name=eval(Tbank_name)

        TBACS_eligibility=eval(TBACS_eligibility)
        TCHAPS_eligibility=eval(TCHAPS_eligibility)
        TFPS_eligibility=eval(TFPS_eligibility)

        if Taccount_type:
            Chaccount_type=Taccount_type
        else:
            Chaccount_type=None
        bankinfo=BankAccount_Info.objects.filter(cust=cust_id,override_flag=0)[0]
        bank_info_repo=Bank_Info_Repo.objects.filter(routing_no=Trouting_number)
        if bank_info_repo:
            bank_info_repo=bank_info_repo[0]
            if (bank_info_repo.branch_name != Tbranch_name or\
                bank_info_repo.branch_phone != Tbranch_phone or \
                bank_info_repo.branch_postcode != Tbranch_postcode or \
                bank_info_repo.branch_address != Tbranch_addr or\
                bank_info_repo.bank_name != Tbank_name or\
                bank_info_repo.FPS_eligibility != TFPS_eligibility or\
                bank_info_repo.CHAPS_eligibility != TCHAPS_eligibility or\
                bank_info_repo.BACS_eligibility != TBACS_eligibility):

                    if (((bank_info_repo.branch_address is None) and (Tbranch_addr is not None)) or \
                        ((bank_info_repo.branch_postcode is None) and (Tbranch_postcode is not None)) or\
                        ((bank_info_repo.branch_phone is None) and (Tbranch_phone is not None)) or\
                        ((bank_info_repo.branch_name is None) and (Tbranch_name is not None))):

                            Bank_Info_Repo.objects.filter(routing_no=Trouting_number).update(override_flag=1,last_modified_dt=curr_date)

                            bank_info_record=Bank_Info_Repo(routing_no=Trouting_number,\
                            bank_name=Tbank_name,branch_name=Tbranch_name,\
                            branch_address=Tbranch_addr,branch_postcode=Tbranch_postcode,\
                            branch_phone=Tbranch_phone,FPS_eligibility=TFPS_eligibility,\
                            BACS_eligibility=TBACS_eligibility,CHAPS_eligibility=TCHAPS_eligibility,\
                            create_dt=curr_date,created_by=username,last_modified_dt=None,modified_by=None,verified_source='Service',\
                            verified_dt=curr_date,override_flag=0)
                            bank_info_record.save()
        else:
            bank_info_repo=None
            bank_info_record=Bank_Info_Repo(routing_no=Trouting_number,\
            bank_name=Tbank_name,branch_name=Tbranch_name,\
            branch_address=Tbranch_addr,branch_postcode=Tbranch_postcode,\
            branch_phone=Tbranch_phone,FPS_eligibility=TFPS_eligibility,\
            BACS_eligibility=TBACS_eligibility,CHAPS_eligibility=TCHAPS_eligibility,\
            create_dt=curr_date,created_by=username,last_modified_dt=None,modified_by=None,verified_source='Service',\
            verified_dt=curr_date,override_flag=0)
            bank_info_record.save()

        if (bankinfo.routing_number != Trouting_number) or \
            (bankinfo.decrypt_account_number() != Taccount_number) or \
            (bankinfo.account_type != Taccount_type) or \
            (bankinfo.swift_cd != Tswift_code) or\
            (bankinfo.account_name!=Taccount_name):
            BankAccount_Info.objects.filter(cust=customer_id[0],override_flag=0 ).update(override_flag=1,last_updated=curr_date,modified_by=username)
            bankobj = BankAccount_Info(routing_number=Trouting_number,\
                account_number=Taccount_number,swift_cd=Tswift_code,\
                account_type=Chaccount_type,\
                account_name=Taccount_name,\
                create_date=str(curr_date),\
                created_by=username,\
                last_updated=None,\
                modified_by=None,\
                cust=customer_id[0],override_flag=0 )
            bankobj.save()
            store = Loan.objects.filter(loan_id=loan_id)[0].store_id
            lead_id = Loan.objects.filter(loan_id=loan_id)[0].lead_id
            if store== "ZEBIT":
                if Taccount_type=="SALARY":
                    payroll_type = "YES"
                else:
                    payroll_type = "NO"
                data_dict = {'sort_code':Trouting_number,\
                            'account_number':Taccount_number,\
                            'payroll_type':payroll_type}
                reportBankAccountChange(lead_id,data_dict)

    #bankinfo=BankAccount_Info.objects.filter(cust=cust_id,override_flag=0)[0]
    #if bankinfo.account_type not in account_type_dict.keys():
    #    bankinfo.account_type='SALARY'
    #    BankAccount_Info.objects.filter(cust=customer_id[0],override_flag=0 ).update(override_flag=1,last_updated=curr_date)
    #    bankobjnew = BankAccount_Info(routing_number=bankinfo.routing_number,\
    #    account_number=bankinfo.decrypt_account_number(),swift_cd=bankinfo.swift_cd,\
    #    account_name=bankinfo.account_name,\
    #    create_date=(curr_date),created_by=username,last_updated=None,modified_by=None,\
    #    account_type='SALARY',cust=customer_id[0],override_flag=0 )
    #    bankobjnew.save()
    bankinfo=BankAccount_Info.objects.filter(cust=cust_id,override_flag=0)[0]
    if bankinfo.routing_number:
        bank_dictionary=search_Bank_Info_Repo(bankinfo.routing_number)
    else:
        bank_dictionary=None

    loanobj=Loan.objects.filter(loan_id=loan_id)[0]
    prodobj=Product.objects.filter(product_id=loanobj.product_id)[0]
    prod_classification = prodobj.product_classification


    return render_to_response("custdetail/bank_info_iframe.html", \
    {'bank_info':bankinfo,'account_type_dict':account_type_dict,\
    'bank_dictionary':bank_dictionary,'cust_id':cust_id,'loan_id':loan_id,'prod_classification':prod_classification})
bank_info = maintenance_deco_popups(bank_info)
def verify_employer(request):
    flag=1
    if request.method=='POST':
        emp_name=str(request.POST['emp_name']) or None
        postcode=str(request.POST['postcode']) or None
        emp_repo=Employer_Info_Repo.objects.filter(employer_name=emp_name,employer_postcode=postcode)
        #print emp_repo
        if emp_repo:
            flag=0
    return HttpResponse(flag, mimetype="data")

# Validation for postcode and Mobile number :
#def checkPostCode(request):
#    #postcode = oKey.infoDict['PostCode']
#    if request.method=="POST":
#        postcode=request.POST['postcode']or None
#        if postcode is None:
#            result = 'Please enter Postal Code'
#        valid_nonfollowers = ('GIR0AA',)
#        invalid_followers = ('D13DN',)
#        postcode = postcode.upper()
#        if postcode.replace(' ','') in valid_nonfollowers:
#            result = 'Null'
#        flag = 0
#        pat_str = "^([A-Z][0-9]|[A-Z][A-Z][0-9]|[A-Z][0-9][0-9]|[A-Z][A-Z][0-9][0-9]|[A-Z][A-Z][0-9][A-Z]|[A-Z][0-9][A-Z])     [0-9][A-Z][A-Z]$"
#        pat = re.compile(pat_str)
#        if pat.match(postcode) == None:
#            pat_str = "^([A-Z][0-9]|[A-Z][A-Z][0-9]|[A-Z][0-9][0-9]|[A-Z][A-Z][0-9][0-9]|[A-Z][A-Z][0-9][A-Z]|[A-Z][0-9][A-Z])[0-9][A-Z][A-Z]$"
#            pat = re.compile(pat_str)
#            flag = 1
#        if not pat.match(postcode):
#            result = 'Postal Code is not valid'
#        if flag == 1:
#            postcode = postcode[:-3]+' '+postcode[-3:]
#        if postcode[0] in ('Q', 'V', 'X') or postcode[1] in ('I', 'J',     'Z') or\
#            ((postcode[2].isalpha()) and (postcode[2] not in ('A', 'B',     'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'S', 'T', 'U', 'W'))) or\
#            ((postcode[3].isalpha()) and (postcode[3] not in ('A', 'B',     'E', 'H', 'M', 'N', 'P', 'R', 'V', 'W', 'X', 'Y'))) or\
#            postcode[-1] in ('C', 'I', 'K', 'M', 'O', 'V') or\
#            postcode[-2] in ('C', 'I', 'K', 'M', 'O', 'V'):
#                result = 'Postal Code is not valid'
#        if postcode.replace(' ','') in invalid_followers:
#            result = 'Postal Code is not valid'
#    return HttpResponse(result, mimetype="data")
#
#def checkPhone(request):
#    numericExpression = "/^[0-9]+$/"
#    nes = re.compile(numericExpression)
#    result = ""
#    if request.method=='POST':
#        homephone=request.POST['homephone'] or None
#        if not nes.match(homephone):
#            result = "Should only be digits"
#        if homephone[0:2] == '00':
#            result = "Please enter valid phone number"
#        if len(str(homephone).strip()) < 9:
#            result = "Should be atleast of 9 digits"
#        if  (homephone[0] == '0' and len(homephone) not in [10, 11]):
#            result = "Should be 10/11 digits starting with 0"
#        if (homephone[0] != '0' and len(homephone) not in [9, 10]):
#            result = "Should be 9/10 digits if not starting with 0"
#    return HttpResponse(result, mimetype="data")
#
#def checkMobile(request):
#    numericExpression = "/^[0-9]+$/"
#    result = ""
#    if request.method=='POST':
#        Phone=request.POST['mobilephone'] or None
#        #debug_logger().info("Phone---> ",Phone)
#        Phone = Phone.replace(' ','')
#        if not Phone:
#            result = "Please enter Mobile Number"
#        list = ['070','074','075','076','077','078', '079']
#        p = re.compile(numericExpression)
#        a = p.search(Phone)
#        if len(Phone) != 11 and a == None:
#            result = "Should be 11 digits starting with 0"
#        if Phone.strip()[0:3] not in list:
#            result = "Enter a valid Mobile Number"
#        if a:
#            result = "Should only be digits"
#    return HttpResponse(result, mimetype="data")
#

def get_duration(request):

    year=0
    month=0
    year_and_month=''

    if request.method=='POST':

        start_date=request.POST['start_date']or None
        end_date=request.POST['end_date']or None

        if start_date is not None:
            syear= int(str(start_date).split('-')[0])
            smonth=int(str(start_date).split('-')[1])
            sdate=int(str(start_date).split('-')[2])
            date1=datetime.date(syear,smonth,sdate)
        else:
            date1=datetime.date.today()

        if end_date is not None:
            eyear= int(str(end_date).split('-')[0])
            emonth=int(str(end_date).split('-')[1])
            edate=int(str(end_date).split('-')[2])
            date2=datetime.date(eyear,emonth,edate)
        else:
            date2=datetime.date.today()

        duration=relativedelta(date2, date1)

        year = duration.years
        month = duration.months

        year_and_month=str(year)+"-"+str(month)

    return HttpResponse(year_and_month, mimetype="data")

def get_holidaylist(cust_county):
    countyMap = {"DOWN": "NI", "FERMANAGH": "NI", "LONDONDERRY": "NI", "TYRONE": "NI", "ARMAGH": "NI", "ANTRIM": "NI", "GLASGOW": "Scotland", "INVERNESS": "Scotland", "STIRLING": "Scotland", "DUNDEE": "Scotland", "ABERDEEN": "Scotland", "EDINBURGH": "Scotland", "NEWRY AND MOURNE": "EngAndWales", "OMAGH": "EngAndWales", "ORKNEY IS": "EngAndWales", "NOTTINGHAMSHIRE": "EngAndWales", "NEWTONABBEY": "EngAndWales", "NORTHUMBERLAND": "EngAndWales", "SOUTH GLAMORGAN": "EngAndWales", "SHETLAND IS": "EngAndWales", "SHROPSHIRE": "EngAndWales", "OXFORDSHIRE": "EngAndWales", "POWYS": "EngAndWales", "RUTLAND": "EngAndWales", "MID GLAMORGAN": "EngAndWales", "MIDDLESEX": "EngAndWales", "MERSEYSIDE": "EngAndWales", "LOTHIAN REGION": "EngAndWales", "LARNE": "EngAndWales", "LISBURN": "EngAndWales", "NORTH DOWN": "EngAndWales", "NORTHAMPTONSHIRE": "EngAndWales", "NORFOLK": "EngAndWales", "MAGHERAFELT": "EngAndWales", "MOYLE": "EngAndWales", "NORTH YORKSHIRE": "EngAndWales", "WORCESTERSHIRE": "EngAndWales", "WEST MIDLANDS": "EngAndWales", "WEST YORKSHIRE": "EngAndWales", "WEST SUSSEX": "EngAndWales", "WARWICKSHIRE": "EngAndWales", "WILTSHIRE": "EngAndWales", "BALLYMENA": "EngAndWales", "BELFAST": "EngAndWales", "BERKSHIRE": "EngAndWales", "BANBRIDGE": "EngAndWales", "BANBRIDGE": "EngAndWales", "BALLYMONEY": "EngAndWales", "STRATHCLYDE REGION": "EngAndWales", "SUFFOLK": "EngAndWales", "SURREY": "EngAndWales", "SOMERSET": "EngAndWales", "STAFFORDSHIRE": "EngAndWales", "STRABANE": "EngAndWales", "BORDERS REGION": "EngAndWales", "WEST GLAMORGAN": "EngAndWales", "WESTERN ISLES": "EngAndWales", "SOUTH YORKSHIRE": "EngAndWales", "TYNE AND WEAR": "EngAndWales", "TAYSIDE REGION": "EngAndWales", "DUMFRIES AND GALLOWAY": "EngAndWales", "DERBYSHIRE": "EngAndWales", "DEVON": "EngAndWales", "CORNWALL": "EngAndWales", "CASTLEREAGH": "EngAndWales", "CUMBRIA": "EngAndWales", "DERRY": "EngAndWales", "DURHAM": "EngAndWales", "DYFED": "EngAndWales", "DUNGANNON": "EngAndWales", "DORSET": "EngAndWales", "BEDFORDSHIRE": "EngAndWales", "CARRICKFERGUS": "EngAndWales", "CRAIGAVON": "EngAndWales", "CHESHIRE": "EngAndWales", "BUCKINGHAMSHIRE": "EngAndWales", "CAMBRIDGESHIRE": "EngAndWales", "CENTRAL REGION": "EngAndWales", "COLERAINE": "EngAndWales", "COLERAINE": "EngAndWales", "CLWYD": "EngAndWales", "CHANNEL IS": "EngAndWales", "COOKSTOWN": "EngAndWales", "COOKSTOWN": "EngAndWales", "ISLE OF MAN": "EngAndWales", "ISLES OF SCILLY": "EngAndWales", "ISLE OF WIGHT": "EngAndWales", "HERTFORDSHIRE": "EngAndWales", "HEREFORDSHIRE": "EngAndWales", "HIGHLAND REGION": "EngAndWales", "LINCOLNSHIRE": "EngAndWales", "LIMAVADY": "EngAndWales", "ARDS": "EngAndWales", "KENT": "EngAndWales", "LANCASHIRE": "EngAndWales", "LEICESTERSHIRE": "EngAndWales", "BRISTOL": "EngAndWales", "FIFE": "EngAndWales", "GLOUCESTERSHIRE": "EngAndWales", "EAST RIDING OF YORKSHIRE": "EngAndWales", "EAST SUSSEX": "EngAndWales", "ESSEX": "EngAndWales", "GWENT": "EngAndWales", "GWYNEDD": "EngAndWales", "HAMPSHIRE": "EngAndWales", "GRAMPIAN REGION": "EngAndWales", "GREATER LONDON": "EngAndWales", "GREATER MANCHESTER": "EngAndWales"}
    listname=''
    county=str(cust_county) or None
    if county is None:
        listname='EngAndWales'
    else:
        county=county.upper()
        for key in countyMap:
            if county == key:
               listname=countyMap[key]
               break
        if listname=='':
            listname='EngAndWales'
    return HttpResponse(listname, mimetype="data")


def emp_info(request):
    """
    This renders iframe for Employment Info where Customer's Bank information\
    can be viewed and also edited.
    """
    if 'username' in request.session:
        username = request.session['username']#username must be captured wherever possible
    else:
       return HttpResponseRedirect('/auth/index')
    db_emp=[]
    flag_to_refresh_paydate=0
    loan_info_flag = 0 # this flag is used to disable the show schedule button in employment_info_iframe if repayment_frequency and_repayment date are present in Loan_info;
    if request.method=='GET':
        cust_id = request.GET['cust_id']
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        cust_id = request.POST['cust_id']
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Customer ID is Missing check with Back End Team!')

    try:
        db_emp=Employment_Info.objects.filter(cust=cust_id,override_flag=0)[0]
    except IndexError:
        print "No Initial Records are available in the Employment Info Table"
    if db_emp.pay_freq=='A SPECIFIC DAY OF THE MONTH':
        Employment_Info.objects.filter(cust=cust_id,override_flag=0).update(pay_freq='A SPECIFIC DATE OF THE MONTH')
    verified_source=[['GOOGLE','Google'],['SWITCH BOARD','Switch Board'],['YAHOO','Yahoo'],['YELL','Yell'],['DATABASE','Database'],['OTHER','Other']]
    payroll=[["DIRECT DEPOSIT","Direct Deposit"],["PAY CHEQUE","Pay Cheque"],["CASH","Cash"],["OTHER","Other"]]
#    product_repay_freq=get_product_repay_freq(loan_id)
#    if product_repay_freq[0]['repayment_frequency']=='monthly':
    payfreq = [[key,value["Value"]] for key,value in EMP_PAYROLLFREQ.iteritems()]
#    payfreq=[['LAST WORKING DAY OF A MONTH',"Last working day of a month"],\
#            ['LAST DAY OF MONTH',"Last day of month"],\
#            ['LAST MONDAY OF EACH MONTH',"Last Monday of each month"],\
#            ['LAST TUESDAY OF EACH MONTH',"Last Tuesday of each month"],\
#            ['LAST WEDNESDAY OF EACH MONTH',"Last Wednesday of each month"],\
#            ['LAST THURSDAY OF EACH MONTH',"Last Thursday of each month"],\
#            ['LAST FRIDAY OF EACH MONTH',"Last Friday of each month"],
#            ['A SPECIFIC DATE OF THE MONTH',"A specific date of the month"],\
#            ['WEEKLY',"Weekly"],\
#            ['BI-WEEKLY',"Bi-Weekly"],\
#            ['FOUR-WEEKLY',"Four-Weekly"],\
#            ['TWICE IN A MONTH',"Twice in a month"]
#            ]

    emp_payroll_freqs = simplejson.dumps(EMP_PAYROLLFREQ)

    cust_county=Address_Info.objects.filter(cust=cust_id).latest('create_date').county
    repaymentdate_payfreq_info=get_repaymentdate_payfreq_info(loan_id)
    if repaymentdate_payfreq_info['repayment_frequency']:
        loan_info_flag = 1
    if cust_county is None:
        cust_county=''
    if request.method == 'POST':
        curr_date=datetime.datetime.now()
        employerName = str(request.POST['employerName']) or None
        jobTitle = str(request.POST['jobTitle']) or None
        employerAddress = str(request.POST['employerAddress']) or None

        try:
            monthlyIncome = float(request.POST['monthlyIncome'])
        except ValueError:
            monthlyIncome=0
        try:
            monthlyExpense = float(request.POST['monthlyExpense'])
        except ValueError:
            monthlyExpense=0
        phone1 = str(request.POST['phone1']) or None
        phone2 = str(request.POST['phone2']) or None
        phone3 = str(request.POST['phone3']) or None
        payRollType = str(request.POST['payRollType'])or None
        datum1 = str(request.POST['datum1']) or None
        payRollFreq = str(request.POST['payRollFreq']) or None
        datum2 = str(request.POST['datum2']) or None
        datum3 = str(request.POST['datum3']) or None
        datum4 = str(request.POST['datum4']) or None
        employerPostcode = str(request.POST['postcode']) or None
        v_source1=str(request.POST['v_source1']) or None
        v_source2=str(request.POST['v_source2']) or None
        v_source3=str(request.POST['v_source3']) or None
        reason=request.POST.get('freq_reason',False)
        updateToUI = eval(request.POST['updateToUI'])

        for val in updateToUI.keys():
            if updateToUI[val] == request.POST[val]:
                updateToUI.pop(val)
            else:
                updateToUI[val] = request.POST[val]

        if v_source1=='OTHER':
                verified_source1=request.POST['source1_text']
                v_source1="other_"+str(verified_source1)
        if v_source2=='OTHER':
                verified_source2=request.POST['source2_text']
                v_source2="other_"+str(verified_source2)
        if v_source3=='OTHER':
                verified_source3=request.POST['source3_text']
                v_source3="other_"+str(verified_source3)
        if db_emp.start_dt:
            db_emp.start_dt=str(db_emp.start_dt)
        if db_emp.end_dt:
            db_emp.end_dt=str(db_emp.end_dt)
        if db_emp.pay_date:
            db_emp.pay_date=str(db_emp.pay_date)
        if db_emp.next_paydate:
            db_emp.next_paydate=str(db_emp.next_paydate)
        if db_emp is not None:
               if payRollFreq != db_emp.pay_freq or datum3 !=db_emp.pay_date or datum4 != db_emp.next_paydate:
                   flag_to_refresh_paydate=1
               if employerName !=db_emp.employer_name or phone1 != db_emp.employer_phone1\
                        or phone2!=db_emp.employer_phone2 or phone3 !=db_emp.employer_phone3\
                        or v_source1 != db_emp.verified_source1 or v_source2 !=db_emp.verified_source2\
                        or v_source3 != db_emp.verified_source3 or datum1 !=db_emp.start_dt\
                        or datum2 != db_emp.end_dt or jobTitle!=db_emp.decrypt_job_title() \
                        or payRollType!=db_emp.payroll_type or payRollFreq != db_emp.pay_freq\
                        or monthlyIncome != db_emp.monthly_income or datum3 !=db_emp.pay_date\
                        or monthlyExpense != db_emp.monthly_expense\
                        or datum4 != db_emp.next_paydate or employerPostcode!=db_emp.employer_postcode \
                        or employerAddress != db_emp.employer_addr:
                            Employment_Info.objects.filter(employment_id=db_emp.employment_id).update(override_flag=1,last_updated=str(curr_date),modified_by=None)
                            emp_data=Employment_Info(employer_name=employerName,\
                            employer_addr=employerAddress,\
                            employer_postcode=employerPostcode,employer_phone1=phone1,\
                            employer_phone2=phone2,employer_phone3=phone3,\
                            verified_source1=v_source1,verified_source2=v_source2,\
                            verified_source3=v_source3,start_dt=datum1,end_dt=datum2,\
                            job_title=jobTitle,payroll_type=payRollType,pay_freq=payRollFreq,\
                            monthly_income=monthlyIncome,monthly_expense=monthlyExpense,create_date=curr_date,created_by=username,\
                            pay_date=datum3,\
                            next_paydate=datum4,override_flag=0,cust_id=cust_id)
                            emp_data.save()
               if flag_to_refresh_paydate:
                   datum3 = datum3 and toDate(datum3)
                   datum4 = datum4 and toDate(datum4)
                   update_payFreq_and_related_tables(username, loan_id, payRollFreq, \
                                datum3, second_paydate = datum4,
                                freq_type = 'PAYROLL_FREQUENCY',reason=reason, update_table = 0)
               repo_data1=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                employer_postcode=employerPostcode,employer_phone=phone1,employer_verified_source=v_source1)
               if repo_data1:
                       repo_data1.update(employer_last_verified=curr_date)
               else:
                    if phone1 is not None and v_source1 is not None:
                        emp_repo1=Employer_Info_Repo(employer_name=employerName,\
                        employer_address=employerAddress,employer_postcode=employerPostcode,\
                        employer_phone=phone1,employer_verified_source=v_source1,\
                        employer_last_verified=curr_date)
                        emp_repo1.save()
               repo_data2=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                          employer_postcode=employerPostcode,employer_phone=phone2,employer_verified_source=v_source2)
               if repo_data2:
                       repo_data2.update(employer_last_verified=curr_date)
               else:
                    if phone2 is not None and v_source2 is not None:
                        if phone2==phone1 and v_source2 !=v_source1:
                            emp_repo2=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone2,employer_verified_source=v_source2,\
                            employer_last_verified=curr_date)
                            emp_repo2.save()
                        if phone2 !=phone1 :
                            emp_repo2=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone2,employer_verified_source=v_source2,\
                            employer_last_verified=curr_date)
                            emp_repo2.save()

               repo_data3=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                          employer_postcode=employerPostcode,employer_phone=phone3,employer_verified_source=v_source3)
               if repo_data3:
                       repo_data3.update(employer_last_verified=curr_date)
               else:
                    if phone3 is not None and v_source3 is not None:
                        if (phone3 ==phone1 and v_source3 != v_source1) or (phone3 ==phone2 and v_source3 != v_source2):
                            emp_repo3=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone3,employer_verified_source=v_source3,\
                            employer_last_verified=curr_date)
                            emp_repo3.save()
                        if phone3 !=phone2 and phone3 !=phone1:
                            emp_repo3=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone3,employer_verified_source=v_source3,\
                            employer_last_verified=curr_date)
                            emp_repo3.save()
        else:
                Employment_Info.objects.filter(employment_id=db_emp.employment_id).update(override_flag=1)
                emp_data=Employment_Info(employer_name=employerName,\
                employer_addr=employerAddress,\
                employer_postcode=employerPostcode,employer_phone1=phone1,\
                employer_phone2=phone2,employer_phone3=phone3,\
                verified_source1=v_source1,verified_source2=v_source2,\
                verified_source3=v_source3,start_dt=datum1,end_dt=datum2,\
                job_title=jobTitle,payroll_type=payRollType,pay_freq=payRollFreq,\
                monthly_income=monthlyIncome,monthly_expense=monthlyExpense,\
                create_date=db_emp.create_date,created_by=username,\
                last_updated=curr_date,pay_date=datum3,\
                next_paydate=datum4,override_flag=0,cust_id=cust_id)
                emp_data.save()
                repo_data1=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                employer_postcode=employerPostcode,employer_phone=phone1)
                if repo_data1:
                   repo_record1=repo_data1.latest('employer_last_verified')
                   if repo_record1.employer_verified_source ==v_source1:
                       repo_data1.update(employer_last_verified=curr_date)
                   else:
                       if v_source1:
                           entry1=Employer_Info_Repo(employer_name=employerName,\
                           employer_address=employerAddress,\
                           employer_postcode=employerPostcode,\
                           employer_phone=phone1,\
                           employer_verified_source=v_source1,\
                           employer_last_verified=curr_date)
                           entry1.save()
                else:
                    if phone1 is not None and v_source1 is not None :
                        emp_repo1=Employer_Info_Repo(employer_name=employerName,\
                        employer_address=employerAddress,employer_postcode=employerPostcode,\
                        employer_phone=phone1,employer_verified_source=v_source1,\
                        employer_last_verified=curr_date)
                        emp_repo1.save()

                repo_data2=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                          employer_postcode=employerPostcode,employer_phone=phone2,employer_verified_source=v_source2)
                if repo_data2:
                       repo_data2.update(employer_last_verified=curr_date)
                else:
                    if phone2 is not None and v_source2 is not None:
                        if phone2==phone1 and v_source2 !=v_source1:
                            emp_repo2=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone2,employer_verified_source=v_source2,\
                            employer_last_verified=curr_date)
                            emp_repo2.save()
                        if phone2 !=phone1 :
                            emp_repo2=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone2,employer_verified_source=v_source2,\
                            employer_last_verified=curr_date)
                            emp_repo2.save()
                repo_data3=Employer_Info_Repo.objects.filter(employer_name=employerName,\
                          employer_postcode=employerPostcode,employer_phone=phone3,employer_verified_source=v_source3)
                if repo_data3:
                       repo_data3.update(employer_last_verified=curr_date)
                else:
                    if phone3 is not None and v_source3 is not None:
                        if (phone3 ==phone1 and v_source3 != v_source1) or (phone3 ==phone2 and v_source3 != v_source2):
                            emp_repo3=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone3,employer_verified_source=v_source3,\
                            employer_last_verified=curr_date)
                            emp_repo3.save()
                        if phone3 !=phone2 and phone3 !=phone1:
                            emp_repo3=Employer_Info_Repo(employer_name=employerName,\
                            employer_address=employerAddress,employer_postcode=employerPostcode,\
                            employer_phone=phone3,employer_verified_source=v_source3,\
                            employer_last_verified=curr_date)
                            emp_repo3.save()

        product_classification = get_product_classification(loan_id)
        if product_classification in ('LOC','INTERIM','LOAN'):
            if updateToUI:
                keyList = updateToUI.keys()
                if 'datum3' in keyList and updateToUI['datum3']:
                    updateToUI['paydate'] = updateToUI['datum3']
                    updateToUI.pop('datum3')

                if 'datum4' in keyList and updateToUI['datum4']:
                    updateToUI['next_paydate'] = updateToUI['datum4']
                    updateToUI.pop('datum4')

                if 'datum1' in keyList and updateToUI['datum1']:
                    updateToUI['CustTimeAtEmployer'] = updateToUI['datum1']
                    updateToUI.pop('datum1')
                    updateToUI.pop('datum2')
                    
                if 'phone1' in keyList and updateToUI['phone1']:
                    updateToUI['employerphone1']  = updateToUI['phone1']
                    updateToUI.pop('phone1')

                    '''
                    stDate = datetime.datetime.strptime(str(updateToUI['datum1']),'%Y-%m-%d').date()

                    if updateToUI['datum2'] is None or updateToUI['datum2'] == '':
                        edDate = datetime.datetime.now().date()
                    else:
                        edDate = datetime.datetime.strptime(str(updateToUI['datum2']),'%Y-%m-%d').date()
                    updateToUI['CustTimeAtEmployer'] = (edDate - stDate).days
                    updateToUI.pop('datum1')
                    updateToUI.pop('datum2')
                '''
                try:
                    rtiapi.LOC_bank_profile_infoUpdate(loan_id=loan_id,data=updateToUI,service_code='6103')
                    logger.info("Employer Information update is informed to UI for the Loan Id :: "+str(loan_id))
                except Exception,e:
                    logger.debug("Error in Update for Employer Information to UI for the loan Id :: "+str(loan_id))

                try:
                    rtiInfo = {}
                    if 'monthlyIncome' in keyList:
                        rtiInfo['newIncome'] = updateToUI['monthlyIncome']
                    if 'monthlyExpense' in keyList:
                        rtiInfo['newExpenditure'] = updateToUI['monthlyExpense']

                    if rtiInfo:
                        rtiInfo['loan_id']          = loan_id
                        logger.info("Sending Income Expence Info to UE RTI API for the Loan Id :: "+str(loan_id)+"::" +str(rtiInfo))
                        rtiapi.LOC_ChangeIncomeAndExpenditure(rtiInfo)
                except Exception,e:
                    logger.debug("Error in Sending Income Expence Info to UE RTI API for the Loan Id :: "+str(loan_id) + " :: " + str(e))

    try:
        emp_info=Employment_Info.objects.filter(cust=cust_id,override_flag=0)[0]
        fieldToInformToUI = {}
        fieldToInformToUI['monthlyIncome'] = str(emp_info.monthly_income)
        fieldToInformToUI['payRollFreq'] = emp_info.pay_freq
        fieldToInformToUI['monthlyExpense'] = str(emp_info.monthly_expense)
        #fieldToInformToUI['phone1'] = emp_info.employer_phone1
        fieldToInformToUI['employerName'] = emp_info.employer_name
        fieldToInformToUI['datum1'] = str(emp_info.start_dt)
        #fieldToInformToUI['datum2'] = str(emp_info.end_dt)
        fieldToInformToUI['datum3'] = str(emp_info.pay_date)
        fieldToInformToUI['datum4'] = str(emp_info.next_paydate)
        fieldToInformToUI['phone1'] = str(emp_info.employer_phone1)
    except IndexError:
        print "No Initial Records are available in the Employment Info Table"


    try:
        emp_data=Employer_Info_Repo.objects.filter(employer_name=emp_info.employer_name,employer_postcode=emp_info.employer_postcode)
    except AttributeError:
          print "No Initial Records are available in Repo"
    if emp_data:
        chk_bx_value='true'
    else:
        chk_bx_value='false'
    flag1='false'
    flag2='false'
    flag3='false'
    if emp_info.verified_source1:
        for i in xrange(len(verified_source)):
            if emp_info.verified_source1.upper() in verified_source[i]:
                flag1='false'
                break
            else:
                flag1='true'
    if emp_info.verified_source2:
        for i in xrange(len(verified_source)):
            if emp_info.verified_source2.upper() in verified_source[i]:
                flag2='false'
                break
            else:
                flag2='true'
    if emp_info.verified_source3:
        for i in xrange(len(verified_source)):
            if emp_info.verified_source3.upper() in verified_source[i]:
                flag3='false'
                break
            else:
                flag3='true'
    holidaylist = get_holidaylist(cust_county)
    holidays = get_holiday_list(holidaylist)
#    conn = TranDB(section="TMS_DATA")
#    cur = conn.getcursor()
#    sql_status= "select holiday_logic from Product a join Loan b on a.product_id=b.product_id where loan_id= %s " %(loan_id)
#    holiday_logic=conn.processquery(query=sql_status, curs=cur ,fetch=True, count=1)
#    conn.close()
    return render_to_response("custdetail/emp_info_iframe.html", {'emp_info':\
    emp_info,"payroll":payroll,"payfreq":payfreq,"chk_bx_value":chk_bx_value,\
    "cust_county":cust_county,'verified_source':verified_source,'flag1':flag1,\
    'flag2':flag2,'flag3':flag3,'cust_id':cust_id,'loan_id':loan_id,\
    'loan_info_flag':loan_info_flag,'flag_to_refresh_paydate':flag_to_refresh_paydate,\
    'holidaylist':holidaylist,'holidays':holidays,'change_reasons': paydate_change_reasons,\
    'emp_payroll_freqs':emp_payroll_freqs,'fieldToInformToUI':fieldToInformToUI})

emp_info = maintenance_deco_popups(emp_info)
def reference(request):
    """
    This renders iframe for References where Customer's References \
    can be viewed and also edited.
    """

    if request.method=='GET':
        customer_id = request.GET['cust_id']
    elif request.method=='POST':
        customer_id = request.POST['cust_id']
    else:
        return HttpResponse('Customer ID is Missing check with Back End Team!')

    reference_info = ""
    reference_info = Reference_Info.objects.filter(cust=customer_id,override_flag=False).order_by("-create_date")[:2]

    try:
        ref1=reference_info[0]
    except IndexError:
        ref1 =None
    try:
        ref2=reference_info[1]
    except IndexError:
        ref2 =None
    d2=""
    d1=""
    refdate=""
    refid = ""
    refobj1 =""
    refobj2 =""
    if request.method=='POST':
        curr_date=datetime.datetime.now()
        first_name1=request.POST['first_name1'].strip()
        middle_name1=request.POST['middle_name1'].strip()
        last_name1=request.POST['last_name1'].strip()
        address1=request.POST['address1'].strip()
        phone_no1=request.POST['phone_no1'].strip()
        dnc1=request.POST['dnc1']
        ref_relation1=request.POST['ref_relation1'].strip()
        ref_postcode1=request.POST['ref_postcode1'].strip()
#        ref_type1=request.POST['ref_type1']
        if dnc1 == 'None':
            dnc1=False
        first_name2=request.POST['first_name2'].strip()
        middle_name2=request.POST['middle_name2'].strip()
        last_name2=request.POST['last_name2'].strip()
        address2=request.POST['address2'].strip()
        phone_no2=request.POST['phone_no2'].strip()
        dnc2=request.POST['dnc2']
        if dnc2 == 'None':
            dnc2=False

        ref_relation2=request.POST['ref_relation2'].strip()
        ref_postcode2=request.POST['ref_postcode2'].strip()
#        ref_type2=request.POST['ref_type2']

        if dnc1=='1':
            d1=True
        else:
            d1=False

        if dnc2=='1':
            d2=True
        else:
            d2=False


        if not ( str(first_name1) ==""  and \
                 str(middle_name1)  == "" and \
                 str(last_name1) == "" and \
                 str(address1) == "" and \
                 str(phone_no1) == "" and \
                 str(ref_relation1) =="" and \
                 str(ref_postcode1) =="" \
                 ):
            if ref1:
                if ref1.first_name == None:
                    ref1.first_name = ""
                if ref1.middle_name == None:
                    ref1.middle_name = ""
                if ref1.last_name == None:
                    ref1.last_name = ""
                if ref1.address == None:
                    ref1.address = ""
                if ref1.phone_no == None:
                    ref1.phone_no = ""
                if ref1.DNC_flag == None:
                    ref1.DNC_flag = False
                if ref1.ref_relation == None:
                    ref1.ref_relation = ""
                if ref1.postcode == None:
                    ref1.postcode = ""
                if ( (str(ref1.decrypt_first_name()) != str(first_name1)) or \
                    (str(ref1.decrypt_middle_name()) != str(middle_name1) ) or \
                    (str(ref1.decrypt_last_name()) != str(last_name1) ) or \
                    (str(ref1.decrypt_address()) != str(address1)) or \
                    (str(ref1.decrypt_phone_no()) != str(phone_no1))  or \
                    (str(ref1.DNC_flag) != str(dnc1)) or \
                    (str(ref1.ref_relation) != str(ref_relation1)) or\
                    (str(ref1.postcode) != str(ref_postcode1))
                    ):

                    refdate = ref1.create_date
                    refid = ref1.reference_id
                    refobj1 =  Reference_Info.objects.get(reference_id=refid)
                    refobj1.override_flag=True
                    refobj1.last_updated=str(curr_date)
                    refobj1.save()

                    r1=Reference_Info(first_name=first_name1,middle_name=middle_name1,\
                    last_name=last_name1,address=address1,phone_no=phone_no1,\
                    create_date=curr_date,cust_id=customer_id, DNC_flag=d1,\
                    ref_relation=ref_relation1,override_flag=False,postcode=ref_postcode1)
                    r1.save()
            else:
                r1=Reference_Info(first_name=first_name1,middle_name=middle_name1,\
                last_name=last_name1,address=address1,phone_no=phone_no1,\
                create_date=curr_date,cust_id=customer_id, DNC_flag=d1,\
                ref_relation=ref_relation1,override_flag=False,postcode=ref_postcode1)
                r1.save()

        if not ( str(first_name2) ==""  and \
                 str(middle_name2)  == "" and \
                 str(last_name2) == "" and \
                 str(address2) == "" and \
                 str(phone_no2) == "" and \
                 str(ref_relation2) =="" and \
                 str(ref_postcode2) =="" \
                 ):

            if ref2:
                if ref2.first_name == None:
                    ref2.first_name = ""
                if ref2.middle_name == None:
                    ref2.middle_name = ""
                if ref2.last_name == None:
                    ref2.last_name = ""
                if ref2.address == None:
                    ref2.address = ""
                if ref2.phone_no == None:
                    ref2.phone_no = ""
                if ref2.DNC_flag == None:
                    ref2.DNC_flag = False
                if ref2.ref_relation == None:
                    ref2.ref_relation = ""
                if ref2.postcode == None:
                    ref2.postcode = ""

                if ( (str(ref2.decrypt_first_name()) != str(first_name2) ) or \
                     ( str(ref2.decrypt_middle_name()) != str(middle_name2) ) or \
                     (str(ref2.decrypt_last_name()) != str(last_name2) ) or \
                     (str(ref2.decrypt_address()) != str(address2) ) or \
                     (str(ref2.decrypt_phone_no()) != str(phone_no2) ) or \
                     (str(ref2.DNC_flag) != str(dnc2) ) or \
                     (str(ref2.ref_relation) != str(ref_relation2)) or \
                     (str(ref2.postcode) != str(ref_postcode2))
                     ):
#                    print "something has changed in second field"
                    refdate = ref2.create_date
                    refid = ref2.reference_id
                    refobj2 =  Reference_Info.objects.get(reference_id=refid)
                    refobj2.override_flag=True
                    refobj2.last_updated=str(curr_date)
                    refobj2.save()

                    r2=Reference_Info(first_name=first_name2,middle_name=middle_name2,\
                    last_name=last_name2,address=address2,phone_no=phone_no2,\
                    create_date=curr_date,cust_id=customer_id, DNC_flag=d2,\
                    ref_relation=ref_relation2,override_flag=False,postcode=ref_postcode2)
                    r2.save()
            else:
                r2=Reference_Info(first_name=first_name2,middle_name=middle_name2,\
                last_name=last_name2,address=address2,phone_no=phone_no2,\
                create_date=curr_date,cust_id=customer_id, DNC_flag=d2,\
                ref_relation=ref_relation2,override_flag=False,postcode=ref_postcode2)
                r2.save()

        reference_info = Reference_Info.objects.filter(cust=customer_id,override_flag=False).order_by("-create_date")[:2]
        try:
            ref1=reference_info[0]
        except IndexError:
            ref1 =None
        try:
            ref2=reference_info[1]
        except IndexError:
            ref2 =None

    return render_to_response("custdetail/reference_iframe.html",{"reference1":\
    ref1,"reference2":ref2,'cust_id':customer_id})
reference = maintenance_deco_popups(reference)
def loan_gen_info(request):
    """
    This renders iframe for Loan General Info where Customer's General Loan \
    information can be viewed and also edited.    """
    # Removed post_flag_status from session, since the iframes in payment_reload
    # where reloading in a loop.
#     import pdb;pdb.set_trace()
    loan_info_flag = 0 # this flag is used to disable the show schedule button in employment_info_iframe if repayment_frequency and_repayment date are present in Loan_info;
    active_flag=0
    fraud_msg=''
    month_flag = 0
    username=request.session['username']
    post_payment_flag=False
    payfreq=""
    reason_cd = ""
    fraud_reason_post= ""
    unreturnedMoney_flag = 0
    cashbackpaidflag = 0
    resp_msg=''
    update_tables_for_pay_freq_change = 0
    crn_filed_list=['Customer','Lender']
    to_disable_payfreq_dt=['CLOSED','PRECLOSED','CLOSED']
    missing_card=0

    #if request.method == 'POST' and request.is_ajax:
    if request.method == 'POST':
        cim_present=''
        loan_id = request.POST['loan_id']
        loan_status = request.POST['loan_status']
        if loan_status in ('BOOKED','CARD CHECK DONE'):
            con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
            sql_cimtranid="select * from Ext_Bureau_Info where loan_id='%s' and override_flag=0 and reference_id is not null \
            and ((status='success' and FraudRulesStatus='valid') or (status='success' and FraudRulesStatus='NotValid' and reason='Bank Statement' and FraudRulesRejectReason in ('Penny_Auth','PA_Auth')))"%(loan_id)
            cimtranid_loan=con.get_all_results(query = sql_cimtranid)
            if not cimtranid_loan:
                cim_present='CARD DETAILS MISSING'
                resp_msg='Please collect a valid card details'
                missing_card=1
                #return HttpResponse(simplejson.dumps({'cim_present':cim_present}), mimetype="text/javascript")
                ##return HttpResponse(simplejson.dumps({'cim_present':cim_present}),mimetype='application/json')


    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
#        fraud_reason_post=request.GET['fraud_reason_post']
        ll = LoanLatest.objects.get(loan_id=loan_id ,cust_id=int(cust_id))
        loaded_dt=ll.loaded_dt
        before_booked_flag=eval(request.GET['menu_flag'])
        if 'fraud_msg' in request.GET:
            fraud_msg=request.GET['fraud_msg']
        if 'post_payment_flag' in request.GET:
            post_payment_flag=request.GET['post_payment_flag']
        if 'resp_msg' in request.GET:
            resp_msg=request.GET['resp_msg']
        if 'update_tables_for_pay_freq_change' in request.GET:
            update_tables_for_pay_freq_change=request.GET['update_tables_for_pay_freq_change']
        if 'fraud_reason_post' in request.GET:
            fraud_reason_post=request.GET['fraud_reason_post']

    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.GET['cust_id']
        before_booked_flag=request.POST['menu_flag']

    if checkUnreturnedMoney(loan_id)!=0: #checks if there is any money we need to return to the customer before making him to REVERSAL status!!
        unreturnedMoney_flag = 1
    if checkCashBackPaid(loan_id)!=0: #checks if there is any cashbash we had paid already before we make the customer as REVERSAL status!!
        cashbackpaidflag = 1

    StoreID = getStoreId(loan_id).upper()
    product_repay_freq=get_product_repay_freq(loan_id)
    freq_type = product_repay_freq[0]['repayment_frequency'].upper()
    product_classification = get_product_classification(loan_id)
    freq_key = freq_type
    if product_classification == 'LOC':  # Extending the key to access cross over repayment frequencies: LOC_MONTHLY
        freq_key = 'LOC_'+freq_type
    paydate_frequencies = PAYDATES_FREQ_MAP[StoreID][freq_key]

    val_paydt_payfreq = simplejson.dumps(paydate_frequencies)
    payfreq = [[key,value['Value']] for key,value in paydate_frequencies.iteritems()]
    month_flag = 1 if product_repay_freq[0]['repayment_frequency']=='monthly' else 0

#    if product_repay_freq[0]['repayment_frequency']=='monthly':
#        month_flag = 1
#        if getStoreId(loan_id).lower()=='zebit':
#            payfreq = [
#                ['LAST WORKING DAY OF A MONTH',"Last working day of a month"],\
#                ['LAST DAY OF MONTH',"Last day of month"],\
#                ['LAST MONDAY OF EACH MONTH',"Last Monday of each month"],\
#                ['LAST TUESDAY OF EACH MONTH',"Last Tuesday of each month"],\
#                ['LAST WEDNESDAY OF EACH MONTH',"Last Wednesday of each month"],\
#                ['LAST THURSDAY OF EACH MONTH',"Last Thursday of each month"],\
#                ['LAST FRIDAY OF EACH MONTH',"Last Friday of each month"],
#                ['A SPECIFIC DATE OF THE MONTH',"A specific date of the month"],\
#    #           ['WEEKLY',"Weekly"],\commented because this frequency is not applicable for monthly products
#    #           ['BI-WEEKLY',"Bi-Weekly"],\ commented because currently not supported
#    #           commented because currently not supported
#                ['FOUR-WEEKLY',"Four-Weekly"],\
#                ['MONTHLY_PAID_WEEKLY',"monthly_paid_weekly"],\
#                ['MONTHLY_PAID_BI-WEEKLY',"monthly_paid_bi-weekly"],\
#                ['MONTHLY_PAID_TWICE IN A MONTH',"monthly_paid_twice in a month"],\
#
#            ]
#        else:
#            payfreq = [['LAST WORKING DAY OF A MONTH',"Last working day of a month"],\
#                ['LAST DAY OF MONTH',"Last day of month"],\
#                ['LAST MONDAY OF EACH MONTH',"Last Monday of each month"],\
#                ['LAST TUESDAY OF EACH MONTH',"Last Tuesday of each month"],\
#                ['LAST WEDNESDAY OF EACH MONTH',"Last Wednesday of each month"],\
#                ['LAST THURSDAY OF EACH MONTH',"Last Thursday of each month"],\
#                ['LAST FRIDAY OF EACH MONTH',"Last Friday of each month"],
#                ['A SPECIFIC DATE OF THE MONTH',"A specific date of the month"],\
#    #           ['WEEKLY',"Weekly"],\commented because this frequency is not applicable for monthly products
#    #           ['BI-WEEKLY',"Bi-Weekly"],\ commented because currently not supported
#    #           commented because currently not supported
#                ['FOUR-WEEKLY',"Four-Weekly"],\
#            ]
#
#    elif product_repay_freq[0]['repayment_frequency']=='weekly':
#        month_flag = 0
#        if getStoreId(loan_id).lower()=='zebit':
#            payfreq = [
#    #            ['LAST WORKING DAY OF A MONTH',"Last working day of a month"],\commented because these frequencies are not applicable for weekly products
#    #            ['LAST DAY OF MONTH',"Last day of month"],\
#    #            ['LAST MONDAY OF EACH MONTH',"Last Monday of each month"],\
#    #            ['LAST TUESDAY OF EACH MONTH',"Last Tuesday of each month"],\
#    #            ['LAST WEDNESDAY OF EACH MONTH',"Last Wednesday of each month"],\
#    #            ['LAST THURSDAY OF EACH MONTH',"Last Thursday of each month"],\
#    #            ['LAST FRIDAY OF EACH MONTH',"Last Friday of each month"],
#    #            ['A SPECIFIC DATE OF THE MONTH',"A specific date of the month"],\
#                ['WEEKLY',"Weekly"],\
#                ['WEEKLY_PAID_TWICE IN A MONTH',"weekly_paid_twice in a month"],\
#                ['WEEKLY_PAID_FOUR-WEEKLY',"weekly_paid_four-weekly"],\
#                ['WEEKLY_PAID_A SPECIFIC DATE OF THE MONTH',"weekly_paid_a specific date of the month"],\
#                ['WEEKLY_PAID_LAST WORKING DAY OF A MONTH',"weekly_paid_last working day of a month"],\
#                ['WEEKLY_PAID_LAST MONDAY OF EACH MONTH',"weekly_paid_last monday of each month"],\
#                ['WEEKLY_PAID_LAST TUESDAY OF EACH MONTH',"weekly_paid_last tuesday of each month"],\
#                ['WEEKLY_PAID_LAST WEDNESDAY OF EACH MONTH',"weekly_paid_last wednesday of each month"],\
#                ['WEEKLY_PAID_LAST THURSDAY OF EACH MONTH',"weekly_paid_last thursday of each month"],\
#                ['WEEKLY_PAID_LAST FRIDAY OF EACH MONTH',"weekly_paid_last friday of each month"],\
#                ['WEEKLY_PAID_BI-WEEKLY','weekly_paid_bi-weekly'],\
#    #            ['BI-WEEKLY',"Bi-Weekly"],\ commented because currently not supported
#    #            ['FOUR-WEEKLY',"Four-Weekly"]commented because currently not supported
#                ]
#        else:
#            payfreq = [
#                ['WEEKLY',"Weekly"],\
#            ]
    reject_reason_post=""
    reject_reason_select=""
    dispute_reason_post=""
    nodealagain_reason_post=""
    write_off_reason_post=""
    decline_reason_post=""
    status_cd=""
    prorata_flag=""
    flag_shipping=0
    money_to_return=0
    update_flag=0
    flag_disable_payfreq=0
    repaymentdate_payfreq_info=get_repaymentdate_payfreq_info(loan_id)
    if repaymentdate_payfreq_info['repayment_frequency']:
        loan_info_flag = 1
    case_id=get_case_id_by_entity_id(loan_id,'LOAN')
    status=get_loan_status_by_loan_id(loan_id)
    withdrawal_reason=''
    status_from=''
    if status == 'RETURNED':
        quer_last_status = "select start_status_cd from GCMS_Data.gcm_case_log gcl \
                    where case_id = (select loan_case_id from TMS_Data.Loan_Latest where loan_id =%s) \
                    and gcl.end_status_cd is not NULL order by end_date desc limit 1; "%(str(loan_id))
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        last_loan_status=con.get_all_results(query = quer_last_status)
        status_from = last_loan_status[0]['start_status_cd']
    if status in ("WITHDRAWAL"):
        withdrawal_reason=get_withdrawal_reason(case_id,status)
    if withdrawal_reason:
        reason_cd=withdrawal_reason[0]['reason_cd']
    #    reject_reason=queueconfig.REJECT_REASON
#    withdrawal_reason=queueconfig.WITHDRAWAL_REASON
    log_id=get_logid_by_caseid(case_id)
    status_codes=[]
    username=request.session['username']
    funding_method=["FPS","CHAPS","BACS"]
    current_status=deepcopy(loanstatusconfig.loan_status)
    identifying_product=to_identify_pdtinfo(loan_id)
    if identifying_product['credit_check']==0 and identifying_product['dp_cycles']==0 and identifying_product['shipping_flag']==0 :
        current_status["IDENTITY CHECK DONE"].remove("CREDIT CHECK")
        current_status["IDENTITY CHECK DONE"].remove("DOWNPAYMENT")
        current_status["EMPLOYER CHECK DONE"].remove("CREDIT CHECK")
        current_status["EMPLOYER CHECK DONE"].remove("DOWNPAYMENT")
        current_status["CARD CHECK DONE"].remove("CREDIT CHECK")
        current_status["CARD CHECK DONE"].remove("DOWNPAYMENT")
        current_status["BANK CHECK DONE"].remove("CREDIT CHECK")
        current_status["BANK CHECK DONE"].remove("DOWNPAYMENT")
        current_status["BOOKED"].remove("CREDIT CHECK")
        current_status["BOOKED"].remove("DOWNPAYMENT")
        current_status["READY TO PAY"].remove("CANCELLATION")
        #current_status["SENT TO PAY"].remove("CANCELLATION")
        current_status["ACTIVE"].remove("CANCELLATION")
    elif identifying_product['credit_check']!=0 and identifying_product['dp_cycles']==0 and identifying_product['shipping_flag']==0:
        current_status["IDENTITY CHECK DONE"].remove("DOWNPAYMENT")
        current_status["EMPLOYER CHECK DONE"].remove("DOWNPAYMENT")
        current_status["CARD CHECK DONE"].remove("DOWNPAYMENT")
        current_status["BANK CHECK DONE"].remove("DOWNPAYMENT")
        current_status["IDENTITY CHECK DONE"].remove("CREDIT CHECK")
        current_status["EMPLOYER CHECK DONE"].remove("CREDIT CHECK")
        current_status["CARD CHECK DONE"].remove("CREDIT CHECK")
        current_status["BANK CHECK DONE"].remove("CREDIT CHECK")
        current_status["BOOKED"].remove("DOWNPAYMENT")
#       current_status["BOOKED"].remove("READY TO PAY")
        current_status["READY TO PAY"].remove("CANCELLATION")
        #current_status["SENT TO PAY"].remove("CANCELLATION")
        current_status["ACTIVE"].remove("CANCELLATION")
    elif identifying_product['dp_cycles']!=0 and identifying_product['shipping_flag']!=0:
        flag_shipping=1
        current_status["IDENTITY CHECK DONE"].remove("CREDIT CHECK")
        current_status["EMPLOYER CHECK DONE"].remove("CREDIT CHECK")
        current_status["CARD CHECK DONE"].remove("CREDIT CHECK")
        current_status["BANK CHECK DONE"].remove("CREDIT CHECK")
        current_status["BOOKED"].remove("CREDIT CHECK")
        current_status["BOOKED"].remove("READY TO PAY")
    states_aft_booked=["READY TO PAY","SENT TO PAY","READY TO SHIP","SENT TO SHIP","DEFAULTED","TERMINATED","TEMPORARY ARRANGEMENT","BANKRUPTCY",\
                        "WITHDRAWAL","PRECLOSED","POSTCLOSED","CALLED","CLOSED","FRAUD","WRITE-OFF","DEBT MANAGEMENT","ACTIVE","RECOVERIES","ARREARS","REVERSAL"]
    states_aft_booked_bfe_active=['READY TO PAY','SENT TO PAY','READY TO SHIP','SENT TO SHIP']
#    states_aft_active = ["DEFAULTED","TERMINATED","TEMPORARY ARRANGEMENT","BANKRUPTCY","WITHDRAWAL","PRECLOSED","POSTCLOSED","CALLED","CLOSED",\
#                        "FRAUD","WRITE-OFF","DEBT MANAGEMENT","ACTIVE","RECOVERIES","ARREARS","REVERSAL"]
    states_for_schedule_before_active = ['NEW','PENDING','BOOKED','IDENTITY CHECK DONE','EMPLOYER CHECK DONE','CARD CHECK DONE','DOCUMENT CHECK DONE',\
                                    'READY TO PAY','SENT TO PAY','READY TO SHIP','SENT TO SHIP']
    loan_gen_info = Loan_Info.objects.filter(loan=loan_id,override_flag=0).order_by("-create_dt")[0]
    repayfreq = loan_gen_info.repayment_frequency
    repaydt = loan_gen_info.repayment_dt
    next_repaydt = loan_gen_info.next_repayment_dt
    lone_info_frm_loan=Loan.objects.filter(loan_id=loan_id)[0]
    status_cd=get_loan_status_by_loan_case_id(lone_info_frm_loan.case_id)
    if loan_gen_info.fund_dt:
        current_status["POTENTIAL FRAUD"].remove("NEW")
        current_status["POTENTIAL FRAUD"].remove("BOOKED")
        current_status["POTENTIAL FRAUD"].remove("READY TO PAY")
#    else:
#        current_status["POTENTIAL FRAUD"].remove("ACTIVE")
#    if status_cd=='DECLINED':
#        end_status= get_end_status_cd_by_case_id(case_id)
#        if end_status.__len__()>2:
#            len=end_status.__len__()
#            if (current_status[end_status[len-1][0]]!= current_status['DECLINED']):
#                current_status['DECLINED'].remove('DECLINED')
#                current_status['DECLINED'].extend(current_status[end_status[len-1][0]])
#        else:
#            current_status['DECLINED'].remove('DECLINED')
#            current_status['DECLINED'].extend( current_status['IDENTITY CHECK DONE'])
#    if status_cd=='REJECTED':
#        end_status= get_end_status_cd_by_case_id(case_id)[1]
#        if end_status.__len__()>2:
#            len=end_status.__len__()
#            if (current_status[end_status[len-1][0]]!= current_status['REJECTED']):
#                current_status['REJECTED'].remove('REJECTED')
#                current_status['REJECTED'].extend(current_status[end_status[len-1][0]])
#            else:
#                current_status['REJECTED'].remove('REJECTED')
#                current_status['REJECTED'].extend( current_status['IDENTITY CHECK DONE'])

    if states_aft_booked.__contains__(status_cd):
        active_flag=1
    else:
        active_flag=0
    request.session["start_status"]=status_cd
    current_dt =  datetime.date.today()
    if status_cd in ('CANCEL','CANCELLED'):
#        money_to_return = get_amount_collected(loan_id,current_dt)
        money_to_return = getPaidAmt(loan_id,current_dt)
    else:
        money_to_return = 0
    if request.session.has_key('fund_dt'):
        del request.session['fund_dt']
    if loan_gen_info.fund_dt:
        request.session['fund_dt'] = datetime.date.strftime(loan_gen_info.fund_dt, "%Y-%m-%d")
    decline_reason=''
    reject_reason_select=get_reason_code(case_id,status_cd)
    if status_cd=="PARTIAL":
        reject_reason=queueconfig.PARTIAL_REJECT_REASON
        manual_underwriting_reject_reason=[]
    else:
        reject_reason=queueconfig.REJECT_REASON
        manual_underwriting_reject_reason=queueconfig.MANUAL_UNDERWRITING_REJECT_REASON
    decline_reason=queueconfig.DECLINED_REASON
    write_off_reason=queueconfig.WRITE_OFF_REASON
    fraud_reason=queueconfig.FRAUD_REASON
    dispute_reason=queueconfig.DISPUTE_REASON
    nodeal_reason=queueconfig.NODEALAGAIN_REASON
    if request.method=='POST':

        current_date = datetime.datetime.now()
        if "fund_method" in request.POST:
            fund_method=request.POST["fund_method"] or None
        elif loan_gen_info.fund_to=='PREPAID CARD':
            fund_method = 'PDC'
        else:
            fund_method=None
        if "repayfreq" in request.POST:
            if request.POST["repayfreq"] != loan_gen_info.repayment_frequency:
                repayfreq=request.POST["repayfreq"]
#                update_flag=1
                rea=request.POST["freq_reason"]
                if(rea=='others'):
                    reason=request.POST["detail_reason"]
                else:
                    reason=request.POST["freq_reason"]
                update_tables_for_pay_freq_change = 1
        if "repaydate" in request.POST or "next_repaydate" in request.POST:
            if not loan_gen_info.next_repayment_dt:
                nrd = ''
            else:
                nrd = loan_gen_info.next_repayment_dt
            if request.POST["repaydate"] != str(loan_gen_info.repayment_dt) or request.POST["next_repaydate"] != str(nrd):
                next_repaydt = None
                if request.POST['next_repaydate']:
                    next_repaydt=toDate(request.POST["next_repaydate"])

                repaydt = None
                if request.POST["repaydate"]:
                    repaydt=toDate(request.POST["repaydate"])
#                update_flag=1
                rea=request.POST["freq_reason"]
                if(rea=='others'):
                    reason=request.POST["detail_reason"]
                else:
                    reason=request.POST["freq_reason"]
                update_tables_for_pay_freq_change = 1

        loan_status=request.POST["loan_status"]
        if 'bwd_amt' in request.POST:
            borrowed_amt=request.POST["bwd_amt"].strip()
        else:
            borrowed_amt=None
        if request.POST.has_key("reject_reason"):
            reject_reason_post=str(request.POST["reject_reason"])
        if request.POST.has_key("withdrawal_reson"):
            withdrawal_reason_post=str(request.POST["withdrawal_reson"])
        if request.POST.has_key("write_off_reason"):
            write_off_reason_post=str(request.POST["write_off_reason"])
        if request.POST.has_key("fraud_reason"):
            fraud_reason_post=str(request.POST["fraud_reason"])
        if request.POST.has_key("dispute_reason"):
            dispute_reason_post=str(request.POST["dispute_reason"])
        if request.POST.has_key("decline_reason"):
            decline_reason_post=str(request.POST["decline_reason"])
        if request.POST.has_key("nodeal_reason"):
            nodealagain_reason_post=str(request.POST["nodeal_reason"])
        if loan_status=="BOOKED" and not loan_gen_info.booked_dt and missing_card==0:
            booked_dt=str(datetime.date.today())
            active_flag=1
            update_flag=1
        else:
            booked_dt=loan_gen_info.booked_dt

        if (fund_method!= loan_gen_info.funding_method and status_cd not in ('PARTIAL','CALLED')):
            fund_method=fund_method
            update_flag=1
        else:
            fund_method=loan_gen_info.funding_method

        if  loan_status == 'CANCEL' and not loan_gen_info.noc_req_on:
            noc_req_on=current_date
            update_flag=1
        else:
            noc_req_on=loan_gen_info.noc_req_on

        if update_flag:
                Loan_Info.objects.filter(loan_info_id=loan_gen_info.loan_info_id,override_flag=0).\
                update(override_flag=1,last_updated_on=current_date)
                insert_Loan_Info=Loan_Info(override_flag=0,request_amt=loan_gen_info.request_amt,\
                approved_amt=loan_gen_info.approved_amt,repayment_frequency=repayfreq,borrowed_amt=borrowed_amt,loc_limit=loan_gen_info.loc_limit,\
                funded_amt=loan_gen_info.funded_amt,EMI_amt=loan_gen_info.EMI_amt,request_dt=loan_gen_info.request_dt,\
                approved_dt=loan_gen_info.approved_dt,repayment_dt=repaydt,next_repayment_dt=next_repaydt,funding_method=fund_method,\
                booked_dt=booked_dt,fund_dt=loan_gen_info.fund_dt,commencement_dt=loan_gen_info.commencement_dt,\
                dp_esign_dt=loan_gen_info.dp_esign_dt,APR=loan_gen_info.APR,relevant_dt=loan_gen_info.relevant_dt,\
                now_dt=loan_gen_info.now_dt,wd_proposed_on=loan_gen_info.wd_proposed_on,loan_esign_dt=loan_gen_info.loan_esign_dt,\
                pco_dt=loan_gen_info.pco_dt,downpayment_amt=loan_gen_info.downpayment_amt,cb_fund_to=loan_gen_info.cb_fund_to,creditcheck_amt=loan_gen_info.creditcheck_amt,selling_price=loan_gen_info.selling_price,\
                noc_req_on=noc_req_on,create_dt=current_date,done_by= username,fund_to = loan_gen_info.fund_to,loan_id=loan_id,nosia_sent_on=loan_gen_info.nosia_sent_on)
                insert_Loan_Info.save()

        if update_tables_for_pay_freq_change:
            if update_flag :
                update_payFreq_and_related_tables(username, loan_id, repayfreq, repaydt,next_repaydt, \
                                            freq_type = 'REPAYMENT_FREQUENCY',reason=reason, update_table = 0)
            else:
                update_payFreq_and_related_tables(username, loan_id, repayfreq, repaydt,next_repaydt, \
                                            freq_type = 'REPAYMENT_FREQUENCY',reason=reason, update_table = 1)
        date_elem = datetime.datetime.now()
        if loan_status in to_disable_payfreq_dt:
            flag_disable_payfreq=1
        if loan_status=="FRAUD" :
                conn = TranDB(section="TMS_DATA")
                if loan_gen_info.fund_dt:
                    if "crn_no" in request.POST:
                        crn_no=request.POST["crn_no"]
                        if "crn_filed_by" in request.POST:
                            crn_filed_by=request.POST["crn_filed_by"]
                        if "legal_agency"  in request.POST:
                            legal_agency=request.POST['legal_agency']

                        fraud_info=Legal_Info.objects.filter(loan=loan_id,override_flag=0)

                        if fraud_info:
                            if (fraud_info[0].crn_no!=crn_no or  fraud_info[0].crn_filed_by!=crn_filed_by or fraud_info[0].legal_agency!=legal_agency):
                                msg=editinfraud(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id)
                        else:
                            if crn_no != "":
                                msg=insertinfraud(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id)

                    trandbupdateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=fraud_reason_post,date_elem=current_date)
                    fraud_msg=pcfunc.fraud(case_id,username,date_elem=current_date,conn_close=0)
                    conn.commit()
                    conn.close()

                else:
                    if "crn_no" in request.POST:
                        crn_no=request.POST["crn_no"]
                        if "crn_filed_by" in request.POST:
                            crn_filed_by=request.POST["crn_filed_by"]
                        if "legal_agency"  in request.POST:
                            legal_agency=request.POST['legal_agency']

                        fraud_info=Legal_Info.objects.filter(loan=loan_id,override_flag=0)

                        if fraud_info:
                            if (fraud_info[0].crn_no!=crn_no or  fraud_info[0].crn_filed_by!=crn_filed_by or fraud_info[0].legal_agency!=legal_agency):
                                msg=editinfraud(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id)
                        else:
                            if crn_no != "":
                                msg=insertinfraud(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id)

                    trandbupdateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=fraud_reason_post,date_elem=current_date)
                    conn.commit()
                    conn.close()
        if loan_status.lower()!=status_cd.lower():
            request.session["changed_state"]=loan_status
            if   loan_gen_info.fund_dt and loan_status not in  loanstatusconfig.STATUS_BEFORE_ACTIVE:
                if loan_status=="WRITE OFF":
                    write_off_msg=pcfunc.writeOff(case_id, username,date_elem=current_date)
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=write_off_reason_post,date_elem=current_date)
#                elif loan_status=="DEBT MANAGEMENT":
#                    debt_msg=pcfunc.debt(case_id, username,date_elem=current_date)
#                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)
                elif loan_status=="NO DEAL AGAIN":
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=nodealagain_reason_post,date_elem=current_date)
                elif loan_status in ['WITHDRAWAL']:
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=withdrawal_reason_post,date_elem=current_date)
                elif loan_status in ["SOLD","TRUST DEED","DEBT RELIEF ORDER","IVA","STATUTE-BARRED","BANKRUPTCY"]:
                    msg=pcfunc.general_status_change(loan_status,case_id, username,date_elem=current_date)
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd='',date_elem=current_date)
#                elif loan_status=="SOLD":
#                     sold_msg=pcfunc.general_status_change("SOLD",case_id, username,date_elem=current_date)
#                     updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd='',date_elem=current_date)
#                elif loan_status=="TRUST DEED":
#                     td_msg=pcfunc.general_status_change("TRUST DEED",case_id, username,date_elem=current_date)
#                     updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd='',date_elem=current_date)
#                elif loan_status=="DEBT RELIEF ORDER":
#                     dbr_msg=pcfunc.general_status_change("DEBT RELIEF ORDER",case_id, username,date_elem=current_date)
#                     updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd='',date_elem=current_date)
#                elif loan_status=="IVA":
#                     dbr_msg=pcfunc.general_status_change("IVA",case_id, username,date_elem=current_date)
#                     updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd='',date_elem=current_date)

                elif loan_status=="REVERSAL":
                    pc_obj = pcfactory.getpcobj()
                    payments_obj = pcfactory.getpmobj()
                    update_or_insert_Notice_Flags(loan_id,current_date,REV='TO BE SENT')
                    unreturned_money = checkUnreturnedMoney(loan_id)
                    if unreturned_money == 0:
                        cashbackpaid = checkCashBackPaid(loan_id)
                        if cashbackpaid!=0:
                            cashbackpaidflag = 1
                            if 'update' in request.POST:
                                if request.POST['update']=="true":
                                    overridePayCalRecords(loan_id, date_elem)  #updates payment calendar records with override_flag 1 and override_reason as REVERSAL
                                    updatePaymentRecords(loan_id, date_elem)   # updates payments table with OPB = 0, suppress_flag = 1, generation_flag = 7
                                    insertIntoTransOffTrans(loan_id, borrowed_amt, date_elem)  # updates Transactions table and offline_Transaction table.
                                    pc_obj.updateonterm(payments_obj, loan_id, current_date, date_elem, to_status="reversal")
                                    updateNoticeFlagsAndGCMDocs(loan_id, case_id)
                                    updateGCMCase(case_id, status_cd=loan_status, done_by=username, date_elem=current_date) # updates gcm_case
                                    rtmsg = pcfunc.manualsuppress(loan_id,
                                                      prn_sup=1,
                                                      int_sup=1,
                                                      fee_sup=1,
                                                      wat_sup=1,
                                                      accrual_sup_reason='REVERSAL',
                                                      wat_sup_reason='REVERSAL',
                                                      user=username,date_elem=current_date)
#                                    if rtmsg == "Suppress/Un-Suppress updated successfully":
#                                         conn.commit()
#                                         conn.close()
                                elif request.POST['update']=='false':
                                    pass
                        else:
                            overridePayCalRecords(loan_id, date_elem)  #updates payment calendar records with override_flag 1 and override_reason as REVERSAL
                            updatePaymentRecords(loan_id, date_elem)   # updates payments table with OPB = 0, suppress_flag = 1, generation_flag = 7
                            insertIntoTransOffTrans(loan_id, borrowed_amt, date_elem)  # updates Transactions table and offline_Transaction table.
                            pc_obj.updateonterm(payments_obj, loan_id, current_date, date_elem, to_status="reversal")
                            updateNoticeFlagsAndGCMDocs(loan_id, case_id)
                            updateGCMCase(case_id, status_cd=loan_status, done_by=username, date_elem=current_date) # updates gcm_case
                            rtmsg = pcfunc.manualsuppress(loan_id,
                                                      prn_sup=1,
                                                      int_sup=1,
                                                      fee_sup=1,
                                                      wat_sup=1,
                                                      accrual_sup_reason='REVERSAL',
                                                      wat_sup_reason='REVERSAL',
                                                      user=username,date_elem=current_date)
#                            if rtmsg == "Suppress/Un-Suppress updated successfully":
#                                 conn.commit()
#                                 conn.close()
                    else:
                        unreturnedMoney_flag = 1
#                        return HttpResponseRedirect("/info/loan_gen_info/?loan_id="+str(loan_id)+"&menu_flag="+str(before_booked_flag)+"&fraud_msg="+str(fraud_msg)+"&cust_id="+str(cust_id)+"loan_status="+str("REVERSAL")+"&unreturnedMoney_flag="+str(unreturnedMoney_flag))
            #1) One Person open the loan in Funding "READY TO  PAY " and other in Search "READY TO PAY"
                  #  1)Funding  Person changed to "SENT TO PAY",HERE LOAN IS IN READY TO PAY.
                  #  2)Before  update we have to check loan already in SENT TO PAY --->Dont update in GCM_CASE_LOG
            #2) One Person open the loan in Funding "SENT TO  PAY " and other in Search "SENT TO PAY"
                  #  1)Funding  Person changed to ACTIVE",HERE LOAN IS IN SENT TO PAY.
                  #  2)Before  update we have to check loan already in ACTIVE --->Dont update in GCM_CASE_LOG
            #3)Otherwise update the GCMCASE Table
            elif loan_status in states_aft_booked_bfe_active:
                lone_info_frm_loan=Loan.objects.filter(loan_id=loan_id)[0]
                status_cd=get_loan_status_by_loan_case_id(lone_info_frm_loan.case_id)
                if status_cd=="ACTIVE" or status_cd=="SENT TO PAY":
                    pass
                elif status_cd=="READY TO PAY" or  status_cd=="SENT TO PAY" or status_cd=="BOOKED" or status_cd=="CREDIT CHECK" or status_cd=="PAYOUT REJECT":
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)
                elif status_cd=="POTENTIAL FRAUD":
                      updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)
            elif loan_status=="REJECTED":
                updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=reject_reason_post,date_elem=current_date)
                if reject_reason_post=='Duplicate Application':
                       rtmsg = pcfunc.manualsuppress(loan_id,
                                                       wat_sup_reason=fraud_reason_post,
                                                      user=username,date_elem=current_date)
                if reject_reason_post == 'CRA based Reject':
                     update_or_insert_Notice_Flags(loan_id,current_date,RJCT="TO BE SENT")
#                    result_tuple = Notice_Flags.objects.get_or_create(loan=Loan.objects.get(loan_id=loan_id), defaults={'RJCT_flag':'TO BE SENT'})
#                    if result_tuple[1] is False:
#                        Notice_Flags.objects.filter(loan=loan_id).update(RJCT_flag='TO BE SENT')
            elif loan_status == "DECLINED":
                decline_reason =queueconfig.DECLINED_REASON
                updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=decline_reason_post,date_elem=current_date)
            elif loan_status == 'CALLED':
                updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=reject_reason_post,date_elem=current_date)
            elif loan_status == 'NOT CALLED':
                reject_reason=queueconfig.PARTIAL_REJECT_REASON
                updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=reject_reason_post,date_elem=current_date)
            elif loan_status == 'CANCEL':
                pay_obj = Payments.objects.filter(loan = loan_id)
                if not pay_obj:
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)
                else:
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)
                    pay_obj.update(due_amt=0.0,suppress_flag=1,suppress_till_date = None,generate_flag=7,modified_date=current_date,modified_by=username)
            elif loan_status == 'CANCELLED':
                updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)
#                pcfunc.refundOnCancel(loan_id,current_date,0,money_to_return,username,current_date)
#                updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=fraud_reason_post,date_elem=current_date)
            elif loan_status=="POTENTIAL FRAUD":
                if loan_gen_info.fund_dt:
                    reason = 'POTENTIAL FRAUD'
                    freeze_till_dt = (current_date +datetime.timedelta(queueconfig.FREEZE_LIMIT['POTENTIAL FRAUD'])).date()
                    freeze_resp = chargeBack.freeze_loan(loan_id, username, reason, freeze_till_dt, current_date)
                    if freeze_resp:
                        msg = "Loan has been freezed till %s for POTENTIAL FRAUD. Update CRN ASAP" %(freeze_till_dt)
                    else:
                        msg = "Loan has not been freezed. Contact dev team"
#                    rtmsg = pcfunc.manualsuppress(loan_id,
#                                                  fee_sup=1,
#                                                  wat_sup=1,
#                                                  wat_sup_reason='POTENTIAL FRAUD',
#                                                  user=username,date_elem=current_date)
#                    msg = "Suppress/Un-Suppress informations updated successfully "

                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=fraud_reason_post,date_elem=current_date)
                else:
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=fraud_reason_post,date_elem=current_date)
            elif loan_status=="DISPUTE":
                conn = TranDB(section="TMS_DATA")
                if loan_gen_info.fund_dt:
                    if dispute_reason_post=="Law Suit/Litigation":
                        dsp_msg=pcfunc.general_status_change("DISPUTE",case_id, username,date_elem=current_date)
                        updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=dispute_reason_post,date_elem=current_date)
                    else:
                       updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=dispute_reason_post,date_elem=current_date)
                else:
                    updateGCMCase(case_id,status_cd=loan_status,done_by=username,reason_cd=dispute_reason_post,date_elem=current_date)
            elif loan_status=="DOWNPAYMENT":
                dpfunc.dpfirstrecord(loan_id,username,date_elem=current_date)
                updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)
            elif loan_status in ("CARD CHECK DONE","BOOKED") and missing_card==1:
                pass
            else:
                updateGCMCase(case_id,status_cd=loan_status,done_by=username,date_elem=current_date)

        post_payment_flag=isEndStatus(loan_id)

#        fraud_info=Fraud_Info.objects.filter(loan=loan_id,override_flag=0)
#        if fraud_info:
#    fraud_info=fraud_info[0]
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        quer="select * from Legal_Info where loan_id = %s and override_flag = 0 \
           "%(loan_id)
        fraud_info=con.get_all_results(query = quer)
        if fraud_info:
            fraud_info=fraud_info[0]
        return HttpResponseRedirect("/info/loan_gen_info/?loan_id="+str(loan_id)+"&menu_flag="+str(before_booked_flag)+"&fraud_msg="+str(fraud_msg)+"&fraud_info="+str(fraud_info)+"&cust_id="+str(cust_id)+"&post_payment_flag="+str(post_payment_flag)+'&update_tables_for_pay_freq_change='+str(update_tables_for_pay_freq_change)+'&fraud_reason_post='+str(fraud_reason_post)+'&dispute_reason_post='+str(dispute_reason_post)+"&unreturnedMoney_flag="+str(unreturnedMoney_flag)+"cashbackpaidflag="+str(cashbackpaidflag)+"&resp_msg="+str(resp_msg))

    #   Fetches the end status, for which the payments,pre-payments,payment caledar & pay dates iframe should disable all the entries
    end_status=queueconfig.END_STATUS
#    partial_status=queueconfig.PARTIAL_STATUS
    end_status_code_frm_log=get_end_status_cd_by_case_id(lone_info_frm_loan.case_id)
    for state,sub_state in current_status.iteritems():
        if status_cd==state:
            status_codes=sub_state

    if product_classification != 'LOC' and 'BANK CHECK DONE' in status_codes:
        status_codes.remove('BANK CHECK DONE')

    for end_status in end_status_code_frm_log:
        if end_status[0]=="REJECTED" or end_status[0]=="WITHDRAWAL":
            break
        if (str(status_cd)!=str(end_status[0])) and ((status_cd=="IDENTITY CHECK DONE") or (status_cd=="EMPLOYER CHECK DONE") or (status_cd=="CARD CHECK DONE")  or (status_cd=="DOCUMENT CHECK DONE") or (status_cd=="BANK CHECK DONE")):
            if ((end_status[0]=="IDENTITY CHECK DONE") or (end_status[0]=="EMPLOYER CHECK DONE") or (end_status[0]=="CARD CHECK DONE") or (end_status[0]=="DOCUMENT CHECK DONE") or (end_status[0] == "BANK CHECK DONE")):
                status_codes.remove(end_status[0])

    loan_gen_info = Loan_Info.objects.filter(loan=loan_id,override_flag=0).order_by("-create_dt")[0]
    lone_info_frm_loan=Loan.objects.filter(loan_id=loan_id)[0]
    show_manual_underwriting_reject_reason=False
    if lone_info_frm_loan.store_id=="LS":#show manual approval reject reasons only for LS
        show_manual_underwriting_reject_reason=True
    prorata_flag = 1
    if(loan_gen_info.relevant_dt is None or (loan_gen_info.now_dt is None and loan_gen_info.wd_proposed_on is None)):
        prorata_flag = 0
    else:
        if(loan_gen_info.now_dt is None and (datetime.datetime.today() - loan_gen_info.relevant_dt).days > 14):
            prorata_flag = 0
#    fraud_info=Fraud_Info.objects.filter(loan=loan_id)
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    quer="select * from Legal_Info where loan_id = %s and override_flag = 0 \
       "%(loan_id)
    fraud_info=con.get_all_results(query = quer)
    if fraud_info:
        fraud_info=fraud_info[0]
        
    if product_classification == 'LOC' and 'REVERSAL' in status_codes:
        sql = "select count(*) as cnt from LOC_Draw where loan_id=%s and draw_status in ('NEW','READY TO PAY','SENT TO PAY','FUNDED') and draw_type='ADDITIONAL DRAW'"%(loan_id)
        resultCount = con.get_one_result(sql)
        if resultCount['cnt']:
            status_codes.remove('REVERSAL')

    sold_info = {}
    dca_info={}
    sold_info['sold_status'] = 0
    if status == 'SOLD':
        sql_sold = """select date(sold_dt) as sold_dt,agency_name,contact_no from Collection_Agency CA join Debt_Sale_Info DSI on CA.agency_id=DSI.sold_to where loan_id = %s and DSI.override_flag=0"""%(loan_id)
        sold_res = con.get_all_results(query = sql_sold)
        if sold_res:
            sold_info['sold_status'] = 1
            sold_info['sold_dt'] = sold_res[0]['sold_dt']
            sold_info['agency_name'] =  sold_res[0]['agency_name']
            sold_info['agency_phone'] =  sold_res[0]['contact_no']
    else:
        dca_info['dca_segment']=0
        sql_dca_status = "select * from LinkDebtPlan where loan_id=%s and debt_status in ('READY TO SEND','SENT') and override_flag = 0"%(loan_id)
        sql_dca_res = con.get_all_results(query = sql_dca_status)
        if sql_dca_res:
            dca_info['dca_segment'] = 1
        sql_dca = """select dca_name,date(start_dt) as start_dt,contact_no,contact_no2,a.segment_type,override_flag from Collection_Info a join Collection_Agency CA on a.dca_name = CA.agency_id where loan_id = %s and dca_name != 'WF' """ % (loan_id)
        dca_res = con.get_all_results(query=sql_dca)
        for dca_row in dca_res:
            dca_info['history_flag'] = 1
            if dca_row['override_flag'] == 0:
                " Based on the potential DMP Sub status contact number and Reason code will selected here."
                chk_reason_query = "select status from DCAIntermediateStatus where loan_id=%s order by create_dt desc" %(loan_id)
                dca_reason = con.get_one_result(query=chk_reason_query)

                dca_info['dca_name'] = collection_config.DCA_NAMEDICT[dca_row['dca_name']]
                dca_info['start_dt'] = dca_row['start_dt']
                if dca_reason:
                    if dca_reason['status'] !='POTENTIAL DMP' and dca_row['segment_type']=="Potential DMP":
                        reject_reason_select = dca_reason['status']

                    if dca_reason['status'] == 'CONFIRMED DMP' or dca_reason['status']=='POTENTIAL DMP':
                        dca_info['contact_no'] = dca_row['contact_no2']
                    else:
                        dca_info['contact_no'] = dca_row['contact_no']
                else:
                    dca_info['contact_no'] = dca_row['contact_no']

    potential_dmp_chk = queueconfig.POTENTIAL_DMP_BUTTON['ENABLE']

    """
    Reopen default loans.
    Allows to repoen the default loans with date difference between loan created date and current date should be less than 30.
    """

    if status_cd in ('DECLINED','REJECTED'):

        sql_loan = "select case_id,date(entry_dt) as entry_dt from GCMS_Data.gcm_case a join GCMS_Data.gcm_case_log b using(case_id) \
                        where entity_id = %s and (start_status_cd = '%s' or start_status_cd = '%s') and end_status_cd is Null " \
                        %(loan_id,'DECLINED', 'REJECTED')
        loan_dict = con.get_all_results(query = sql_loan)

        cur_date = datetime.date.today()
        date_diff = (cur_date - loan_dict[0]['entry_dt']).days
        if date_diff > collection_config.default_loan_reopen_days:
            if status_cd in ('DECLINED'):
                status_codes.remove("NEW")
            elif status_cd in ('REJECTED'):
                status_codes.remove('NEW')
    """
    The below variable (Supl_UE_Segment) stores the UE segment(Manual UE, Yodlee, VDNA,...) from Loan table.
    """
    Supl_UE_Segment=Loan.objects.filter(loan_id=loan_id)[0].supplementary_segment
    Supl_flag=Loan.objects.filter(loan_id=loan_id)[0].supplementary_flag
    locLimitIncOffer = 0
    locLimit = ''    
    if product_classification == 'LOC':
        sql = "select loc_limit from Loan_Info where loan_id=%s and override_flag=0"%(loan_id)
        locLimit = con.get_one_result(query=sql)
        locLimit = locLimit['loc_limit']
        
        sql = "select count(*) as cnt from LOC_Increase_Decrease where loan_id=%s and is_implemented=0 and override_flag=0"%(loan_id)
        locLimitIncOffer = con.get_one_result(query=sql)
        locLimitIncOffer = locLimitIncOffer['cnt']
             
       
    return render_to_response("custdetail/loan_gen_info_iframe.html",\
    {'funding_method':funding_method,'post_payment_flag':post_payment_flag,'loan_id':loan_id,'cust_id':cust_id,\
    'reject_reason_select':reject_reason_select,'reject_reason':reject_reason,'manual_underwriting_reject_reason':manual_underwriting_reject_reason,'show_manual_underwriting_reject_reason':show_manual_underwriting_reject_reason,'decline_reason':decline_reason,\
    'dispute_reason':dispute_reason,'nodeal_reason':nodeal_reason,'nodealagain_reason':nodealagain_reason_post,\
    'write_off_reason':write_off_reason,'fraud_reason':fraud_reason,'payfreq':payfreq,'reason_cd':reason_cd,'dispute_reason_post':dispute_reason_post,\
    'write_off_reason_post':write_off_reason_post,'fraud_reason_post':fraud_reason_post,'loan_info_flag':loan_info_flag,\
    'before_booked_flag':before_booked_flag,'fraud_msg':fraud_msg,'fraud_info':fraud_info,'month_flag':month_flag,'status_codes':status_codes,\
    'status_cd':status_cd,'lone_info_frm_loan':lone_info_frm_loan,'prorata_flag':prorata_flag,'money_to_return':money_to_return,\
    'loan_gen_info':loan_gen_info,"flag_shipping":flag_shipping,'active_flag':active_flag,'unreturnedMoney_flag':unreturnedMoney_flag,
    'cashbackpaidflag':cashbackpaidflag,'update_tables_for_pay_freq_change':update_tables_for_pay_freq_change,'states_for_schedule_before_active':states_for_schedule_before_active,\
    'loaded_dt':loaded_dt,'crn_filedby_reason':crn_filed_list,'dca_info':dca_info,'sold_info':sold_info,\
    'resp_msg':resp_msg,'status_from':status_from,'change_reasons': paydate_change_reasons,\
    'val_paydt_payfreq':val_paydt_payfreq,'potential_dmp_chk':potential_dmp_chk, "Supl_UE_Segment":Supl_UE_Segment, "Supl_flag":Supl_flag,\
    'product_classification':product_classification,'locLimit':locLimit,'locLimitIncOffer':locLimitIncOffer})
loan_gen_info = maintenance_deco_popups(loan_gen_info)
def insertinfraud(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id):
    glob_logger = pcfactory.glob_logger

    db = TranDB(section='TMS_DATA', logger=glob_logger)
    curs = db.getcursor()
    record_query = "select * from Legal_Info where loan_id = %s and override_flag = 0"
    args = (loan_id)
    record_res = db.processquery(query=record_query, curs=curs,\
                                                  count=1, args=args)
    if record_res:
        pass
    else:
         insert_query = "insert into TMS_Data.Legal_Info (crn_no,crn_filed_by,legal_agency,create_date,created_by,loan_id) \
                                            values ('%s','%s','%s','%s','%s',%s)"%(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id)
         count=db.processquery(query=insert_query, curs=curs,fetch=False)
         if count==1:
              return "Success"
         else:
              return "Failure"
def editinfraud(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id):
    glob_logger = pcfactory.glob_logger
    current_date = datetime.datetime.now()
    db = TranDB(section='TMS_DATA', logger=glob_logger)
    curs = db.getcursor()
    record_query = "select * from Legal_Info where loan_id = %s and override_flag = 0"
    args = (loan_id)
    record_res = db.processquery(query=record_query, curs=curs,\
                                                  count=1, args=args)
    if record_res:
        if crn_no!=record_res['crn_no'] or crn_filed_by!=record_res['crn_filed_by'] or legal_agency!=record_res['legal_agency']:
            update_query = "update Legal_Info set override_flag = 1, modified_date = %s,modified_by=%s\
                                where fraud_info_id = %s and override_flag = 0 "
            args = (current_date,username,record_res['fraud_info_id'])
            db.processquery(query=update_query, curs=curs,args=args, fetch=False)



            insert_query = "insert into TMS_Data.Legal_Info (crn_no,crn_filed_by,legal_agency,create_date,created_by,loan_id) \
                                                    values ('%s','%s','%s','%s','%s',%s)"%(crn_no,crn_filed_by,legal_agency,current_date,username,loan_id)
            count=db.processquery(query=insert_query, curs=curs,fetch=False)
            if count==1:
               return "Success"
            else:
               return "Failure"
        else:
            pass

def product_info(request):
    """
        Displays the product informations like
        product name, product type and based on product type
        the relevant informations are displayed
    """

    dict_fee={}
    virtual_flags = {0 : "Virtual Cycles Not Allowed", 1 : "Virtual Cycles Allowed"}
    oft_flags = {0 : "Disabled", 1 : "Enabled"}
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    loan=Loan.objects.filter(loan_id=loan_id)
    store_id = ''
    if len(loan):
        store_id = loan[0].store_id
        product=Product.objects.filter(product_id=loan[0].product_id,override_flag=0)
        if len(product):
                    virtual_cycle = virtual_flags[product[0].virtual_cycle]
                    oft_val = oft_flags[product[0].OFT]
        fee_obj=Fees.objects.filter(product=product[0].product_id)
        dic={'BACS':None,'CHAPS':None,'FPS':None,'PROCFEE':None,'ARRFEE':None,'DEFLTFEE':None,'SHFEE':None,'HANDLFEE':None,'TERMFEE':None,'SHPFEE':None}
        for fee in fee_obj:
            dic[fee.fee_type] = fee.fee_amt


    return render_to_response("custdetail/product_info_iframe.html", \
            {"product":product[0],'dic':dic,"virtual_cycle":virtual_cycle,"oft":oft_val,'store_id':store_id})


def cashback(request):
    """
    Contains the information regarding cashback for a particular loan
    """

    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']


    cashback_info = get_cashback_info_by_loan_id(loan_id)
    loan_flag = 1

    loan_status = get_loan_status_by_loan_id(loan_id)
    if loan_status in END_STATUS:
        loan_flag = 0

    #Replacing cashback type abbrivations with their explanations
    for record in cashback_info:
        record['cashback_type']=cashbackTypeExplanation[record['cashback_type']]
        record['paid_flag']=0
        if (record['cashback_amount']==record['cashback_paid']):
            record['paid_flag']=1

    earned_total = 0
    paid_total = 0
    balance_amount = 0

    for record in cashback_info:
        if record['override_flag']==0:
            earned_total = record['cashback_amount'] + earned_total
            paid_total = record['cashback_paid'] + paid_total

    balance_amount = earned_total-paid_total

    if request.method == "POST":
        if request.POST.has_key('cashback_chk'):
            getalllist = request.POST.getlist('cashback_chk')
            dictObj=[]
            for record in getalllist:
                loanid_splited = int(record.split('@')[0])
                accumulator_id_splited = record.split('@')[1]
                override_reason_for_accumulator_id=request.POST['override_reason.'+str(accumulator_id_splited)]
                dict_record={'override_reason':str(override_reason_for_accumulator_id),'cashback_accumulator_id':accumulator_id_splited}
                dictObj.append(dict_record)

            #call the update function
            discard(loanid_splited, dictObj, runDateTime=None, user='WEB-SERVICE')

            return HttpResponseRedirect("/info/cashback/?loan_id="+str(loanid_splited))


    return render_to_response("custdetail/cashback_iframe.html",\
        {"cashback_info":cashback_info,"loan_id":loan_id, "earned_total":earned_total, \
        "balance_amount":balance_amount, "paid_total":paid_total, "loan_flag":loan_flag})
cashback = maintenance_deco_popups(cashback)
def cashback_calculator(request):
    """
    This renders popup to show the cashback earned by the customer and \
    future cashback can be earned information.
    """

    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team')
    # api for getting the information of cashback values of differnet cycles from Cashback_Accumulator

    cashback_info = get_cashbackcalci_info_by_loan_id(loan_id)
    earned_total = 0
    f_earned_total = 0
    earned_cashback = {}

    loan = {'loan_id':'', 'loan_status':''}
    loan['loan_id'] = loan_id
    loan['loan_status'] = get_loan_status_by_loan_id(loan_id)

    if "ac_cycle" in request.POST:
        ac_cycle = request.POST['ac_cycle']
        if ac_cycle==0:
            uncleared_cycleinfo = get_uncleared_cycleinfo_by_loan_id(loan_id)
        else:
            uncleared_cycleinfo = get_uncleared_cycleinfo_by_loan_id(loan_id,ac_cycle)
    else:
        uncleared_cycleinfo = get_uncleared_cycleinfo_by_loan_id(loan_id)

    cashback_types = get_feegrace_paytypes_by_loan_id(loan_id)
    uncleared_cycles = get_uncleared_cycles_by_loan_id(loan_id)

    cashback_amount = get_cashbackamount_info_by_loan_id(uncleared_cycleinfo,cashback_types)
    cashback_repay = cashback_amount[0]['repay_details']
    cashback_late_repay = cashback_amount[1]['late_repay_details']

    for record in cashback_info:
        record['cashback_type']=cashbackTypeExplanation[record['cashback_type']]
        earned_total = record['cashback_amount'] + earned_total

    for record in cashback_repay:
        f_earned_total = f_earned_total + record['payamount']

    for record in cashback_late_repay:
        f_earned_total = f_earned_total + record['payamount']

    earned_cashback['earned_total'] = earned_total
    earned_cashback['f_earned_total'] = f_earned_total
    earned_cashback['total'] = Money(earned_total) + Money(f_earned_total)

    return render_to_response("custdetail/cashback_calculator.html" ,
        {'cashback_info':cashback_info, 'loan':loan, 'earned_cashback':earned_cashback, 'uncleared_cycles':uncleared_cycles, \
        'cashback_repay':cashback_repay, 'cashback_late_repay':cashback_late_repay})
cashback_calculator= maintenance_deco_popups(cashback_calculator)
def down_payments(request):
        """
        Contains the functionalities for downpayment iframe in custdetail page.
        """
        status=""
        username=request.session['username']
        if request.method=='GET':
            loan_id = request.GET['loan_id']
        elif request.method=='POST':
            loan_id = request.POST['loan_id']
        else:
            return HttpResponse('Loan ID is Missing check with Back End Team!')

        downpayment_type = pcconfig.downpayment_type
    #Getting Current Date
        date_time=datetime.datetime.now()
        curr_date=date_time.date()
        current_date=str(datetime.date.today())
        down_pay_list=""
    #      checking that loan is active if it is ....Disable the  buttons
        loan_status = get_loan_status_by_loan_id(loan_id)
        if loan_status in ('ACTIVE', 'CANCEL', 'CANCELLED'):
            loan_is_active=1
        else:
            loan_is_active=0
        if loan_status in ('DOWNPAYMENT'):
            loan_is_downpayment=1
        else:
            loan_is_downpayment=0

        chk_box_key=[]
        chk=[]
        records=[]
        dict=request.POST
        if request.method=='POST':
           # cur_date = datetime.datetime.now()
            for k,v in dict.iteritems():
                if v=='on':
                    chk.append(k)
            chk.sort()

            chk_box_key=chk

            for item in chk_box_key:
                if not ("payment_chk" in item):
                    tmp_record={"loan_id":loan_id,"downpayment_dt":dict["["+item+",1]"],"downpayment_nbr":dict["["+item+",2]"],"downpayment_type":dict["["+item+",3]"],"downpayment_amt":dict["["+item+",4]"],"user":username,"flag":1}
                    if tmp_record["downpayment_dt"] and tmp_record["downpayment_nbr"] and tmp_record["downpayment_type"] and tmp_record["downpayment_amt"]:
                         records.append(tmp_record)
                else:
#                    The index for item is length("payment_chk") for getting the index value example if payment_chk1 means the index_payment_chk is 1
                    index_payment_chk=item[11:]
                    pre_check=Downpayments.objects.filter(downpayment_id=dict["downpayment_id"+index_payment_chk]);
                    if pre_check[0].downpayment_amt!=float(dict["downpayment_amt"+index_payment_chk]) or (str(pre_check[0].downpayment_dt)!=str(dict["downpayment_dt"+index_payment_chk])):
                        records.append({"downpayment_id":int(dict["downpayment_id"+index_payment_chk]),"loan_id":loan_id,"paydate":dict["downpayment_dt"+index_payment_chk],\
                        "downpayment_nbr":dict["downpayment_nbr"+index_payment_chk],"amount":dict["downpayment_amt"+index_payment_chk],\
                        "downpayment_type":dict["downpayment_type"+index_payment_chk],"reason":dict["override_reason"+index_payment_chk].strip() or None,"user":username,"flag":0})
            if records:
               status=dpfunc.dpmanual(records,current_date)

               if status.__contains__('updated successfully'):
                    request.session["update_flag"]=1

            return HttpResponseRedirect("/info/down_payments/?loan_id="+str(loan_id))
        payment_calender_records=dpfunc.getdpdata(loan_id)
        if isinstance(payment_calender_records,str) or isinstance(payment_calender_records,unicode):
#        no_records=payment_calender_records
            no_records="Loan is not yet Active"
        else:
            down_pay_list=payment_calender_records
            for pay_sch in down_pay_list:
                if str(pay_sch["downpayment_dt"])< current_date:
                    pay_sch["past_date"]=1
                else:
                    pay_sch["past_date"]=0
        loan_status = get_loan_status_by_loan_id(loan_id)
        return render_to_response("custdetail/downpayment_iframe.html",\
        {'down_pay_list':down_pay_list,'curr_date':curr_date,'loan_is_active':loan_is_active,\
            'downpayment_type':downpayment_type,'status':status,'loan_is_downpayment':loan_is_downpayment,'loan_id':loan_id})



def customerproduct_info(request):
     flag=0
     message=""
     if request.method=='GET':
        loan_id = request.GET['loan_id']
        custproductlist=CustomerProducts.objects.filter(loan=loan_id)

        if len(custproductlist)==0:
            message="No Customer Products Information  for this Loan"
     return render_to_response("custdetail/customerproduct_info_iframe.html",{'custproductlist':custproductlist,'flag':flag,'message':message})
customerproduct_info = maintenance_deco_popups(customerproduct_info)

def payment_schedule(request):
    """
    This renders iframe for Payment schedule where payment information \
    can be viewed and also edited.
    """
#   Fetches the end status, for which the payments,pre-payments,payment caledar & pay dates iframe should disable al the entries

    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

#    Initiated Payment Types
    payment_schedule=[]
    payment_type={"select":"select","PRNDUE":"Principal Due","INTCAPLZD":"Interest Capitalized","ARRFEE":"Arrear Fee","DEFLTFEE":"Default Fee","TERMNFEE":"Termination Fee","XTRPREPYMT":"Extra Prepayment","PRTINTCAPLZD":"Prorata Interest Capitalized", "RMPB" : "Remaining Principal Balance","MEMOFEE":'Memo Fee'}
    no_records=""
    current_date=str(datetime.date.today())
#    Setting this flag to reload the relevent pages
    update_flag=0
    if request.session.has_key("update_flag"):
        update_flag=request.session["update_flag"]
        del request.session["update_flag"]
#    Getting user name and loan_id from session
    username=request.session['username']
#    spcl privileges check
    revert_flag=0
    revert_special_prev=get_spl_privileges_by_usr_id(str(username),2)
    if revert_special_prev=='Grant':
        revert_flag=1

    payment_flag=isEndStatus(loan_id)
    prorata_flag = 1
    pblLoan=Loan_Info.objects.filter(loan=loan_id,override_flag=0).order_by("-create_dt")[0]
    print payment_flag

    con = mysqldbwrapper.MySQLWrapper(config_file_path, 'TMS_DATA')
    sql="select status_cd,end_status_cd,end_date from GCMS_Data.gcm_case_log a join GCMS_Data.gcm_case b on b.case_id=a.case_id where b.entity_id=%s  order by end_date desc limit 1"
    res=con.get_one_result(sql,args=loan_id)

    #if(pblLoan.relevant_dt is None):
        #prorata_flag = 0
    if(pblLoan.relevant_dt is not None):
        if (pblLoan.now_dt is None and (datetime.datetime.today() - pblLoan.relevant_dt).days > 14):
            if not (((res["end_date"]-pblLoan.relevant_dt).days<=14) and res["status_cd"]== res["end_status_cd"]  and res["end_status_cd"] in('PRECLOSED'or'POSTCLOSED'or'CLOSED') and revert_flag):
                prorata_flag = 0
        else:
            if not revert_flag and (res["end_status_cd"] in('PRECLOSED'or'POSTCLOSED'or'CLOSED')):
                prorata_flag=0
    elif(pblLoan.fund_dt is not None):
        if (pblLoan.now_dt is None and (datetime.date.today() - pblLoan.fund_dt).days > 14):
            if not (((res["end_date"].date()-pblLoan.fund_dt).days<=14) and res["status_cd"]== res["end_status_cd"]  and res["end_status_cd"] in('PRECLOSED'or'POSTCLOSED'or'CLOSED') and revert_flag):
                prorata_flag = 0
        else:
            if not revert_flag and (res["end_status_cd"] in('PRECLOSED'or'POSTCLOSED'or'CLOSED')):
                prorata_flag=0


    index_chk=None
    status=""
    records=[]


    chk_box_key=[]
    chk=[]
    dict= request.POST
    if request.method=='POST':
        cur_date = datetime.datetime.now()
        for k,v in dict.iteritems():
            if v=='on':
                chk.append(k)
        chk.sort()

        for chk_item in chk:
            if chk_item.__contains__("payment_chk"):
                index_chk=chk.index(chk_item)
                break

        if not (index_chk==None):
            chk_box_key=chk[index_chk:]
            chk_box_key.extend(chk[:index_chk])
        else:
            chk_box_key=chk

        chk_box_key=chk
        for item in chk_box_key:
                if not ("payment_chk" in item):

                    tmp_record={"loan_id":loan_id,"paydate":dict["["+item+",1]"],"payment_nbr":dict["["+item+",2]"],"payment_type":dict["["+item+",3]"],"amount":dict["["+item+",4]"],"user":username,"flag":1}

                    if tmp_record["paydate"] and tmp_record["payment_nbr"] and tmp_record["payment_type"] and tmp_record["amount"]:
                        records.append(tmp_record)


                else:
                    index_payment_chk=item[11:]
                    pre_check=PaymentCalendar.objects.filter(payment_id=dict["payment_id"+index_payment_chk]);
                    if pre_check[0].payment_amt!=float(dict["payment_amt"+index_payment_chk]) or (str(pre_check[0].payment_dt)!=str(dict["payment_dt"+index_payment_chk])):
                        records.append({"payment_id":int(dict["payment_id"+index_payment_chk]),"loan_id":loan_id,"paydate":dict["payment_dt"+index_payment_chk],\
                        "payment_nbr":dict["payment_nmr"+index_payment_chk],"amount":dict["payment_amt"+index_payment_chk],\
                        "payment_type":dict["payment_type"+index_payment_chk],"reason":dict["override_reason"+index_payment_chk].strip() or None,"user":username,"flag":0})
#                    The index for item is length("payment_chk") for getting the index value example if payment_chk1 means the index_payment_chk is 1
        if records:
            status=pcfunc.manual(records, cur_date)
            request.session["update_flag"]=1

        return HttpResponseRedirect("/info/payment_schedule/?loan_id="+str(loan_id)+"&cust_id="+str(cust_id))

    payment_calender_records=pcfunc.getpcdata(loan_id)

    if isinstance(payment_calender_records,str) or isinstance(payment_calender_records,unicode):
        no_records="Loan is not yet Active"
    else:

        payment_schedule=payment_calender_records
        for pay_sch in payment_schedule:
            if str(pay_sch["payment_dt"])<current_date:
                pay_sch["past_date"]=1
            else:
                pay_sch["past_date"]=0
    related_tbl=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
    fund_date=""
    loan_status = get_loan_status_by_loan_id(loan_id)
    if related_tbl.fund_dt :
        fund_date=datetime.date.strftime(related_tbl.fund_dt, "%Y-%m-%d")
    else:
        return HttpResponse('Loan is not yet ACTIVE!')
#    import pdb;pdb.set_trace()
    prorata_status=payment_flag
    if payment_flag and loan_status in ('CLOSED','PRECLOSED','POSTCLOSED'):
        prorata_status=0

    productClassification = dbtmsapi.get_product_classification(loan_id)
    return render_to_response("custdetail/payment_schedule_iframe.html",
            {"loan_id":loan_id,"cust_id":cust_id,"loan_status":loan_status,"update_flag":update_flag,
            "payment_schedule":payment_schedule,"status":status,
            "no_records":no_records,"payment_types":payment_type,
             "payment_flag":payment_flag,'fund_dt':fund_date,"prorata_flag":prorata_flag,
             "current_date":current_date,'prorata_status':prorata_status,"productClassification":productClassification})
payment_schedule = maintenance_deco_popups(payment_schedule)

'''
This functionality has been replaced by class WaiversView
def waiveoff(request):
    """
    This renders iframe for Payment schedule where payment information \
    can be viewed and also overridden flag field set to 1.
    """
    #   Fetches the end status, for which the payments,pre-payments,payment caledar & pay dates iframe should not displayes

    update_flag=0

    if request.method=='GET':
        loan_id = request.GET['loan_id']
        if "update_flag" in request.GET:
            update_flag=request.GET["update_flag"]
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id=request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    payment_schedule=[]
    payment_type={"select":"select","PRNDUE":"Principal Due","INTCAPLZD":"Interest Capitalized","ARRFEE":"Arrear Fee","DEFLTFEE":"Default Fee","TERMNFEE":"Termination Fee","XTRPREPYMT":"Extra Prepayment"}
    no_records=""

    username=request.session['username']
    payment_flag=isEndStatus(loan_id)
    current_date=str(datetime.date.today())

    status=""
    payment_id=[]
    chk_box_key=[]
    dict= request.POST
    waiveoff_type = request.GET['id']
#    print id
    prorata_flag = 1
    pdlLoan=Loan_Info.objects.filter(loan=loan_id,override_flag=0).order_by("-create_dt")[0]
    if(pdlLoan.relevant_dt is None):
        prorata_flag = 0
    else:
        if(pdlLoan.now_dt is None and (datetime.datetime.today() - pdlLoan.relevant_dt).days > 14):
            prorata_flag = 0

    if request.method=='POST':
        cur_date = datetime.datetime.now()
        for k,v in dict.iteritems():
            if v=='on':
                chk_box_key.append(k)
        for item in chk_box_key:
                if not ("payment_chk" in item):

                    status="Please check the correct record to be waiveoff"

                else:
                    index_payment_chk=item[11:]
                    if waiveoff_type == 'paymentcalendar':
                        payment_id.append(int(dict["payment_id"+index_payment_chk]))
                    else:
                        payment_id.append(int(dict["downpayment_id"+index_payment_chk]))
        if payment_id :
            if waiveoff_type == 'paymentcalendar':
                status=pcfunc.waiveoff(username, payment_id, cur_date)
                request.session["update_flag"]=1

                ## for daily_run phase 2: whenever there is a transaction, paydates change, status change
                #loan_id shd be flagged in DeltaMatrix table
                daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
                if isDailyRunStarted(date_of_run=daily_run_date):
                    updateDeltaMatrix(loan_id,'transaction')

                return HttpResponseRedirect("/info/payment_schedule/?loan_id="+str(loan_id)+"&cust_id="+str(cust_id))
            elif waiveoff_type == 'downpayment':
                status=dpfunc.dpwaiveoff(username, payment_id, cur_date)
                request.session["update_flag"]=1
                return HttpResponseRedirect("/info/down_payments/?loan_id="+str(loan_id))
        if waiveoff_type == 'paymentcalendar':
            payment_calender_records=pcfunc.getpcdata(loan_id)

            status=pcfunc.waiveoff(username, payment_id, cur_date)
            update_flag=1
            return HttpResponseRedirect("/info/payment_schedule/?update_flag="+str(update_flag)+"&loan_id="+str(loan_id))

            # if isinstance(payment_calender_records,str) or isinstance(payment_calender_records,unicode) :
            #         no_records=payment_calender_records
            # else:
            #         payment_schedule=payment_calender_records
            #         for pay_sch in payment_schedule:
            #             if str(pay_sch["payment_dt"])<current_date:
            #                 pay_sch["past_date"]=1
            #             else:
            #                 pay_sch["past_date"]=0
            return render_to_response("custdetail/payment_schedule_iframe.html",{"update_flag":update_flag,"payment_type":payment_type,"payment_schedule":payment_schedule,"set_edit":1,"status":status,"no_records":no_records,"payment_flag":payment_flag,"prorata_flag":prorata_flag})

        elif waiveoff_type == 'downpayment':
            payment_calender_records=dpfunc.getdpdata(loan_id)

            if isinstance(payment_calender_records,str) or isinstance(payment_calender_records,unicode) :
                no_records=payment_calender_records
            else:
                payment_schedule=payment_calender_records
                for pay_sch in payment_schedule:
                    if str(pay_sch["downpayment_dt"])<current_date:
                        pay_sch["past_date"]=1
                    else:
                        pay_sch["past_date"]=0
            return render_to_response("custdetail/downpayment_iframe.html",{"update_flag":update_flag,"payment_type":payment_type,"payment_schedule":payment_schedule,"set_edit":1,"status":status,"no_records":no_records,"payment_flag":payment_flag,"prorata_flag":prorata_flag})
#    return render_to_response("custdetail/downpayment_iframe.html",{"loan_id":loan_id,"update_flag":update_flag,"payment_type":payment_type,"payment_schedule":payment_schedule,"set_edit":1,"status":status,"no_records":no_records,"payment_flag":payment_flag,"prorata_flag":prorata_flag})
waiveoff = maintenance_deco_popups(waiveoff)
'''

def generate_schedule(request):
    """
    This renders iframe for Payment schedule where payment information \
    can be viewed and also overridden flag field set to 1.
    """
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        schedule_type = request.GET['schedule_type']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        schedule_type ='Loan'
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    currentDate = datetime.datetime.now()
    bal_infm = {}
    payments_obj = pcfactory.getpmobj()
    pre_date=currentDate-timedelta(days=1)
    due_amt = payments_obj.calculate_due_amount(loan_id,pre_date)
    payments_obj.db.commit()
    payments_obj.db.close()
    bal_infm=get_balance_dtls(loan_id)[0]
    OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
    bal_infm['OB']=OB
    bal_infm['OA']=due_amt
    schedule = {}
    index = 0
    payment_type={"select":"select","PRNDUE":"Principal Due","INTCAPLZD":"Interest Capitalized","ARRFEE":"Arrear Fee","DEFLTFEE":"Default Fee","TERMNFEE":"Termination Fee","XTRPREPYMT":"Extra Prepayment"}
    payment_calendar_entries = PaymentCalendar.objects.filter(loan = loan_id,override_reason__isnull = True)
    if schedule_type=='Downpayment':
        schedule = downpaymentschedulegenerator.generate_downpaymentschedule(loan_id)
    elif schedule_type=='Loan':
        Schedule1 = payment_schedule_with_accounting(loan_id,schedule_req ='Schedule1')['schedule_with_future']
#        Schedule2 = payment_schedule_with_accounting(loan_id,schedule_req ='Schedule2')['schedule_with_future']
#        Schedule2 = paymentschedulegenerator.generate_paymentschedule(loan_id)["Schedule2"]
        Schedule2 = {}
        Schedule1accounting = {}
        Schedule2accounting = {}
        list_of_records1 = []
        list_of_records2 = []
        sorted_sch1 = []
        sorted_sch2 = []

        for cyle_key,cycle_rec in Schedule1.iteritems():
            for rec in cycle_rec:
                tmp_list1 = [cyle_key]
                tmp_list1.extend(rec)
                list_of_records1.append(tmp_list1)
        for cyle_key,cycle_rec in Schedule2.iteritems():
            for rec in cycle_rec:
                tmp_list2 = [cyle_key]
                tmp_list2.extend(rec)
                list_of_records2.append(tmp_list2)

        index_dict = {'cycle_sort':0,'date_sort':2}

        if request.method == "POST" and 'date_sort' in request.POST:
            sort_key = "date_sort"
        else:
            sort_key = 'cycle_sort'
        index = index_dict[sort_key]
        # here we sort the original schedule in to datesort or cycle sort for sch1
        for record in list_of_records1:
            if sorted_sch1 and sorted_sch1[-1] and sorted_sch1[-1][-1][index]==record[index]:
                sorted_sch1[-1].append(record)
            else:
                sorted_sch1.append([record])
        # here we sort the original schedule in to datesort or cycle sort for sch2
        for record in list_of_records2:
            if sorted_sch2 and sorted_sch2[-1] and sorted_sch2[-1][-1][index]==record[index]:
                sorted_sch2[-1].append(record)
            else:
                sorted_sch2.append([record])
        for sorted_group in sorted_sch1:
            x = Decimal(0.00)
            y = Decimal(0.00)
            for record in sorted_group:
                x+= record[3]
                y+= record[5]
            Schedule1accounting[record[index]] = (x,y)
        for sorted_group in sorted_sch2:
            x = Decimal(0.00)
            y = Decimal(0.00)
            for record in sorted_group:
                x+= record[3]
                y+= record[5]
            Schedule2accounting[record[index]] = (x,y)
        datelist1 = []
        datelist2 = []
        new_sorted_sch1 = []
        new_sorted_sch2 = []
        if index == 2:
            for dategroup in sorted_sch1:
                datelist1.append(dategroup[0][2])
            datelist1.sort()
            for date in datelist1:
                for group in sorted_sch1:
                    if date == group[0][2]:
                        new_sorted_sch1.append(group)
            for dategroup in sorted_sch2:
                datelist2.append(dategroup[0][2])
            datelist2.sort()
            for date in datelist2:
                for group in sorted_sch2:
                    if date == group[0][2]:
                        new_sorted_sch2.append(group)
            sorted_sch1 = new_sorted_sch1
            sorted_sch2 = new_sorted_sch2
        schedule['Schedule1'] = sorted_sch1
        schedule['Schedule2'] = sorted_sch2

    return render_to_response("custdetail/generate_popup.html",{"loan_id":loan_id,"schedule":schedule,
                                "payment_type":payment_type,"flag":0,"Schedule1accounting":Schedule1accounting,
                                "Schedule2accounting":Schedule2accounting,"index":index,"result":bal_infm})


def pay_dates(request):
    if request.method=='GET':
        loanid = request.GET['loan_id']
    elif request.method=='POST':
        loanid = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    payment_type_abr={"LNCYC":"Loan Cycle","DWNPMT":"Downpayment",
                      "STCYC":"Statement Cycle"}
    payment_flag=isEndStatus(loanid)
    #   Fetches the end status, for which the payments,pre-payments,payment caledar & pay dates iframe should not displayes

    dict=[]
    current_date=str(datetime.date.today())
    username=request.session['username']
    chk_box_key=[]
    post_attrib=request.POST
    if request.POST.get('reason',False)=='others':
        reason=post_attrib["detail_reason"]
    else:
        reason=request.POST.get('reason',False)

    product_details = get_product_details_of_loan(loanid)
    product_classification = product_details['product_classification']
    statement_breather_period = product_details['statement_breather_period']

    payments_rec = Payments.objects.filter(loan=loanid)[0]
    due_date = payments_rec.due_date
    suppress_till_date = payments_rec.suppress_till_date

    cur_date = str(datetime.datetime.now())
    loan_latest_obj = LoanLatest.objects.filter(loan_id=loanid)[0]
    product_name = loan_latest_obj.product_id
    account_cust_id = loan_latest_obj.account_cust_id
    cycle_gp = Product.objects.filter(product_id = product_name)[0].cycle_grace_period + 1
    if request.method=='POST':
        for k,v in post_attrib.iteritems():
            if v=='on':
                chk_box_key.append(k)
        paydate_list = PayDates.objects.filter(loan = loanid,override_flag=0).order_by("cycle","-payment_type")

        paydates_id = False
        pc_obj = pcfactory.getpcobj()
        curs = pc_obj.db.getcursor()

        if product_classification == 'LOC':
            update_payments_table = False
            update_suppress_till_date = False
            updated_statements_dict = {'loan_id':loanid,
                                       'account_cust_id':account_cust_id}

            for item in chk_box_key:
                index_payment_chk=item[11:]

                for pay_dates in paydate_list:

                    if pay_dates.payment_type == 'LNCYC':

                        if (str(pay_dates.cycle)==str(post_attrib["payment_cycle"+  index_payment_chk])) and  (str(pay_dates.paydate)!=str(post_attrib["payment_dt" +index_payment_chk])):
                            new_due_date = post_attrib["payment_dt" +index_payment_chk]
                            new_statement_date = str(toDate(new_due_date) - datetime.timedelta(days=statement_breather_period))

                            # Check if pay-date to be changed is used as
                            # a reference in Payments table fields
                            if payments_rec.arrangement_type in (1,2,3,4):
                                if payments_rec.delin_suppress_tilldate == pay_dates.paydate:
                                    update_payments_table = True
                                    old_pay_date = pay_dates.paydate
                                    date_to_be_updated = toDate(new_due_date)

                                if payments_rec.suppress_till_date == pay_dates.paydate - datetime.timedelta(days=1):
                                    update_suppress_till_date = True
                                    old_suppress_date = pay_dates.paydate
                                    new_suppress_date = toDate(new_due_date) - datetime.timedelta(days=1)

                            # Update new pay-dates
                            paydates_id = update_paydate(post_attrib["loan_id"+index_payment_chk],int(post_attrib["payment_cycle"+index_payment_chk]),new_due_date,"Date Changed",post_attrib["payment_type"+index_payment_chk],4,cur_date,username,con_trandb=pc_obj.db,reason=reason)

                            #update payment calendar with the new paydate
                            sql="select * from PaymentCalendar where loan_id=%s and payment_nbr=%s and override_flag=0 and payment_type in ('PRNDUE','INTCAPLZD','XTRPREPYMT','RMPB', 'ARRFEE')"
                            res=pc_obj.db.processquery(query=sql, curs=curs,args=(loanid,pay_dates.cycle), fetch=True)
                            for record in res:
                                pc_obj.manualeditrecord(record["payment_id"],loanid,post_attrib["payment_dt"+index_payment_chk],record["payment_nbr"],record["payment_amt"] ,record ["payment_type"],username,reason=pcconfig.OVERRIDE_VALUE["ddchg"],date_elem=cur_date,returnprikey = 1)

                            # Update new statement date
                            update_paydate(post_attrib["loan_id"+index_payment_chk],int(post_attrib["payment_cycle"+index_payment_chk]),new_statement_date,"Date Changed",'STCYC',4,cur_date,username,con_trandb=pc_obj.db,reason=reason)
                            updated_statements_dict[pay_dates.cycle] = str(new_statement_date)

            # Update Payments table with new paydate
            if update_payments_table:
                update_paydate_in_payments_table(loanid, old_pay_date,
                                                 date_to_be_updated,
                                                 payments_rec, username, reason='PAYDATE CHANGED')

                update_future_waiver_date(loanid, old_pay_date-datetime.timedelta(days=statement_breather_period),
                                          date_to_be_updated-datetime.timedelta(days=statement_breather_period),
                                          username)
            # If old_suppress_date != old_pay_date, waterfall is suppressed for some other reason than PH/CH. Update it.
            if update_suppress_till_date and old_suppress_date != old_pay_date:
                update_paydate_in_payments_table(loanid, old_suppress_date,
                                                 new_suppress_date,
                                                 payments_rec, username, reason='PAYDATE CHANGED')
            pc_obj.db.commit()
            pc_obj.db.close()

            if updated_statements_dict:
                updated_statements_dict.update(loanid=loanid,
                                               account_cust_id=account_cust_id)
                LOC_sendStatementsToUE([updated_statements_dict])

        else:
            for item in chk_box_key:
                index_payment_chk=item[11:]
                for pay_dates in paydate_list:
                    if (str(pay_dates.cycle)==str(post_attrib["payment_cycle"+index_payment_chk])) and (str(pay_dates.paydate)!=str(post_attrib["payment_dt"+index_payment_chk])):
                        paydates_id = update_paydate(post_attrib["loan_id"+index_payment_chk],int(post_attrib["payment_cycle"+index_payment_chk]),post_attrib["payment_dt"+index_payment_chk],"Date Changed",post_attrib["payment_type"+index_payment_chk],4,cur_date,username,reason=reason)
                        #update payment calendar with the new paydate
                        sql="select * from PaymentCalendar where loan_id=%s and payment_nbr=%s and override_flag=0 and payment_type in ('PRNDUE','INTCAPLZD','XTRPREPYMT','RMPB')"
                        res=pc_obj.db.processquery(query=sql, curs=curs,args=(loanid,pay_dates.cycle), fetch=True)
                        for record in res:
                            pc_obj.manualeditrecord(record["payment_id"],loanid,post_attrib["payment_dt"+index_payment_chk],record["payment_nbr"],record["payment_amt"] ,record ["payment_type"],username,reason=pcconfig.OVERRIDE_VALUE["ddchg"],date_elem=cur_date,returnprikey = 1)
            pc_obj.db.commit()
            pc_obj.db.close()
        if paydates_id:
            #update gcm notes for paydate change
            case_id=get_case_id_by_entity_id(post_attrib["loan_id"],'LOAN')
            log_id=get_logid_by_caseid(case_id)
            notes_id=add_gcm_notes(log_id["log_id"],"PAYDATE CHANGE",reason,username,cur_date)
            ## for daily_run phase 2: whenever there is a transaction, paydates change, status change
            #loan_id shd be flagged in DeltaMatrix table
            daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
            if isDailyRunStarted(date_of_run=daily_run_date):
                updateDeltaMatrix(loanid,'paydates')

        return HttpResponseRedirect("/info/pay_dates/?loan_id="+str(loanid))


    paydate_list = PayDates.objects.filter(loan = loanid,override_flag=0).order_by("cycle","-payment_type")
#commenting as we don't need to pass future cycles for the time being
#     if product_classification == 'LOC':
# 
#         paydate_list = list(paydate_list)
# 
#         loan_details = Loan_Info.objects.filter(loan=loanid, override_flag=0)[0]
#         repay_frequency=loan_details.repayment_frequency.upper()
#         grace_period = product_details['breather_time']
# 
#         future_paydate_list = getPayCycle(frequency=repay_frequency, cycles=2, gracePeriod=grace_period, firstUserDate=paydate_list[1].paydate, secondUserDate='', payoutDate=paydate_list[-1].paydate)
# 
#         logger.info("future_paydate_list : " + str(future_paydate_list))
# 
#         temp_dict = {
#              'paydates':{},
#              'statementdates':[x-datetime.timedelta(days=10) for x in future_paydate_list]
#              }
# 
#         i =1
#         for elem in future_paydate_list:
#             temp_dict['paydates'][i] = elem
#             i+=1
# 
#         logger.info("Future Paydate and Statement dates : " + str(temp_dict))
# 
#         future_paydates_dict = temp_dict['paydates']
#         future_paydates = future_paydates_dict.values()
#         future_statement_dates = temp_dict['statementdates']
# 
#         for cycle_no in xrange(len(future_paydates)):
#             statement_cycle = PayDates(loan_id=loanid,paydate=future_statement_dates[cycle_no],payment_type='STCYC')
#             paydate_list.append(statement_cycle)
#             paydate_cycle = PayDates(loan_id=loanid,paydate=future_paydates[cycle_no],payment_type='LNCYC')
#             paydate_list.append(paydate_cycle)

    for pay_date in paydate_list:
        if str(pay_date.paydate) < current_date:
            pay_date.override_flag=1
        elif product_classification in ('LOC'):
            if pay_date.payment_type == 'STCYC':
                pay_date.override_flag = 1
            elif due_date and pay_date.paydate <= due_date:
                pay_date.override_flag = 1
            elif pay_date.payment_holiday_flag == 1:
                pay_date.override_flag = 1

    related_tbl=Loan_Info.objects.filter(loan=loanid,override_flag=0)[0]
    fund_date=""
    if related_tbl.fund_dt:
        fund_date=datetime.date.strftime(related_tbl.fund_dt, "%Y-%m-%d")

    return render_to_response("custdetail/pay_dates_iframe.html",{"paydate_list":paydate_list,
                                                                  "payment_flag":payment_flag, 'due_date':str(due_date),
                                                                 "fund_date":fund_date,'loan_id':loanid,
                                                                 'payment_type_abr':payment_type_abr,'current_date':current_date,
                                                                 'change_reasons': paydate_change_reasons,'cycle_grace_period':cycle_gp,
                                                                 'product_classification': product_classification,
                                                                 'statement_breather_period':statement_breather_period,
                                                                 'suppress_till_date': suppress_till_date})
pay_dates = maintenance_deco_popups(pay_dates)
def prepaid_card(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id=request.GET["cust_id"]
        member_id = Customer.objects.filter(cust_id=cust_id)[0].member_id
        loan_info=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
        bureau_obj = Ext_Bureau_Info.objects.filter(loan =loan_id,\
                            override_flag=0,bureau_name='PDC')
        if bureau_obj:
            token_id = bureau_obj[0].bureau_id
        else:
            token_id = None
        responseDict={}
        physical_card_status = None
        fund_to=loan_info.fund_to
        Source = Loan.objects.filter(loan_id = loan_id)[0].lead_source
        status_cd = get_loan_status_by_loan_id(loan_id)
        if fund_to == "PREPAID CARD" and status_cd not in loanstatusconfig.PDC_STATUS:
            try:
                PDC_Dict = {'AccountID':member_id,'CardID':token_id,'Source':Source}
                responseDict = cardInfoFn(PDC_Dict)
                pc_stat = responseDict['Is_PC_Requested']
                card_typ = responseDict['CardType']
                if pc_stat:
                    physical_card_status = PHYSICAL_CARD_STATUS[pc_stat][card_typ]
                else:
                    physical_card_status = PHYSICAL_CARD_STATUS[0]
            except:
                responseDict = {'Error':True}
        else:
            responseDict["CardID"]=0
    return render_to_response("custdetail/prepaid_card_iframe.html",\
        {"responseDict":responseDict,"loan_id":loan_id,"cust_id":cust_id,
        'physical_card':physical_card_status})

def pdc_tran_popup(request):
    if request.method=='GET':
        cust_id=request.GET["cust_id"]
        loan_id = request.GET['loan_id']
    tran_dict_list = []
    member_id = Customer.objects.filter(cust_id=cust_id)[0].member_id
    msg = ''
    Source = Loan.objects.filter(loan_id = loan_id)[0].lead_source
    bureau_obj = Ext_Bureau_Info.objects.filter(loan =loan_id,\
                            override_flag=0,bureau_name='PDC')
    if bureau_obj:
        token_id = bureau_obj[0].bureau_id
    else:
        token_id = None
    PDC_Dict = {"AccountID":member_id,'CardID':token_id,'Source':Source}
    try:
        responseDict = cardStatementFn(PDC_Dict)
    except:
        responseDict = {'Error':True}
    error_flag = responseDict['Error']
    if not error_flag:
        if not isinstance(responseDict['Transactions'],list):
            tran_dict_list.append(responseDict['Transactions'])
        else:
            tran_dict_list = responseDict['Transactions']
    else:
        msg = 'Tran Info Currently Not Available !'
    for item in tran_dict_list:
        if ('TxnTime' in item) and (item['TxnTime']):
            item['TxnTime'] = item['TxnTime'][:2] + ':' + item['TxnTime'][2:]
        else:
            item['TxnTime'] = ''
    return render_to_response("custdetail/pdc_tran_popup.html",{"tran_dict_list":tran_dict_list,'msg':msg,'error_flag':error_flag})

def other_loans(request):
    loan_list = []
    username=request.session['username']
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
#    elif request.method=='GET':
#        loan_id = request.POST['loan_id']
#        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    account_id = request.session['accountid']
    store_cust_id1=Customer.objects.filter(cust_id=cust_id)[0].store_cust_id
    customer_objs=Customer.objects.filter(store_cust_id=store_cust_id1)

    #     product_id = Loan.objects.filter(cust_id = cust_id)[0].product
    case_list=[]
    for customer in customer_objs:
        cust_case_id=get_case_id_by_entity_id(customer.cust_id,'CUSTOMER')
        loan_case_ids=get_related_loan_case_id(cust_case_id)
        for cases in loan_case_ids:
            case_list.append(cases)
    for case_id in case_list:
        loan_id1=get_entity_id_by_case_id(case_id)
        loan_res1 = Loan.objects.filter(loan_id=loan_id1)
        new_cust_id = LoanLatest.objects.filter(loan_id = loan_id1)[0].cust_id

        cust_details = Customer_Basic_Info.objects.filter(cust = new_cust_id, override_flag = 0)
        customer_name = str(cust_details[0].first_name) + ' ' + str(cust_details[0].last_name)
        post_code = Address_Info.objects.filter(cust = new_cust_id, override_flag = 0)[0].postCode

        privilage_check = check_user_privilege_on_store_id(username,loan_res1[0].store_id)

        if privilage_check:
            if loan_id1 !=int(loan_id):
                loan_res = Loan.objects.filter(loan_id=loan_id1,account=account_id)
                #check_store_underuser_priv(loan_res.store_id,username)
                #check_user_privilege_on_store_id(loan_res.store_id, username)
                for loan in loan_res:
                    if loan:
                        loan_data=[]
                        loan_data.append(loan.loan_id)
                        loan_data.append(loan.loan_type)
                        loan_data.append(loan.product.product_id)
                        loan_case_id=get_case_id_by_entity_id(loan.loan_id,'LOAN')
                        loan_status=get_loan_status_by_loan_case_id(loan_case_id)
                        reason_cd=get_reason_code(loan_case_id,loan_status)
                        loan_data.append(loan_status)
                        loan_data.append(reason_cd)
                        loan_data.append(customer_name)
                        loan_data.append(post_code)
                        loan_pro_class=get_product_classification(loan.loan_id)
                        loan_data.append(loan_pro_class)
                        loan_list.append(loan_data)
                        
                        

    return render_to_response("custdetail/other_loan_iframe.html",\
    {'loan_list':loan_list,'loan_id':loan_id})

def amt_due(request):
    message=""
#   Fetches the end status, for which the payments,pre-payments,payment caledar & pay dates iframe should not displayes

    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    status=get_loan_status_by_loan_id(loan_id)
    if status in ("PARTIAL", "CALLED", "NOT CALLED"):
        return HttpResponse("Loan is not yet ACTIVE !")

    if status in queueconfig.END_STATUS:
        payment_flag = True
    else:
        payment_flag = False
#    payment_flag=isEndStatus(loan_id)
    fee_flag=None
    generate_flag=None
    virtual_cycle=0
    update_flag=0
    no_records=''


    if request.session.has_key("update_flag"):
        update_flag=request.session["update_flag"]
        del request.session["update_flag"]
    flag_torefresh_loan=0
    if request.session.has_key("flag_torefresh_loan"):
        update_flag=request.session["flag_torefresh_loan"]
        del request.session["flag_torefresh_loan"]
    payment_records=pcfunc.getpmdata(loan_id)
    generate_flags={0:"No Suppress",1:"Principal Suppress",2:"Interest Suppress",3:"P-I Suppress",4:"Fee Suppress",5:"F-P Suppress",6:"F-I Suppress",7:"F-I-P Suppress"}
    fee_flags={0:"No Fees",1:"Arrears Fees",2:"NOD Fees",3:"NOT Fees"}
    virtual_flags={0:"OFF", 1: "ON"}
    if isinstance(payment_records,str) or isinstance(payment_records,unicode):
        message="Loan is not yet Active"
        payment_records={}
    else:
        fee_flag=fee_flags[payment_records["fees_flag"]]
        generate_flag=generate_flags[payment_records["generate_flag"]]
        virtual_cycle = virtual_flags[payment_records["virtual_cycle"]]
    cxt = Context({"update_flag":update_flag,"generate_flag":generate_flag,"fee_flag":fee_flag,'message':message,'payment_records':payment_records,"payment_flag":payment_flag,'loan_id':loan_id,'virtual_cycle':virtual_cycle,'flag_torefresh_loan':flag_torefresh_loan})

    loanobj=Loan.objects.filter(loan_id=loan_id)[0]
    prodobj=Product.objects.filter(product_id=loanobj.product_id)[0]
    prod_classification = prodobj.product_classification
    logger.debug('Logging Product object '+str(prod_classification))
    isOB = isOutStandingBalance(loan_id)
    OB = get_amount_dtls(loan_id)
    transfer_flag = 0
    loaninfo = Loan_Info.objects.filter(loan=loan_id,fund_dt__isnull=False,override_flag=0)
    if loaninfo:
        transfer_flag = 1
    payment_calender_records=pcfunc.getpcdata(loan_id)
    if isinstance(payment_calender_records,str) or isinstance(payment_calender_records,unicode):
        no_records="Loan is not yet Active"
    cxt = Context({"isOB":isOB,"update_flag":update_flag,"generate_flag":generate_flag,"fee_flag":fee_flag,'message':message,'payment_records':payment_records,"payment_flag":payment_flag,'loan_id':loan_id,'virtual_cycle':virtual_cycle,'flag_torefresh_loan':flag_torefresh_loan,'status':status,'not_active':no_records,'transfer_flag':transfer_flag, 'OB':OB})

    custExclnFlag = 0
    loanExclnFlag = 0
    cpaSupressFlag = 'Required'
    cpaSupressDate = '-'
    cpaRenderDict = {'showResumeCPA':0,'cpaSupressFlag':'','cpaSupressDate':'','custExclnFlag':'','loanExclnFlag':'','lnSts':''}

    if request.session.has_key("username"):
        username=request.session['username']
    else:
        return HttpResponse("Session Expired")

    card_special_prev    = get_spl_privileges_by_usr_id(username,8)

    store_id=Loan.objects.filter(loan_id=loan_id)[0].store_id
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    try:
        hideRefundBtn = 0
        if prod_classification == 'LOC':
            sql = "select * from LOC_Draw where loan_id=%s and draw_status in ('READY TO PAY','SENT TO PAY')"%(loan_id)
            getReDraw = con.get_one_result(sql)
            
            if getReDraw:
                hideRefundBtn = 1
        
        sql = "select status_cd,entity_id,account_cust_id from GCMS_Data.gcm_case \
            join (select loan_id,account_cust_id,fund_dt,store_id from Loan_Latest \
            where account_cust_id = (select account_cust_id from Loan_Latest where loan_id=%s )) acc \
            on loan_id=entity_id and entity_type='loan' and acc.store_id='%s' \
            "%(loan_id,store_id)
        loanStatus = con.get_all_results(sql)

        if len(loanStatus):
            cust_id = loanStatus[0]['account_cust_id']
            #chkCPAFlag,cpaSupFlag,cpaSupRsn,cpaReinstFlag,cpaImmPullFlag,cpaUpdateFlag = dbtmsapi.update_cpa_status(cust_id,store_id,username,logger)

            cpaInfoDict = getTotalHitsFrmDriver(loanStatus,cust_id,store_id,username)
            if cpaInfoDict['cpa_suppress'] or cpaInfoDict['did_customer_contact']:
                cpaSupressFlag = 'Required'
            else:
                cpaSupressFlag = 'Not Required'

            if cpaInfoDict['reinstate_time']:
                cpaSupressDate = cpaInfoDict['reinstate_time']

            chkCPACnclQry = "select count(*) as cnt from CPA_cancellations where override_flag=0 and loan_id=%s"%(loan_id)
            cpaCnclLoan = con.get_one_result(chkCPACnclQry)

            if cpaCnclLoan['cnt']:
                loanExclnFlag = 1
            else:
                for loanDtls in loanStatus:
                    if loanDtls['status_cd'] in CUSTOMER_LEVEL_EXCLUSION_LIST:
                        custExclnFlag = 1
                        break
                    elif loanDtls['status_cd'] in LOAN_LEVEL_EXCLUSION_LIST and str(loanDtls['entity_id']) == str(loan_id):
                        loanExclnFlag = 1
                        break
        else:
            loanExclnFlag = 1
            cpaSupressFlag = 'Not Required'

        cpaRenderDict['cpaSupressFlag']= cpaSupressFlag
        cpaRenderDict['cpaSupressDate']= cpaSupressDate
        cpaRenderDict['custExclnFlag'] = custExclnFlag
        cpaRenderDict['loanExclnFlag'] = loanExclnFlag
        #cpaRenderDict['lnSts']         = loanStatus
    except Exception,e:
        cpaRenderDict['showResumeCPA']=0
        cpaSupressFlag= 'Technical Error. Please try again.'
        logger.debug('CPA :: Show Resume CPA :: '+str(traceback.format_exc()) + str(e))


    if str(card_special_prev).upper() == 'GRANT':
        cpaRenderDict['showResumeCPA']=1

    cxt = Context({'showResumeCPA':cpaRenderDict['showResumeCPA'],'cpaSupressFlag':cpaRenderDict['cpaSupressFlag'],\
               'cpaSupressDate':cpaRenderDict['cpaSupressDate'],'custExclnFlag':cpaRenderDict['custExclnFlag'],\
               'loanExclnFlag':cpaRenderDict['loanExclnFlag'],"isOB":isOB,"update_flag":update_flag,\
               "generate_flag":generate_flag,"fee_flag":fee_flag,'message':message,'payment_records':payment_records,\
                   "payment_flag":payment_flag,'loan_id':loan_id,'virtual_cycle':virtual_cycle,\
                   'flag_torefresh_loan':flag_torefresh_loan,'status':status,\
                   'not_active':no_records,'transfer_flag':transfer_flag,'OB':OB,'cust_id':cust_id,'store_id':store_id,'username':username,'prod_classification':prod_classification,'hideRefundBtn':hideRefundBtn})

    return render_to_response("custdetail/amt_due_iframe.html",cxt)
amt_due = maintenance_deco_popups(amt_due)

def add_notes_popup(request,offset):
    """
    This renders popup to Add notes where loan or customer notes  \
    can be added to gcm_notes table.
    """
    try:
        gcm_notes.info(":: Inside add_note_popup() ::")
        offset=int(offset)
        gcm_notes.info(":: Inside add_note_popup():: Updating notes based on offset: "+str(offset)+"::")
        status=""
        if request.method=='GET':
            gcm_notes.info(":: Inside add_note_popup() :: Inside Get request ::")
            loan_id=request.GET["loan_id"]
            cust_id=request.GET["cust_id"]
        elif request.method=='POST':
            gcm_notes.info(":: Inside add_note_popup() :: Inside post Request ::")
            loan_id=request.POST["loan_id"]
            cust_id=request.POST["cust_id"]
        else:
            gcm_notes.info(":: Inside add_note_popup() :: Errror response  - Loan ID is Missing check with Back End Team! ::")
            return HttpResponse('Loan ID is Missing check with Back End Team!')
        
        store_id=Loan.objects.filter(loan_id=loan_id)[0].store_id
        product_id = Loan.objects.filter(loan_id=loan_id)[0].product_id
        product_classification = Product.objects.filter(product_id=product_id)[0].product_classification
        
        if product_classification != 'LOC':
            product_classification = 'LS'
        else:
            product_classification  = 'LOC'
            
        notes_questions = queueconfig.Notes_Questions[product_classification]
        
        gcm_notes.info(":: Inside add_note_popup() :: Loan id "+str(loan_id)+"Store id "+str(store_id)+\
                       "product classification "+str(product_classification)+"Notes questions "+str(notes_questions)+"::") 
        
        SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=False
        if store_id=="LS":      # show manual underwriting note summary only for LS
            SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=True
        summary = queueconfig.NOTE_SUMMARIES
        manual_underwriting_summary=queueconfig.MANUAL_UNDERWRITING_NOTE_SUMMARIES
        notes_reason_category = queueconfig.NOTES_REASON_CATEGORY
        notes_reason_code = queueconfig.NOTES_REASON_CODE
        notes_reason_category_list = queueconfig.NOTES_REASON_CATEGORY.keys()

        summary[0] = "Select"
        
        offset=int(offset)
         
        if offset==1:
#             status=""
#             if request.method=='GET':
#                 loan_id=request.GET["loan_id"]
#                 cust_id=request.GET["cust_id"]
#             elif request.method=='POST':
#                 loan_id=request.POST["loan_id"]
#                 cust_id=request.POST["cust_id"]
#             else:
#                 return HttpResponse('Loan ID is Missing check with Back End Team!')
#             store_id=Loan.objects.filter(loan_id=loan_id)[0].store_id
#             SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=False
#             if store_id=="LS":      # show manual underwriting note summary only for LS
#                 SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=True
#             summary = queueconfig.NOTE_SUMMARIES
#             manual_underwriting_summary=queueconfig.MANUAL_UNDERWRITING_NOTE_SUMMARIES
#             notes_reason_category = queueconfig.NOTES_REASON_CATEGORY
#             notes_reason_code = queueconfig.NOTES_REASON_CODE
#             notes_reason_category_list = queueconfig.NOTES_REASON_CATEGORY.keys()
#             summary[0] = "Select"
            
            if request.method=='POST':
                summary1 = request.POST['reasonCategory']
                reasonCode = request.POST['reason_code']
                username=request.session['username']
                check = request.POST.get('update_all_loans',False)
                create_date=datetime.datetime.now()
                if check:
                    case_id=get_case_id_by_entity_id(cust_id,'CUSTOMER')
                    log_id=get_logid_by_caseid(case_id)
                    detail_info= "["+store_id+"_"+loan_id+"]"+" "+ ":"+" " + request.POST['detail_info']
                else:
                    case_id=get_case_id_by_entity_id(loan_id,'LOAN')
                    log_id=get_logid_by_caseid(case_id)
                    detail_info= request.POST['detail_info']
                notes_id=add_gcm_notes(log_id["log_id"],summary1,detail_info,username,create_date, reasonCode=reasonCode)
                if notes_id:
                    add_gcm_notes_checks(int(log_id["log_id"]),int(loan_id),  product_id, summary1,username,create_date,notes_questions, request.POST)
                    status="Note added sucessfully"
                    gcm_notes.info(":: Inside add_note_popup() :: Loan id "+str(loan_id)+ "Status"+ str(status)+"::")
                return HttpResponseRedirect("/info/add_notes_popup/type1?loan_id="+str(loan_id)+"&cust_id="+str(cust_id))
            return render_to_response("custdetail/add_notes_popup.html",{"status":status,"summary":summary,"manual_underwriting_summary":manual_underwriting_summary,"show_manual_underwriting_summary":SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES ,"offset":offset,"loan_id":loan_id,"cust_id":cust_id,"questions":notes_questions, "keys":notes_questions.keys(),"notes_reason_category":notes_reason_category,'notes_reason_code':notes_reason_code,'notes_reason_category_list':notes_reason_category_list})
        elif offset==2:
#             status=""
#             if request.method=='GET':
#                 loan_id=request.GET["loan_id"]
#                 cust_id=request.GET["cust_id"]
#             elif request.method=='POST':
#                 loan_id=request.POST["loan_id"]
#                 cust_id=request.POST["cust_id"]
#             else:
#                 return HttpResponse('Loan ID is Missing check with Back End Team!')
#             store_id=Loan.objects.filter(loan_id=loan_id)[0].store_id
#             SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=False
#             if store_id=="LS":      # show manual underwriting note summary only for LS
#                 SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=True
#             summary = queueconfig.NOTE_SUMMARIES
#             notes_reason_category = queueconfig.NOTES_REASON_CATEGORY
#             notes_reason_code = queueconfig.NOTES_REASON_CODE
#             notes_reason_category_list = queueconfig.NOTES_REASON_CATEGORY.keys()
#             manual_underwriting_summary=queueconfig.MANUAL_UNDERWRITING_NOTE_SUMMARIES
#             summary[0] = "Select"
            
            if request.method=='POST':
                summary1 = request.POST['reasonCategory']
                reasonCode = request.POST['reason_code']
                username=request.session['username']
                check = request.POST.get('update_all_loans',False)
                create_date=datetime.datetime.now()
                if check:
                    case_id=get_case_id_by_entity_id(cust_id,'CUSTOMER')
                    log_id=get_logid_by_caseid(case_id)
                    detail_info= "["+store_id+"_"+loan_id+"]"+" "+ ":"+" " + request.POST['detail_info']
                else:
                    case_id=get_case_id_by_entity_id(loan_id,'LOAN')
                    log_id=get_logid_by_caseid(case_id)
                    detail_info= request.POST['detail_info']
                notes_id=add_gcm_notes(log_id["log_id"],summary1,detail_info,username,create_date, reasonCode=reasonCode)
                if notes_id:
                    add_gcm_notes_checks(int(notes_id),int(loan_id),  product_classification, summary1,username,create_date,notes_questions, request.POST)
                    status="Note added sucessfully"
                    gcm_notes.info(":: Inside add_note_popup() :: Loan id "+str(loan_id)+ "Status"+ str(status)+"::")
                return HttpResponseRedirect("/info/add_notes_popup/type2?loan_id="+str(loan_id)+"&cust_id="+str(cust_id))
            return render_to_response("custdetail/add_notes_popup.html",{"status":status,"summary":summary,
                    "manual_underwriting_summary":manual_underwriting_summary,
                    "show_manual_underwriting_summary":SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES,
                    "offset":offset,"loan_id":loan_id,"cust_id":cust_id,"questions":notes_questions, "keys":notes_questions.keys(),"notes_reason_category":notes_reason_category,'notes_reason_code':notes_reason_code,'notes_reason_category_list':notes_reason_category_list})
    except Exception,e:
        msg = "Error in adding notes. Please contact back end team"        
        gcm_notes.info(":: Inside add_note_popup() :: Loan id "+str(loan_id)+ "Error"+ str(e)+ "::")
        return render_to_response("custdetail/add_notes_popup.html",{"msg":msg})      
add_notes_popup = maintenance_deco_popups(add_notes_popup)

def view_notes(request,offset):
    """
    This renders popup to View notes where loan or customer notes  \
    can be viewed from the gcm_notes table.
    """
    offset=int(offset)    
    if offset==1:
        username=request.session['username']
        status=""
        detail_notes=[]

        if request.method=='GET':
            loan_id=request.GET["loan_id"]
            cust_id=request.GET["cust_id"]
        elif request.method=='POST':
            loan_id=request.POST["loan_id"]
            cust_id=request.POST["cust_id"]
        else:
            return HttpResponse('Loan ID is Missing check with Back End Team!')
        case_id=get_case_id_by_entity_id(loan_id,'LOAN')
        temp=[]
        store_id=Loan.objects.filter(loan_id=loan_id)[0].store_id
        SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=False
        if store_id=="LS":      # show manual underwriting note summary only for LS
            SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES=True
        summary = queueconfig.VIEW_NOTE_SUMMARIES
        manual_underwriting_summary=queueconfig.MANUAL_UNDERWRITING_NOTE_SUMMARIES

        summary[0] = "All"
        res1=[]
        get_note=[]
        list_notef=[]
        customer_case_id=get_related_customer_case_id(int(case_id))[0]
        get_all_notes=list(getAllNotes(int(case_id),customer_case_id))
        #get all associated loans
        con = mysqldbwrapper.MySQLWrapper(config_file_path, 'TMS_DATA')
        sql="""select store_cust_id from GCMS_Data.gcm_case gc join GCMS_Data.gcm_case_links gcl on gc.case_id=gcl.related_case_id \
                    join TMS_Data.Customer cus on cus.case_id=gcl.case_id where entity_id='%s' """%(loan_id)
        con.unset_return_as_dict()
        res=con.get_all_results(sql)
        if res:
            sql="""select distinct entity_id,first_name,last_name,status_cd  from GCMS_Data.gcm_case gc join GCMS_Data.gcm_case_links gcl on gc.case_id=gcl.related_case_id join \
                    TMS_Data.Customer cus on cus.case_id=gcl.case_id  join TMS_Data.Customer_Basic_Info cbi on cus.cust_id=cbi.cust_id where store_cust_id='%s' and entity_type='loan'\
                    and override_flag=0 and entity_id!='%s'"""%(res[0][0],loan_id)
            res1=con.get_all_results(sql)

        for each_loan in res1:
            nloan_id=each_loan[0]
            ncase_id=get_case_id_by_entity_id(nloan_id,'LOAN')
            cust_case_id=get_related_customer_case_id(int(ncase_id))[0]
            note=getAllNotes(0,cust_case_id)
            for a in note:
                get_note.append(a)
        for i in get_note:
            list_note1=[]
            list_note2=[]
            for j in get_all_notes:
                if (i[3]<=j[3]):
                    list_note1.append(j)
                else:
                    list_note2.append(j)
            list_note1.append(i)
            list_notef=list_note1+list_note2
            if list_notef:
                get_all_notes=list_notef

        summary_selected = request.GET.get('summary_selected', None)
        if summary_selected and summary_selected !='All':
            note_summary=[]
            for k in get_all_notes:
                if k[7]==summary_selected:
                    note_summary.append(k)
            get_all_notes=note_summary
        else:
            summary_selected="All"

            if list_notef:
                get_all_notes=list_notef
        if request.method=='POST':
            request_parameters=request.POST
            summary_selected = request.POST['notes']
            create_date=datetime.datetime.now()
            username=request.session['username']

            if request.POST.has_key("Save"):
                getalllist_notes_id = request.POST.getlist('notes_id')
                getalllist_notes_id.sort()


                for index in getalllist_notes_id:
                    temp_param=index.split('@')
                    temp.append(temp_param[0])
                    temp.append(temp_param[1])
                    detail_notes.append(temp)
                    temp=[]

                for detail_note in detail_notes:
                    records={"username":username,"notesdetailed":request_parameters[detail_note[1]],"notes_id":int(detail_note[0])}
                    update_gcm_notes(records,create_date)

            return HttpResponseRedirect("/info/view_notes/type1?summary_selected="+str(summary_selected)+"&case_id="+str(case_id)+"&loan_id="+str(loan_id)+"&cust_id="+str(cust_id))
        return render_to_response("custdetail/view_notes.html",{"summary":summary,"manual_underwriting_summary":manual_underwriting_summary,"show_manual_underwriting_summary":SHOW_MANUAL_UNDERWRITING_NOTE_SUMMARIES,"offset":offset,"get_all_notes":get_all_notes,"summary_selected":summary_selected,"cust_id":cust_id,"loan_id":loan_id})
    elif offset==2:        
        username=request.session['username']
        status=""
        summary_selected="All"
        detail_notes=[]

        if request.method=='GET':
            if 'caseid' in request.GET:
                case_id= request.GET['caseid']
            loan_id=get_entity_id_by_case_id(int(case_id))
        elif request.method=='POST':
            case_id=request.POST["hidden_caseid"]
            loan_id=get_entity_id_by_case_id(int(case_id))
            summary_selected = request.POST['notes']

        temp=[]
        summary = queueconfig.VIEW_NOTE_SUMMARIES
        manual_underwriting_summary=queueconfig.MANUAL_UNDERWRITING_NOTE_SUMMARIES
        summary[0] = "All"

        res1=[]
        get_note=[]
        list_notef=[]
        customer_case_id=get_related_customer_case_id(int(case_id))[0]
        get_all_notes=list(getAllNotes(int(case_id),customer_case_id))
        #get all associated loans
        con = mysqldbwrapper.MySQLWrapper(config_file_path, 'TMS_DATA')
        sql="""select store_cust_id from GCMS_Data.gcm_case gc join GCMS_Data.gcm_case_links gcl on gc.case_id=gcl.related_case_id \
                    join TMS_Data.Customer cus on cus.case_id=gcl.case_id where entity_id='%s' """%(loan_id)
        con.unset_return_as_dict()
        res=con.get_all_results(sql)
        if res:
            sql="""select distinct entity_id,first_name,last_name,status_cd  from GCMS_Data.gcm_case gc join GCMS_Data.gcm_case_links gcl on gc.case_id=gcl.related_case_id join \
                    TMS_Data.Customer cus on cus.case_id=gcl.case_id  join TMS_Data.Customer_Basic_Info cbi on cus.cust_id=cbi.cust_id where store_cust_id='%s' and entity_type='loan'\
                    and override_flag=0 and entity_id!='%s'"""%(res[0][0],loan_id)
            res1=con.get_all_results(sql)

        for each_loan in res1:
            nloan_id=each_loan[0]
            ncase_id=get_case_id_by_entity_id(nloan_id,'LOAN')
            cust_case_id=get_related_customer_case_id(int(ncase_id))[0]
            note=getAllNotes(0,cust_case_id)
            for a in note:
                get_note.append(a)
        for i in get_note:
            list_note1=[]
            list_note2=[]
            for j in get_all_notes:
                if (i[3]<=j[3]):
                    list_note1.append(j)
                else:
                    list_note2.append(j)
            list_note1.append(i)
            list_notef=list_note1+list_note2
            if list_notef:
                get_all_notes=list_notef

        if summary_selected and summary_selected !='All':
            note_summary=[]
            for k in get_all_notes:
                if k[7]==summary_selected:
                    note_summary.append(k)
            get_all_notes=note_summary
        else:
            summary_selected="All"

            if list_notef:
                get_all_notes=list_notef

        return render_to_response("custdetail/view_notes.html",{"summary":summary,"manual_underwriting_summary":manual_underwriting_summary,"offset":offset,"get_all_notes":get_all_notes,"summary_selected":summary_selected,"case_id":case_id})
view_notes = maintenance_deco_popups(view_notes)
def add_comments_popup(request):
    """
    This renders popup to Add comments where loan or customer comments  \
    can be added to gcm_notes table.
    """
    status=""
    if request.method=='GET':
        loan_id=request.GET["loan_id"]
    elif request.method=='POST':
        loan_id=request.POST["loan_id"]
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    case_id=get_case_id_by_entity_id(loan_id,'LOAN')

    if request.method=='POST':
        detail_info=request.POST['detail_info']
        username=request.session['username']
        create_date=datetime.datetime.now()
        comments_id=add_gcm_case_comments(case_id,detail_info,username,create_date)
        if comments_id:
            status="Note added sucessfully"

    return render_to_response("custdetail/add_comments_popup.html",{"status":status,'loan_id':loan_id})


def done_rls_lock(request,offset):
    """
    Release the lock
    """
    offset=int(offset)
    username = request.session['username']
    menu = request.session['sessionmenu']
    pending_status=['IDENTITY CHECK DONE','EMPLOYER CHECK DONE','CARD CHECK DONE']
    remove_date=datetime.datetime.now()
    create_date=remove_date

    if offset==1 or offset==3:
        if request.method=="POST":
            loan_id=request.POST["loan_id"]
            accountID=request.session["accountid"]
            loanInfo=Loan.objects.filter(loan_id=loan_id)[0]
            portfolioID=loanInfo.store_id
            case_id=loanInfo.case_id
            review_time_post=request.POST["review_time"] or 00
            review_time_mins=request.POST["mins"] or 00
            #            To add review time in gcm_notes table
            pyroLock = 0
            if pyroLock:
                noOfStore = len(Store.objects.filter(account=accountID))
                for i in range(noOfStore):
                    port = queueconfig.PORT+i
                    url = "PYROLOC://localhost:%s/tmsqueue"%(str(port))
                    try:
                        pyroConnection = connect_pyro(url)
                        portfolioInstanceRunning = pyroConnection.getStore()
                        if portfolioID == portfolioInstanceRunning:
                            msg = None
                            break
                    except ProtocolError:
                        continue
                if portfolioID == portfolioInstanceRunning:
                    try:
                        lock = pyroConnection.releaseSemLock(case_id)
                    except ConnectionClosedError:
                        pyroConnection = connect_pyro(url)
                        pyroConnection.releaseSemLock(case_id)
                update_get_user_table_by_case_id(case_id,username,remove_date)
            else:
                unlockLead(case_id,username)
            if review_time_post or review_time_mins:
                review_time=datetime.datetime.now()+datetime.timedelta(hours=int(review_time_post),minutes=int(review_time_mins))
                update_gcm_case_log_review_time(case_id,review_time)
            if review_time_post or review_time_mins:
                log_id=get_logid_by_caseid(case_id)
                add_gcm_notes(log_id["log_id"],"Review Time","Please call him/her after  "+str(review_time_post)+" hrs "+str(review_time_mins)+" mins("+str(datetime.datetime.now()+datetime.timedelta(hours=int(review_time_post),minutes=int(review_time_mins)))+")",username,create_date)
        if offset==1:
            return HttpResponseRedirect('/loanqueue/newloan/')
        elif offset==3:
            return HttpResponseRedirect('/search/')
    else:
        pyroLock = 0
        if request.method=="POST":
            if request.POST.has_key("case_id"):
                case_ids=request.POST.getlist("case_id")
                for case_id in case_ids:
                    if pyroLock:
                        update_get_user_table_by_case_id(case_id,username,remove_date)
                    else:
                        unlockLead(case_id,username)
        return HttpResponseRedirect('/loanqueue/locked_loan/')

#@transaction.commit_manually
def cheque(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    msg = ''
    update_flag=0
    transaction_commit_flag=0
    status=get_loan_status_by_loan_id(loan_id)

    if request.session.has_key("update_flag"):
        update_flag=request.session["update_flag"]
        del request.session["update_flag"]

    if request.session.has_key('cheque_msg'):
        msg = request.session['cheque_msg']
        del request.session['cheque_msg']

    cheques, direct_deps = [], []
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        fund_flag =Loan_Info.objects.filter(loan=loan.loan_id, override_flag=0)
        loan_status= get_loan_status_by_loan_id(loan_id)
        if not fund_flag[0].booked_dt or loan_status=='BOOKED':
            if transaction_commit_flag:
                transaction.commit()
            else:
                transaction.rollback()
            return HttpResponse('Not Applicable')
        direct_deps = list(Direct_Deposit.objects.filter(loan=loan.loan_id))
        cheques = list(Cheque.objects.filter(loan=loan.loan_id, override_flag=0))
    except Loan.DoesNotExist:
        msg = "Invalid Loan!"
    except Exception, e:
        print e
    isOB = isOutStandingBalance(loan_id)

    if request.method=='POST':

        logger.info('cheque :: loan_id :: '+str(loan_id))
        create_date=datetime.datetime.now()
        try:
            waterfall_flag = pcfunc.waterfallcheck(loan.loan_id)
            if waterfall_flag:
                msg = "Waterfall is currently running. Please try later."
                raise Exception
            record_list = []
            new_record_list = []
            data = request.POST.copy()
            for k, v in data.iteritems():
                if v == 'on':
                    record_list.append(k)
            for rec in record_list:
                if rec.__contains__('record_nbr'):
                    idx = rec[10:]
                    if idx == u'0' and data['payment_method'+idx] == 'direct_dep':
                        new_record_list.append({'reference_id': data['reference_id'+idx],'payment_method':data['payment_method'+idx],'amount': data['amount'+idx],'receive_dt': data['receiving_dt'+idx]})
                    else:
                        new_record_list.append({'reference_id': data['reference_id'+idx],'payment_method':data['payment_method'+idx],'amount': data['amount'+idx],'receive_dt': data['receiving_dt'+idx],'status': data['status'+idx],'status_dt': data['status_dt'+idx]})
                else:
                    idx = rec[0]
                    if data['['+idx+',2]'] == 'direct_dep':
                        new_record_list.append({'reference_id': data['['+idx+',1]'],'payment_method':data['['+idx+',2]'],'amount':data['['+idx+',3]'],'receive_dt': data['['+idx+',4]']})
                    else:
                        new_record_list.append({'reference_id': data['['+idx+',1]'],'payment_method':data['['+idx+',2]'],'amount':data['['+idx+',3]'],'receive_dt': data['['+idx+',4]'],'status': data['['+idx+',5]'],'status_dt': data['['+idx+',6]']})

            for record in new_record_list:
                logger.info('cheque :: loan_id :: '+str(loan_id)+' :: record :: '+str(record))
                reference_id = record['reference_id']
                amount = record['amount']
                receive_dt = record['receive_dt']
                logid= get_log_id_by_loan_id(loan_id)
                if record['payment_method'] == 'cheque':
                    if reference_id and amount and receive_dt:
                        state_change_dt=record['status_dt'] or receive_dt
                        if record['status'] == "bounced":
                            bounced=1
                        elif record['status'] == 'cleared':
                            bounced=0
                        try:
                            refund_flag = 0
                            payment_flag = 0
                            cheque = Cheque.objects.get(cheque_nbr=reference_id, loan=loan, override_flag=0)
                            logger.info('cheque :: loan_id :: '+str(loan_id)+' :: Updating existing cheque ')
                            if cheque.bounce_flag != bounced or str(cheque.clear_dt) != state_change_dt:
                                if cheque.bounce_flag == 0 and bounced == 1:
                                    refund_flag = 1
                                    logger.info('cheque :: loan_id :: '+str(loan_id)+' :: Cheque bounced!! ')
                                elif cheque.bounce_flag == 1 and bounced == 0:
                                    payment_flag = 1
                                    logger.info('cheque :: loan_id :: '+str(loan_id)+' :: cheque cleared!! ')
                                cheque.override_flag=1
                                cheque.save()
                                new_cheque = Cheque(cheque_nbr=reference_id, cheque_amt=amount, \
                                                    receive_dt=receive_dt, clear_dt=state_change_dt, \
                                                    bounce_flag=bounced, override_flag=0, create_dt=create_date, \
                                                    loan=loan)
                                new_cheque.save()
                                if refund_flag:
                                    msg = pcfunc.refund(loan_id, new_cheque.cheque_nbr, state_change_dt, 0,
                                                        float(amount), 'CHEQUE', "", "",
                                                        request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["NORMALREFUND"],
                                                        done_on="BANK ACCOUNT")
                                    logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: response from refund :: '+str(msg))
                                    if msg.__contains__('FAILURE::'):
                                        raise CustomException, msg
                                    add_gcm_notes(logid,"Cheque","Cheque with "+str(amount)+" has bounced on "+str(state_change_dt),
                                                  request.session['username'],create_date)
                                    request.session['cheque_msg'] = msg
                                    request.session["update_flag"]=1
                                if payment_flag:
                                    msg = pcfunc.recvmoney(loan_id,cheque.cheque_nbr, receive_dt, float(amount), 0,
                                                    'CHEQUE','', '', request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"],done_on="BANK ACCOUNT")
                                    if msg.__contains__('FAILURE::'):
                                        raise CustomException, msg
                                    add_gcm_notes(logid,"Cheque","A cheque was received with amount "+str(amount)+" on "+str(receive_dt),
                                                  request.session['username'],create_date)
                                    request.session['cheque_msg'] = msg
                                    request.session["update_flag"]=1
                            else:
                                logger.info('cheque :: loan_id :: '+str(loan_id)+' :: No changes made!  ')

                        except Cheque.DoesNotExist:
                            try:
                                logger.info('cheque :: loan_id :: '+str(loan_id)+' :: Adding new cheque ')
                                cheque = Cheque(cheque_nbr=reference_id, cheque_amt=amount, \
                                                receive_dt=receive_dt, clear_dt=state_change_dt, \
                                                bounce_flag=0, override_flag=0, create_dt=create_date, \
                                                loan=loan)
                                cheque.save()
                                msg = pcfunc.recvmoney(loan_id,cheque.cheque_nbr, receive_dt, float(amount), 0,
                                                'CHEQUE','', '', request.session['username'],create_date,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"],done_on="BANK ACCOUNT")
                                logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: response from recvmoney :: '+str(msg))
                                if msg.__contains__('FAILURE::'):
                                    raise CustomException, msg
                                add_gcm_notes(logid,"Cheque",str(amount)+" has recieved as a cheque on "+str(receive_dt),
                                              request.session['username'],create_date)
                                request.session['cheque_msg'] = msg
                                request.session["update_flag"]=1

                            except CustomException, e:
                                request.session['cheque_msg'] = e
                                delete_transaction(loan_id, cheque.cheque_nbr, float(amount),0, 'cheque')
                                transaction.rollback()
#                                return HttpResponseRedirect('/info/cheque/')
                            except Exception, e:
                                request.session['cheque_msg'] = "Failed, Please try again later."
                                transaction.rollback()
                                logger.info('cheque :: loan_id :: '+str(loan_id)+' :: '+str(traceback.format_exc()))
#                                return HttpResponseRedirect('/info/cheque/')
                            else:
                                transaction.commit()
                                transaction_commit_flag=1
                                chk_cc_paid_not=Downpayments.objects.filter(loan=loan_id,override_flag=0,downpayment_type='CC')
                                if chk_cc_paid_not:
                                    if chk_cc_paid_not[0].paid_amt>0:
                                          flag=1
                                    else:
                                          flag=0
                                    updateCreditCheckStatus(loan_id,flag)

#                                return HttpResponseRedirect('/info/cheque/')

                        except CustomException, e:
                            request.session['cheque_msg'] = e
                            delete_transaction(loan_id, cheque.cheque_nbr, 0, float(amount),'cheque')
                            transaction.rollback()
#                            return HttpResponseRedirect('/info/cheque/')
                        except Exception, e:
                            transaction.rollback()
                            request.session['cheque_msg'] = "Failed!! Please try again!!"
                            logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: '+str(traceback.format_exc()))
#                            return HttpResponseRedirect('/info/cheque/')
                        else:
                            transaction.commit()
                            transaction_commit_flag=1
#                            return HttpResponseRedirect('/info/cheque/')
                    else:
                        logger.info('cheque :: loan_id :: '+str(loan_id)+' :: there is no valid data')
                elif record['payment_method'] == 'direct_dep':
                    if reference_id and amount and receive_dt:
                        try:
                            direct_dep = Direct_Deposit(dd_nbr=reference_id, deposit_amt=amount, deposit_date=receive_dt, create_dt=create_date, loan=loan)
                            direct_dep.save()
                            msg = pcfunc.recvmoney(loan_id, direct_dep.dd_nbr, receive_dt, float(amount), 0,
                                            'DIRECT DEPOSIT', '', '', request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"],done_on="BANK ACCOUNT")
                            logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: direct deposit :: response from recvmoney :: '+str(msg))
                            if msg.__contains__('FAILURE::'):
                                raise CustomException, msg
                            #direct_deps.append(direct_dep)
                            add_gcm_notes(logid,"Direct Deposit",str(amount)+" has recieved as a Direct Deposit on "+str(receive_dt),request.session['username'],create_date)
                            request.session['cheque_msg'] = msg
                            request.session["update_flag"]=1
                        except CustomException, e:
                            request.session['cheque_msg'] = e
                            delete_transaction(loan_id, direct_dep.dd_nbr, float(amount),0, 'direct deposit')
                            transaction.rollback()
#                            return HttpResponseRedirect('/info/cheque/')
                        except Exception, e:
                            request.session['cheque_msg'] = 'Falied!! Please try later.'
                            transaction.rollback()
                            logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: direct deposit :: '+str(traceback.format_exc()))
#                            return HttpResponseRedirect('/info/cheque/')
                        else:
                            transaction.commit()
                            transaction_commit_flag=1
                            chk_cc_paid_not=Downpayments.objects.filter(loan=loan_id,override_flag=0,downpayment_type='CC')
                            if chk_cc_paid_not:
                                    if chk_cc_paid_not[0].paid_amt>0:
                                          flag=1
                                    else:
                                          flag=0
                                    updateCreditCheckStatus(loan_id,flag)
#                            return HttpResponseRedirect('/info/cheque/')
                    else:
                        request.session['cheque_msg'] = "Please give all values."
                        logger.info('cheque :: loan_id :: '+str(loan_id)+' ::direct deposit :: there is no valid data')
            else:
                if transaction_commit_flag:
                    transaction.commit()
                else:
                    transaction.rollback()
                return HttpResponseRedirect('/info/cheque/?loan_id='+loan_id)

        except Exception, e:
            logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: '+str(traceback.format_exc()))
    fund_date=fund_flag[0].booked_dt
    if transaction_commit_flag:
        transaction.commit()
    else:
        transaction.rollback()

    bal_infm=get_balance_dtls(loan_id)[0]
    Max_OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
    return render_to_response("custdetail/cheque_iframe.html", {'cheques':cheques,'status':status,
                                                                 'direct_deps':direct_deps,'msg': msg,"isOB":isOB,
                                                                 "update_flag":update_flag,'fund_date':fund_date,'loan_id':loan_id,"Max_OB":Max_OB})
cheque = transaction.commit_manually(cheque)
cheque=maintenance_deco_popups(cheque)

def card_info(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    username = request.session['username']
    data_dict = cardconfig.DATA_DICT_CVS_Info.copy()
    message=""
    validation_dict={}
    card_details=None
    lp_tranid=None
#    Gets the LPTranID from Ext_Bureau_Info table
#    The below code is to get card_status
    card_flag=0
    link_eligible=0
    history_flag=0
    card_special_prev=get_spl_privileges_by_usr_id(str(username),1)
    if card_special_prev=='Grant':
        card_flag=1

    if request.method=="GET":
        if request.GET.has_key("id"):
            history_flag=1
            lp_tranid=str(request.GET["id"])
            card_url="custdetail/card_info_history.html"
        else:
            lp_tranid=Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name=cardconfig.BUREAU_NAME,override_flag=0).order_by("-create_dt") | Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name="CallCredit",override_flag=0).order_by("-create_dt")
            if not lp_tranid:
                lp_tranid=Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name=cardconfig.BUREAU_NAME,override_flag=1).order_by("-create_dt") | Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name="CallCredit",override_flag=1).order_by("-create_dt")
            if lp_tranid:
                lp_tranid=lp_tranid[0]
                if lp_tranid.reference_id:
                    lp_tranid=str(lp_tranid.reference_id)
                else:
                    lp_tranid=None
            card_url="custdetail/card_info.html"

    if lp_tranid:
        try:
            data_dict.update(cimtranid=str(lp_tranid),servicecode=SERVICE_CODE["service_code_1003"],tranid=getKeyTranID())
            if cardconfig.DATA_DICT_CI_Info['testing'] == 1:
                data_dict.update(cardconfig.DATA_DICT_CI_Info.copy())
                # to encode the fields
                head = data_dict['tranid']
                tail=base64.b64encode(head)
                data_dict['testing']=cardconfig.TESTING
                data_dict['RetrieveInfo']="1"
                data_dict['ServiceType']=base64.b64encode(head+"2"+tail)
                data_dict['cimtranid']=base64.b64encode(head+str(data_dict['cimtranid'])+tail)
                data_dict['StoreID']=cardconfig.CI_STOREID['loanacquisition'] #for 1003 request we can use any of the store id, as this will only fetch the records
                xml = CustomXMLBuilder(data_dict, cardconfig.TAG_DICT_CVS_Info_CI,
                                       cardconfig.REQ_ROOT_CVS_CI,
                                       cardconfig.EMPTY_TAG_CI)
                post_data = Poster(cardconfig.POSTER_URL_CI_Info , xml.request,
                               cardconfig.TIMEOUT_CI_Info)
            else:

                xml = CustomXMLBuilder(data_dict, cardconfig.TAG_DICT_CVS_Info,
                                       cardconfig.REQ_ROOT_CVS_Info,
                                       cardconfig.EMPTY_TAG_CVS_Info)
                post_data = Poster(cardconfig.POSTER_URL_CVS_Info , xml.request,
                               cardconfig.TIMEOUT_CVS_Info)

            post_data.setmisc(data_dict['tranid'],logger)
            card_logger.info(' CARD INFO AVS :: Request :: Service 1003 ::  Transaction ID <'+str(data_dict['tranid'])+'> :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username)+' LP TranID:: '+ str(lp_tranid))
            response = post_data.post()
            # Parsing the Response received from the Card Information Manager
            if cardconfig.DATA_DICT_CI_Info['testing'] == 1:
                resp = Request([xmlconfig.xpaths_CVS_Info_CI, xmlconfig.multiValuedTags_CI_Info ,
                            xmlconfig.mandatoryTags_CI_Info])
            else:
                resp = Request([xmlconfig.xpaths_CVS_Info, xmlconfig.multiValuedTags_CVS_Info ,
                            xmlconfig.mandatoryTags_CVS_Info])

            resp.xmlParseAndCheck(response)
            validation_dict_temp = resp.clientDict
            if 'Message_FraudRules' in validation_dict_temp.keys():
                if validation_dict_temp['Message_FraudRules'] in cardconfig.FRAUDRULES_MAP.keys():
                    #validation_dict_temp['Message_FraudRules']=cardconfig.FRAUDRULES_MAP[validation_dict_temp['Message_FraudRules']]
                    validation_dict_temp['Message_FraudRules']=validation_dict_temp['Message_FraudRules']
            else:
                validation_dict_temp['Message_FraudRules']=''

            for key,value in validation_dict_temp.iteritems():
                if value=="None":
                   validation_dict[key]=None
                else:
                    validation_dict[key]=value
            if "Authorisation" in validation_dict and validation_dict['Authorisation']=='CARD SERVICE DOWN':
                validation_dict['Authorisation'] = None
            eligible_link_associated = "select * from Ext_Bureau_Info where loan_id =%s and override_flag=0 and ((status = 'SUCCESS' and FraudRulesStatus='valid' and\
            card_usage = 'PERMANENT CARD') or (status is null and FraudRulesStatus is null))  order by create_dt desc"
            res_eligible_link_associated= con.get_one_result(eligible_link_associated, args = loan_id)
            if res_eligible_link_associated:
                link_eligible=1
            #if 'Status' in validation_dict and validation_dict['Status'].upper()=='SUCCESS':
            if cardconfig.DATA_DICT_CI_Info['testing'] == 1:
                if str(validation_dict['CardVerifyStatus']) == '1' and str(validation_dict['DPVerifiedStatus']) == '1':
                    card_logger.info(' CARD INFO AVS :: Response Success:: Service 1003 :: Transaction Id <'+str(data_dict['tranid'])+'> :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username)+' LP TranID:: '+ str(lp_tranid)+' XML RESPONSE :: SUCCESS')
                else:
                    card_logger.info(' CARD INFO AVS :: Response Failed:: Service 1003 :: Transaction Id <'+str(data_dict['tranid'])+'> :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username)+' LP TranID:: '+ str(lp_tranid)+' XML RESPONSE :: '+str(response))
            elif  'Status' in validation_dict and validation_dict['Status'].upper()=='SUCCESS':
                card_logger.info(' CARD INFO AVS :: Response Success:: Service 1003 :: Transaction Id <'+str(data_dict['tranid'])+'> :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username)+' LP TranID:: '+ str(lp_tranid)+' XML RESPONSE :: SUCCESS')
            else:
                 card_logger.info(' CARD INFO AVS :: Response Failed:: Service 1003 :: Transaction Id <'+str(data_dict['tranid'])+'> :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username)+' LP TranID:: '+ str(lp_tranid)+' XML RESPONSE :: '+str(response))

        except Exception,e:
            card_logger.error("CARD INFO AVS :: ERROR :: Loan ID :: "+str(loan_id)+" :: Response Error :: "+str(e)+ " :: "+ str(response) + '\n' + str(traceback.format_exc()))
            message="Connection Refused(CVS server down) ! "
    else:
        message="No Card Information Available ! "

    if message:
        if "Description" in validation_dict:
           validation_dict['Description'].append(message)
        else:
            validation_dict['Description']=[message]
    try:
        if lp_tranid:
            card_details=getCardDetails(loan_id,cimtran_id=lp_tranid,tran_id=data_dict['tranid'])

            card_type_mapping={"VISA":"Visa Card","DELTA":"Visa Delta Card","MC":"Mastercard","SWITCH":"Maestro","SOLO":"Solo","UKE":"Visa Electron"}
            if "cardtype" in card_details:
                for card_type_map,value in card_type_mapping.iteritems():
                    if (str(card_type_map)==str(card_details["cardtype"])):
                        card_details["cardtype"]=value
                        break
            if not card_details:
                message="Connection Refused(CIM server down) !"
                link_eligible=0
                if "Description" in validation_dict and validation_dict['Description']:
                   validation_dict['Description'].append(message)
                else:
                    validation_dict['Description']=[message]
        else:
            pass

        flag = 0

        bnk_val_chk = "select ext_bureau_info_id from Ext_Bureau_Info where loan_id = %s and override_flag=0 and status = 'SUCCESS' \
                        and card_usage = 'PERMANENT CARD' and reason = 'Bank Statement' and created_by = 'BanKValidationService' \
                        order by create_dt desc limit 1"
        res = con.get_one_result(bnk_val_chk, args = loan_id)
        if res:
            flag = 1

    except Exception,e:
        card_logger.error("CARD INFO CIM :: ERROR :: Loan ID :: "+str(loan_id)+' Username:: '+ str(username)+" :: BUREAU ID MISSING :: "+str(e) + "\n" + str(traceback.format_exc()))

    return render_to_response(card_url, {"validation_dict":validation_dict, "loan_id":loan_id,"cust_id":cust_id,
                                                            "card_details":card_details,"message":message,"card_flag":card_flag,"card_id":lp_tranid, "flag" : flag,"link_eligible":link_eligible})
card_info = maintenance_deco_popups(card_info)
def card_info_popup(request):

    display_msg = ''
    upd_status=0
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
        submit_type = str(request.POST['button'])
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username=request.session['username']
    address_info=Address_Info.objects.filter(cust=cust_id,override_flag=0)
    create_date = datetime.datetime.now()
    if request.method=="POST":
        request_dict = {}
        loan_id = request.POST['loan_id']
        request_dict['buildingname']=str(request.POST['buildingname'])
        request_dict['flatnumber']=str(request.POST['flatnumber'])
        request_dict['buildingnumber']=str(request.POST['buildingnumber'])
        request_dict['street']=str(request.POST['street'])
        request_dict['county']=str(request.POST['county'])
        request_dict['postcode']=str(request.POST['postcode'])
        request_dict["pannum"]=str(request.POST["pannum"])
        request_dict["nameoncard"]=str(request.POST["nameoncard"])
        request_dict["cardtype"]=str(request.POST["cardtype"])
        ccissuenumber=""
        ccvalidfrom=None
        request_dict['validto_month'] = int(request.POST['validto_month'])
        request_dict['validto_year']=str(request.POST['validto_year'])
        request_dict['cvv2']=str(request.POST['cvv2'])
        request_dict['button'] = submit_type
        if cardconfig.DATA_DICT_CVS_CI['testing']==1:
            card_validate,parsed,error_code,message = debitcardcheckandfraudrules(loan_id,cust_id,'Card_Info_popup',submit_type,
                                                                                         username,request_dict,card_logger)
        else:
            card_validate,parsed,error_code,message = cardSaveAndValidate(loan_id,cust_id,'Card_Info_popup',submit_type,
                                                                                         username,request_dict,card_logger)
        if card_validate == True or card_validate == False:
            if parsed["CIMTranID"]:
                if cardconfig.DATA_DICT_CVS_CI['testing']==1:
#                     bureau_name=str(parsed["DPName"]) or "CallCredit"
                    bureau_name=str(parsed["DPName"])
                else:
#                     bureau_name=str(parsed["Name"]) or "CallCredit"
                    bureau_name=str(parsed["Name"])

                made_as_primary = False

                if cardconfig.DATA_DICT_CVS_CI['testing']==1:
                    #if parsed['Message_FraudRules'] in cardconfig.FRAUDRULES_MAP.keys():
                        #parsed['Message_FraudRules']=cardconfig.FRAUDRULES_MAP[parsed['Message_FraudRules']]
                        ##parsed['Message_FraudRules']=parsed['Message_FraudRules']

                    response_lptran_id=str(parsed["CIMTranID"])
                    response_carduniqid=str(parsed['CardUniqueID'])

                    #source added as TMS because card collected from TMS application
                    if parsed['DPVerifiedStatus'] == 'Success' and parsed['CardVerifyStatus']=='Valid':

                        update_card_reference(loan_id=loan_id, bureau_name = bureau_name, CIMTranId=response_lptran_id, source='TMSADDCARD', username=username,
                                    save_card='1', cardUniq_id=response_carduniqid, cardStatus=parsed['DPVerifiedStatus'],
                                    reason=parsed['DPStatusDescription'], fraudRuleStatus=parsed['CardVerifyStatus'],
                                    fraudRuleDesc=parsed['Message_FraudRules'], bureau_id=parsed["DPTransactionID"], key_id=None, logger=card_logger,
                                    response = None, card_usage='PERMANENT CARD',create_dt=create_date,cardwithpull=0)

                        display_msg = 'Card succesfully Added'
                        made_as_primary = True
                        card_logger.info("Card succesfully Added for loan_id :: "+str(loan_id))

                    else:
                        update_card_reference(loan_id=loan_id, bureau_name = bureau_name, CIMTranId=response_lptran_id, source='TMSADDCARD', username=username,
                                    save_card='0', cardUniq_id=response_carduniqid, cardStatus=parsed['DPVerifiedStatus'],
                                    reason=parsed['DPStatusDescription'], fraudRuleStatus=parsed['CardVerifyStatus'],
                                    fraudRuleDesc=parsed['Message_FraudRules'], bureau_id=parsed["DPTransactionID"], key_id=None, logger=card_logger,
                                    response = None, card_usage='PERMANENT CARD',create_dt=create_date,cardwithpull=0)

                        card_logger.error("Invalid card !!! CardVerifyStatus / UnderwritingStatus was not matched")
                        upd_status=response_lptran_id
                        display_msg = 'Invalid card !!! CardVerifyStatus / UnderwritingStatus was not matched'
                else:
                    response_lptran_id=str(parsed["CIMTranID"])
#                    updateExt = Ext_Bureau_Info.objects.filter(loan=loan_id,override_flag=0,\
#                            bureau_name='LendProtect') | Ext_Bureau_Info.objects.filter(loan=loan_id,override_flag=0,bureau_name="CallCredit")
#                    updateExt.update(override_flag=1,modified_by=username,modified_dt=create_date)
#
#                    external_bureau_info_check=Ext_Bureau_Info(\
#                    reference_id=response_lptran_id,bureau_id=parsed["LendProtectTranID"],loan_id=loan_id,bureau_name="CallCredit",\
#                    override_flag=0,create_dt=create_date,created_by=username)

                    update_card_reference(loan_id=loan_id, bureau_name = bureau_name, CIMTranId=response_lptran_id, source='TMSADDCARD', username=username,
                    save_card='1', cardUniq_id=None, cardStatus=None,reason=None, fraudRuleStatus=None,fraudRuleDesc=None,
                    bureau_id=parsed["LendProtectTranID"], key_id=None, logger=card_logger,response = None,
                    card_usage='PERMANENT CARD',create_dt=create_date,cardwithpull=0)

                    display_msg = 'Card succesfully Added'
                    made_as_primary = True


                card_logger.info('CARD INFO POP UP :: Response Success :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username))
                case_id=get_case_id_by_entity_id(loan_id,'LOAN')
                log_id=get_logid_by_caseid(case_id)

                pro_class = dbtmsapi.get_product_classification(loan_id)

                if pro_class=='LOC' and made_as_primary:
                    rtiDCInfo = {}
                    rtiDCInfo['loan_id'] = loan_id
                    rtiDCInfo['CIMTranID'] = str(parsed["CIMTranID"])
                    rtiApi = rtiapi.LOC_debitCardUpdate(loan_det=rtiDCInfo)

                    if rtiApi:
                        logger.info("Debit Card Details has been informed successfully to UE for the loan id :: "+str(loan_id))
                    else:
                        logger.info("Error in sending Debit Card Details to UE for the loan id :: "+str(loan_id))

                if cardconfig.DATA_DICT_CVS_CI['testing']==1:
                    add_gcm_notes(log_id["log_id"],"CARD","CIM TRANID - "+str(response_lptran_id)+" added at "+str(create_date),username,create_date)
                else:
                    add_gcm_notes(log_id["log_id"],"CARD","Bureau name- LendProtect. LP ID - "+str(response_lptran_id)+" added at "+str(create_date),username,create_date)
        else:
            display_msg = 'Card Could not be Added succesfully. DONT TRY AGAIN. Contact back end team'
            card_logger.error('Error Code :: '+str(error_code) + " : Explaination::"+str(message))
    return render_to_response("custdetail/card_info_popup.html",{"address_info":address_info,"loan_id":loan_id,'cust_id':cust_id,'display_msg':display_msg,\
                              'upd_status':upd_status,'expiry_range':range(datetime.datetime.now().year, (datetime.datetime.now().year + 20))})
card_info_popup = maintenance_deco_popups(card_info_popup)

def update_card_info(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username=request.session['username']
    create_date = datetime.datetime.now()

    message = ""

    if 'reference_id' in request.POST and request.POST['reference_id']:
        reference_id = request.POST['reference_id']
        response_reference_id = str(reference_id)
        bureau_name = "LendProtect"

        tranid=getKeyTranID()
    try:
        if reference_id:
            card_details=getCardDetails(loan_id,cimtran_id=reference_id,tran_id=tranid)
            if "pannum" in card_details :
                if card_details["pannum"]:
                    duplicate = check_card_exists(reference_id, bureau_name, loan_id)
                    if duplicate:
                        message = "Card already Exists in Database"
                    else:
                        card_update = add_existing_card_info(reference_id, bureau_name, loan_id,username = username)
                        message = "Card Details Added Successfully"
                        case_id=get_case_id_by_entity_id(loan_id,'LOAN')
                        log_id=get_logid_by_caseid(case_id)
                        add_gcm_notes(log_id["log_id"],"CARD","CIMTran ID  -"+str(response_reference_id)+" added from IVRS ",username, create_date)
                    card_logger.info('UPDATE CARD INFO :: Response Success:: CIM TRANID::'+ str(reference_id)+' :: Loan ID :: '+str(loan_id))
                else:
                    message = "Please confirm details and try again"
                    card_logger.info('UPDATE CARD INFO :: Response Failure:: Loan ID :: '+str(loan_id)+':: Message :: '+str(message))

            else:
                message = "Encountered some technical issues. Please try again."
                card_logger.info('UPDATE CARD INFO :: Response Failure:: Loan ID :: '+str(loan_id)+':: Message :: '+str(message))

    except Exception,e:
        card_logger.error("CARD INFO CIM :: ERROR :: Loan ID :: "+str(loan_id)+" :: CIMTRAN ID MISSING :: "+str(e))

    return render_to_response("custdetail/update_card_info.html",{"message":message,"loan_id":loan_id})
update_card_info = maintenance_deco_popups(update_card_info)

def topup_popup(request):

    topup_flag = 1
    if request.method=='GET':
        loan_id=request.GET['loan_id']

    fin_display=[]
    store_id=Loan.objects.filter(loan_id=loan_id)[0].store_id

    username = url_settings.CIA_LSTOPUP_USERNAME
    password=url_settings.CIA_LSTOPUP_PASSWORD


    data_dict={'username':username,'password':password,'loanId':loan_id, 'profile_info':1}
    try:
        from utils.builder.xml import custombuilder

        tagdict={"TransactionInfo":{"UserID" : "['username']",
                                    "Password" : "['password']"
                                    },
                  "TransactionData":{"Key":{"ApplicationKey":{"AgreementNumber":"['loanId']"}},
                                   "Services":{"CustomerServices":{"ProfileInfo":"['profile_info']"}}
                                    }
                }
        root='RequestHeaderEnvelope'
        xml_req =custombuilder.CustomXMLBuilder(data_dict,tagdict,root,True)

        response = sslv3.postUsingSSLV3(url_settings.CIA_TOPUP_URL,xml_req.request).read()

    except:
        msg=" FAIL !! Try Again........"
        t=traceback.format_exc()
        logger.debug(" ERROR :: \n"+t+"\n\n")
        topup_flag = 0
    try:
        from utils.parsers import xmlparser
        parentTag='ResponseHeaderEnvelope'
        resp_dict=xmlparser.xmlParseDict(response , parentTag)
        if resp_dict:
            if int(resp_dict['TransactionData']['ProfileInfo']['TPFlag']) > 0:
                eligibility = 'YES'
                amount = resp_dict['TransactionData']['ProfileInfo']['TopUpEligibleAmount']
            elif int(resp_dict['TransactionData']['ProfileInfo']['RF']) > 0:
                eligibility = 'YES'
                amount = resp_dict['TransactionData']['ProfileInfo']['LOC']
            else:
                eligibility = 'NO'
                amount = ''
            fin_display=[{"TopUpEligible":eligibility,\
                          "Topup_amt": amount}]
    except Exception,e:
            msg = "FAIL!!!! Please Try Again"
            t=traceback.format_exc()
            logger.debug(" ERROR :: \n"+t+"\n\n")
            topup_flag = 0

    return render_to_response("custdetail/topup_popup.html",{"fin_display":fin_display,"topup_flag":topup_flag})
topup_popup = maintenance_deco_popups(topup_popup)

def select_card(request):

    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username = request.session['username']
    bureau_name = cardconfig.BUREAU_NAME
    message = ""

 #   card_list = get_card_list_from_loan_id(loan_id,bureau_name)
    card_list = get_card_list_withbintail(loan_id,bureau_name)
    for item in card_list:
        if item['override_flag'] == 0:
            reference_id_old = item['reference_id']
            break

    if 'card_select' in request.POST and request.POST['card_select']:
        reference_id_new = request.POST['card_select']
        try:
            if reference_id_new:
                if reference_id_new != reference_id_old:
                    card_change = update_selected_card_from_loan_id(loan_id,bureau_name,reference_id_old,reference_id_new,username)
                    if card_change:
                        message = "Card Changed Successfully"
                    else:
                        message = "Card Change Failed"
        except Exception, e:
            card_logger.error("CARD INFO CIM :: ERROR :: Loan ID :: "+str(loan_id)+" :: INVALID CIMTRAN ID :: "+str(e))
            message = "Encountered some technical issues. Please try again."

    #card_list = get_card_list_from_loan_id(loan_id,bureau_name)

    return render_to_response("custdetail/select_card.html",{"card_list":card_list,"message":message,"loan_id":loan_id})
select_card = maintenance_deco_popups(select_card)
def get_card_number(request):
    """Gets cardnumber and displays the card number with ajax call

    Gets loan_id from post data.
    Calls gerCardData API
    logs the time and user who made the ajax call.

    """
    if request.method == 'POST' and request.is_ajax:
        loan_id = request.POST['loan_id']
        if 'card_id' in request.POST:
            card_id = request.POST['card_id']
        else:
            card_id=Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name=cardconfig.BUREAU_NAME,override_flag=0).order_by("-create_dt") | Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name="CallCredit",override_flag=0).order_by("-create_dt")
            if not card_id:
                card_id=Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name=cardconfig.BUREAU_NAME,override_flag=1).order_by("-create_dt") | Ext_Bureau_Info.objects.filter(loan=loan_id,bureau_name="CallCredit",override_flag=1).order_by("-create_dt")
            if card_id:
                card_id=card_id[0]
                if card_id.reference_id:
                    card_id=str(card_id.reference_id)
                else:
                    card_id=None


        card_details=getCardDetails(loan_id, card_id)
        if card_details:
            card_number = card_details['pannum']
        else:
            card_number = ""
        card_access_logger.info(request.session['username']+' has accessed card number of Loan with loan_id '+loan_id)
        return HttpResponse(simplejson.dumps({'card_number':card_number}), mimetype="text/javascript")

def tran_history_popup(request):
    username = request.session['username']
    transaction=None
    tran_change_flag=0
    spl_privilege_list = ('refund','cheque','discard')
    spl_priv_approved_list = gcmauthapi.get_spl_privileges_by_usr_id_list(username, spl_privilege_list)
#    else:
#        tran_change_flag = 0
#    if tran_change_flag == 'Grant':
#        tran_change_flag = 1
#    else:
#        tran_change_flag = 0
    if request.method=='GET':
        loan_id=request.GET['loan_id']
        transaction=Transactions.objects.filter(loan=loan_id).order_by('-create_dt')
#        txn = Refund_Request.objects.values('txn')
#        txn = Refund_Status.objects.values('transaction_id')
        con = mysqldbwrapper.MySQLWrapper(config_file_path, 'TMS_DATA')
        sql="select transaction_id from Refund_Status where transaction_id is not NULL"
        txn=con.get_all_results(sql)
        txn_fin = []
        for i in txn:
            txn_fin.extend(i.values())
        for i in transaction:
             if i.debit and i.transaction_id in txn_fin:
                  i.__dict__.update({'reverse':'under-process'})
             elif i.debit and i.payment_method.lower() == 'cheque':
                  i.__dict__.update({'reverse':'bounce'})
             elif i.debit and i.payment_method.lower() == 'direct deposit':
                  i.__dict__.update({'reverse':'discard'})
             elif i.debit:
                  i.__dict__.update({'reverse':'refund'})
             else:
                  i.__dict__.update({'reverse':'na'})

        sql = "select date(tr.tran_dt),statement_date,li.loc_limit as loc_limit,OPB, li.loc_limit - OPB as add_draw,\
        draw_amount,tr.transaction_id,draw_type, draw_status, if((statement_date>=date(tr.tran_dt) or date(tr.tran_dt) is NULL or \
        draw_type='FIRST DRAW' or draw_status='REVERSED'),0,1) as showChk,locDraw.create_dt as trandate\
         from Loan_Info li join Payments ps on li.loan_id=ps.loan_id join LOC_Draw as locDraw on \
         ps.loan_id=locDraw.loan_id left join (select statement_date,loan_id from Statements where loan_id=%s \
         order by statement_id desc limit 1 ) stmts on                 stmts.loan_id=locDraw.loan_id left join \
          Transactions tr on tr.transaction_id=locDraw.transaction_id where                 ps.loan_id=%s \
          and li.override_flag=0 group by draw_id"%(loan_id,loan_id)
        result = con.get_all_results(sql)
        logger.info("LOC draw Details Result Set :: "+str(result))
        returnMsg = ''
        draw_status = ['NEW','READY TO PAY','SENT TO PAY','FUNDED','REVERSED','REJECTED']
        locLimit = None
        addDraw  = None
        drawAmt  = None

        if result:
            locLimit = result[0]['loc_limit']
            addDraw  = result[0]['add_draw']
            drawAmt  = result[0]['OPB']
            #return render_to_response('custdetail/tran_history_popup.html',{})
        else:
            returnMsg = "No Records Found."
            #return render_to_response('custdetail/tran_history_popup.html',{'msg':'No Records Found.'})
        product_classification = get_product_classification(loan_id)
    return render_to_response("custdetail/tran_history_popup.html",{"transaction":transaction, 'spl_priv_list':spl_priv_approved_list,'contextDict':result,'loc_limit':locLimit,'add_draw':addDraw,'draw_amount':drawAmt,'loan_id':loan_id,'msg':returnMsg,'product_classification':product_classification,'draw_status':draw_status})

tran_history_popup = maintenance_deco_popups(tran_history_popup)

def paydates_history_popup(request):
    if request.method=='GET':
#         import pdb;pdb.set_trace()
        loan_id=request.GET['loan_id']
        product_details = get_product_details_of_loan(loan_id)        
        con = mysqldbwrapper.MySQLWrapper(config_file_path, 'TMS_DATA')
        payment_type_abr={"LNCYC":"Loan Cycle","DWNPMT":"Downpayment",
                      "STCYC":"Statement Cycle"}
        
        sql="""select * from PayDates where loan_id='%s' and cycle>0  order by create_dt,cycle"""%(loan_id)
        res=con.get_all_results(sql)
        last=0
        fin_display=[]
        list1=[]
        count = 0
        user_names = {}
        display_dict = {}
        for i in res:
            user_names[i["modified_dt"]] = [i["modified_by"],i["reason"]]
            dict1={'cycle':None,'payment_type':None,'date':None}
            if i["override_flag"] == 0:
                dict1["cycle"]=i["cycle"]
                dict1["date"]=i["paydate"]
                dict1["payment_type"]=payment_type_abr[i["payment_type"]]
                list1.append(dict1)
            if last !=i["create_dt"]:
                if count == 1:
                    fin_display.append(display_dict)
                count = 1
                display_dict={'user':None,'paydates':[],'reason':None,'create_date':None}
            if user_names.has_key(i["create_dt"]):
                display_dict["user"]=user_names[i["create_dt"]][0]
                display_dict["reason"]=user_names[i["create_dt"]][1]
            display_dict['create_date'] = i["create_dt"]
            date_dict={'cycle':None,'date':None,'override_reason':None,'payment_type':None}
            date_dict["cycle"]= i["cycle"]
            date_dict["date"]=i["paydate"]
            date_dict["override_reason"]=i["override_reason"]
            date_dict["payment_type"]=payment_type_abr[i["payment_type"]]
            display_dict['paydates'].append(date_dict)
            last = i["create_dt"]
        fin_display.append(display_dict)

        newlist=sorted(list1, key=lambda k: k['cycle'])
        cur_dict={'user':'CURRENT','paydates':newlist,'reason':'N/A','create_date':'N/A'}
        fin_display.append(cur_dict)
        fin_display[0]['user']='E-SIGNED'
        fin_display[0]['reason']='N/A'
        if fin_display[0]['paydates'][0]['override_reason']=='NOV':
            fin_display[1]['user']='LOAN ACTIVATION'
            fin_display[1]['reason']='NOV'
    return render_to_response("custdetail/paydates_history_popup.html",{"fin_display":fin_display,'product_class':product_details['product_classification']})
paydates_history_popup = maintenance_deco_popups(paydates_history_popup)

def refund(request):
    """
    Refund the amount to customer back.
    Gets Trasaction date range and refund amount through post.
    calls the api 'refund' for refunding
    """

    msg= ''
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        if 'msg' in request.GET:
           msg = request.GET['msg']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    #adding status variable initialisation##for dailyrun temp table
    status = None

    sanity_check_done = 0

    refund_reason = ['Dispute','Normal']
    #logger.info('refund :: loan_id :: '+str(loan_id))
    if request.session.has_key('refnd_msg'):
        msg = request.session['refnd_msg']
        del request.session['refnd_msg']


    if request.method == 'POST':
        payment_method = request.POST['refund_reason']
        create_date = datetime.datetime.now()
        try:
            loan = Loan.objects.get(pk=loan_id)
            waterfall_flag = pcfunc.waterfallcheck(loan.loan_id)
            keytranid = getkeytranid(loan_id)
            if not waterfall_flag:
                from_date = request.POST['from_dt']
                to_date = request.POST['to_dt']
                refund_amt = request.POST['amt']
                logger.info('refund :: '+str(keytranid)+' :: loan_id,refund_amt,from_date,to_date :: '+str(loan_id)+','+str(refund_amt)+','+str(from_date)+','+str(to_date))
                if from_date:
                    if not to_date:
                        transactions = Transactions.objects.filter(tran_dt__gte=from_date, loan=loan.loan_id, debit__gt=0, payment_type__in=loanstatusconfig.PAYMENTTYPE["PULL"],payment_method__in=['WATERFALL','IMMEDIATE PULL','SSP']).order_by('-debit')
                    else:
                        to_date = to_date + datetime.timedelta(days=1)
                        transactions = Transactions.objects.filter(tran_dt__range=[from_date, to_date], loan=loan.loan_id, debit__gt=0, payment_type__in=loanstatusconfig.PAYMENTTYPE["PULL"],payment_method__in=['WATERFALL','IMMEDIATE PULL','SSP']).order_by('-debit')
                    excess = 0
                    if transactions:
                        tran_list=[]
                        rem_amt = float(refund_amt)
                        transactions = list(transactions)
                        #Getting already refunded list
                        refunded_list = get_refunded_transactions(loan_id, from_date, to_date)
                        logger.info('refund :: '+str(keytranid)+' :: list of transactions having already refunded :: '+str(refunded_list))
                        # Making neccessary correction in transactions.
                        if refunded_list:
                            #tranid_list = [tran_id[0] for tran_id in refunded_list]
                            for tran in transactions:
                                for tranid in refunded_list:
                                    if tran.merchant_txn_id == tranid[0]:
                                        transactions[transactions.index(tran)].debit -= tranid[1]
                            transactions = sorted(transactions, key=lambda x: x.debit, reverse=True)

                        for tran in transactions:
                            if float(tran.debit) == rem_amt:
                                tran_list.append((tran, tran.debit))
                                rem_amt = 0
                                excess = 0
                                break
                            elif float(tran.debit) > rem_amt:
                                excess = tran
                            elif tran.debit >0:
                                if excess:
                                    tran_list.append((excess, rem_amt))
                                    rem_amt = 0
                                    excess =0
                                    break
                                tran_list.append((tran, tran.debit))
                                rem_amt -= float(tran.debit)
                                if not rem_amt:
                                    break
                        if excess:
                            tran_list.append((excess, rem_amt))
                            rem_amt = 0

                        if not rem_amt:
                            logger.info('refund :: '+str(keytranid)+' :: transactions for refund :: '+str([(vars(i), j) for (i,j) in tran_list]))
                            logger.info('refund :: '+str(keytranid)+' :: Got all required transactions ')
                            returned = 0
                            loan_dict = {"tranid" :keytranid}
                            for record in tran_list:
                                loan_dict.update(merchant_service=str(record[0].merchant_name),
                                                  merchant_tid=str(record[0].merchant_txn_id),
                                                  return_amt=record[1],
                                                  trantype=payment_method + ' Refund',
                                                  loan_id=str(loan_id))
                                req_dict = {}
                                try:
                                    if  record[0].merchant_name not in ('Barclays', 'VoicePay'):
                                        msg = "Please select any Merchant service provider"
                                    req_dict.update({"KeyTranID" : loan_dict['tranid'],
                                                     "TranType" : loan_dict['trantype'],
                                                     "ReturnAmount" : loan_dict['return_amt'],
                                                     "OrigId" : loan_dict['merchant_tid'],
                                                     'MerchantService': record[0].merchant_name,
                                                     'LoanID': 'loan_id'})
                                    sanityParser.check_sanity(req_dict, 0)
                                    sanity_check_done = 1
                                    logger.info('refund :: '+str(keytranid)+' :: sanity check done :: merchant_txn_id ::'+str(record[0].merchant_txn_id))

                                except FieldNotFound, e:
                                    msg = '<ERROR>Missing Field or Empty Field:: '+str(e.args[1])
                                except LoggedExceptions, e:
                                    msg = str(e.args[1])
                                tran_time = create_date
                                logger.info("refund :: REQUEST :: "+str(keytranid)+ " :: "+str(req_dict))
                                if sanity_check_done:
                                    logger.info('refund :: '+str(keytranid)+' :: refunding the transaction:: '+str(vars(record[0])))
                                    logger.info('refund :: '+str(keytranid)+ ':: refunding amount of '+str(record[1]))
                                    if str(record[0].merchant_name) == 'VoicePay':
                                        voicepay_obj = VoicePay(logger)
                                        status, txn_id, exitmsg, failure_note = voicepay_obj.connectService(req_dict)
                                    elif str(record[0].merchant_name) == 'Barclays':
                                        barclays_obj = Barclays(logger)
                                        status, txn_id, exitmsg, failure_note = barclays_obj.connectService(req_dict)
                                    logger.info("refund :: "+str(keytranid)+" ::  amount, status, reason,payment_type, tran_time,merchant_name, loan_id :: " + str(loan_dict['return_amt'])+","+ status+","+exitmsg+","+"Refund"+","+ str(tran_time)+","+ str(req_dict['MerchantService'])+","+ str(loan_dict['loan_id']))
                                    Merchant_service_log_id = dbtmsapi.update_merchant_service_log(str(loan_dict['return_amt']), status, exitmsg, "Refund", str(tran_time), str(req_dict['MerchantService']), str(loan_dict['loan_id']), failure_note)
                                    logger.info("refund :: "+str(keytranid)+" :: updated merchant service log :: "+str(Merchant_service_log_id))
                                    if status == 'success':
                                        logger.info('refund :: '+str(keytranid)+' return successful :: merchant_txn_id ::'+str(record[0].merchant_txn_id))
                                        logger.info('refund :: '+str(keytranid)+' return successful ')

                                        print traceback.format_exc()
                                        if payment_method == 'Normal':
                                            msg = pcfunc.refund(loan_id,None, tran_time, 0, loan_dict['return_amt'], "MERCHANT PROVIDER",loan_dict['merchant_tid'], str(req_dict['MerchantService']), request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["NORMALREFUND"],done_on="DEBIT CARD")
                                        elif payment_method == 'Dispute':
                                           transaction=Transactions(loan_id=loan_id,credit=loan_dict['return_amt'],debit=0.0,tran_dt=tran_time,\
                                                                    payment_method="MERCHANT PROVIDER",merchant_txn_id=loan_dict['merchant_tid'],\
                                                                    merchant_name=str(req_dict['MerchantService']),create_dt=create_date,changed_by=request.session['username'],payment_type=loanstatusconfig.PAYMENTTYPE["OPF"],done_on="DEBIT CARD")
                                           transaction.save()
                                        returned = returned + loan_dict['return_amt']
                                        logger.info('refund :: '+str(keytranid)+' returned_amt ::'+str(returned))
                                        request.session["update_flag"]=1
                                    else:
                                        logger.warn('refund :: '+str(keytranid)+' failure pull :: '+failure_note)
                                        msg = "[Refund Failed] ", exitmsg or status


                            if returned > 0:
                                msg= 'money returned = '+str(returned)
                            else:
                                msg = 'Failure to refund money from merchant service. money returned = '+str(returned)
                        else:
                            msg = "The amount for refund is greater than amount pulled."
                    else:
                        msg = "No transaction found!!"
            else:
                msg = "Waterfall is currently running for this Loan. Please try later."
            if status == 'success':
                ## for daily_run phase 2: whenever there is a transaction, paydates change, status change
                #loan_id shd be flagged in DeltaMatrix table
                daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
                if isDailyRunStarted(date_of_run=daily_run_date):
                    updateDeltaMatrix(loan_id,'transaction')
            logger.info('refund :: '+str(keytranid)+' '+str(msg)+'\n\n')
            return HttpResponseRedirect('/info/amt_due/refund/?loan_id='+str(loan_id)+"&msg="+str(msg))
        except Loan.DoesNotExist:
            msg = 'Invalid Loan'
            logger.debug('refund :: '+str(keytranid)+' '+str(msg)+'\n\n')
            return HttpResponseRedirect('/info/amt_due/refund/?loan_id='+str(loan_id)+"&msg="+str(msg))
        except Exception, e:
            t = traceback.format_exc()
            print t
            msg = 'Failed to refund!'
            logger.warn('refund :: '+str(keytranid)+' '+str(msg))
            logger.error('refund :: '+str(keytranid)+' '+str(e))
            logger.debug('refund :: '+str(keytranid)+' '+str(t)+'\n\n')
            return HttpResponseRedirect('/info/amt_due/refund/?loan_id='+str(loan_id)+"&msg="+str(msg))
#    related_tbl=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
#    fund_date=""
#    if related_tbl.fund_dt:
#        fund_date=datetime.date.strftime(related_tbl.fund_dt, "%Y-%m-%d")
#    else:
#        return HttpResponse('Loan is not yet ACTIVE!')

    cxt = Context({'loan_id':loan_id, 'msg':msg, 'refund_reason':refund_reason})
    return render_to_response('custdetail/refund.html', cxt)
refund = maintenance_deco_popups(refund)

def promise_to_pay_old(request):
    currentDate=datetime.date.today()
    flag_idtfy_get_post=0
    max_cycle_number=0
    pay_type_cnt=0
    query_res={}
#    key=0
    type_post=""
    type_status=""
    status_cd=""
    msg=0
    chk_save_click=0
    temp_max_nu=0
    prepayment_flag=0
    paycal_max_cy=0
    bal_infm={}
    tempquery_res=''
    sup_reason = ''
    sup_alert = 0
    repayment_type=["Select","Full Temporary Arrangement","Partial Temporary Arrangement"]
    status=["TEMPORARY ARRANGEMENT"]
    payment_type={"select":"select","PRNDUE":"Principal Due","INTCAPLZD":"Interest Capitalized",\
                  "ARRFEE":"Arrear Fee","DEFLTFEE":"Default Fee","TERMNFEE":"Termination Fee","XTRPREPYMT":"Extra Prepayment"}
    date_elem=datetime.datetime.now()
    username=request.session['username']
    conn = TranDB(section="TMS_DATA")
    cur = conn.getcursor()
    schedule={}
    if request.method=='GET':
        loan_id=request.GET['loan_id']
    else:
        loan_id=request.POST['loan_id']
    reason_query="select * from Payments where loan_id = %s"%(loan_id)
    reason_result=conn.processquery(query = reason_query, curs = cur, count=1,fetch = True)

    if reason_result['suppress_flag']:
        if reason_result['wat_sup_reason'] in ['CARD  NOT IN USE','NO BALANCE IN CARD','Card theft','CARD LOST','CARD EXPIRED','CARD BLOCKED','CARD NOT IN USE','NO BALANACE IN CARD']:
            sup_reason = str(reason_result['wat_sup_reason'])
            sup_alert = 1
    try:
        if request.method=='GET':
            loan_id=request.GET['loan_id']
            paycal=PaymentCalendar.objects.filter(loan=loan_id,override_flag=0).order_by("-payment_nbr")[0]
            last_cycle=paycal.payment_nbr
            case_id=get_case_id_by_entity_id(loan_id,'LOAN')
            status_cd=get_loan_status_by_loan_case_id(case_id)
            if status_cd  not in ("TEMPORARY ARRANGEMENT","DEBT MANAGEMENT"):
                repayment_type=["Select","Full Temporary Arrangement","Partial Temporary Arrangement"]
            else:
                repayment_type=["Select","Full Temporary Arrangement"]
            Sch_Obj= schedule_for_loan.Schedule(loan_id)
            schedule = {'Schedule1':Sch_Obj.actualSchedule()}
        else:
            flag_idtfy_get_post=1
            loan_id=request.POST['loan_id']
            paycal=PaymentCalendar.objects.filter(loan=loan_id,override_flag=0).order_by("-payment_nbr")[0]
            last_cycle=paycal.payment_nbr
            case_id=get_case_id_by_entity_id(loan_id,'LOAN')
            status_cd=get_loan_status_by_loan_case_id(case_id)
            if status_cd  not in ("TEMPORARY ARRANGEMENT","DEBT MANAGEMENT"):
                repayment_type=["Select","Full Temporary Arrangement","Partial Temporary Arrangement"]
            else:
                repayment_type=["Select","Full Temporary Arrangement"]
            type_post=request.POST['reschedule_type']
#            currDate=datetime.datetime.now()
#            con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
#            quer="select * from temparrangement where loan_id = %s and override_flag = 0 \
#            and active=1 order by payment_nbr,temppayment_nbr"%(loan_id)
#            tempquery_res=con.get_all_results(query = quer)
            dict= request.POST

            if dict.has_key("save") or  dict.has_key("discard"):
                chk_save_click=1
                originalrecords={}
                quer="select * from temparrangement where loan_id = %s and override_flag = 0 \
                        and active=1 order by payment_nbr,temppayment_nbr"%(loan_id)
                query_res=conn.processquery(query = quer, curs = cur, count=0,fetch = True)
                if query_res or dict.has_key("discard"):
                    pay_type_cnt=1
                else:
                    pay_type_cnt=0
                schedule_with_future,schedule_without_future,max_cycle_number=append_paycal_temp(loan_id)
                query_dict=deepcopy(request.POST)
                originalrecords=orginal_dictionary_formation(query_dict,schedule_without_future)
                if pay_type_cnt == 0:
                    actionrequired = "insert"
                    newlist=new_dictionary_formation(query_dict,loan_id)
                    msg=pcfunc.tmpmanual(originalrecords, newlist, loan_id,actionrequired,username)
        #                            return HttpResponseRedirect("/info/promise_to_pay/?loan_id="+loan_id)
                else:
                    actionrequired="edit"
                    lis=partial_new_dictionary_formation(query_dict,schedule_without_future,loan_id,discard_flag = dict.has_key("discard"))
                    valid=validate_ptp(lis,loan_id)
                    if dict.has_key("save"):
                        if valid:
                            msg=pcfunc.tmpmanual(originalrecords, lis, loan_id,actionrequired,username)
                    if dict.has_key("discard"):
                        msg=pcfunc.tmpmanual(originalrecords, lis, loan_id,actionrequired,username)
            if dict.has_key("fullptpsave"):
                originalrecords={}
                pay_type_cnt=0
                chk_save_click=1
                old_elem=request.POST.getlist('oldcheckticks')
#                new_elem=request.POST.getlist('fullcheckticks')
                dict=deepcopy(request.POST)
                if 'status' in request.POST:
                    type_status=request.POST['status']
                status_cd=get_loan_status_by_loan_case_id(case_id)
                if status_cd != type_status:
                    if type_status!=status_cd:
                        if type_status=='DEBT MANAGEMENT':
                            pcfunc.debt(case_id, username,date_elem=date_elem,conn_close=0)
                            trandbupdateGCMCase(case_id,status_cd=type_status,done_by=username,date_elem=date_elem)
                        else:
                            pcfunc.promisetopay(case_id, username,date_elem=date_elem,conn_close=0)
                            trandbupdateGCMCase(case_id,status_cd=type_status,done_by=username,date_elem=date_elem)
                    actionrequired = "insert"
                else:
                    pay_type_cnt = 0
                    actionrequired="edit"

                checkedcyclelist=[]
                schedule_with_future,schedule_without_future,max_cycle_number=append_paycal_temp(loan_id)
                for item in old_elem:
                    checkedcyclelist.append(item)

                if actionrequired == "insert":
                    originalrecords={}
                    query_dict=deepcopy(schedule_without_future['schedule_without_future'])
                    originalrecords=full_insert_original_dict_formation(query_dict)
                    new_chk_elem=request.POST.getlist('fullcheckticks')
                    newlist=full_insert_new_dict_formation(new_chk_elem,dict,loan_id)
                    msg=pcfunc.tmpmanual(originalrecords, newlist, loan_id,actionrequired,username,status=type_status)

                elif actionrequired=="edit":
                    query_dict=deepcopy(schedule_without_future['schedule_without_future'])
                    originalrecords=full_edit_original_dict_formation(query_dict)
                    newlist=full_edit_new_dict_formation(dict,loan_id)
                    msg=pcfunc.tmpmanual(originalrecords, newlist, loan_id,actionrequired,username,status=type_status)
            schedule_with_future,schedule_without_future,max_cycle_number=append_paycal_temp(loan_id)
            schedule=schedule_with_future['schedule_with_future']
            schedule_without_future=schedule_without_future['schedule_without_future']
            max_cycle_number= max_cycle_number['max_cycle_number']
            ## for daily_run phase 2: whenever there is a transaction, paydates change, status change
            #loan_id shd be flagged in DeltaMatrix table
            if msg is True:
                daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
                if isDailyRunStarted(date_of_run=daily_run_date):
                    updateDeltaMatrix(loan_id,'ta')
        paycal=PaymentCalendar.objects.filter(loan=loan_id,override_flag=0).order_by("-payment_nbr")[0]
        paycal_max_cy=paycal.payment_nbr
        last_cycle=paycal.payment_nbr
        bal_infm=get_balance_dtls(loan_id)[0]
        payments_obj = pcfactory.getpmobj()
        pre_date=currentDate-timedelta(days=1)
        due_amt = payments_obj.calculate_due_amount(loan_id,pre_date)
        payments_obj.db.commit()
        payments_obj.db.close()
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        quer="select * from temparrangement where loan_id = %s and override_flag = 0 \
            and active=1 order by payment_nbr,temppayment_nbr"%(loan_id)
        tempquery_res=con.get_all_results(query = quer)
        if tempquery_res:
            temp_max_nu=tempquery_res[-1]['payment_nbr']
#        res={}
        OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
        bal_infm['OB']=OB
        bal_infm['OA']=due_amt
        quer="select * from Prepayments where loan_id = %s and override_flag = 0 \
            and active=1"%(loan_id)
        prepayment_check=con.get_all_results(query = quer)
    #    prepayment_check=Prepayments.objects.filter(loan=loan_id,override_flag=0,active=1)
        if prepayment_check:
            prepayment_flag=1
        else:
            prepayment_flag=0
    #    dup=deepcopy(schedule)
    #    request.session["dup_schedule"]=dup
#        max_nu=last_cycle-max_cycle_number

    except Exception,e:
        paycal_logger.debug('Exception received in custdetail.promise_to_pay :: '+str(e)+"\nTraceback :: "+str(traceback.format_exc()))
        if 'open' in conn.conn.__str__():
            paycal_logger.info('Connection Thread_id :: '+str(conn.conn.thread_id()) +' Connection status :: '+str(conn.conn.__str__()))
            conn.rollback()
            conn.close()
            paycal_logger.info('Connection rolled back and closed!')

    status_cd=get_loan_status_by_loan_case_id(case_id)
    return render_to_response('custdetail/promise_to_pay.html',{'loan_id':loan_id,'schedule':schedule,'repayment_type':repayment_type,\
        'type_post':type_post ,'flag_idtfy_get_post':flag_idtfy_get_post,'paycal_max_cy':paycal_max_cy,\
        'max_cycle_number':max_cycle_number,'payment_type':payment_type,'result':bal_infm,\
        'last_cycle':last_cycle,'pay_type_cnt':pay_type_cnt,'prepayment_flag':prepayment_flag,'temp_max_nu':temp_max_nu,\
        'temp_rec':tempquery_res,'currentDate':currentDate,'status':status,'type_status':type_status,'status_cd':status_cd,\
        'msg':msg,'chk_save_click':chk_save_click,'sup_alert':sup_alert,'sup_reason':sup_reason})

#Start of New TA Functionality

def new_TA_records_dict_formation(dict,loan_id,ta_type=1,discard_flag=0):
    '''
    Creates the format under which the new TA List needs to be updated.
    Lookst for two cases....
    1: Any older loans for which there is a change and the same needs to be updated
    2: For the new schedule list it creates the format.
    ta_type = 1: Full TA
    ta_type = 0: Partial TA
    discard_flag = 1: If True, then we ignore that record for new disct consideration
    '''
    newlist=[]
    to_obtain_cycle = 0
    if ta_type:
        if dict.getlist('oldcheckticks'):
            old_chk_elem = dict.getlist('oldcheckticks')
            for cnt in old_chk_elem:
                oldrecords={}
                temparrangement_id = ''
                temppayment_nbr = ''
                temp_pay_dt  = dict["oldpayment_dt"+str(cnt)]
                temp_pay_nbr = ''
                temp_pay_type = dict["oldpayment_type"+str(cnt)]
                pay=dict["oldpayment_amt"+str(cnt)]
                paid=dict["oldpaid_amt"+str(cnt)]
                temp_pay_amt = Money(pay,2)
                temp_pay_paid = Money(paid,2)
                oldrecords={"temparrangement_id":temparrangement_id,"temppayment_nbr":temppayment_nbr,"payment_dt":toDate(temp_pay_dt),"payment_nbr":temp_pay_nbr,
                            "payment_type":temp_pay_type,"payment_amt":temp_pay_amt,"paid_amt":temp_pay_paid,"active":1,"override_flag":0,"loan_id":loan_id}
                newlist.append(oldrecords)
        if dict.getlist('fullcheckticks'):
            new_chk_elem=dict.getlist('fullcheckticks')
            for cnt in new_chk_elem:
                newrecords={}
                temparrangement_id = ''
                temppayment_nbr = ''
                temp_pay_dt  = dict["fullpayment_dt"+str(cnt)]
                temp_pay_nbr = ''
                temp_pay_type = dict["fullpayment_type"+str(cnt)]
#                temp_pay_type = "Full Temporary Arrangement"
                pay=dict["fullpayment_amt"+str(cnt)]
                paid=dict["fullpaid_amt"+str(cnt)]
                temp_pay_amt = Money(pay,2)
                temp_pay_paid = Money(paid,2)
                newrecords={"temparrangement_id":temparrangement_id,"temppayment_nbr":temppayment_nbr,"payment_dt":toDate(temp_pay_dt),
                            "payment_nbr":temp_pay_nbr,"payment_type":temp_pay_type,"payment_amt":temp_pay_amt,"paid_amt":temp_pay_paid,
                            "active":1,"override_flag":0,"loan_id":loan_id}
                newlist.append(newrecords)
    else:
        chk_elem=dict.getlist('checkticks')
        ticklist=dict.getlist('ticks')
        cycledetail=dict.getlist('cycledetail')
        for row in cycledetail:
            fieldname='checkticks'+row
            index_list=row.split("-")
            cycle=index_list[0]
            elem=index_list[1]
            for counter in xrange(1,int(elem)+1):
                condition=0
                field2='hpayment_type'+str(cycle)+"-"+str(counter)
                tickname="ticks"+str(cycle)+","+str(counter)+"-"+str(elem)
                '''
                Functionality used to obtain the min_cycle for which the Partial TA is applicable.
                (i.e) If PTA is scheduled for 1st cycle, then the new TA schedule needs to be applicable for 1 only.
                '''
                if fieldname in chk_elem and not discard_flag:
                    to_obtain_cycle = cycle
                elif dict[field2]=='Partial Temporary Arrangement' and not discard_flag:
                    to_obtain_cycle = cycle
                if not discard_flag and dict["hpayment_type"+str(cycle)+"-"+str(counter)]=='Partial Temporary Arrangement':
                    condition = 1
                elif discard_flag and tickname not in ticklist and dict["hpayment_type"+str(cycle)+"-"+str(counter)]=='Partial Temporary Arrangement':
                    condition = 1
                    to_obtain_cycle = cycle
                if condition:
                    chkpay_id=dict["temp_id"+str(cycle)+"-"+str(counter)]
                    chktemp_pay_id=dict["temp_nbr"+str(cycle)+"-"+str(counter)]
                    chkpay_dt = dict["payment_dt"+str(cycle)+"-"+str(counter)]
                    chkpay_nbr = dict["payment_nmr"+str(cycle)+"-"+str(counter)]
                    chkpay_type = dict["hpayment_type"+str(cycle)+"-"+str(counter)]
                    chkpay_amt = Money(dict["payment_amt"+str(cycle)+"-"+str(counter)],2)
                    chkpay_paid = Money(dict["paid_amt"+str(cycle)+"-"+str(counter)],2)
                    newrecords={"temparrangement_id":chkpay_id,"temppayment_nbr":chktemp_pay_id,"payment_dt":toDate(chkpay_dt),
                                "payment_nbr":chkpay_nbr,"payment_type":chkpay_type,"payment_amt":chkpay_amt,"paid_amt":chkpay_paid,
                                "active":1,"override_flag":0,"loan_id":loan_id}
                    newlist.append(newrecords)

        if dict.has_key("new") and not discard_flag:
            tmp_elem=dict.getlist('new')
            for item in tmp_elem:
                newrecords={}
                temp_id = ''
                temppayment_nbr = ''
                temp_pay_dt  = dict["new_pay_dt"+str(item)]
                temp_pay_nbr = dict["new_cycle"+str(item)]
                temp_pay_type = dict["new_payment_type"+str(item)]
#                temp_pay_type = "Partial Temporary Arrangement"
                pay=dict["new_pay_amt"+str(item)]
                paid=dict["new_paid_amt"+str(item)]
                temp_pay_amt = Money(pay,2)
                temp_pay_paid = Money(paid,2)
                newrecords={"temparrangement_id":temp_id,"temppayment_nbr":temppayment_nbr,"payment_dt":toDate(temp_pay_dt),
                            "payment_nbr":temp_pay_nbr,"payment_type":temp_pay_type,"payment_amt":temp_pay_amt,"paid_amt":temp_pay_paid,
                            "active":1,"override_flag":0,"loan_id":loan_id}
                newlist.append(newrecords)

    return to_obtain_cycle, sorted(newlist,key=itemgetter('payment_dt'))

def validating_pta(new_dic,loan_id,conn=None):
    '''
    This functionality validates the given TA schedule from TA-UI and
    checks if the new TA schedule provided is same as that of one existing available in TA table.
    '''
    if not conn:
        conn = TranDB(section="TMS_DATA")
        cur = conn.getcursor()
    else:
        cur = conn.getcursor()

    quer="select * from temparrangement where loan_id = %s and override_flag = 0 \
        and active=1 order by payment_nbr,temppayment_nbr"%(loan_id)
    query_res=conn.processquery(query = quer, curs = cur, count=0,fetch = True)
    count_chk = 0
    if query_res:
        for record in query_res:
            for i in new_dic:
                if ((i['payment_dt']==record['payment_dt']) and (i['payment_amt']== record['payment_amt'])):
                    count_chk+=1
        if count_chk == len(query_res) and len(new_dic) == len(query_res):
            return 0
    else:
        quer="select * from PaymentCalendar where loan_id = %s and override_flag = 0 \
        order by payment_nbr"%(loan_id)
        query_res=conn.processquery(query = quer, curs = cur, count=0,fetch = True)
        if query_res:
            if new_dic:
                for record in query_res:
                    for i in new_dic:
                        if ((i['payment_dt']==record['payment_dt']) and (i['payment_amt']== record['payment_amt'])):
                            count_chk+=1
                if count_chk == len(query_res) and len(new_dic) == len(query_res):
                    return 0
            else:
                return 0
    return 1

def fetch_unpaid_amount_from_pc(loan_id,to_obtain_cycle=0):
    '''
    Fetches the schedule from Payment Calendar along with the total amount paid for the loan
    and adjusts the same cycle wise towards each PC record.
    @param to_obtain_cycle: Used under Partial TA, to judge the cycles for which the schedule needs to be calculated.
    '''
    unpaid_amount = {}
    unpaidamt = []
    currDate=datetime.datetime.now()
#    Step1: Get a TranDB Connection
    conn = TranDB(section="TMS_DATA")
    cur = conn.getcursor()
#    Step2: Take PaymentCalendar entries.
    if not to_obtain_cycle:
        sql = "select payment_id,payment_nbr,payment_type,payment_amt,paid_amt,payment_dt from\
               PaymentCalendar where loan_id='%s' and override_flag=0  order by payment_nbr" %(loan_id)
    else:
        sql = "select payment_id,payment_nbr,payment_type,payment_amt,paid_amt,payment_dt from PaymentCalendar \
                where loan_id='%s' and override_flag=0  and payment_nbr <= %s order by payment_nbr" %(loan_id, to_obtain_cycle)

    result=conn.processquery(query = sql, curs = cur, count=0,fetch = True)

#    Step3: Form the dictionary  with all PAID amount as Zero for PC entries
    if result:
        schedule = {}
        for record in result:
            temp=schedule.get(record['payment_nbr'],[])
            temp.append([record['payment_id'],record['payment_dt'],
                                 LSS_DICT[record['payment_type']],
                                 Money(record['payment_amt'],2),
                                 Money('0.00',2),0])
            schedule[record['payment_nbr']] = temp

#    Step4: Logic here for Accounting  paid amount cycle wise for the new schedule.
    totalPaid = getPaidAmt_tran(loan_id,currDate,conn)
    amount = Money(totalPaid,2)
    for key,items in schedule.iteritems():
        due = 0
        for k in range(len(items)):
            due = due + Money(items[k][3],2)
            payment=Money(items[k][3],2)
            if amount>=payment:
                items[k][4]=payment
                amount=amount-payment
            else:
                items[k][4]=amount
                amount = 0
                break

    if schedule:
        for cycle_no,pc_record in schedule.iteritems():
            for record in pc_record:
                if cycle_no in unpaid_amount:
                    unpaid_amount[cycle_no]+= record[3] - record[4]
                else:
                    unpaid_amount[cycle_no] = record[3] - record[4]

        unpaidamt = [[int(cyclekey),unpaid_amount[cyclekey]] for cyclekey in unpaid_amount.keys() if unpaid_amount[cyclekey] > 0]

    return unpaidamt

def promise_to_pay(request):
    '''
    Functionality for scheduling TA. Either FULL or Partial TA

    if(int(datetime.datetime.now().month) <= 10):
        if last_day_of_month == currentDate.day:
            display_months = {mnthno:name_month[mnthno] for mnthno in range(int(datetime.datetime.now().month)+1,int(datetime.datetime.now().month)+4) }
        else:
            display_months = {mnthno:name_month[mnthno] for mnthno in range(int(datetime.datetime.now().month),int(datetime.datetime.now().month)+3) }
        print display_months
    elif (int(datetime.datetime.now().month) == 11):
        display_months = {11:'November', 12:'December',1:'January'}
    elif (int(datetime.datetime.now().month) == 12):
        display_months = {12:'December',1:'January',2:'February'}'''

    every_option = ['A SPECIFIC DATE OF THE MONTH','LAST WORKING DAY OF A MONTH','LAST DAY OF MONTH','LAST MONDAY OF EACH MONTH',
                    'LAST TUESDAY OF EACH MONTH','LAST WEDNESDAY OF EACH MONTH','LAST THURSDAY OF EACH MONTH','LAST FRIDAY OF EACH MONTH']
    payment_type={"select":"select","PRNDUE":"Principal Due","INTCAPLZD":"Interest Capitalized",\
                  "ARRFEE":"Arrear Fee","DEFLTFEE":"Default Fee","TERMNFEE":"Termination Fee","XTRPREPYMT":"Extra Prepayment"}
    repayment_type=["Select","Full Temporary Arrangement","Partial Temporary Arrangement"]
    status=["TEMPORARY ARRANGEMENT"]
    mnth_range =range(1,32)
    flag_idtfy_get_post=0
    max_cycle_number=0
    pay_type_cnt=0
    existing_TASchedule={}
    type_post=""
    type_status=""
    msg=0
    other_msg = 0
    chk_save_click=0
    temp_max_nu=0
    prepayment_flag=0
    paycal_max_cy=0
    bal_infm={}
    tempquery_res=''
    schedule_no = 1
    refund_msg = None
    last_cycle = 0
    trivial_refund_id=0
    refund_amt =0
    from_page = ""
    schedule={}
    unpaidamt = []
    discard_flag = 0
    ta_month_to_show = pcconfig.TA_AUTO_SCHEDULE_MONTHS
    ta_reasons = queueconfig.TA_REASONS
    currentDate=datetime.date.today()
    date_elem=datetime.datetime.now()
    username=request.session['username']
    taReason = ""
    OPB = 0.0
    last_cycle_number = 0
    paymentHoliday = None
    #Fetching Tran DB Connection
    conn = TranDB(section="TMS_DATA")
    cur = conn.getcursor()
    
    if request.method=='GET':
        loan_id=request.GET['loan_id']
    else:
        loan_id=request.POST['loan_id']

    #Displays repayment type based on the status of the loan
    case_id=get_case_id_by_entity_id(loan_id,'LOAN')
    status_cd=get_loan_status_by_loan_case_id(case_id)
    # chk the RMPB record created for the loan, if so donot allow PTA
    chk_RMPB="select * from PaymentCalendar where loan_id = %s and override_flag = 0 \
                                and payment_type = '%s' "%(loan_id,"RMPB")
    chk_RMPB_res=conn.processquery(query = chk_RMPB, curs = cur, count=0,fetch = True)
    pro_class = get_product_classification(loan_id)
    #sql = "select product_classification from Product p join Loan_Latest ll on ll.product_id=p.product_id\
    #        where loan_id=%s"%(loan_id)
    #prodClassification = conn.processquery(query = sql, curs = cur, count=1,fetch = True)
    paycal_logger.info('Product Classification :: '+str(pro_class))
    if status_cd  not in ("TEMPORARY ARRANGEMENT","DEBT MANAGEMENT","WITHDRAWAL") and not chk_RMPB_res:
        if pro_class == 'LOC':
            repayment_type=["Select","Full Temporary Arrangement","Payment Holiday"]
        else:
            repayment_type=["Select","Full Temporary Arrangement","Partial Temporary Arrangement"]
    else:
        repayment_type=["Select","Full Temporary Arrangement"]
    from gcms import dbtmsapi
    try:
        if request.method=='GET':
            Sch_Obj = schedule_for_loan.Schedule(loan_id)
            if status_cd=="TEMPORARY ARRANGEMENT":
                schedule['Schedule1'] = Sch_Obj.TAschedule()
            else:
                if pro_class == 'LOC':
                    schedule['Schedule1']=Sch_Obj.LOC_actualSchedule()                    
                else:
                    schedule['Schedule1']=Sch_Obj.actualSchedule(return_type=0)
                    
        else:
            flag_idtfy_get_post=1
            dict = request.POST

            '''
            Based on the provided reschedule type, decides whether its Full / Partial TA.
            For Full TA - ta_flag = 1.
            For Partial TA - ta_flag = 0.
            For Payment Holiday (LOC) - ta_flag = 2.
            '''
            type_post = request.POST['reschedule_type']
            if type_post == 'Full Temporary Arrangement':
                ta_flag = 1
                if request.POST.getlist('ta_reason'):
                    taReason = "FTA: "+str(request.POST['ta_reason'])
            elif type_post == 'Partial Temporary Arrangement':
                ta_flag = 0
#                if request.POST.getlist('ta_reason'):
                taReason = "PTA: "+str("TA_Scheduled_by_"+str(username))
            elif type_post == 'Payment Holiday':
                ta_flag = 2
#                 import pdb;pdb.set_trace()
                if pro_class == 'LOC':
                    from_page=''
                    if request.POST.get('from_page',''):
                        from_page =  request.POST['from_page']
                        trivial_refund_id = request.POST['triv_id']
#                         refund_amt = Money(request.POST.get('ob',''),2)
#                         OPB = request.POST['opb']  
                    if from_page=='refund' :
                        paymentHoliday = payment_holiday(loan_id=loan_id,from_page=from_page,trivial_refund_id=trivial_refund_id)
                    else:
                        paymentHoliday = payment_holiday(loan_id=loan_id)
                    paycal_logger.info('Payment Holiday Dict :: '+str(paymentHoliday))

            '''
            If the request is made by Refund Service then the following values get populated.
            '''
            if request.POST.get('from_page',''):
                from_page =  request.POST['from_page']
                trivial_refund_id = request.POST['triv_id']
                refund_amt = Money(request.POST.get('ob',''),2)
                OPB = request.POST['opb']

            '''
            Based on type of ta_flag the below functionality generates schedule.
            ta_flag = 0 : Generates Partial TA Schedule based on CC Rep input.
            ta_flag = 1 : Generates Full TA Schedule based on CC Rep input.
            if from_page = 'refund' : Generates schedule based on the refund amount entered by CC Rep and
                                        generates schedule.
            '''
            #if pro_class == 'LOC':
                #payments_obj = pcfactory.getpmobj('TMS_DATA')
                #payments_obj.generalsuppress(loan_id, "Web Service", wat_sup = 1,status_sup= -1,int_sup= -1,delin_sup= -1,mpc_sup= -1,arr_sup= -1,fee_sup= -1,wat_sup_tilldate=None,wat_sup_reason=pcconfig.WAT_UNSUP_REASON['CSTD'])
            
            if dict.has_key("save") or dict.has_key("fullptpsave") or dict.has_key("discard"):
#                 import pdb;pdb.set_trace()
                chk_save_click=1
                if dict.has_key("discard"):
                    discard_flag = 1
                    taReason = "PTA: "+str("TA_Discarded_by_"+str(username))
                if 'status' in request.POST:
                    type_status=request.POST['status']

                '''
                if ta_flag = 1:
                    Recalcula OPB / Deciding the payment Plan for TA / DMGT.
                    Creates New TA List based on the UI Input.
                if ta_flag = 0:
                    Just creates TA List based on the input
                    Validation takes place for the PTA records with the one available in DB.
                    valid = 1 : Changes are made under TA and the same can be SAVED / DISCARDED. (DEFAULT = 1)
                    valid = 0 : No Changes Made. Hence exists the TA Process.
                '''
                valid = 0
                if ta_flag == 1:
                    status_cd=get_loan_status_by_loan_case_id(case_id)
                    if status_cd != type_status:

                        pcfunc.promisetopay(case_id, username,date_elem=date_elem,conn_close=0)
                        trandbupdateGCMCase(case_id,status_cd=type_status,done_by=username,date_elem=date_elem)
                    #For Full TA : ta_type = 1(default value)
                    to_obtain_cycle, new_TAList = new_TA_records_dict_formation(dict,loan_id)
                    #By default the valid flag is set to 1, for FULL TEMPORARY ARRANGEMENT
                    valid = 1
                    temp_pay_type = "FTA"
                elif ta_flag == 0:
                    #For Partial TA : ta_type = 0
                    to_obtain_cycle, new_TAList = new_TA_records_dict_formation(dict,loan_id,ta_type=0,discard_flag=discard_flag)
                    valid=validating_pta(new_TAList,loan_id,conn=conn)
                    temp_pay_type = "PTA"
                '''
                Enters the functionality for Processing TA.
                '''
                if valid:
                    '''
                    Fetches the No of times the TA has been rescheduled by customer / CC Rep and updates it.
                    '''
                    quer="select * from temparrangement where loan_id = %s and override_flag = 0 \
                                and active=1 order by payment_nbr,temppayment_nbr"%(loan_id)
                    existing_TASchedule=conn.processquery(query = quer, curs = cur, count=0,fetch = True)
                    if existing_TASchedule and existing_TASchedule[0]['schedule_no']:
                        schedule_no = int(max(result['schedule_no'] for result in existing_TASchedule) + 1)

                    '''
                    Calls fetch_unpaid_amount_from_pc frunctionality to get the unpaid amount.
                    '''
                    unpaidamt = fetch_unpaid_amount_from_pc(loan_id,to_obtain_cycle)

                    '''
                    If any active TA is available for the requested loan, then the same will be overridden any new TA
                    schedule will be added.
                    Existing Availability is based on the query response obtained above : existing_TASchedule.
                    '''
                    ta_obj = pcfactory.gettaobj(section='TMS_Data',loan_id=loan_id)
                    if not existing_TASchedule:
                        msg = ta_obj.temparrangement_new(new_TAList,unpaidamt,username,date_elem,temp_pay_type=temp_pay_type,
                                                   schedule_no=schedule_no,ta_flag=ta_flag,loan_id=loan_id)
                    elif existing_TASchedule:
                        msg = ta_obj.edittemparrangement_new(existing_TASchedule,new_TAList,unpaidamt,username,temp_pay_type=temp_pay_type,
                                                             cur_date=date_elem,schedule_no=schedule_no,ta_flag=ta_flag,loan_id=loan_id)

                    
                    if pro_class == 'LOC':  # For LOC - FTA Reset MPC & Set to_be_closed & suspend_flag=1
                        reset_sql = '''update Payments set missed_payment_counter=0, arrangement_type=2, to_be_closed=1,suspend_flag=1,
                        modified_date=%s, modified_by=%s where loan_id=%s'''
                        conn.processquery(query=reset_sql, curs=cur, args=(date_elem, username, loan_id))
                else:
                    other_msg = 1

                '''
                Adding to gcm_notes table only if msg is TRUE
                '''
                if msg:
                    caseID = gcmcaseapi.trandb_get_case_id_by_entity_id(loan_id, "LOAN")
                    logID = gcmcaseapi.tranget_logid_by_caseid(caseID)
                    gcmcaseapi.trandbadd_gcm_notes(logID['log_id'],"TA_SCHEDULER",taReason,username,date_elem)
                '''
                If new TA scheduled , will be inserted in TA_DelinquentInfo
                '''
                paymentutils.createTA_delinquent(loan_id,username,conn,paycal_logger,date_elem,0)
                paymentutils.sync_main_current_delinquent(loan_id,paycal_logger,conn,date_elem,username)

                query = "select account_cust_id,store_id from Loan_Latest where loan_id=%s"%(loan_id)
                result = conn.processquery(query = query, curs = cur, count=1,fetch = True)
                updateImmPullinCPAInfo(result['account_cust_id'],result['store_id'],username,maxHit=None)


            '''
            Updates daily run phase 2, if any changes are made in transactions / paydates / status for given loan
            '''
            if msg is True and not refund_msg:
                daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
                if isDailyRunStarted(date_of_run=daily_run_date):
                    updateDeltaMatrix(loan_id,'ta')
            elif refund_msg and refund_msg.upper() in ("SUCCESS"):
                msg = True

            '''
            Fetches the schedule for Partial TA to Display in UI
            '''
            if type_post == "Partial Temporary Arrangement":

                if from_page=='refund' :
                    schedule = eval(request.POST['schedule'])
                    max_cycle_number = eval(request.POST['max_cycle_no'])
                    last_cycle_number = eval(request.POST['last_cycle_number'])
                else:
                    if not msg:
                        conn.rollback()
                    Sch_Obj = schedule_for_loan.Schedule(loan_id)
                    cycle_number = Sch_Obj.last_cycle
                    schedule,max_cycle_number=Sch_Obj.actualSchedule(return_type=1)
                    schedule_without_future={}
                    for cycle in schedule:
                        if cycle <= cycle_number:
                            schedule_without_future[cycle]=schedule[cycle]

        #check whether daily interest product or if not follow existing logic
        chk_daily = "select * from Loan l join Product p on l.product_id=p.product_id and p.interest_frequency='daily' where l.loan_id= %s"%(loan_id)
        chk_daily_res=conn.processquery(query = chk_daily, curs = cur, count=0,fetch = True)
        if chk_daily_res:
            # get the crossed cycle from Payment calendar as max cycle
            get_last_cycle="select ifnull(max(payment_nbr),0) as cycle from PaymentCalendar where loan_id = %s and override_flag = 0 and payment_dt <= curdate() "%(loan_id)
            get_last_cycle_res=conn.processquery(query = get_last_cycle, curs = cur, count=0,fetch = True)
            last_cycle = get_last_cycle_res[0]['cycle']
        else:
            if not last_cycle_number:
                paycal=PaymentCalendar.objects.filter(loan=loan_id,override_flag=0).order_by("-payment_nbr")[0]
                paycal_max_cy=paycal.payment_nbr
                last_cycle=paycal.payment_nbr
            else:
                last_cycle = last_cycle_number

        '''
        Fetches the outstanding DUE AMOUNT details for the loan.
        '''
        bal_infm=get_balance_dtls(loan_id)[0]
#        payments_obj = pcfactory.getpmobj()
#        pre_date=currentDate-timedelta(days=1)
#        due_amt = payments_obj.calculate_due_amount(loan_id,pre_date)
        OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
        bal_infm['OB']=OB
        bal_infm['OA']=dbtmsapi.calculate_outstanding_arrears(loan_id,conn)

        '''
        Fetches the TA details from temparrangement table for FTA
        '''
        status_cd=gcmcaseapi.trandb_get_loan_status_by_loan_id(loan_id)
        if status_cd == "TEMPORARY ARRANGEMENT":
#            tempquery_res=Sch_Obj.TAschedule(conn_close=0)
#            if tempquery_res:
#                temp_max_nu=max(tempquery_res.keys())
            quer = "select *,sum(payment_amt) as consolidated_payment_amt, sum(paid_amt) as consolidated_paid_amt from temparrangement where loan_id = %s and \
            override_flag = 0 and active=1 group by temppayment_nbr  order by temppayment_nbr"%(loan_id)
            tempquery_res = conn.processquery(query = quer, curs = cur, fetch = True)
            if tempquery_res:
                temp_max_nu=tempquery_res[-1]['payment_nbr']
        '''
        Checks whether any Early Payment is scheduled for this loan.
        '''
        query_prep="select * from Prepayments where loan_id = %s and override_flag = 0 \
            and active=1"%(loan_id)
        prepayment_check = conn.processquery(query = query_prep, curs = cur, fetch = True)
        if prepayment_check:
            prepayment_flag=1
        else:
            prepayment_flag=0


        '''
        Closes the TranDB connection created for this transaction.
        '''
        if msg is True:
            conn.commit()
        conn.close()

    except Exception,e:
        paycal_logger.debug('Exception received in custdetail.promise_to_pay :: '+str(e)+"\nTraceback :: "+str(traceback.format_exc()))
        if 'open' in conn.conn.__str__():
            paycal_logger.info('Connection Thread_id :: '+str(conn.conn.thread_id()) +' Connection status :: '+str(conn.conn.__str__()))
            conn.rollback()
            conn.close()
            paycal_logger.info('Connection rolled back and closed!')

    status_cd=get_loan_status_by_loan_case_id(case_id)
    return render_to_response('custdetail/promise_to_pay.html',{'loan_id':loan_id,'schedule':schedule,'repayment_type':repayment_type,
        'type_post':type_post ,'flag_idtfy_get_post':flag_idtfy_get_post,'paycal_max_cy':paycal_max_cy,
        'max_cycle_number':max_cycle_number,'payment_type':payment_type,'result':bal_infm,
        'last_cycle':last_cycle,'pay_type_cnt':pay_type_cnt,'prepayment_flag':prepayment_flag,'temp_max_nu':temp_max_nu,
        'temp_rec':tempquery_res,'currentDate':currentDate,'status':status,'type_status':type_status,'status_cd':status_cd,'msg':msg,
        'chk_save_click':chk_save_click,'mnth_range':mnth_range,'every_option':every_option,'from_page':from_page,
        'refund_amt': refund_amt, 'triv_refund_id':trivial_refund_id, 'OPB':OPB,'ta_month_to_show':ta_month_to_show,
        'other_msg':other_msg,'ta_reasons':ta_reasons,'paymentHoliday':paymentHoliday})

#End of New TA Functionality

promise_to_pay = maintenance_deco_popups(promise_to_pay)

def full_insert_new_dict_formation(new_chk_elem,dict,loan_id):
    newlist = []
    for item in new_chk_elem:
        newrecords={}
        temparrangement_id = ''
        temppayment_nbr = ''
        temp_pay_dt  = dict["fullpayment_dt"+str(item)]
        temp_pay_nbr = dict["fullpayment_nbr"+str(item)]
        temp_pay_type = dict["fullpayment_type"+str(item)]
        pay=dict["fullpayment_amt"+str(item)]
        paid=dict["fullpaid_amt"+str(item)]
        temp_pay_amt = Money(pay,2)
        temp_pay_paid = Money(paid,2)
        if temparrangement_id:
            temparrangement_id = int(temparrangement_id)
        newrecords={"temparrangement_id":temparrangement_id,"temppayment_nbr":temppayment_nbr,"payment_dt":toDate(temp_pay_dt),"payment_nbr":temp_pay_nbr,
           "payment_type":temp_pay_type,"payment_amt":temp_pay_amt,"paid_amt":temp_pay_paid,"active":1,"override_flag":0,"loan_id":loan_id}
        newlist.append(newrecords)
    return newlist
def full_edit_original_dict_formation(schedule):
    originalrecords={}
    origdict={}
    for key,value in schedule.iteritems():
        tot_pay_amt=0
        tot_paid_amt=0
        origlist=[]
        for item in value:
            pay_id  = item[0]
            pay_dt  = item[1]
            pay_cycle=key
            pay_type = item[2]
            pay_amt = item[3]
            pay_paid = item[4]
            tot_pay_amt += Money(item[3])
            tot_paid_amt += Money(item[4])
            temp_pay_nbr=item[5]
            if (pay_amt-pay_paid)>0:
                origdict = {"temparrangement_id":pay_id,"temppayment_nbr":temp_pay_nbr,"payment_dt":pay_dt,"payment_nbr":pay_cycle,\
                       "payment_type":pay_type,"payment_amt":pay_amt,\
                       "payment_amt":pay_amt,"paid_amt":pay_paid }
                origlist.append(origdict)
        unpaid=tot_pay_amt-tot_paid_amt
        originalrecords[key]=(unpaid,origlist)
    return originalrecords
def full_edit_new_dict_formation(dict,loan_id):
     unchk_elem=dict.getlist('cycledetail')# required for new and original records in unchecked TA records
     new_chk_elem=dict.getlist('fullcheckticks')# for new records from ui
     old_chk_elem=dict.getlist('oldcheckticks')
     newlist=[]
     for cnt in unchk_elem:
         if dict.has_key("oldpayment_dt"+str(cnt)):
           temparrangement_id = dict["oldptpid"+str(cnt)]
           temppayment_nbr = ''
           temp_pay_dt  = dict["oldpayment_dt"+str(cnt)]
           temp_pay_nbr = dict["oldpayment_nbr"+str(cnt)]
           temp_pay_type = dict["oldpayment_type"+str(cnt)]
           pay=dict["oldpayment_amt"+str(cnt)]
           paid=dict["oldpaid_amt"+str(cnt)]
           temp_pay_amt = Money(pay,2)
           temp_pay_paid = Money(paid,2)
           if temp_pay_type == 'Temporary Arrangement':
               temparrangement_id = int(temparrangement_id)
           newrecords={"temparrangement_id":temparrangement_id,"temppayment_nbr":temppayment_nbr,"payment_dt":toDate(temp_pay_dt),"payment_nbr":temp_pay_nbr,
           "payment_type":temp_pay_type,"payment_amt":temp_pay_amt,"paid_amt":temp_pay_paid,"active":1,"override_flag":0,"loan_id":loan_id}
           newlist.append(newrecords)
##                         Forming a dictionary for NEW checked elements
     for cnt in new_chk_elem:
           newrecords={}
           temparrangement_id = ''
           temppayment_nbr = ''
           temp_pay_dt  = dict["fullpayment_dt"+str(cnt)]
           temp_pay_nbr = ''
           temp_pay_type = dict["fullpayment_type"+str(cnt)]
           pay=dict["fullpayment_amt"+str(cnt)]
           paid=dict["fullpaid_amt"+str(cnt)]
           temp_pay_amt = Money(pay,2)
           temp_pay_paid = Money(paid,2)
           if temparrangement_id:
               temparrangement_id = int(temparrangement_id)
           newrecords={"temparrangement_id":temparrangement_id,"temppayment_nbr":temppayment_nbr,"payment_dt":toDate(temp_pay_dt),"payment_nbr":temp_pay_nbr,
           "payment_type":temp_pay_type,"payment_amt":temp_pay_amt,"paid_amt":temp_pay_paid,"active":1,"override_flag":0,"loan_id":loan_id}
           newlist.append(newrecords)
     oldlist=[]
     return   newlist

def full_insert_original_dict_formation(schedule):

    originalrecords={}
    for key,value in schedule.iteritems():
         tot_pay_amt=0
         tot_paid_amt=0
         origlist=[]
         for item in value:
            pay_id  = item[0]
            pay_dt  = item[1]
            pay_cycle=key
            pay_type = item[2]
            pay_amt = item[3]
            pay_paid = item[4]
            tot_pay_amt += Money(item[3])
            tot_paid_amt += Money(item[4])
            temp_pay_nbr=item[5]
            origdict = {"temparrangement_id":pay_id,"temppayment_nbr":temp_pay_nbr,"payment_dt":pay_dt,"payment_nbr":pay_cycle,\
                       "payment_type":pay_type,"payment_amt":pay_amt,\
                       "payment_amt":pay_amt,"paid_amt":pay_paid }
            origlist.append(origdict)
         unpaid=tot_pay_amt-tot_paid_amt
         originalrecords[key]=(unpaid,origlist)

    return originalrecords

def partial_new_dictionary_formation(dict,schedule_without_future,loan_id,discard_flag = 0):
    chk_list=[]
    newlist=[]
    chk_elem=dict.getlist('checkticks')
    ticklist=dict.getlist('ticks')
    cycledetail=dict.getlist('cycledetail')
    for row in cycledetail:
        fieldname='checkticks'+row
        index_list=row.split("-")
        cycle=index_list[0]
        elem=index_list[1]
        for counter in xrange(1,int(elem)+1):
            condition=0
            field2='hpayment_type'+str(cycle)+"-"+str(counter)#
            checkbox_name = "checkticks"+str(cycle)+"-"+str(counter)
            tickname="ticks"+str(cycle)+","+str(counter)+"-"+str(elem)
            if not discard_flag and dict["hpayment_type"+str(cycle)+"-"+str(counter)]=='Temporary Arrangement':
                condition = 1
            elif discard_flag and tickname not in ticklist and dict["hpayment_type"+str(cycle)+"-"+str(counter)]=='Temporary Arrangement':
                condition = 1
            if condition:
                chkpay_id=dict["temp_id"+str(cycle)+"-"+str(counter)]
                chktemp_pay_id=dict["temp_nbr"+str(cycle)+"-"+str(counter)]
                chkpay_dt = dict["payment_dt"+str(cycle)+"-"+str(counter)]
                chkpay_nbr = dict["payment_nmr"+str(cycle)+"-"+str(counter)]
                chkpay_type = dict["hpayment_type"+str(cycle)+"-"+str(counter)]
                chkpay_amt = Money(dict["payment_amt"+str(cycle)+"-"+str(counter)],2)
                chkpay_paid = Money(dict["paid_amt"+str(cycle)+"-"+str(counter)],2)
                item_list=[chkpay_id,toDate(chkpay_dt),chkpay_type,chkpay_amt,chkpay_paid,chkpay_nbr]
                chk_list.append(item_list)
    if not discard_flag and dict.has_key("new"):
        tmp_elem=dict.getlist('new')
        for item in tmp_elem:
            newrecords={}
            temp_id=""
            temppaydt  =dict["new_pay_dt"+str(item)]
            temp_pay_nbr = dict["new_cycle"+str(item)]
            temp_pay_type = dict["new_payment_type"+str(item)]
            temp_pay_amt = Money(dict["new_pay_amt"+str(item)],2)
            temp_pay_paid = Money(dict ["new_paid_amt"+str(item)],2)
            new = [temp_id,toDate(temppaydt),temp_pay_type,temp_pay_amt,temp_pay_paid,temp_pay_nbr]
            newlist.append(new)
    lis=[]
    if newlist!=[]:
        chk_list.extend(newlist)
    print chk_list
    if chk_list!=[]:
        for item in chk_list:
            if item[0]:
                temp_id = int(item[0])
            else:
                temp_id = item[0]
            dict={"temparrangement_id":temp_id,\
               "payment_dt":item[1],"payment_nbr":item[5],\
               "payment_type":item[2],"payment_amt": Money(item[3],2),\
               "paid_amt": Money(item[4],2),"loan_id":loan_id}
            lis.append(dict)
    return lis

def new_dictionary_formation(dict,loan_id):
     newlist = []
     if dict.has_key("new"):
        tmp_elem=dict.getlist('new')
        for item in tmp_elem:
           newrecords={}
           temparrangement_id = ''
           temppayment_nbr = ''
           temp_pay_dt  = dict["new_pay_dt"+str(item)]
           temp_pay_nbr = dict["new_cycle"+str(item)]
           temp_pay_type = dict["new_payment_type"+str(item)]
           pay=dict["new_pay_amt"+str(item)]
           paid=dict["new_paid_amt"+str(item)]
           temp_pay_amt = Money(pay,2)
           temp_pay_paid = Money(paid,2)
           if temparrangement_id:
               temp_id = int(temparrangement_id)
           else:
               temp_id = temparrangement_id
           newrecords={"temparrangement_id":temp_id,"temppayment_nbr":temppayment_nbr,"payment_dt":toDate(temp_pay_dt),"payment_nbr":temp_pay_nbr,
           "payment_type":temp_pay_type,"payment_amt":temp_pay_amt,"paid_amt":temp_pay_paid,"active":1,"override_flag":0,"loan_id":loan_id}
           newlist.append(newrecords)
     return newlist
def orginal_dictionary_formation(dict,schedule_without_future):
    org_sch={}
    originalrecords={}
    if dict.has_key("checkticks"):
        chk_elem=dict.getlist('checkticks')
        cycledetail=dict.getlist('cycledetail')
        for row in cycledetail:
            fieldname='checkticks'+row
            index_list=row.split("-")
            cycle=index_list[0]
            elem=index_list[1]
            if fieldname in chk_elem:
                for counter in xrange(1,int(elem)+1):
                    field2='hpayment_type'+str(cycle)+"-"+str(counter);
                    org_sch[int(cycle)]=schedule_without_future['schedule_without_future'][int(cycle)]
            else:
                for counter in xrange(1,int(elem)+1):
                    field2='hpayment_type'+str(cycle)+"-"+str(counter);
                    if dict[field2]=='Temporary Arrangement':
                        org_sch[int(cycle)]=schedule_without_future['schedule_without_future'][int(cycle)]
    for key,value in org_sch.iteritems():
        tot_pay_amt=0
        tot_paid_amt=0
        origlist=[]
        for item in value:
            pay_id  = item[0]
            pay_dt  = item[1]
            pay_cycle=key
            pay_type = item[2]
            pay_amt = item[3]
            pay_paid = item[4]
            tot_pay_amt += Money(item[3])
            tot_paid_amt += Money(item[4])
            temp_pay_nbr=item[5]
            origdict = {"temparrangement_id":pay_id,"temppayment_nbr":temp_pay_nbr,"payment_dt":pay_dt,"payment_nbr":pay_cycle,\
                       "payment_type":pay_type,"payment_amt":pay_amt,\
                       "payment_amt":pay_amt,"paid_amt":pay_paid }
            origlist.append(origdict)
        unpaid=tot_pay_amt-tot_paid_amt
        originalrecords[key]=(unpaid,origlist)
    return originalrecords
def append_paycal_temp(loan_id, refund_amount = 0):
    '''
    Connection Doesn't close by default
    '''
    max_cycle_number=0
    currDate=datetime.datetime.now()
    conn = TranDB(section="TMS_DATA")
#    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    cur = conn.getcursor()
    sql = "select payment_id,payment_nbr,payment_type,payment_amt,paid_amt,payment_dt from\
       PaymentCalendar where loan_id='%s' and \
       override_flag=0  order by payment_nbr,\
       field(right(payment_type,3),'FEE','LZD','DUE','YMT')" %(loan_id)
    result=conn.processquery(query = sql, curs = cur, count=0,fetch = True)
#    result = con.get_all_results(query = sql)

#        Step :Take Temparrangement entries.
    quer="select * from temparrangement where loan_id = %s and override_flag = 0 \
        and active=1 order by payment_nbr,temppayment_nbr"%(loan_id)
#      query_res=con.get_all_results(query = quer)
    query_res=conn.processquery(query = quer, curs = cur, count=0,fetch = True)

    temp_record_entries={}
    if query_res:
        temp_record_entries={}
        for record in query_res:
            temp=temp_record_entries.get(record['payment_nbr'],[])
            temp.append([record['temparrangement_id'],record['payment_dt'],
                                 LSS_DICT[record['payment_type']],
                                 Money(record['payment_amt'],2),
                                 Money('0.00',2),record['temppayment_nbr']])
            temp_record_entries[record['payment_nbr']] = temp
#        Step :Form the dictionary  with all PAID amount as Zero.

    if result:
        pay_cal_entries={}
        for record in result:
            temp=pay_cal_entries.get(record['payment_nbr'],[])
            temp.append([record['payment_id'],record['payment_dt'],
                                 LSS_DICT[record['payment_type']],
                                 Money(record['payment_amt'],2),
                                 Money('0.00',2),0])
            pay_cal_entries[record['payment_nbr']] = temp
#        Step   : Form the new dictinary with integration of temporary and paymentschedule
    schedule={}
    for cycle in  pay_cal_entries:
            if cycle in temp_record_entries:
                tot_temp_payment = 0
                tot_payment = 0
                for items in pay_cal_entries[cycle]:
                    tot_payment+=Money(items[3],2)
                for tempitem in temp_record_entries[cycle]:
                    tot_temp_payment+= Money(tempitem[3],2)
                pay_cal_amount=tot_payment-tot_temp_payment
                i=0

                while(pay_cal_amount>0):
                    if pay_cal_entries[cycle][i][3] <= pay_cal_amount:
                        pay_cal_amount = pay_cal_amount - Money(pay_cal_entries[cycle][i][3],2)
                        if cycle in schedule:
                            schedule[cycle].extend([pay_cal_entries[cycle][i]])
                        else:
                            schedule[cycle] = [pay_cal_entries[cycle][i]]
                    else:
                        pay_cal_entries[cycle][i][3]=pay_cal_amount
                        pay_cal_amount = 0
                        if cycle in schedule:
                            schedule[cycle].extend([pay_cal_entries[cycle][i]])
                        else:
                            schedule[cycle] = [pay_cal_entries[cycle][i]]
                    i=i+1
                if cycle in schedule:
                    schedule[cycle].extend(temp_record_entries[cycle])
                else:
                    schedule[cycle]= temp_record_entries[cycle]
            else:
                schedule[cycle]=pay_cal_entries[cycle]

#         Step : Logic here for Accounting  paid amount in  FIP order money for NEW dictionary.
    totalPaid = getPaidAmt(loan_id,currDate)
    amount = Money((totalPaid - refund_amount),2)
    for key,items in schedule.iteritems():
                    due = 0
                    remain = amount
                    for k in range(len(items)):
                        due = due + Money(items[k][3],2)
                        payment=Money(items[k][3],2)
                        if amount>=payment:
                            items[k][4]=payment
                            amount=amount-payment
                        else:
                            items[k][4]=amount
                            amount = 0
                            break
                    if(remain>=due):
                        max_cycle_number = key
                    else:
                        break

    schedule_without_future=deepcopy(schedule)
#      from tms.tmsapi import loan
#      from tms.tmsapi import paydates
#      from tms.pullengine.paymentschedulegenerator import PaymentScheduleGenerator
    Sch_Obj= schedule_for_loan.Schedule(loan_id)
    future_sch=Sch_Obj.actualSchedule()
    last_cycle=Sch_Obj.last_cycle
    future_entries=deepcopy(future_sch)
    for i in future_entries.keys():
        if i<=last_cycle:
            del future_entries[i]
#    loan_obj = loan.Loan(loan_id)
#    paydates_obj = paydates.PayDates(loan_obj)
#    due_dates_dict = paydates_obj.generate_due_dates()#
#    psg_obj=paymentschedulegenerator.PaymentScheduleGenerator(loan_obj,due_dates_dict,conn_close = 0)
#    psg_obj.eopb =psg_obj.get_expected_opb(cycle_due_will_be_paid=1)
#    paycal=PaymentCalendar.objects.filter(loan=loan_id,override_flag=0).order_by("-payment_nbr")[0]
#    last_cycle=paycal.payment_nbr
#    future_entries =psg_obj.generate_future_transactions(last_cycle,minus_unaccounted_principal=1,flag=1)
    if future_entries:
        for cycle,value in future_entries.iteritems():
            for item in value:
                cycle_list = schedule.get(cycle,[])
                cycle_list.append([0,item[1],item[3],Money(item[2],2),Money('0.00',2),0])
                schedule[cycle]=cycle_list
    schedule_with_future=schedule
    for cyc in schedule_with_future:
        schedule_with_future[cyc] = sorted(schedule_with_future[cyc], key = itemgetter(1))
    return {'schedule_with_future':schedule_with_future},{'schedule_without_future':schedule_without_future},{'max_cycle_number':max_cycle_number}

def validate_ptp(new_dic,loan_id):
    conn = TranDB(section="TMS_DATA")
    cur = conn.getcursor()
    quer="select * from temparrangement where loan_id = %s and override_flag = 0 \
        and active=1 order by payment_nbr,temppayment_nbr"%(loan_id)
    query_res=conn.processquery(query = quer, curs = cur, count=0,fetch = True)
    c=0
    if query_res:
        for record in query_res:
            for i in new_dic:
                if ((i['temparrangement_id']!=record['temparrangement_id']) or (int(i['payment_nbr'])!=record['payment_nbr']) or \
                    (i['payment_dt']!=record['payment_dt']) or (i['payment_amt']!= record['payment_amt'])):
                    c = c + 1
    if c==0:
        return 0
    else:
        return 1
def pre_payment(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    if get_loan_status_by_loan_id(loan_id) in ("PARTIAL", "CALLED", "NOT CALLED"):
        return HttpResponse("Loan is not yet ACTIVE !")

    payment_flag=isEndStatus(loan_id)
    username=request.session['username']
    payment_type={"select":"select","REPPREPYMT":"Replacement Prepayment","XTRPREPYMT":"Extra Prepayment"}
    message=""
    records=[]
    update_flag=0
    paycalobj=PayDates.objects.filter(loan=loan_id,override_flag=0).order_by("-paydate")[0]
    maxcycle=paycalobj.cycle
    loanobj=Loan.objects.filter(loan_id=loan_id)[0]
    prodobj=Product.objects.filter(product_id=loanobj.product_id)[0]
    today = datetime.datetime.today().date()
    interest_frequency = prodobj.interest_frequency
    future_pta_date = None # Date from which Prepayments can be scheduled
    due_amt = pcfunc.getpmdata(loan_id)['due_amt'] # Don't allow prepayments if due_amt > 0
    schedule_obj = Schedule(loan_id)
    if schedule_obj.temp_entry: # Allow prepayments only after All Temp Arrangements
        max_temp_dates = max(map(lambda x: x[1], (reduce(lambda x,y: x+y, schedule_obj.temp_entry.values()))))
        if max_temp_dates > today:
            future_pta_date = max_temp_dates
    if request.session.has_key("update_flag"):
        update_flag=request.session["update_flag"]
        del request.session["update_flag"]
    if request.session.has_key("message"):
        message=request.session["message"]
        del request.session["message"]
    current_date=str(datetime.date.today())
    identifying_product=to_identify_pdtinfo(loan_id)
    if identifying_product['dp_cycles']!=None and identifying_product['shipping_flag']!=0:
        pre_check=len(Downpayments.objects.filter(loan=loan_id))
    else:
        pre_check=len(PaymentCalendar.objects.filter(loan=loan_id))
    index_chk=None
    status=""
    chk_box_key=[]
    chk=[]
#    This ajax is to generate cycle number for the entered paydate
    if request.is_ajax:
         cycle_number=0
         checklastcycle=0
         max_rpp_dir = 0
         max_epp_dir = 0
         advance_cycle = 0
         if request.POST.has_key('paydate'):
             paydate=request.POST['paydate']
             paydate_list = PayDates.objects.filter(loan = loan_id,override_flag=0).order_by("cycle")
             dict={}
             for item in paydate_list:
                 paydate_cycle_grace_period=item.paydate+datetime.timedelta(days=prodobj.cycle_grace_period)
                 dict[item.cycle]=paydate_cycle_grace_period
                 for key,value in dict.iteritems():
                     if dates.toDate(paydate)<=value:
                         cycle_number=key
                         break
             if interest_frequency == 'daily':
                 payment_date = datetime.datetime.strptime(paydate, '%Y-%m-%d').date()
                 future_schedule = schedule_obj.generate_future_schedule(schedule_obj.due_dates, payment_date)
                 advance_cycle = max(future_schedule.keys())
                 future_record = future_schedule[cycle_number]
                 if cycle_number < advance_cycle:
                     logger.info("Paydate has advanced as a result of previous RPPs.")
                 max_rpp_dir = future_record['PRNDUE'] + future_record['INTDUE'] + future_record['FEEDUE']
                 max_epp_dir = future_record['OPB']
                 logger.info("Future Schedule Received for the date %s :: "%payment_date + str(future_record))
                 logger.info("max_rpp_dir Calculated :: " + str(max_rpp_dir))
                 logger.info("max_epp_dir Calculated :: " + str(max_epp_dir))
             if  (cycle_number==maxcycle):
                  checklastcycle=1
             result = simplejson.dumps({'cycle_number':cycle_number,'checklastcycle':checklastcycle,
                                                   'max_rpp_dir':max_rpp_dir, 'max_epp_dir':max_epp_dir,
                                                   'advance_cycle' : advance_cycle})
             return HttpResponse(result,mimetype="application/json")
    if request.method=='POST':
        dict= request.POST
        cur_date = datetime.datetime.now()

        for k,v in dict.iteritems():
            if v=='on':
                chk.append(k)
        chk.sort()

        for chk_item in chk:
            if chk_item.__contains__("pre_payment_chk"):
                index_chk=chk.index(chk_item)
                break

        if not (index_chk==None):
            chk_box_key=chk[index_chk:]
            chk_box_key.extend(chk[:index_chk])
        else:
            chk_box_key=chk

        for item in chk_box_key:
                if not ("pre_payment_chk" in item):
#                    record={"loan_id":loan_id,"payment_dt":dict["["+item+",pre_pay_dt]"],"payment_nbr":dict["["+item+",cycle"],"payment_type":dict["["+item+",pre_payment_type]"],"payment_amt":dict["["+item+",pre_pay_amt]"],"user":username,"flag":1}
                    record={"loan_id":loan_id,"payment_dt":dict["pre_pay_dt"+item],"payment_nbr":dict["cycle"+item],"payment_type":dict["pre_payment_type"+item],"payment_amt":dict["pre_pay_amt"+item],"user":username,"flag":1}

                    if record["payment_dt"] and record["payment_nbr"] and record["payment_amt"] and (record["payment_type"]!='select'):
                        records.append(record)

                else:
                    index_payment_chk=item[15:]
                    pre_check=Prepayments.objects.filter(prepayments_id=int(dict["pre_payment_id"+index_payment_chk]))

                    if (pre_check[0].payment_amt!=float(dict["pre_pay_amt"+index_payment_chk])) or \
                            (pre_check[0].payment_type!=dict["pre_payment_type"+index_payment_chk] or
                                     pre_check[0].override_reason!=dict["override_reason"+index_payment_chk]) :
                        records.append({"prepayments_id":int(dict["pre_payment_id"+index_payment_chk]),
                        "loan_id":loan_id,"payment_dt":dict["pre_pay_dt"+index_payment_chk],
                        "payment_nbr":dict["cycle"+index_payment_chk],
                        "payment_amt":dict["pre_pay_amt"+index_payment_chk],
                        "payment_type":dict["pre_payment_type"+index_payment_chk],
                        'reason':dict['override_reason'+index_payment_chk],"flag":2,"user":username})
        # Don't schedule prepayments unless the prepayment date is after all PTAs
        valid_records = []  # Valid records are those that are on or after the future_pta_date (not before)
        for record in records:
            if future_pta_date is not None and \
                            datetime.datetime.strptime(record['payment_dt'], '%Y-%m-%d').date() < future_pta_date:
                request.session['message'] = 'Cannot schedule Prepayments till %s'%future_pta_date
                logger.error('Prepayment record skipped since there is a PTA in future :: ' + str(record))
                continue
            else:
                valid_records.append(record)
        records = valid_records
        if records:
            status=pcfunc.ppmmanual(records, cur_date)
            if 'SUCCESS' in status: # Trigger the Notice of Prepayment (NOEPP/NORPP) Mailers
                if records[0]['payment_type'] == 'XTRPREPYMT': # Due to UI changes, records will contain only 1 record
                    update_or_insert_Notice_Flags(loan_id=loan_id, date_elem=today, NOEPP = 'TO BE SENT')
                elif records[0]['payment_type'] == 'REPPREPYMT':
                    update_or_insert_Notice_Flags(loan_id=loan_id, date_elem=today, NORPP = 'TO BE SENT')
                else:
                    logger.info("Unable to send Notice of Prepayment (NORPP/NOEPP)")
            request.session["update_flag"]=0
        return HttpResponseRedirect("/info/pre_payment/?loan_id="+loan_id)

    prepayments=pcfunc.getppmdata(loan_id)
    if isinstance(prepayments,str) or isinstance(prepayments,unicode):
#        message=prepayments
        message="As of now no Pre-payments for this Loan"
        prepayments={}
    else:
        for pre_pay_sch in prepayments:
            if str(pre_pay_sch["payment_dt"])<current_date:
                pre_pay_sch["past_date"]=1
            else:
                pre_pay_sch["past_date"]=0
    related_tbl=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
    fund_date=""
    loan_status = get_loan_status_by_loan_id(loan_id)

    #Calculates the maximum EPP that can be set for each cycle
    cycle_wise_epp = {}
    principal_type = ['Extra Prepayment','Principal Due','RMPB']
    loan_schedule_withouttemp = schedule_for_loan.Schedule(loan_id)
    paycal_dict = loan_schedule_withouttemp.actualSchedule_without_temp(flag=0,epp_flag=1)
    for cycle in paycal_dict:
        for paycal_entry in paycal_dict[cycle]:
            for pd_type in principal_type:
                if pd_type in paycal_entry:
                    if cycle_wise_epp.has_key(cycle):
                        cycle_wise_epp[cycle] = cycle_wise_epp[cycle] + paycal_entry[2]
                    else:
                        cycle_wise_epp.update({cycle:paycal_entry[2]})
                    break
    rpb = loan_schedule_withouttemp.borrowed_amt
    for cycle in cycle_wise_epp:
        cycle_wise_epp[cycle] = rpb = rpb - cycle_wise_epp[cycle]
#    Validating RPP
    cycle_wise_rpp = {}
    principal_type = ['Principal Due','Interest Capitalized','Partial Temporary Arrangement']
    loan_schedule_withtemp = Schedule(loan_id)
    paycal_dict = loan_schedule_withtemp.actualSchedule()
    for cycle in paycal_dict:
        for paycal_entry in paycal_dict[cycle]:
            for pd_type in principal_type:
                if pd_type in paycal_entry:
                    amt = paycal_entry[2] - paycal_entry[4]
                    if cycle_wise_rpp.has_key(cycle):
                        cycle_wise_rpp[cycle] = cycle_wise_rpp[cycle] + amt
                    else:
                        cycle_wise_rpp.update({cycle:amt})
                    break

    if related_tbl.fund_dt or loan_status=="DOWNPAYMENT":
            if related_tbl.fund_dt:
                fund_date=datetime.date.strftime(related_tbl.fund_dt, "%Y-%m-%d")
    else:
            return HttpResponse('Loan is not yet ACTIVE!')
    return render_to_response('custdetail/pre_payment.html',{"update_flag":update_flag,
                                                             "payment_flag":payment_flag,
                                                             "prepayments":prepayments,
                                                             "payment_type":payment_type,
                                                             "message":message,"status":status,
                                                             "pre_check":pre_check, "fund_date":fund_date,
                                                             'loan_id':loan_id,
                                                             "cycle_wise_epp":cycle_wise_epp,
                                                             "cycle_wise_rpp":cycle_wise_rpp,
                                                             "interest_frequency":interest_frequency,
                                                             "future_pta_date":future_pta_date,
                                                             "today":today, "due_amt": due_amt})
pre_payment = maintenance_deco_popups(pre_payment)

def Inc_exp_popup(request):

    try:
        conn = TranDB(section="TMS_DATA")
        curs = conn.getcursor()

        IandE_log.info(": Inside Income and Expense form population script:")
        tmsconn = mysqldbwrapper.MySQLWrapper(section='TMS_DATA',charset='latin1')
        username = request.session['username']
        cur_date = datetime.datetime.now()

        dict ={}
        store_db={}
        inc_exp_keys=queueconfig.INC_EXP_LIST

        IandE_log.info(": Created a new :")
        msg = None
        if request.method =="POST":
            IandE_log.info(": request.method "+str(request.method)+ ":")
            IandE_log.info(": Inside Post method :")
            loan_id = request.POST['loan_id']
            cust_id = request.POST['cust_id']
            store_id = Loan.objects.get(loan_id=loan_id).store_id

            if request.POST.has_key('Save'):
                IandE_log.info(": Saving Income and Expense form. loan_id - "+str(loan_id)+":")

                que_dict = request.POST
                fields_value_dict = queueconfig.fields_values.copy()
                fields = fields_value_dict.values()


                loan_dict = fields_value_dict
                loan_dict['loan_id'] = loan_id
                loan_dict['cust_id'] = cust_id
                loan_dict['store_id'] = str(store_id)

                cur_date = (datetime.datetime.today()).strftime('%Y-%m-%d %H:%M:%S')

                if  que_dict.has_key('disI'):
                    disposeinc=que_dict["disI"]
                else:
                    disposeinc = 0

                IandE_log.info(": Updating Loan Info table on Income and Expense. loan_id - "+str(loan_id)+ ":")

                IandE_log.info(": Updating Income_Expense table on new Income and Expense details. loan_id - "+str(loan_id)+ ":")

                query_acc_cust_id = "select account_cust_id from Loan_Latest where loan_id = %s" %(loan_id)
                account_cust_id = conn.processquery(query = query_acc_cust_id, curs = curs,count = 1)

                update_IandE = "update Income_Expense set override_flag = 1, modified_date = %s, modified_by = %s where account_cust_id = %s"
                args = (cur_date, username, account_cust_id['account_cust_id'])
                conn.processquery(query = update_IandE, curs = curs, args = args)

                case_id=get_case_id_by_entity_id(cust_id,'CUSTOMER')

                """
                Inserting into Income and Expense table
                """

                for value in que_dict:
                    if value in queueconfig.fields_values.keys():
                        if que_dict[value] =="":
                            loan_dict[value] = int(0)
                        else:
                            loan_dict[value] = str(que_dict[value])

                query_fields = (','.join(fields))
                query_fields = query_fields+', '+str((r'account_cust_id'))+','+str((r'created_by'))+', '+str((r'created_date'))

                query_values = (tuple(map(lambda x:x , loan_dict.values())))
                query_values = query_values + (str(account_cust_id['account_cust_id']), str(username), str(cur_date),)

                insert_iande = "Insert into Income_Expense (%s) values %s" %(query_fields, query_values)
#                 args = (query_fields, query_values)
                conn.processquery(query = insert_iande, curs = curs)

                IandE_log.info(": Details successfully inserted into Income_Expense table. loan_id - "+str(loan_id)+ ":")


                log_id=get_logid_by_caseid(case_id)
                detail_info ="[%s] : Customer's Income and Expenses were evaluated.The disposable income is %s GBP. This is calculated and added through the loan  %s."%(store_id,disposeinc,loan_id)
                notes_id=add_gcm_notes(log_id["log_id"],'Income and Expense',detail_info,username,cur_date)
                if notes_id:
                    status="Note added sucessfully"
                IandE_log.info(": Notes successfylly added for Income and Expense. loan_id - "+str(loan_id)+ " :")
                conn.commit()
                conn.close()
                msg = "Income and Expense details has been saved successfully."
                #return HttpResponse('custdetail/Inc_Exp_popup.html?msg=success')
                '''
                rtiInfo = {}
                rtiInfo['loan_id']          = loan_id
                rtiInfo['newIncome']        = request.POST['tmi']
                rtiInfo['newExpenditure']   = request.POST['tme']

                rtiapi.LOC_ChangeIncomeAndExpenditure(rtiInfo)
                '''
        else:

              loan_id = request.GET['loan_id']
              cust_id =request.GET['cust_id']

        IandE_log.info(": Selecting Existing Income and Expense details from Income and Expense table. loan_id - "+str(loan_id)+ ":")

#         record_query = "select IandE from Loan_Info where loan_id = %s and override_flag = 0" %loan_id
#         que_1 = tmsconn.get_one_result(record_query)
#         if que_1['IandE'] != None:
#             dict=cPickle.loads(str(que_1['IandE']))
            #         for i in inc_exp_keys:
#             if i not in dict:
#                 dict[i]=''

        record_query = "select * from Income_Expense where loan_id = %s and override_flag = 0" %loan_id
        que = tmsconn.get_one_result(record_query)

        IandE_log.info(": Existing  Income and Expense details. loan_id - "+str(loan_id)+ " IandE- "+str(que)+":")

        if que:
            dict = queueconfig.fields_values.copy()
            dict.pop('loan_id')
            dict.pop('store_id')
            dict.pop('cust_id')

            for key, value in dict.iteritems():
                if value in que.keys():
                    dict[key] = unicode(que[value])
                else:
                    dict[key] = ''
        else:
            for i in inc_exp_keys:
                if i not in dict:
                    dict[i]=''
        dict={}
        return   render_to_response('custdetail/Inc_Exp_popup.html',{'loan_id':loan_id,'cust_id':cust_id,'dict':dict,'msg':msg})

    except Exception:
        if conn:
            conn.rollback()
            conn.close()
        log = traceback.format_exc()
        IandE_log.error(": Error in Income and Expense details. loan_id - Error - "+str(log)+":")
        msg = "Error in update Income and Expense details. Please check logs and contact back end team."
        return   render_to_response('custdetail/Inc_Exp_popup.html',{'loan_id':loan_id,'cust_id':cust_id,'dict':dict,'msg':msg})

def updateLoanInfo(username,loan_id):
    try:
         db = TranDB(section='TMS_DATA')
         cur_date = datetime.datetime.now()
         curs = db.getcursor()
         record_query = "select * from Loan_Info where loan_id = %s and override_flag = 0"
         args = (loan_id)
         loan_info = db.processquery(query=record_query, curs=curs, count=1, args=args)

         update_query = "update Loan_Info set override_flag = 1, last_updated_on = %s \
                            where loan_info_id = %s"
         args = (cur_date.strftime('%Y-%m-%d %H:%M:%S' ), loan_info['loan_info_id'])
         db.processquery(query=update_query, curs=curs,args=args, fetch=False)


         insert_query = "insert into Loan_Info (request_amt,approved_amt,borrowed_amt,funded_amt,EMI_amt,request_dt,approved_dt,loc_limit,\
                        funding_method,booked_dt,fund_dt,commencement_dt,dp_esign_dt,fund_to,cb_fund_to,APR,relevant_dt,now_dt,\
                        wd_proposed_on,loan_esign_dt,pco_dt,downpayment_amt,creditcheck_amt,repayment_frequency,repayment_dt,next_repayment_dt,selling_price,\
                        noc_req_on,create_dt,done_by,override_flag,last_updated_on,loan_id,nosia_sent_on) \
                        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

         args = (loan_info['request_amt'],loan_info['approved_amt'],loan_info['borrowed_amt'],\
                            loan_info['funded_amt'],loan_info['EMI_amt'],loan_info['request_dt'],\
                            loan_info['approved_dt'],loan_info['loc_limit'],loan_info['funding_method'],loan_info['booked_dt'],\
                            loan_info['fund_dt'],loan_info['commencement_dt'],loan_info['dp_esign_dt'],\
                            loan_info['fund_to'],loan_info['cb_fund_to'],loan_info['APR'],loan_info['relevant_dt'],\
                            loan_info['now_dt'],loan_info['wd_proposed_on'],loan_info['loan_esign_dt'],\
                            loan_info['pco_dt'],loan_info['downpayment_amt'],loan_info['creditcheck_amt'],\
                            loan_info['repayment_frequency'],loan_info['repayment_dt'],loan_info['next_repayment_dt'],loan_info['selling_price'],loan_info['noc_req_on'],\
                            cur_date.strftime('%Y-%m-%d %H:%M:%S' ),username,0 ,None,loan_info['loan_id'],loan_info['nosia_sent_on'])

         db.processquery(query=insert_query, curs=curs,args=args, fetch=False, returnprikey=1)
         db.commit()
         db.close()
    except Exception ,e :
        db.rollback()
        db.close()

def pre_payment_discard(request):

    username=request.session['username']
    current_date=str(datetime.date.today())
    message=""
    chk_box_key=[]
    pre_payment_ids=[]
    update_flag=0
    pre_check=None


    if request.session.has_key("update_flag"):
        update_flag=request.session["update_flag"]
        del request.session["update_flag"]
    payment_type={"select":"select","REPPREPYMT":"Replacement Prepayment","XTRPREPYMT":"Extra Prepayment"}

    if request.method=='POST':
        loan_id=request.POST['loan_id']
        pre_check=len(PaymentCalendar.objects.filter(loan=loan_id));
        dict=request.POST
        cur_date = datetime.datetime.now()
        dict_values=sorted(dict.iterkeys())
        for k in dict_values:
            if ("pre_payment_chk" in k):
                chk_box_key.append(k)

        for item in chk_box_key:
                if not ("pre_payment_chk" in item):
                    status="Please check the correct record to be discard"

                else:
                    index_payment_chk=item[15:]
                    pre_payment_id={"reason":dict['override_reason'+index_payment_chk], "prepayments_id":int(dict["pre_payment_id"+index_payment_chk]),"user":username,"flag":3,"loan_id":loan_id}
                    pre_payment_ids.append(pre_payment_id)



        #print pre_payment_ids
        if pre_payment_ids:
            status=pcfunc.ppmmanual(pre_payment_ids, cur_date)
            request.session["update_flag"]=0
        return HttpResponseRedirect("/info/pre_payment/?loan_id="+str(loan_id))

    prepayments=pcfunc.getppmdata(loan_id)
    if isinstance(prepayments,str) or isinstance(prepayments,unicode) :
        message=prepayments
        prepayments={}
    else:
        for pre_pay_sch in prepayments:
            if str(pre_pay_sch["payment_dt"])<current_date:
                pre_pay_sch["past_date"]=1
            else:
                pre_pay_sch["past_date"]=0


    return render_to_response('custdetail/pre_payment.html',{"update_flag":update_flag,"status":status,"prepayments":prepayments,"message":message,"pre_check":pre_check,"payment_type":payment_type})



def search_emp(request):
    if request.method=='GET':
        emp_name=request.GET['emp_name']
        emp_postcode=request.GET['postcode']
        employers=Employer_Info_Repo.objects.filter(employer_name=emp_name,employer_postcode=emp_postcode)
    return render_to_response("custdetail/search_emp.html",{"employers":employers})
search_emp = maintenance_deco_popups(search_emp)

def oldcontact_popup(request):
    """
    This will pop-up a window through which new contact record could be added.
    """
#    id = request.session['loan_id']
    if request.method=='GET':
        cust_id=request.GET['cust_id']
    elif request.method=='POST':
        cust_id=request.GET['cust_id']
    else:
        return HttpResponse('Cust ID is Missing check with Back End Team!')
    #print cust_id
    home_status_list=[['OWNED','Owned'],['RENTAL','Rental'],['TENANT COUNCIL','Tenant council'],
    ['TENANT FURNISHED','Tenant Furnished'],['TENANT UNFURNISHED','Tenant Unfurnished'],
    ['LIVING WITH PARENTS','Living with Parents'],['OTHERS','Others']]
    customer_id = Customer.objects.filter(cust_id=cust_id)
    countrylist = [['AFGHANISTAN','Afghanistan'],["ALBANIA","Albania"],["ALGERIA","Algeria"],
                  ['ANDORRA','Andorra'],['ANGOLA','Angola'],['ANTIGUA AND BARBUDA','Antigua and Barbuda'],
                  ['ARGENTINA','Argentina'],['ARMENIA','Armenia'],['AUSTRALIA','Australia'],
                  ['AUSTRIA','Austria'],['AZERBAIJAN','Azerbaijan'],['BAHAMAS','Bahamas'],
                  ['BAHRAIN','Bahrain'],['BANGLADESH','Bangladesh'],['BARBADOS','Barbados'],
                  ['BELARUS','Belarus'],['BELGIUM','Belgium'],['BELIZE','Belize'],
                  ['BENIN','Benin'],['BHUTAN','Bhutan'],['BOLIVIA','Bolivia'],['BOSNIA','Bosnia'],
                  ['BOTSWANA','Botswana'],['BRAZIL','Brazil'],['BURKINA','Burkina'],
                  ['BURUNDI','Burundi'],['CAMBODIA','Cambodia'],['CAMEROON','Cameroon'],
                  ['CANADA','Canada'],['CAPE','Cape'],['CENTRAL AFRICAN REPUBLIC','Central African Republic'],
                  ['CHAD','Chad'],['CHILE','Chile'],['CHINA','China'],['COLOMBIA','Colombia'],
                  ['COMOROS','Comoros'],['CONGO','Congo'],['COSTA RICA','Costa Rica'],
                  ['CROATIA','Croatia'],['CUBA','Cuba'],['CYPRUS','Cyprus'],
                  ['CZECH REPUBLIC','Czech Republic'],['DENMARK','Denmark'],['DJIBOUTI','Djibouti'],
                  ['DOMINICA','Dominica'],['DOMINICAN REPUBLIC','Dominican Republic'],
                  ['EAST TIMOR','East Timor'],['ECUADOR','Ecuador'],['EGYPT','Egypt'],
                  ['EL SALVADOR','El Salvador'],['ENGLAND','England'],
                  ['EQUATORIAL GUINEA','Equatorial Guinea'],['ERITREA','Eritrea'],
                  ['ESTONIA','Estonia'],['ETHIOPIA','Ethiopia'],['FIJI','Fiji'],
                  ['FINLAND','Finland'],['FRANCE','France'],['GABON','Gabon'],
                  ['GAMBIA','Gambia'],['GEORGIA','Georgia'],['GERMANY','Germany'],
                  ['GHANA','Ghana'],['GREAT BRITAIN','Great Britain'],
                  ['GREECE','Greece'],['GRENADA','Grenada'],['GUATEMALA','Guatemala'],
                  ['GUINEA','Guinea'],['GUINEA-BISSAU','Guinea-Bissau'],
                  ['GUYANA','Guyana'],['HAITI','Haiti'],['HONDURAS','Honduras'],
                  ['HUNGARY','Hungary'],['ICELAND','Iceland'],['INDONESIA','Indonesia'],['INDIA','India'],
                  ['IRAN','Iran'],['IRAQ','Iraq'],["IRELAND","Ireland"],['ISRAEL','Israel'],
                  ['ITALY','Italy'],['IVORY COAST','Ivory Coast'],['JAMAICA','Jamaica'],
                  ['JAPAN','Japan'],['JORDAN','Jordan'],['KAZAKHSTAN','Kazakhstan'],
                  ['KENYA','Kenya'],['KIRIBATI','Kiribati'],['KOREA NORTH','Korea North'],
                  ['KOREA SOUTH','Korea South'],['KOSOVO','Kosovo'],['KUWAIT','Kuwait'],
                  ['KYRGYZSTAN','Kyrgyzstan'],['LAOS','Laos'],['LATVIA','Latvia'],
                  ['LEBANON','Lebanon'],['LESOTHO','Lesotho'],['LIBERIA','Liberia'],
                  ['LIBYA','Libya'],['LIECHTENSTEIN','Liechtenstein'],['LITHUANIA','Lithuania'],
                  ['LUXEMBOURG','Luxembourg'],['MACEDONIA','Macedonia'],['MADAGASCAR','Madagascar'],
                  ['MALAWI','Malawi'],['MALAYSIA','Malaysia'],['MALDIVES','Maldives'],
                  ['MALI','Mali'],['MALTA','Malta'],['MARSHALL ISLANDS','Marshall Islands'],
                  ['MAURITANIA','Mauritania'],['MAURITIUS','Mauritius'],['MEXICO','Mexico'],
                  ['MICRONESIA','Micronesia'],['MOLDOVA','Moldova'],['MONACO','Monaco'],
                  ['MONGOLIA','Mongolia'],['MONTENEGRO','Montenegro'],['MOROCCO','Morocco'],
                  ['MOZAMBIQUE','Mozambique'],['MYANMAR','Myanmar'],['NAMIBIA','Namibia'],
                  ['NAURU','Nauru'],['NEPAL','Nepal'],['NETHERLANDS','Netherlands'],
                  ['NEW ZEALAND','New Zealand'],['NICARAGUA','Nicaragua'],
                  ['NIGER','Niger'],['NIGERIA','Nigeria'],['NORWAY','Norway'],
                  ['OMAN','Oman'],['PAKISTAN','Pakistan'],['PALAU','Palau'],
                  ['PANAMA','Panama'],['PAPUA NEW GUINEA','Papua New Guinea'],
                  ['PARAGUAY','Paraguay'],['PERU','Peru'],['PHILIPPINES','Philippines'],
                  ['POLAND','Poland'],['PORTUGAL','Portugal'],['QATAR','Qatar'],
                  ['ROMANIA','Romania'],['RUSSIAN FEDERATION','Russian Federation'],
                  ['RWANDA','Rwanda'],['SAINT KITTS AND NEVIS','Saint Kitts and Nevis'],
                  ['SAINT LUCIA','Saint Lucia'],['SAINT VINCENT AND GRENADINES','Saint Vincent and Grenadines'],
                  ['SAMOA','Samoa'],['SAN MARINO','San Marino'],['SAO TOME AND PRINCIPE','Sao Tome and Principe'],
                  ['SAUDI ARABIA','Saudi Arabia'],['SCOTLAND','Scotland'],
                  ['SENEGAL','Senegal'],['SERBIA','Serbia'],['SEYCHELLES','Seychelles'],
                  ['SIERRA LEONE','Sierra Leone'],['SINGAPORE','Singapore'],
                  ['SLOVAKIA','Slovakia'],['SLOVENIA','Slovenia'],['SOLOMON ISLANDS','Solomon Islands'],
                  ['SOMALIA','Somalia'],['SOUTH AFRICA','South Africa'],['SPAIN','Spain'],
                  ['SRI LANKA','Sri Lanka'],['SUDAN','Sudan'],['SURINAME','Suriname'],
                  ['SWAZILAND','Swaziland'],['SWEDEN','Sweden'],['SWITZERLAND','Switzerland'],
                  ['SYRIA','Syria'],['TAIWAN','Taiwan'],['TAJIKISTAN','Tajikistan'],
                  ['TANZANIA','Tanzania'],['THAILAND','Thailand'],['TOGO','Togo'],
                  ['TUNISIA','Tunisia'],['TURKEY','Turkey'],['TURKMENISTAN','Turkmenistan'],
                  ['TUVALU','Tuvalu'],['UGANDA','Uganda'],['UKRAINE','Ukraine'],
                  ['UNITED ARAB EMIRATES','United Arab Emirates'],['UNITED KINGDOM','United Kingdom'],
                  ['UNITED STATES','United States'],['URUGUAY','Uruguay'],
                  ['UZBEKISTAN','Uzbekistan'],['VANUATU','Vanuatu'],['VATICAN CITY','Vatican City'],
                  ['VENEZUELA','Venezuela'],['VIETNAM','Vietnam'],['WALES','Wales'],
                  ['YEMEN','Yemen'],['ZAIRE','Zaire'],['ZAMBIA','Zambia'],['ZIMBABWE','Zimbabwe']]

    if request.method == 'POST':
        curr_date=datetime.datetime.now()
        Tapts = request.POST['apts'] or None
        Tbuilding_no=request.POST['building_no'] or None
        Tbuilding_name=request.POST['building_name']or None
        Thome_status=request.POST['home_status']
        Tstart_date=request.POST['datum1']or None
        Tend_date=request.POST['datum2']or None
        Tstreet1= request.POST['street1'] or None
        Tstreet2 = request.POST['street2'] or None
        Tcounty = request.POST['county'] or None
        Tlocality=request.POST['locality'] or None
        Tcity = request.POST['city'] or None
        Ttown=request.POST['town'] or None
        Tpostcode = request.POST['postcode'] or None
        Tcountry = request.POST['country'] or None


        # 1) Entry into Address_Info table

        addressobj = Address_Info(apt_no=Tapts,building_no=Tbuilding_no,
            building_name=Tbuilding_name,street1=Tstreet1,street2=Tstreet2,
            county=Tcounty,city=Tcity,country=Tcountry,
            postCode=Tpostcode,start_date=Tstart_date,locality=Tlocality,
            town=Ttown, end_date=Tend_date,home_status=Thome_status,
            create_date=str(curr_date),
            cust=customer_id[0], override_flag=1,
            last_updated=curr_date)
        addressobj.save()
        # 2) Entry into Email_Info table

    return render_to_response('custdetail/old_custdetail.html', \
        {'sessionobject':request.session,'countrylist':countrylist,\
          'home_status_list': home_status_list,'cust_id':cust_id})
oldcontact_popup = maintenance_deco_popups(oldcontact_popup)
def cust_search(request):
    results =""
    headerlist=""
    req_dict={}
    cust_id=request.GET['cust_id']
    oldcustomer=request.GET['cust_id']
    username=request.session['username']
    if request.method == 'POST':
        headerlist=["Loan ID", "Full Name", "DOB", "Loan Status/Proposal Status", "Loan Amount", "Create Date", "Notes"]
        cust_id = request.POST['customerid']
        cust_fname = request.POST['custfname']
        cust_lname = request.POST['custlname']
        cust_email=request.POST['email']
        dt=request.POST['datum1']
        req_dict = {'cust_id':cust_id,'first_name':cust_fname,\
                    'last_name':cust_lname,'email_address':cust_email,'DOB':dt,'user_id':username,'oldcustomer':oldcustomer}
        sql= "select \
                ll.loan_id,\
                gc.status_cd,\
                gc.case_id,\
                ll.first_name,\
                ll.last_name,\
                ll.dob,\
                ll.proposal_status,\
                ll.loan_amt,\
                ll.loaded_dt,\
                ll.cust_id\
            from \
                TMS_Data.Loan_Latest as ll\
                 ,GCMS_Data.store_privileges as sp, \
                 GCMS_Data.gcm_case as gc \
                  where ll.loan_id = gc.entity_id and ll.store_id=sp.store_id and  \
                  gc.entity_type='LOAN' AND sp.status in('READ','WRITE') AND "
            ## Forms the query based on the search parameters
        def _form_clause(key, value, arg_list):
            clause = ""
            if value:
                if key == "email_address":
                    clause = " (ll.personal_email LIKE %s or " + \
                                " ll.official_email LIKE %s)"
                    arg_list.extend([str(value)+'%', str(value)+'%'])
                elif key =="cust_id":
                    clause = " ll.cust_id LIKE %s"
                    arg_list.append(str(value)+"%")
                elif key =="oldcustomer":
                    clause ="ll.cust_id != %s"
                    arg_list.append(value)
                elif key == "user_id":
                    clause = clause + " sp.user_id  LIKE %s"
                    arg_list.append(str(value)+"%")
                elif key =="first_name":
                    clause = " ll.first_name LIKE %s"
                    arg_list.append(str(value)+"%")
                elif key =="last_name":
                    clause = " ll.last_name LIKE %s"
                    arg_list.append(str(value)+"%")
                else:
                    clause = key + "=%s"
                    arg_list.append(encrypt_data(value))

            return clause
        arg_list = []
        where_clause = ' AND '.join([ _form_clause(key, value, arg_list) for key, value in req_dict.iteritems()  if value ])
        sql = sql + where_clause
        results = execute_search(sql, arg_list)
    return render_to_response('custdetail/custdetail_search.html',{'results':results, 'req_dict':req_dict,
                                                                       'headerlist':headerlist,'cust_id':cust_id})

def generate_schedule_emp(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

#    username=request.session['username']
    payment_type={"select":"select","PRNDUE":"Principal Due","INTCAPLZD":"Interest Capitalized","ARRFEE":"Arrear Fee","DEFLTFEE":"Default Fee","TERMNFEE":"Termination Fee","XTRPREPYMT":"Extra Prepayment"}
#    cust_id=get_custid_from_loanid(loan_id)
    schedule={}
    if request.method=="GET":
        sch_obj = schedule_for_loan.Schedule(loan_id)
        schedule = sch_obj.schedule_before_active()
        sch_obj.close_con()

    return render_to_response("custdetail/generate_schedule_emp.html",{"payment_type":payment_type,"schedule":schedule})
generate_schedule_emp = maintenance_deco_popups(generate_schedule_emp)
def sms(request):
    
    sms_type=""
    if request.method=="GET":
        loan_id=request.GET['loan_id']
        cust_id=request.GET['cust_id']
        try:
            loanlatestobj=LoanLatest.objects.filter(loan_id=loan_id)
            storeinfoobj=Store_Info.objects.filter(store=loanlatestobj[0].store_id)

            if loanlatestobj[0].store_id == 'LS':
                prod_classification = Product.objects.filter(product_id=loanlatestobj[0].product_id)
                if prod_classification[0].product_classification == 'LOC':
                    sms_type = sms_config.SMS_TYPE['LENDINGSTREAMLOC'].copy()
                else:
                    sms_type=sms_config.SMS_TYPE[storeinfoobj[0].brand_name]
            else:
                sms_type=sms_config.SMS_TYPE[storeinfoobj[0].brand_name].copy()
        except Exception ,e:
            sms_logger.error("Error:: "+str(loan_id)+str(traceback.format_exc()))
    return render_to_response("custdetail/sms.html",{"sms_type":sms_type,'loan_id':loan_id,'cust_id':cust_id})
sms = maintenance_deco_popups(sms)


def sms_content(request):
    dict = {}
    username=request.session['username']

    if request.method=='POST' and request.is_ajax:
        cust_id = request.POST['cust_id']
        loan_id = request.POST['loan_id']
        create_date=datetime.datetime.now()
        sms_type_post = request.POST['sms_type']
        loanlatestobj=LoanLatest.objects.filter(loan_id=loan_id)
        storeinfoobj=Store_Info.objects.filter(store=loanlatestobj[0].store_id)
        if loanlatestobj[0].store_id == 'LS':
            prod_classification = Product.objects.filter(product_id=loanlatestobj[0].product_id)
            if prod_classification[0].product_classification == 'LOC':
                sms_type = sms_config.SMS_TYPE['LENDINGSTREAMLOC'].copy()
            else:
                sms_type=sms_config.SMS_TYPE[storeinfoobj[0].brand_name]
        else:
            sms_type=sms_config.SMS_TYPE[storeinfoobj[0].brand_name]
        send_sms=str(request.POST['sms_button'])
        custome_detail=request.POST['sms_custome']
        dict['sms_status']=""
        dict['sms_type_content']=""
        smstext=""
        if sms_type_post:
            mobile_no = Phone_Info.objects.filter(cust=cust_id,phone_type='MOBILE',override_flag=0)
            if mobile_no:
                if mobile_no[0].phone_number:
                    dict['mobile_no'] = mobile_no[0].phone_number
                else:
                    dict['mobile_no'] = "No Mobile no."
            else:
                dict['mobile_no']="No Mobile no."
        try:
            for sms,sms_content in sms_type.iteritems():
                if sms_type_post==sms:
                    loan=Loan.objects.filter(loan_id=loan_id)[0]
                    storeinfo=Store_Info.objects.filter(store=loan.store_id,override_flag=0)[0]
                    personalinfo = Customer_Basic_Info.objects.filter(cust=cust_id,override_flag=0)[0]
                    loaninfo=Loan_Info.objects.filter(loan=loan_id)[0]
                    store=Store.objects.filter(store_id=loan.store_id)[0]
                    if sms=='Crediting 1 GBP SMS':

                        if storeinfo.brand_name=="ZEBIT":
                          sms_content = (sms_content)%(personalinfo.first_name,store.store_name,storeinfo.store_phone1.replace(' ',''))
                        else:
                         sms_content = (sms_content)%(store.store_name,str(storeinfo.store_phone1).replace(' ',''),storeinfo.store_email1)
                    elif sms=="Bank Statement Request SMS":

                          fax_string = ""
                          fax_nbr = storeinfo.store_fax1
                          if fax_nbr:
                              fax_string ="Fax  - "+str(fax_nbr) + " or "
                          if storeinfo.brand_name=="ZEBIT":
                              sms_content = (sms_content)%(personalinfo.first_name,store.store_name,storeinfo.store_fax1.replace(' ',''),storeinfo.store_email1)
                          elif storeinfo.brand_name=="BAFA":
                             sms_content = (sms_content)%(fax_string.replace(' ',''),storeinfo.store_email1)
                          else:
                             sms_content = (sms_content)%(store.store_name,fax_string.replace(' ',''),storeinfo.store_email1)
                    elif sms=="Pay Slip Request SMS":
                          fax_string = ""
                          fax_nbr = storeinfo.store_fax1
                          if fax_nbr:
                              fax_string ="Fax Number - "+str(fax_nbr) + "or "
                          if storeinfo.brand_name=="ZEBIT":
                            sms_content = (sms_content)%(personalinfo.first_name,store.store_name,storeinfo.store_fax1.replace(' ',''),storeinfo.store_email1)
                          elif storeinfo.brand_name=="BAFA":
                            sms_content = (sms_content)%(fax_string.replace(' ',''),storeinfo.store_email1)
                          else:
                            sms_content = (sms_content)%(store.store_name,fax_string.replace(' ',''),storeinfo.store_email1)
                    elif sms=="No Contact SMS":#
                          if storeinfo.brand_name=="ZEBIT":
                             sms_content = (sms_content)%(personalinfo.first_name,store.store_name,storeinfo.store_phone1.replace(' ',''))
                          elif storeinfo.brand_name=="BAFA":
                             sms_content = (sms_content)%(storeinfo.store_phone1.replace(' ',''))
                          else:
                             sms_content = (sms_content)%(store.store_name,storeinfo.store_phone1.replace(' ',''))
                    elif sms=="Debit Check Needed SMS":
                          if storeinfo.brand_name=="ZEBIT":
                            sms_content = (sms_content)%(personalinfo.first_name,store.store_name,storeinfo.store_phone1.replace(' ',''))
                          elif storeinfo.brand_name=="BAFA":
                            sms_content = (sms_content)%(storeinfo.store_phone1.replace(' ',''))
                          else:
                            sms_content = (sms_content)%(store.store_name,storeinfo.store_phone1.replace(' ',''))
                    elif sms=="Store Contact SMS":
                          if storeinfo.brand_name=="ZEBIT":
                            sms_content = (sms_content)%(personalinfo.first_name,store.store_name,storeinfo.store_phone1.replace(' ',''),storeinfo.store_fax1.replace(' ',''),storeinfo.store_email1)
                          else:
                           sms_content = (sms_content)%(store.store_name,storeinfo.store_phone1.replace(' ',''),storeinfo.store_email1)
                    elif sms=="REJECTED SMS":
                          if storeinfo.brand_name=="ZEBIT":
                              sms_content = (sms_content)%(personalinfo.first_name,store.store_name,storeinfo.store_email1)
                          else:
                              sms_content = (sms_content)%(storeinfo.store_phone1.replace(' ',''))
    #                else:
                    dict['sms_content']=sms_content
                    dict['sms']=sms
                    break
        except Exception,e:
             sms_logger.error("Error: "+str(loan_id)+str(traceback.format_exc()))
        if send_sms=="SEND":

            case_id=get_case_id_by_entity_id(loan_id,'LOAN')
            log_id=get_logid_by_caseid(case_id)
            if sms_type_post=="Custom Defined SMS":
                smstext=custome_detail
                dict['sms_type_content']=smstext
            else:
                smstext=dict['sms_content']
            if mobile_no:
                temp_mobile_no=isPhone(mobile_no[0].phone_number)

                if temp_mobile_no and smstext:

                    #response=post_sms(temp_mobile_no,smstext,sms_config.TEST,storeinfoobj[0].brand_name,loan_id)
                    tlo = Loan.objects.get(loan_id = loan_id)
                    msg_type = '_'.join(sms.split())
                    response, res_log = common_sms.sendSMS(temp_mobile_no, smstext, storeinfoobj[0].brand_name, loan_id,  msg_type = msg_type, product = tlo.__dict__.get('product_id'), source='TMS_UI')
                    res_log = str(res_log)
                    if response:
                        dict['sms_status']="Message Sent"
                        sms_logger.info("Message successfully sent :: for this loan")
                    else:
                        dict['sms_status']="*Message Sending Failed"
                        sms_logger.error("SMS :: ERROR :: Loan ID :: "+str(loan_id)+" :: Response Error :: "+str(response)+":: Check for  sem,service running and posting to correct url "+str(traceback.format_exc()))
                    add_gcm_notes(log_id["log_id"],"SMS",str(dict['sms_status'])+" :: "+str(sms_type_post)+" :: "+str(smstext),username,create_date)
            else:
                dict['sms_status']="*No mobile number"
                add_gcm_notes(log_id["log_id"],"SMS","No mobile number"+str(sms_type_post)+"-"+str(smstext),username,create_date)
                if sms_type_post=="Custom Defined SMS":
                    dict['sms_type_content']=smstext
    return HttpResponse(simplejson.dumps(dict), mimetype='text/javascript')
sms_content = maintenance_deco_popups(sms_content)
def docs(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username=request.session['username']
    return render_to_response("custdetail/document.html",{'username':username,"loan_id":loan_id,"cust_id":cust_id})

def docs_new(request):

    accountid=request.session['accountid']
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    store_id = Loan.objects.get(loan_id=loan_id).store_id
    brand_name = get_Store_Info_frm_storeid(store_id)['brand_name']


    username=request.session['username']
    file = ""
    isFile = 0
    exists_flag=0
    flag_set=0
    displaylist=()
    case_id=get_case_id_by_entity_id(loan_id,'LOAN')
    displaylist =  get_all_gcm_documents(case_id)
    if request.method == 'POST':
        exists_flag=0
        if 'datafile' in request.FILES:
            file = request.FILES['datafile']
            if file.size == 0:
                isFile = 1
            else:
                timelist = ctime().split()
                file =  str(loan_id) + "_" + str(file)
                # Replacing the special characters %,?,#,' with underscore(_) since it is not supported by browser.
                for ch in ['%','?','#',"'"]:
                    if ch in file:
                        file=file.replace(ch,'_')
                new_media_root = generate_new_path(MEDIA_ROOT,accountid,brand_name)
                os.system("mkdir -p '%s/%s/%s/%s'" % (new_media_root,timelist[4],timelist[1],timelist[2]) )
                destination = open('%s/%s/%s/%s/%s' % (new_media_root, timelist[4],timelist[1],timelist[2],file), 'wb')
                path = '%s/%s/%s/%s' % (timelist[4],timelist[1],timelist[2],file)
#                loc = MEDIA_ROOT + "/" + str(file)
#                name1 = request.FILES['datafile'].name
                size1 = (request.FILES['datafile'].size)
                logid= get_log_id_by_loan_id(loan_id)

                if logid is not None:
                    date_today = fetch_curr_date()
                    print check_file_name_exists(file,case_id,date_today) ,"::::::::::::"
                    if check_file_name_exists(file,case_id,date_today) == 0:
                        cur_time = datetime.datetime.now()
                        path = "RECEIVED_DOCS" + "/" + path
                        insert_gcm_document(file,path,'RECEIVED',size1,request.POST['file_type'], username,case_id, request.POST['reference'],cur_time)
                        add_gcm_notes(logid,"Document",request.POST['file_type']+" Document recieved from Customer",username,cur_time)
                        exists_flag = 0
                    else:
                        exists_flag = 1
                    print "successfully Inserted into gcm_documents table"
                else:
                    print "thier is no log Id entry for the particular case"
                for chunk in request.FILES['datafile'].chunks():
                    destination.write(chunk)
                destination.close()
                flag_set=1
        else:
            isFile = 1
    return render_to_response("custdetail/document_iframe.html",{"loan_id":loan_id,"cust_id":cust_id,'exists_flag':exists_flag,'file':file,'isFile':isFile,'flag_set':flag_set})
docs_new = maintenance_deco_popups(docs_new)



def docs_view(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username=request.session['username']
    account_id = request.session['accountid']
    brand_name = Store_Info.objects.filter(store = Loan.objects.filter(loan_id = loan_id)[0].store_id)[0].brand_name
    displaylist=()
    case_id=get_case_id_by_entity_id(loan_id,'LOAN')
    displaylist =  get_all_gcm_documents_view(case_id)
    folder = MEDIA_ROOT_INPUT.split("/")[-1]
    folder+='/'+account_id+'/'+brand_name
    return render_to_response("custdetail/document_view.html",{'displaylist':displaylist,'folder':folder})


def generation(doc_name,version,document_type,loan_id,cur_time,temp_dict,flag_set,username,display_flag,dockitid=None):
    msg=''
    field_name = str(document_type+'_flag')
    notice_flags = Notice_Flags.objects.filter(loan=loan_id)
    try:
        result,output_file_path = generate_document(doc_name, version, document_type, loan_id, username,cur_time,dockitid)
    except:
        result=0
    if result == 1:
        eval("notice_flags.update("+document_type+"='GENERATED')")
        try:
            temp_dict.pop(document_type)
        except:
            pass
        if display_flag==1:
            msg = 'Notice generated successfully.'
        else:
            msg = 'Welcome Kit generated successfully.'
        if display_flag==1:
            webbrowser.open_new(output_file_path)
        log_id = get_log_id_by_loan_id(loan_id)
        gcm_log_detail = get_latest_gcmlog_by_caseid(get_case_id_by_entity_id(loan_id,'LOAN'))
        loan_status = gcm_log_detail['start_status_cd']
        add_gcm_notes(log_id,"Document",DOCTYPE[document_type]+" Document is generated at "+loan_status+" state for the LoanID "+str(loan_id),username,cur_time)
        flag_set=1
    else:
        if display_flag==1:
            msg = 'Failed to generate Notice. For more information check the log.'
        else:
            msg = 'Failed to generate Welcome Kit. For more information check the log.'
    return msg,flag_set,temp_dict
def generate_kitpath(loan_id,version,cur_time):
    customer_Info = get_customer_name(loan_id)
    cus_firstName = customer_Info[0]
    cus_lastName = customer_Info[1]
    filename = 'WLKIT_'+str(loan_id)+'_'+str(cus_firstName)+'_'+str(cus_lastName)+'.zip'
    output_file_path = output_Dir('Welcome_Kit',filename, cur_time)
    out_file_path = output_File('Welcome_Kit',filename, cur_time)
    return out_file_path

#@login_required
def generate_notice(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username = request.session['username']
    case_id=get_case_id_by_entity_id(loan_id,"LOAN")
    msg = ''
    cur_time=datetime.datetime.now()
    document_type = ''
    doc_names=''
    flag = ""
    status = 'TO BE GENERATED'

    temp_dict={}
    sent_dict={}
    flag_set=0
    field = ''
    catch_flag=0
    nov_flag=0

    input_file_path=''

    account_id = request.session['accountid']
    loan_obj = Loan.objects.get(loan_id=loan_id)
    #portfolio_id = request.session['portfolio_id']
    store_name = get_Store_Info_frm_storeid(loan_obj.store_id)['brand_name']
    loanid_list = []
#    if not check_user_in_privilege_list(username,'doctemp','generate_notice'):
#        request.session['priv_msg'] = "Sorry You are not Authorized to enjoy this \
#            priviledge,please contact Admin"
#        return HttpResponseRedirect('/auth/index')

    if request.method == 'POST':
        if request.POST['todo'] == "Generate":
            if request.POST.has_key('version'):
                document_type = request.POST['document_type']
                doc_name = request.POST['doc_name']
                version = request.POST['version']
                if str(document_type)=='SOACC':
                    date_elem=datetime.datetime.now()
                    update_or_insert_Notice_Flags(loan_id,date_elem, SOACC='TO BE GENERATED')
                inidividualGeneration(loan_obj.account_id, loan_obj.store_id, loan_obj.product_id,\
                                            str(document_type),[loan_id],username)
#                loanid_list.append(loan_id)
#                (result,msg) = document_generation_method(account_id,loan_obj.store_id,loanid_list,document_type,
#                        doc_name,version,username)
            else :
                msg = "please select Version "

        elif request.POST['todo'] == 'send':
             if request.POST.has_key('send'):
                gcm_doc_id=request.POST['send']
            #    gcm_doc_id_list = []
            #    gcm_doc_id_list.append(gcm_doc_id)
            #    gcm_doc_id_list = tuple(gcm_doc_id_list)
                get_doct_list=get_generated_list_new(gcm_doc_id)
                document_type = get_doct_list[0]['document_type']
            #                (result,msg) = document_send_method(account_id,loan_obj.store_id,get_doct_list,document_type,username)
                individualSend(loan_obj.account_id, loan_obj.store_id, loan_obj.product_id,\
                                    str(document_type),[loan_id],username)
             else:
                 msg='No document is selected for send.'
        elif request.POST['todo'] == 'invalid':
            if request.POST.has_key('send'):
#                to_send=request.POST['send']
                gcm_doc_id=request.POST['send']
                get_doct_list=get_generated_list_new(gcm_doc_id)
                document_type = get_doct_list[0]['document_type']
                (result,msg) = document_invalid_method(store_name,get_doct_list, username, cur_time)
            else:
                msg='No document is selected for invalid.'


    sent_dict={}
    get_doct_list=[]
    for elem in DOCTYPE[store_name]:
            get_doct_list.append(get_generated_list(loan_obj.store_id,elem,case_id))
    try:
        for record_doc in get_doct_list:
            if record_doc:
                sent_dict[record_doc[0]['gcm_document_id']]=DOCTYPE[store_name][record_doc[0]['document_type']]
    except:
        pass

    portfolio_DOCTYPE=DOCTYPE[store_name]
#    notice_flag_obj=Notice_Flags.objects.filter(loan=loan_id,flag_value='TO BE GENERATED')
#    notice_flag_obj=Notice_Flags.objects.filter(loan=loan_id,flag_value='TO BE GENERATED',inUse=0,associatedWith=None)
    notice_flag_obj=getToBeGeneratedList(loan_id,"TO BE GENERATED")

    for record in notice_flag_obj:
            temp_dict[record["flag_name"]] = portfolio_DOCTYPE[record["flag_name"]]
    if 'ES' in temp_dict:
        temp_dict.pop('ES')
    if 'SOACC' in temp_dict:
        temp_dict.pop('SOACC')
    loan_status = get_loan_status_by_loan_id(loan_id)

    if loan_status in SOACC_valid_statuses:
        temp_dict['SOACC'] = portfolio_DOCTYPE['SOACC']

    store_details = []
    store_details.append(loan_obj.store_id)
    store_details.append(store_name)
    return render_to_response('custdetail/generate_notice.html', {'loan_id':loan_id,'cust_id':cust_id,'docnames':doc_names, 'msg':msg,
                                                                    'notice_type': status,
                                                                    'document_type':document_type,
                                                                    'username':request.session['username'],
                                                                    'menu':request.session['sessionmenu'],
                                                                    'document_dict': temp_dict,
                                                                    'sent_dict':sent_dict,
                                                                    'flag_set':flag_set,'input_file_path':input_file_path,
                                                                    'store_id':loan_obj.store_id,
                                                                    'product_id':loan_obj.product_id })
generate_notice = login_required(generate_notice)
generate_notice = maintenance_deco_popups(generate_notice)
def get_version(request):
    dict = {}

    if request.method=='POST' and request.is_ajax:
        doc_name = request.POST['docname']
        print doc_name
        type = request.POST['type']
        store_id = request.POST['store_id']
        template_for = request.POST['template_for']
        product = request.POST['product']
        if doc_name and type and store_id and template_for:

            templates_dict = {'store_id':store_id,'template_for':template_for,'template_type':type}
            template_linker_dict = {'product_id':product,'store_id':store_id,'override_flag':0}
            assosciated_template_info = getLinkedTemplateInfo(templates_dict,template_linker_dict)

            dict['versions'] = []
            for item in assosciated_template_info:
                dict['versions'].append(item['template_version'])
            dict['type'] = type
    return HttpResponse(simplejson.dumps(dict), mimetype='text/javascript')

def get_docinfo(request):
    notices = {'template_name':[],'template_version':[]}
    if request.method=='POST' and request.is_ajax:
        type = request.POST['doc_type'].upper()
        store_id = request.POST['store_id']
        product_id = request.POST['product_id']
        template_for =  request.POST['template_for']
        doc_names = get_document_names(type,store_id,product_id,template_for)
        if doc_names:
            for name in doc_names:
                notices['template_name'].append(name['template_name'])
                notices['template_version'].append(name['template_version'])
    return HttpResponse(simplejson.dumps(notices), mimetype='text/javascript')

def get_associatedinfo(request):
    #ass_loans={'loanlist':[]}

    #cur_yr=datetime.date.today().year
    #cur_month=datetime.date.today().month
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        associate_loans = get_associatedloans(loan_id)
        ass_loans=()
        cur_loan_carddetails=getCardDetails(loan_id)

        if associate_loans:
            loan_dict = {}
            for eachloan in associate_loans:
                temp_dict={}
                card_details=getCardDetails(eachloan[0])
                #exp_card=str(card_details['validto']

                temp_dict['loanid']=eachloan[0]
                temp_dict['first_name']=eachloan[1]
                temp_dict['last_name']=eachloan[2]
                temp_dict['loanstatus']=eachloan[3]
                temp_dict['reference_id']=card_details['CIMTranID']
                temp_dict['uniq_id']=card_details['CardUniqueID']
                temp_dict['bin6']=card_details['bin6']
                temp_dict['tail4']=card_details['tail4']
                temp_dict['validto']=card_details['validto']
                ass_loans+=(temp_dict,)
                same_loan=0
                #if((cur_loan_carddetails['bureau_name'] == card_details['bureau_name']) AND (cur_loan_carddetails['bureau_id'] == card_details['bureau_id']) AND (cur_loan_carddetails['reference_id'] == card_details['reference_id']) AND (cur_loan_carddetails['status'] == card_details['status']) AND (cur_loan_carddetails['uniq_id'] == card_details['uniq_id']) AND (cur_loan_carddetails['reason'] == card_details['reason']) AND (cur_loan_carddetails['card_usage'] == card_details['card_usage'])):
                if cur_loan_carddetails == card_details:
                    same_loan=1
                    loan_dict[eachloan[0]] = same_loan

            #return render_to_response("custdetail/associated_loan_info.html",{"ass_loans":ass_loans,"loan_id":loan_id,"cur_loan_carddetails":cur_loan_carddetails,"associate_loans":associate_loans,"same_loan":same_loan})
            return render_to_response("custdetail/associated_loan_info.html",{"ass_loans":ass_loans,"loan_id":loan_id,"cur_loan_carddetails":cur_loan_carddetails,"associate_loans":associate_loans,"same_loan":loan_dict})
        else:
            return render_to_response("custdetail/associated_loan_info.html",{"ass_loans":ass_loans,"loan_id":loan_id,"message":"No associated loans for this customer"})
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        associate_loans = get_associatedloans(loan_id)
        #res_message = update_associated_carddetails(loan_id,request.POST['cur_loan_carddetails'],request.POST['selected_loanlist'],associate_loans)
        selected_loanlist=request.POST.getlist("selected_loanlist")
        res_message = update_associated_carddetails(loan_id,selected_loanlist,associate_loans)
        return render_to_response("custdetail/associated_loan_info.html",{"res_message":res_message})
        #selected_loanlist
    #return HttpResponse(simplejson.dumps(ass_loans), mimetype='text/javascript')

def doc_name(request):
    dict = {}
    if request.method=='POST' and request.is_ajax:
        doctype = request.POST['temptype']
        if doctype:
            documents = get_doc_names(doctype)
            dict['documents'] = []
            for item in documents:
                dict['documents'].append(item)
    return HttpResponse(simplejson.dumps(dict), mimetype='text/javascript')

def immediate_pull_popup(request):
    """Immediate Pull Pop Up inside Payment Tab. It is possible for the customer to select the amount he pays beyond due_amount as EPP or RPP.

    """
    ### Initialize ###
    msg = ''
    OB = 0.00
    display_msg=''
    pull_amt = ''
    pull_from = ''
    pull_from_list = ''
    flag_torefresh_loan = 0
    bal_infm = {}
    precloseFlag = 0
    freeze_flag = 0
    paymentPending = 0
    sum_pendingPayments = 0
    update_flag = 0
    username = request.session['username']
#    conn = TranDB(section="TMS_DATA")
    product_class = None
    ### Taking things from session if they exist
    if request.session.has_key('AvlBal'):
        AvlBal= request.session['AvlBal']
    else:
        AvlBal = ''
    if request.session.has_key('update_flag'):
        update_flag=request.session['update_flag']
        del request.session['update_flag']
    else:
        update_flag = 0
    if request.session.has_key('flag_torefresh_loan'):
        flag_torefresh_loan=request.session['flag_torefresh_loan']
        del request.session['flag_torefresh_loan']
    else:
        flag_torefresh_loan = 0
    extra_amt = 0
    dueAmt = 0
    PC_amt = 0
    typCard = 'Existing'
    extra_amt_msg = ''


    #### Get request

    if request.method == 'GET':
        loan_id = request.GET['loan_id']
        product_class = Product.objects.get(loan=loan_id).product_classification
        loan_obj = loan.Loan(loan_id)
        freeze_flag = loan_obj.suppress_flag_for_schedule()[0]
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        if not freeze_flag:
            loan_info=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
            fund_to=loan_info.fund_to
            bal_infm = get_balance_dtls(loan_id)[0]
            OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
            dueAmt = Payments.objects.filter(loan = loan_id)[0].due_amt
            sql = "select sum(payment_amt-paid_amt) as PC_amt from PaymentCalendar where loan_id = %s and override_flag = 0" %(loan_id)
            result = con.get_all_results(sql)
    #        result=conn.processquery(query = sql, curs = cur, count=0,fetch = True)
    #        conn.close()
            PC_amt =  result[0]['PC_amt']
            if fund_to == "PREPAID CARD":
                pull_from_list = ['DEBIT CARD','PREPAID CARD']
            else:
                pull_from_list = ['DEBIT CARD']
            if 'pull_from' in request.GET:
                pull_from = request.GET['pull_from']
            else:
                pull_from = pull_from_list[0]
            paymentPending = Payments.objects.filter(loan = loan_id)[0].waterfall_pending
            if paymentPending:
                paymentPending = 1
            ####incase of payment pending
            query = "select ifnull(sum(tran_amount),0) from msp_timeouts where loan_id = %s and status = 'Timeout'"%loan_id
            res = con.get_one_result(query)
            sum_pendingPayments = res["ifnull(sum(tran_amount),0)"]
        else:
            freeze_flag=1

        query_voucher = "select voucher_code,percentage,is_direct,percentage_on,(p.due_amt*percentage)/100 as discount_amount ,(p.due_amt-(p.due_amt*percentage)/100) as amount_to_pay,max_voucher_amount  from Comm_Voucher_Code vc join Payments p on vc.loan_id = p.loan_id  where p.loan_id = %s and override_flag = 0 and status !='Applied'"%loan_id
        query_res_voucher = con.get_all_results(query_voucher)


        ####
#        sum_pendingPayments = msp_timeouts.objects.filter(loan_id = loan_id,status= 'Timeout').aggregate(Sum('payment_amt'))['payment_amt__sum']
    ### Post request #####
    if request.method == 'POST':
        loan_id = request.POST['loan_id']
        product_class = Product.objects.get(loan=loan_id).product_classification
        isOB=isOutStandingBalance(loan_id)
        loan_info=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
        cust_id = get_custid_from_loanid(loan_id)
        address_info=Address_Info.objects.filter(cust=cust_id,override_flag=0)
        fund_to=loan_info.fund_to
        paymentPending = Payments.objects.filter(loan = loan_id)[0].waterfall_pending
        freeze_flag = Payments.objects.filter(loan = loan_id)[0].freeze_flag

#         import pdb;pdb.set_trace()


        if not freeze_flag:
            if paymentPending:
                paymentPending = 1
            ####incase of payment pending
            con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
            query = "select ifnull(sum(tran_amount),0) from msp_timeouts where loan_id = %s and status = 'Timeout'"%loan_id
            res = con.get_one_result(query)
            sum_pendingPayments = res["ifnull(sum(tran_amount),0)"]
            ####
    #        sum_pendingPayments = msp_timeouts.objects.filter(loan_id = loan_id,status= 'Timeout').aggregate(Sum('payment_amt'))['payment_amt__sum']
            bal_infm = get_balance_dtls(loan_id)[0]
            OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
            sql = "select sum(payment_amt-paid_amt) as PC_amt from PaymentCalendar where loan_id = %s and override_flag = 0" %(loan_id)
            result = con.get_all_results(sql)
    #        result=conn.processquery(query = sql, curs = cur, count=0,fetch = True)
    #        conn.close()
            PC_amt =  result[0]['PC_amt']
            if fund_to == "PREPAID CARD":
                pull_from_list = ['DEBIT CARD','PREPAID CARD']
            else:
                pull_from_list = ['DEBIT CARD']
            if 'pull_from' in request.POST:
                pull_from = request.POST['pull_from']
            else:
                pull_from = pull_from_list[0]
            if pull_from == 'PREPAID CARD':
                merchant_name = 'PDC'
            else:
                merchant_name = 'GPG'
            dueAmt = Payments.objects.filter(loan = loan_id)[0].due_amt
            if pull_from == 'PREPAID CARD':
                Source = Loan.objects.filter(loan_id = loan_id)[0].lead_source
                member_id = Customer.objects.filter(cust_id=cust_id)[0].member_id
                bureau_obj = Ext_Bureau_Info.objects.filter(loan =loan_id,\
                                override_flag=0,bureau_name='PDC')
                if bureau_obj:
                    token_id = bureau_obj[0].bureau_id
                else:
                    token_id = None
                PDC_Dict = {"AccountID":member_id,'CardID':token_id,'Source':Source}
                responseDict = cardEnquiryFn(PDC_Dict)
                if responseDict['Error']:
                    request.session['AvlBal'] = 'Service Error'
                else:
                    request.session['AvlBal'] = Money(responseDict['AvlBal'])
            if 'card' in request.POST:
                typCard = request.POST['card']
                imm_pull_logger.info('Card:: Immediate Pull '+str(typCard)+" Card is chosen for the immediate pull!")
            if request.POST['pulltype']=='preclose':
                precloseFlag = 1
            if request.POST['amount']:
                pull_amt = Money(request.POST['amount'])
                imm_pull_logger.info("\nCard:: Immediate Pull "+"Attempting Immediatepull......")
                if pull_amt > dueAmt:
                    extra_amt = pull_amt - dueAmt
                if pull_from == 'PREPAID CARD':
                    if pull_amt > AvlBal:
                        msg = 'Pull amount should be less than available amount'

                setCVV = ''
                cvvIndicator = 0
                if 'pull' in request.POST and 'extCVV2' in request.POST:
                    setCVV = request.POST['extCVV2']
                    cvvIndicator = 1

                if 'pull' in request.POST and 'cvv2' in request.POST:
                    setCVV = request.POST['cvv2']
                    cvvIndicator = 1

                if 'pull' in request.POST and (len(setCVV)<3 or len(setCVV)>5):
                    msg = 'Invalid CVV'

                if 'pull' in request.POST and not setCVV.isdigit():
                    msg = 'Invalid CVV'

                if not msg:
                    if 'pull' in request.POST:

                        cust_pp_type = None
                        if 'extMoney' in request.POST:
                            if request.POST['extMoney']=='RPP':
                                cust_pp_type = 'RPP'
                            elif request.POST['extMoney']=='EPP':
                                cust_pp_type = 'EPP'
                        if typCard == 'New':
                            create_date=datetime.datetime.now()
                            request_dict = {}
                            request_dict['buildingname']=str(request.POST['buildingname'])
                            request_dict['flatnumber']=str(request.POST['flatnumber'])
                            request_dict['buildingnumber']=str(request.POST['buildingnumber'])
                            request_dict['street']=str(request.POST['street'])
                            request_dict['county']=str(request.POST['county'])
                            request_dict['postcode']=str(request.POST['postcode'])
                            request_dict["pannum"]=str(request.POST["pannum"])
                            request_dict["nameoncard"]=str(request.POST["nameoncard"])
                            request_dict["cardtype"]=str(request.POST["cardtype"])
                            ccissuenumber=""
                            ccvalidfrom=None
                            request_dict['validto_month'] = int(request.POST['validto_month'])
                            request_dict['validto_year']=str(request.POST['validto_year'])
                            request_dict['cvv2']=str(request.POST['cvv2'])

                            if cardconfig.DATA_DICT_CVS_CI['testing']==1:
                                card_validate,parsed,error_code,message = debitcardcheckandfraudrules(loan_id,cust_id,'Immediate_Pull','Validate',
                                                                                             username,request_dict,imm_pull_logger)
                            else:
                                card_validate,parsed,error_code,message = cardSaveAndValidate(loan_id,cust_id,'Immediate_Pull','Validate',
                                                                                        username,request_dict,imm_pull_logger)
                            if card_validate == True or card_validate == False:
                                if parsed["CIMTranID"]:
                                    if cardconfig.DATA_DICT_CVS_CI['testing']==1:
#                                         bureau_name=str(parsed['DPName']) or "CallCredit" # Check to remove
                                        bureau_name=str(parsed["DPName"])
                                        response_lptran_id=str(parsed["CIMTranID"])
                                        response_carduniqid=str(parsed["CardUniqueID"])

                                        update_card_reference(loan_id=loan_id, bureau_name = bureau_name, CIMTranId=response_lptran_id, source='IMMEDIATE PULL', username=username,
                                            save_card='0', cardUniq_id=response_carduniqid, cardStatus=parsed['DPVerifiedStatus'],
                                            reason=parsed['DPStatusDescription'], fraudRuleStatus=parsed['CardVerifyStatus'],
                                            fraudRuleDesc=parsed['Message_FraudRules'], bureau_id=parsed["DPTransactionID"], key_id=None, logger=card_logger,
                                            response = None, card_usage='TEMPORARY CARD',create_dt=create_date,cardwithpull=1)

                                        imm_pull_logger.info('Immediate_Pull :: Response Success:: DP TranID::'+ str(parsed["DPTransactionID"])+' :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username))
                                        case_id=get_case_id_by_entity_id(loan_id,'LOAN')
                                        log_id=get_logid_by_caseid(case_id)
                                        add_gcm_notes(log_id["log_id"],"ImmPull","Bureau name- ID -"+str(response_lptran_id)+"added at"+str(create_date),username,create_date)

                                    else:

                                        response_lptran_id=str(parsed["CIMTranID"])

                                        update_card_reference(loan_id=loan_id, bureau_name = bureau_name, CIMTranId=response_lptran_id, source='IMMEDIATE PULL', username=username,
                                            save_card='0', cardUniq_id=None, cardStatus=None,reason=None, fraudRuleStatus=None,fraudRuleDesc=None,
                                            bureau_id=parsed["LendProtectTranID"], key_id=None, logger=card_logger,response = None,
                                            card_usage='TEMPORARY CARD',create_dt=create_date,cardwithpull=1)


                                        imm_pull_logger.info('Immediate_Pull :: Response Success:: LP TranID::'+ str(parsed["LendProtectTranID"])+' :: Loan ID :: '+str(loan_id)+' Username:: '+ str(username))
                                        case_id=get_case_id_by_entity_id(loan_id,'LOAN')
                                        log_id=get_logid_by_caseid(case_id)
                                        add_gcm_notes(log_id["log_id"],"ImmPull","Bureau name- LendProtect. LP ID -"+str(response_lptran_id)+"added at"+str(create_date),username,create_date)

                            else:
                                imm_pull_logger.error('Card Validation :: ' +str(card_validate)+ 'Error Code :: '+str(error_code) + " : Explaination::"+str(message))
                                display_msg = 'Card is not valid. Please provide correct card details.'

                        loan_obj = Loan.objects.get(loan_id=loan_id)
                        store_id = loan_obj.store_id
                        query = "select account_cust_id from Loan_Latest where loan_id=%s"%(loan_id)
                        acc_cust_id = con.get_one_result(query)

                        query = "select max(total_CPA_hits) as maxHit from Driver dr join (select ll.loan_id from GCMS_Data.gcm_case gc \
                                    join Loan_Latest ll on loan_id=entity_id and entity_type='loan' and account_cust_id='%s' \
                                    and store_id='%s' and status_cd not in %s and fund_dt is not null left join CPA_cancellations cc \
                                    on cc.loan_id=ll.loan_id where cc.loan_id is null) acc on acc.loan_id=dr.loan_id"%(acc_cust_id['account_cust_id'],store_id,\
                                    str(tuple(set(END_STATUS_CPA+LOAN_LEVEL_EXCLUSION_LIST+CUSTOMER_LEVEL_EXCLUSION_LIST))))
                        maxHit = con.get_one_result(query)

                        if pull_from == 'PREPAID CARD' and typCard == 'Existing':
                            ## In prepaid card case, we only have existing card, No new card.

                            msg = imm_pull_tms(loan_id, pull_amt, merchant_name, request.session['username'], pdc_log, None, None, "1", 0, cvvIndicator=cvvIndicator, rcvCVV=setCVV, cust_pp_type=cust_pp_type)
                            # Checking the balance after the pull is done
                            responseDict = cardEnquiryFn(PDC_Dict)
                            if responseDict['Error']:
                                request.session['AvlBal'] = 'Service Error'
                            else:
                                request.session['AvlBal'] = responseDict['AvlBal']
                        else:

                            if typCard == 'Existing':
                                msg = imm_pull_tms(loan_id, pull_amt, merchant_name, request.session['username'], imm_pull_logger, None, None, "1", 0, cvvIndicator=cvvIndicator, rcvCVV=setCVV, cust_pp_type=cust_pp_type)
                            else:
                                if card_validate == True:
                                    dataDict = getCardDetails(loanid = loan_id,cimtran_id= parsed['CIMTranID'],cun_id=str(parsed["CardUniqueID"]))
    #                                msg = imm_pull(loan_id, pull_amt, merchant_name, request.session['username'], logger, None, data_dict_copy, 0, 1, cust_pp_type=cust_pp_type)
                                    if cardconfig.DATA_DICT_CVS_CI['testing']==1:
                                        if parsed['DPVerifiedStatus'] == 'Success' and parsed['CardVerifyStatus']=='Valid':
                                            msg = imm_pull_tms(loan_id, pull_amt, merchant_name, request.session['username'], imm_pull_logger, None, dataDict, "0", 1, cvvIndicator=cvvIndicator, rcvCVV=setCVV, cust_pp_type=cust_pp_type)
                                        else:
                                            msg = "Invalid card !!! CardVerifyStatus / UnderwritingStatus was not matched. Please note pull was not attempted"
                                    else:
                                        msg = imm_pull_tms(loan_id, pull_amt, merchant_name, request.session['username'], imm_pull_logger, None, dataDict, "0", 1,cvvIndicator=cvvIndicator, rcvCVV=setCVV, cust_pp_type=cust_pp_type)
                                else:
                                    msg = message
                                    imm_pull_logger.error('Error Code :: '+str(error_code) + " : Explaination::"+str(message))
            #import pdb;pdb.set_trace()

            request.session['msg'] = msg

            #import pdb;pdb.set_trace()
            if( "Success" in msg):
                try:
                    date = datetime.datetime.now()
                    voucher_flag = request.POST.get('voucher_flag')
                    if voucher_flag:
                        offer_given = Decimal(request.POST['offer_given'+voucher_flag])
                        generic_reason = "IMMEDIATE PULL"
                        specific_reason = "VOUCHER"
                        waivemsg = pcfunc.waivingByAmount(loan_id, offer_given,
                                                          generic_reason, specific_reason, username, date)
                        if("SUCCESS" in waivemsg):
                            if voucher_flag and request.POST['voucher_update_flag']!='0':
                                section = 'TMS_DATA'
                                conn = TranDB(section=section)
                                curs = conn.getcursor()
                                voucher_code = request.POST['voucher_code'+voucher_flag]
                                amount_to_pay = request.POST['amount_to_pay'+voucher_flag]
                                offer_given = request.POST['offer_given'+voucher_flag]
                                query_applied = "update TMS_Data.Comm_Voucher_Code set applied_on = '%s',applied_by ='%s',\
                                actual_voucher_given =%s,status='Applied',modified_dt='%s' ,modified_by='%s' where voucher_code ='%s' and override_flag=0 and loan_id =%s"\
                                %(date,username,offer_given,date,username,voucher_code,loan_id)
                                conn.processquery(query_applied , curs)
                                query_not_applicable = "update TMS_Data.Comm_Voucher_Code set status='NotApplicable',override_flag = 1,override_reason ='AppliedAnotherVoucher',modified_dt='%s' ,modified_by='%s' where voucher_code !='%s' and override_flag=0 and loan_id =%s"\
                                %(date,username,voucher_code,loan_id)
                                conn.processquery(query_not_applicable , curs)
                                conn.commit()
                        else:
                            mail_send(0,to='tmsdev_alerts@global-analytics.com',sub="Waive amount and update voucher is failed ",content="Immediate pull is successful but waive is failed.Please update the appropriate table for waiving and voucher.(loan_id::"+str(loan_id)+')' ,cc=[],flag=0,hst=1)
                except:
                    log.error("Waive amount is failed loan_id = "+str(loan_id)+str(traceback.format_exc()))
                    #ob = Payments.objects.filter(loan = loan_id)[0].due_amt

            if msg:
                update_flag = 1

            if msg.__contains__("have been updated successfully"):
                request.session['update_flag'] = 1
            #if msg.lower().__contains__("success"):
            if 'success' in msg.lower():
                updateImmPullinCPAInfo(acc_cust_id['account_cust_id'],store_id,username,maxHit['maxHit'])

            lone_info_frm_loan=Loan.objects.filter(loan_id=loan_id)[0]
            status_cd=get_loan_status_by_loan_case_id(lone_info_frm_loan.case_id)
            if status_cd=="CREDIT CHECK":
                #This flag to refresh loan_gen_info frame
                flag_torefresh_loan=1
                request.session['flag_torefresh_loan'] =flag_torefresh_loan
                chk_cc_paid_not=Downpayments.objects.filter(loan=loan_id,override_flag=0,downpayment_type='CC')[0]
                if chk_cc_paid_not.paid_amt>0:
                    flag=1
                else:
                    flag=0
                updateCreditCheckStatus(loan_id,flag)
            date_elem=datetime.datetime.today()
            bal_infm = get_balance_dtls(loan_id)[0]
            #import pdb;pdb.set_trace()
            OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
            dueAmt = Payments.objects.filter(loan = loan_id)[0].due_amt
            query_voucher = "select voucher_code,percentage,is_direct,percentage_on,(p.due_amt*percentage)/100 as discount_amount ,(p.due_amt-(p.due_amt*percentage)/100) as amount_to_pay,max_voucher_amount  from Comm_Voucher_Code vc join Payments p on vc.loan_id = p.loan_id  where p.loan_id = %s and override_flag = 0 and status !='Applied'"%loan_id
            query_res_voucher = con.get_all_results(query_voucher)
            return render_to_response('custdetail/immediatepull.html',
                        {'msg':msg,'address_info':address_info,'precloseFlag':precloseFlag,'OB':OB,\
                        'dueAmt':dueAmt,'typCard':typCard, 'extra_amt':extra_amt,'loan_id':loan_id,\
                        'update_flag':update_flag,'pull_from':pull_from,'pull_from_list':pull_from_list,\
                        'AvlBal':AvlBal,'isOB':isOB,'flag_torefresh_loan':flag_torefresh_loan,\
                        'extra_amt_msg':extra_amt_msg,'pull_amt':pull_amt,'PC_amt':PC_amt,'display_msg':display_msg,'voucher_dtls':query_res_voucher,\
                        'expiry_range':range(datetime.datetime.now().year, (datetime.datetime.now().year + 20)),
                        'product_class': product_class})
    #        return HttpResponseRedirect('/info/immediatepull_popup/?loan_id='+str(loan_id)+'&pull_from='+pull_from+'&cardtype='+cardtype)
        else:
            freeze_flag = 1
    isOB=isOutStandingBalance(loan_id)
    if pull_from == 'PREPAID CARD':
        return render_to_response('custdetail/immediatepull.html', {'msg':msg,'precloseFlag':precloseFlag,'OB':OB,'dueAmt':dueAmt,'typCard':typCard, 'extra_amt':extra_amt,'loan_id':loan_id, 'update_flag':update_flag,'pull_from':pull_from,'pull_from_list':pull_from_list,'AvlBal':AvlBal,'isOB':isOB,'flag_torefresh_loan':flag_torefresh_loan,'PC_amt':PC_amt, 'paymentPending':paymentPending, 'sum_pendingPayments':sum_pendingPayments,'freeze_flag':freeze_flag,'voucher_dtls':query_res_voucher,
                                                                    'product_class': product_class})
    else:
        return render_to_response('custdetail/immediatepull.html', {'msg':msg,'precloseFlag':precloseFlag,'OB':OB,'dueAmt':dueAmt,'typCard':typCard, 'extra_amt':extra_amt,'loan_id':loan_id, 'update_flag':update_flag,'pull_from':pull_from,'pull_from_list':pull_from_list,'isOB':isOB,'flag_torefresh_loan':flag_torefresh_loan,'PC_amt':PC_amt, 'paymentPending':paymentPending, 'sum_pendingPayments':sum_pendingPayments,'freeze_flag':freeze_flag,'voucher_dtls':query_res_voucher,
                                                                    'product_class': product_class})

immediate_pull_popup = maintenance_deco_popups(immediate_pull_popup)

def get_holiday_list(holidaylist):
    """
    Gets the holiday list
    """
    return ""
    #if request.is_ajax:
    #holidaylist_name = request.POST['holidaylist_name']
#    holidays =eval("list(bankHolidayList_"+str(holidaylist)+")")
#    return holidays

def get_address(request):
    """
    Get the list of address from 3rd party service
    """
    post_code=None
    resp={}
    if request.method=='POST' and request.is_ajax:
        if request.POST.has_key("post_code"):
            post_code=request.POST["post_code"]
            loan_id=request.POST["loan_id"]
            if post_code:
                resp=PostCodeLookUp_Utils(post_code,loan_id)
        elif request.POST.has_key("post_code_id"):
            loan_id = request.POST['loan_id']
            post_code_id=request.POST["post_code_id"]
            if post_code_id:
                resp=AddressLookUp_Utils(post_code_id,loan_id)

    return HttpResponse(simplejson.dumps(resp), mimetype='text/javascript')
get_address = maintenance_deco_popups(get_address)




def account_close_popup(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    account_close_dtls=get_account_close_dtls(loan_id)
    amount_to_be_paid = 0.0
#    amount_to_be_paidEPP = 0.0
    current_date = datetime.date.today()
    return render_to_response("custdetail/account_close_popup.html",{"current_date":current_date,'account_close_dtls':account_close_dtls,"amount_to_be_paid":amount_to_be_paid,'loan_id':loan_id})
account_close_popup = maintenance_deco_popups(account_close_popup)



def calculate_account_close(request):
    if request.is_ajax:
        cl_date1 = request.POST['closing_date'].strip()
        cl_date = toDateTime(cl_date1+" 00:00:00")
        loan_id = request.POST['loan_id']
        amount_dict={}
        amount_dict = amount_cal(loan_id,cl_date1)
        amount_dict['amount_to_be_paid'] = str(amount_dict['amount_to_be_paid'])
    return HttpResponse(simplejson.dumps(amount_dict),mimetype="data")


def find_dup_record(request):

    if request.is_ajax:
        loan_id     = str(request.POST['loan_id']).strip()
        payMethod   = str(request.POST['payMethod']).strip()
        amt         = str(request.POST['amount']).strip()
        recDate     = str(request.POST['recDate']).strip()
        if payMethod == 'direct_dep':
            payMethod = 'DIRECT DEPOSIT'
        else:
            payMethod = payMethod.upper()

        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        ccQuery = "select count(*) as cnt from Transactions where loan_id=%s and date(tran_dt)='%s' and debit = %s and payment_method = '%s'"%(loan_id,recDate,amt,payMethod)
        ccResult = con.get_one_result(ccQuery)
        if int(ccResult['cnt'])>=1:
            return HttpResponse(ccResult['cnt'],mimetype="data")
        else:
            return HttpResponse(None,mimetype="data")
#def add_account_close(request):
#    if request.is_ajax:
#        cl_date1 = request.POST['closing_date'].strip()
#        cl_date = toDateTime(cl_date1+" 00:00:00")
#        loan_id = request.POST['loan_id']
#        date_elem=datetime.datetime.now()
#        user = request.session['username']
#        closing_amount = dbtmsapi.get_amountEPP_dtls(loan_id,cl_date1)
#        try:
#            msg = pcfunc.update_account_closure(loan_id,closing_amount, str(cl_date1), user, date_elem)
#            if "FAILURE::" in msg:
#                raise Exception
#        except Exception:
#            transaction.rollback()
#        else:
#            request.session['update_flag'] = 1
#    return HttpResponse(mimetype="data")


def prorata_popup(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username = request.session['username']
    case_id=get_case_id_by_entity_id(loan_id,'LOAN')
    reason_cd=''
    withdrawal_reason=''
    status=get_loan_status_by_loan_id(loan_id)
    prorata_dtls = dbtmsapi.get_prorata_dtls(loan_id)
    relv_date = prorata_dtls[-1]['relevant_dt']
    if status in ("WITHDRAWAL"):
         withdrawal_reason=get_withdrawal_reason(case_id,status)
    if withdrawal_reason:
        reason_cd=withdrawal_reason[0]['reason_cd']
    prorata = 0.0
    pdlobj=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
    prorata_dtls = dbtmsapi.get_prorata_dtls(loan_id)
    relv_date = prorata_dtls[-1]['relevant_dt']

    conn = TranDB(section="TMS_DATA")
    cur = conn.getcursor()
    #fetching product details for that loan_id
    wd_date_exist = "select wd_proposed_on from Loan_Info where loan_id=%s and override_flag =0" %(loan_id)
    date_res = conn.processquery(query = wd_date_exist, curs = cur, fetch = True, count=1)

    if date_res['wd_proposed_on'] is not None:
        date_res=date_res['wd_proposed_on'].date()
    conn.close()



    if pdlobj.now_dt:
        now_date=pdlobj.now_dt.date()
    else:
        now_date = datetime.date.today()
    if pdlobj.wd_proposed_on:
        wd_date = pdlobj.wd_proposed_on
        pcobj = PaymentCalendar.objects.filter(loan=loan_id,override_flag=0,payment_type=pcconfig.TYPE_VALUE['PIC']).order_by("-create_date")
        if pcobj and pcobj[0].payment_amt:
            prorata = pcobj[0].payment_amt
    else:
        wd_date = ""
    reasons=queueconfig.WITHDRAWAL_REASON
#    if request.POST.has_key("withdrawal_reason"):
#            withdrawal_reason_select=str(request.POST["withdrawal_reason"])

#   spcl privilege check for revert feature
    revert_flag=0
    revert_special_prev=get_spl_privileges_by_usr_id(str(username),2)
    if revert_special_prev=='Grant' and status=='WITHDRAWAL':
        revert_flag=1

    status_flag=0
    if status in ('CLOSED','PRECLOSED','POSTCLOSED'):
#       import pdb;pdb.set_trace()
        sql = "select end_date from gcm_case_log where end_status_cd='%s' and case_id=%s order by log_id desc limit 1"%(status,case_id)
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'GCMS_DATA')
        res = con.get_one_result(sql)
        wd_date=res["end_date"]

        prorata = prorata_cal(loan_id,wd_date)
        status_flag=1

    return render_to_response("custdetail/prorata_popup.html",{"date_res":date_res,"relv_date":relv_date,"now_date":now_date,"wd_date":wd_date,"reason_cd":reason_cd,"reasons":reasons,"prorata":prorata,'loan_id':loan_id,'revert_flag':revert_flag,'loan_status':status,'status_flag':status_flag})
prorata_popup = maintenance_deco_popups(prorata_popup)


def calculate_prorata(request):
    prorata=0.0

    if request.is_ajax:
        wd_date1 = request.POST['wd_date'].strip()
        wd_date = toDateTime(wd_date1+" 00:00:00")
        loan_id = request.POST['loan_id']
        interest_frequency = Product.objects.filter(loan=loan_id)[0].interest_frequency
        if interest_frequency != 'daily':
            wd_date = get_prorata_calc_date(loan_id, wd_date)
        prorata = prorata_cal(loan_id, wd_date)
    return HttpResponse(prorata,mimetype="data")


def add_prorata(request):
    prorata=0.0
    if request.is_ajax:
        wd_date1 = request.POST['wd_date'].strip()
        wd_date = toDateTime(wd_date1+" 00:00:00")
        loan_id = request.POST['loan_id']
        date_elem=datetime.datetime.now()
        user = request.session['username']
        reason_cd=str(request.POST["reason_cd"])
        status_flag=request.POST["status_flag"]
        case_id=get_case_id_by_entity_id(loan_id,'LOAN')
        conn = TranDB(section="TMS_DATA")
        cur = conn.getcursor()
        #fetching product details for that loan_id
        prod_dtls = "select * from Product P,Loan L where P.product_id=L.product_id and loan_id = %s" %(loan_id)
        prod_result = conn.processquery(query = prod_dtls, curs = cur, fetch = True)
        conn.close()


        #for daily interest product calculate interest till the current date
        if prod_result[0]['interest_frequency'] =='daily':
            prorata=prorata_cal(loan_id,date_elem)

        else:
            # Fetch date till which prorata interest needs to be calculated, for non-daily loans
            prt_date = get_prorata_calc_date(loan_id, wd_date)
            prorata = prorata_cal(loan_id, prt_date)

        try:
            pblLoan=Loan_Info.objects.filter(loan=loan_id,override_flag=0).order_by("-create_dt")[0]
            if pblLoan.now_dt is None:
                now_dt = date_elem
            else:
                now_dt = pblLoan.now_dt
            Loan_Info.objects.filter(loan=loan_id,override_flag=0).update(override_flag=1,last_updated_on=date_elem)
            Loan_Info(override_flag=0,\
                request_amt=pblLoan.request_amt, approved_amt=pblLoan.approved_amt,downpayment_amt=pblLoan.downpayment_amt, creditcheck_amt=pblLoan.creditcheck_amt,borrowed_amt=pblLoan.borrowed_amt,loc_limit=pblLoan.loc_limit,\
                funded_amt=pblLoan.funded_amt, request_dt=pblLoan.request_dt, approved_dt=pblLoan.approved_dt,funding_method=pblLoan.funding_method,\
                booked_dt=pblLoan.booked_dt, EMI_amt=pblLoan.EMI_amt,repayment_dt=pblLoan.repayment_dt,next_repayment_dt=pblLoan.next_repayment_dt,repayment_frequency=pblLoan.repayment_frequency, fund_dt=pblLoan.fund_dt,create_dt=date_elem,commencement_dt=pblLoan.commencement_dt,\
                dp_esign_dt=pblLoan.dp_esign_dt, APR=pblLoan.APR,noc_req_on=pblLoan.noc_req_on,now_dt=now_dt,loan_esign_dt=pblLoan.loan_esign_dt,\
                relevant_dt=pblLoan.relevant_dt,loan_id=pblLoan.loan_id,done_by=user,wd_proposed_on=str(wd_date),\
                fund_to=pblLoan.fund_to,cb_fund_to=pblLoan.cb_fund_to,pco_dt=pblLoan.pco_dt,selling_price=pblLoan.selling_price,nosia_sent_on=pblLoan.nosia_sent_on).save()
#            Commeted because the below insert is handle in updategcmcase api
#            if  int(status_flag):
#                db = TranDB(section='TMS_DATA')
#                curs = db.getcursor()
#                query = "select * from GCMS_Data.gcm_case_log where case_id=%s order by log_id desc limit 1"
#                args = (case_id)
#                res = db.processquery(query=query, curs=curs,count=1, args=args)
#                insert_query ="insert into GCMS_Data.gcm_case_log (entry_dt,start_status_cd,done_by,case_id) values (%s,%s,%s,%s)"
#                args1=(res["end_date"],res["end_status_cd"],res["done_by"],res["case_id"])
#                db.processquery(query=insert_query,curs=curs,args=args1,fetch=False)

            log_id=get_log_id_by_loan_id(loan_id)
            add_gcm_notes(log_id,"Special Case","Time of Withdrawal Proposal "+str(date_elem)+"\nDate of Withdrawal "+str(wd_date1),user,date_elem)

            msg = pcfunc.update_pro_rata(loan_id, prorata, str(wd_date1), user, date_elem,reason_cd)

            if "FAILURE::" in msg:
                raise Exception

            # Update Notice flags table if loan is not closed
            if status_flag == '0':
                nf_entry = Notice_Flags.objects.filter(loan=loan_id,
                                                       flag_name='NOWDL',
                                                       override_flag=0)
                if not nf_entry:
                    update_or_insert_Notice_Flags(loan_id, date_elem,
                                                  NOWDL='TO BE SENT')

            ##delta matrix table is updated whenever there is change in status to WDL or change in WDL date
            daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
            if isDailyRunStarted(date_of_run=daily_run_date):
                updateDeltaMatrix(loan_id,'status')
        except Exception:
            transaction.rollback()
        else:
            transaction.commit()
            request.session['update_flag'] = 1
    return HttpResponse(prorata,mimetype="data")
add_prorata = transaction.commit_manually(add_prorata)
add_prorata = maintenance_deco_popups(add_prorata)


def generate_email(request):
    """
    This view is called on ajax call from the Mail tab.
    It generated the email content of the selected type and returns it to the page.
    """
    mail_dict={}
    if request.is_ajax:
        accountid=request.session['accountid']
        mail_type = request.POST['mail_type']
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
        template_name = request.POST['template_name']
        template_version = request.POST['version']
        loan_obj = Loan.objects.get(loan_id=loan_id)
        store_id =loan_obj.store_id
        brand_name = get_Store_Info_frm_storeid(store_id)['brand_name']
    #----------------CONTENT
        context_dict = {}
        if mail_type in EMAILDOC[brand_name]:
            if mail_type == 'WDAC' or mail_type ==  'ACL':
                generating_function = getattr(utils,"generate_ACL_doc")
            else:
                generating_function = getattr(utils,"generate_"+mail_type+"_doc")
            try:
                context_dict = generating_function(loan_id,store_id,loan_obj.account_id)
            except:
                mail_dict['msg']="Failed to fetch the mail content"
                log.error("Failed to fetch for loan_id = "+str(loan_id)+str(traceback.format_exc()))
#                context_dict = eval("generate_"+mail_type+"_doc(loan_id)")
            try:
                temp_obj = None
#                temp_obj = Template.objects.filter(store=store_id,
#                                               template_for='EMAIL',
#                                               template_type=mail_type,
#                                               template_name=template_name,
#                                               template_version=float(template_version))
                if temp_obj:
                    path = MEDIA_ROOT_INPUT+"/"+accountid+"/"+brand_name+"/"+temp_obj[0].template_path
                else:
                    mail_dict['msg']="Failed to fetch the template"
                    log.error("Failed to fetch the template loan_id = "+str(loan_id))
            except:
                mail_dict['msg']="Failed to fetch the template"
                log.error("Failed to fetch the template loan_id = "+str(loan_id))
            try:
                content = pdf_generator.genWLTFromHTML(path,context_dict)
                mail_dict['content'] = content
            except:
                mail_dict['msg']="Failed to fetch the mail content"

                log.error("Failed to fetch for loan_id = "+str(loan_id)+str(traceback.format_exc()))

        else:
            mail_dict['msg']="Failed to fetch the mail content"

            log.error("Failed to fetch for loan_id = "+str(loan_id)+" "+str(mail_type)+" not found in Document_path")
    #----------------MAIL SUBJECT
        if mail_type in mail_subject[brand_name]:
#            if mail_type =='DWNPMNT':
#                mail_dict['subject'] = mail_subject[brand_name][mail_type]+" "+context_dict['status']
#            else:
            cur_date = datetime.date.today()
            fundDt = Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0].fund_dt
            customer_Info = get_CustomerInfo(loan_id)
            renderingVariables = {'prefix':customer_Info['prefix'],
            'first_name':customer_Info['first_name'],
            'last_name':customer_Info['last_name'],
            'from_date':fundDt,
            'to_date':cur_date}
            subject = mail_subject[brand_name][mail_type]
            subject = django_Template(subject).render(django_Context(renderingVariables))
            mail_dict['subject'] = subject
        else:
            if mail_dict.has_key('msg'):
                mail_dict['msg']+=" subject"
            else:
                mail_dict['msg']="Failed to generate the subject"

    #---------------CUSTOMER EMAIL
        cust_email = get_customer_email_from_cust_id(cust_id)
        if not cust_email:
            log.error("Failed to generate Email :: No email address for Loan %s" %loan_id)
            if mail_dict.has_key('msg'):
                mail_dict['msg']+=" Email"
            else:
                mail_dict['msg']="Failed to generate the Email"

        else:
             mail_dict['Email'] = cust_email
        if mail_dict.has_key('msg'):
            mail_dict['msg']+=". Please refer the log for more information."
            mail_dict['content'] = ''
            mail_dict['Email'] = ''
            mail_dict['subject'] = ''
        else:
             mail_dict['msg']=''
    return HttpResponse(simplejson.dumps(mail_dict), mimetype="text/javascript")

class WaiversView(View):

    model = PaymentCalendar
    context = {}

    def get(self, request, *args, **kwargs):
        self.context['success_msg'] = request.session.get('success_msg', "")
        self.context['failure_msg'] = request.session.get('failure_msg', "")
        request.session["success_msg"] = None
        request.session["failure_msg"] = None
        msg = self.get_context_data()
        if 'ERROR' in msg:
            return HttpResponse(msg)
        return render_to_response('custdetail/waivers.html', self.context)
    get = maintenance_deco_popups(get)

    def post(self, request, *args, **kwargs):
        msg = self.get_context_data()
        if 'ERROR' in msg:
            return HttpResponse(msg)
        generic_reason = request.POST['generic_reason']
        specific_reason = request.POST['specific_reason']
        if specific_reason == "OTHERS":
            specific_reason += (":" + request.POST['other_reason'])
        success_msg = ""
        failure_msg = ""
        msg = ""
        redirect_tab = ""
        if 'amt_form' in request.POST:  # Waive by Amount submission
            waiver_type = request.POST['waive_amt_type']
            waive_amt = Decimal(request.POST['waive_amount'], 2)
            paycal_logger.info('WAIVERS :: Waive By Amount - Type: %s and Waiver Amount: %s' % (waiver_type, waive_amt))
            # Partial Waiver - Less than Outstanding Balance
            if waiver_type == 'partial':
                if 0 < waive_amt <= self.context['waiveable_amt']:
                    msg = pcfunc.waivingByAmount(self.context['loan_id'], waive_amt, generic_reason, specific_reason,
                                                 self.context['username'], self.context['now'])
                else:
                    failure_msg = "The amount entered is greater than the amount that can be waived off!! " \
                                  "Please enter less than %s" % self.context['waiveable_amt']

            # Full Waiver - Loan is Preclosed
            elif waiver_type == 'preclose':
                if waive_amt != self.context['outstanding_balance']:
                    failure_msg = "Loan cannot be closed as the amount is incorrect and cannot be waived off!"
                else:
                    msg = pcfunc.waivingByAmount(self.context['loan_id'], waive_amt, generic_reason, specific_reason,
                                                 self.context['username'], self.context['now'])
            redirect_tab = "#tabs-amt"

        elif 'rec_form' in request.POST:  # Waive by Record submission
            # Waive individual records in Payment Calendar
            waivers = []
            future_waiver = None
            for key in request.POST:
                if key[0:13] == 'future_waiver':  # Records to be waived are of the format 'payment_id######'
                    future_waiver = request.POST[key]
                if key[0:10] == 'payment_id':  # Records to be waived are of the format 'payment_id######'
                    waivers.append((long(key[11:]), ))
            paycal_logger.info('WAIVERS :: Waive By Record Selected')

            # Add future waiver record
            if future_waiver:
                msg = waive_future(self.context['loan_id'], future_waiver, pcconfig.FUTURE_WAIVER_TYPES[0],
                                   self.context['username'], self.context['waive_till_date'])
                paycal_logger.info('WAIVERS :: Future Cycle %s waived' % future_waiver)
            # Construct records to pass to pcfunc.manual for waiving
            for i, waiver_tuple in enumerate(waivers):
                waive_amt = Decimal(request.POST[str(waiver_tuple[0])+'_amt'])
                waivers[i] = waiver_tuple + (waive_amt, )
            records = []
            for waiver in waivers:
                def f(x):
                    return x if x.payment_id == waiver[0] else None
                payment_record = filter(f, self.context['waiveable_records'])[0]
                if payment_record:
                    update_amt = Money(payment_record.payment_amt - waiver[1], 2)
                    waived_amt = Money(waiver[1], 2)
                    if update_amt >= 0:
                        records.append({"payment_id": waiver[0], "loan_id": self.context['loan_id'],
                                        "paydate": payment_record.payment_dt, "payment_nbr": payment_record.payment_nbr,
                                        "amount": update_amt, "payment_type": payment_record.payment_type,
                                        "reason": None, "user": self.context['username'], "flag": 0,
                                        "waived_amt": waived_amt})
            if records:
                paycal_logger.info('WAIVERS :: Records being waived: %s' % str(records))
                # Call manual to update changes in the payment calendar table
                msg = pcfunc.manual(records, self.context['username'], generic_reason, specific_reason, True,
                                    self.context['now'])
                request.session["update_flag"] = 1
            redirect_tab = "#tabs-rec"

        if "SUCCESS" in msg:
            success_msg = "Successfully Waived Off."
            # For daily_run phase 2: whenever there is a transaction, paydates change, status change
            # Loan_id shd be flagged in DeltaMatrix table
            daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
            if isDailyRunStarted(date_of_run=daily_run_date):
                updateDeltaMatrix(self.context['loan_id'], 'transaction')

        else:
            failure_msg = "Failed to waive off the amount/record. Please Contact backend team."
        request.session['success_msg'] = success_msg
        request.session['failure_msg'] = failure_msg
        return HttpResponseRedirect("/info/waivers/?loan_id="+str(self.context['loan_id'])+redirect_tab)
    post = maintenance_deco_popups(post)

    def get_context_data(self, **kwargs):
        today = datetime.datetime.now()
        loan_id = self.request.GET.get('loan_id', None)
        username = self.request.session.get('username', None)
        if loan_id is None or username is None:
            return 'ERROR :: Username or LoanID is missing. Please Login to continue.'
        balance_info = get_balance_dtls(loan_id)[0]
        outstanding_balance = balance_info['OutstandingPrincipal'] + balance_info['OutstandingInterest'] + \
                              balance_info['OutstandingFee']
        loan = Loan.objects.filter(loan_id=loan_id)[0]
        waiveable_records = PaymentCalendar.objects.filter(loan=loan, override_flag=0).exclude(
            payment_type__in=(pcconfig.TYPE_VALUE['PD'], pcconfig.TYPE_VALUE["RPB"], pcconfig.TYPE_VALUE['EPP']))\
            .order_by('-payment_dt')
        waiveable_amt = 0
        self.context['future_cycles'] = None
        self.context['waive_till_date'] = None  # Should be None for interim product
        if loan.product.interest_frequency == 'daily':
            if queueconfig.WAIVE_FUTURE_CURRENT_CYCLE:
                if loan.product.product_classification == 'LOC':
                    # waiver_end_date is the Statement Date.
                    # Due date taken from PayDates as no guarantee for Future Rec in PC
                    paydt_rec = PayDates.objects.filter(loan=loan, override_flag=0, payment_type='STCYC',
                                                        paydate__gte=today.date()).order_by('cycle')[0]
                    cur_cycle = paydt_rec.cycle
                    self.context['waive_till_date'] = paydt_rec.paydate  # Waive until the Statement Date
                    due_date = PayDates.objects.filter(loan=loan, override_flag=0,
                                                       payment_type='LNCYC', cycle=cur_cycle)[0].paydate
                    waiver_end_date = paydt_rec.paydate  # Used to Hide Future Waiver on Statement Date for LOC
                else:  # For interim product, due_date is same as waiver_end_date
                    paycal_rec = PaymentCalendar.objects.filter(loan=loan, override_flag=0).order_by('-payment_dt')[0]
                    due_date = paycal_rec.payment_dt
                    cur_cycle = paycal_rec.payment_nbr
                    waiver_end_date = due_date  # Used to Hide Future Waiver on Due Date for Interim
                if waiver_end_date > today.date() and len(FutureWaiver.objects.filter(
                        loan=loan, cycle=cur_cycle, waiver_type=pcconfig.FUTURE_WAIVER_TYPES[0])) == 0:
                    self.context['future_cycles'] = [{'payment_nbr': cur_cycle, 'payment_dt': due_date,
                                                     'payment_type': 'Future Interest'}]
        self.context['product_class'] = loan.product.product_classification
        if waiveable_records:  # Sum of the payment amounts of all waiveable_records
            waiveable_amt = sum(map(lambda x: x.payment_amt, waiveable_records))
        self.context['now'] = today
        self.context['loan_id'] = loan_id
        self.context['username'] = username
        self.context['outstanding_balance'] = outstanding_balance
        self.context['waiveable_amt'] = waiveable_amt
        self.context['waiveable_records'] = waiveable_records
        self.context['payment_flag'] = isEndStatus(loan_id)
        self.context['generic_reasons'] = queueconfig.WAIVER_GENERIC_REASONS
        self.context['specific_reasons'] = queueconfig.WAIVER_SPECIFIC_REASONS
        return 'SUCCESS'

'''
This functionality has been replaced by class WaiversView
def WaiveByAmount(request):
    """
    This api waives off the amount entered!!
    """
    failure_msg=''
    success_msg=''
    OB=''
    waiveable_amt=''
    WaiveAmountFlag=0
    disable_flag=0
    user=request.session['username']
    date_elem = datetime.datetime.now()
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        bal_infm = {}
        bal_infm=get_balance_dtls(loan_id)[0]
        OB = bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']

        sql = "select sum(payment_amt) as amt_to_waive from PaymentCalendar where loan_id=%s \
            and override_flag=0 and payment_type not in \
            ('%s','%s','%s')"%(loan_id,pcconfig.TYPE_VALUE['PD'],pcconfig.TYPE_VALUE["RPB"],pcconfig.TYPE_VALUE['EPP'])
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        res = con.get_one_result(sql)
        waiveable_amt=res["amt_to_waive"]

    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        generic_reason=request.POST['generic_reason']
        specific_reason=request.POST['specific_reason']

        if request.POST["pulltype"]=="preclose":
            WaiveAmountFlag = 1
        bal_infm = {}
        bal_infm=get_balance_dtls(loan_id)[0]
        OB = bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']

        sql = "select sum(payment_amt) as amt_to_waive from PaymentCalendar where loan_id=%s \
            and override_flag=0 and payment_type not in \
            ('%s','%s','%s')"%(loan_id,pcconfig.TYPE_VALUE['PD'],pcconfig.TYPE_VALUE["RPB"],pcconfig.TYPE_VALUE['EPP'])
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        res = con.get_one_result(sql)
        waiveable_amt=res["amt_to_waive"]
        if request.POST['pulltype']=="partial" and "enter" in request.POST:
            waived_amt = Decimal(request.POST['amt'])
            if waived_amt<=res["amt_to_waive"]:
        #        pcfunc.waivebyamount(loan_id, waived_amt, user, date_elem, key_id)con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
                pcfunc.waivingByAmount(loan_id, waived_amt, user,generic_reason,specific_reason,date_elem)
                success_msg = "Successfully WaivedOff an amount of %s" % waived_amt
            elif waived_amt > res["amt_to_waive"]:
                failure_msg  = "The amount entered is greater than the amount that can be waived off!! Please enter less than %s"%(res['amt_to_waive'])
        if request.POST['pulltype']=="preclose" :
            if res["amt_to_waive"] < OB:
                disable_flag=1
                failure_msg = "Loan cannot be closed as this amount cannot be waived off!"
            else:
                waived_amt = Decimal(OB)
                pcfunc.waivingByAmount(loan_id, waived_amt, user, date_elem)
                success_msg = "Successfully Closed the Loan"
    return render_to_response('custdetail/WaiveByAmount.html',{'loan_id':loan_id,'success_msg':success_msg,'failure_msg':failure_msg,'OB':OB,'disable_flag':disable_flag,'waiveable_amt':waiveable_amt,'WaiveAmountFlag':WaiveAmountFlag})
'''

def mail(request):
    """
    This view renders the Mail tab
    """
    mail_type=''
    msg = ''
    display_dict = {}
    cur_time = datetime.datetime.now()
    accountid=request.session['accountid']
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    cust_email = get_customer_email_from_cust_id(cust_id)

    loan_obj = Loan.objects.get(loan_id=loan_id)
    store_id =loan_obj.store_id
    product_id = loan_obj.product_id
    store_obj = get_Store_Info_frm_storeid(store_id)
    if store_obj:
        brand_name = store_obj['brand_name']
        brand_EMAILDOC = EMAILDOC[brand_name]

        username = request.session['username']
    #    cust_id=request.session['cust_id']
#        AUTOMATIC_SMS={'ESIGN':'Dear %s, we have sent your Flex agreement to %s.',\
#    #                'Downpayment Successful':'Dear %s, We have successfully collected the down payment for your Flex purchase. Your first Flex instalment falls due on %s.',\
#                    'Downpayment Failed':'Dear %s, We were unable to collect the down payment for your Flex purchase. Call 0800 512 0543 between 12PM and 4PM GMT for assistance.',\
#                    'ACCOUNT CLOSED LETTER':'Congratulations %s! You have successfully completed all your Flex payments. Thank you for choosing Flex.'}


        notice_flag_obj = Notice_Flags.objects.filter(loan=loan_id,flag_value='TO BE SENT')

        if request.method == 'POST' and notice_flag_obj.filter(flag_name = request.POST['mail_type']):
            to1 = (request.POST['to_field']).split(',')
            cc = (request.POST['cc_field']).split(',')
            bcc = (request.POST['bcc_field']).split(',')
            subject = request.POST['subject']
            case_id = get_case_id_by_entity_id(loan_id, 'LOAN')
            log_id = get_logid_by_caseid(case_id)

            mail_type = request.POST['mail_type']
    #-------------CUSTOM MAIL
            if mail_type == 'custom':
                mail_content = request.POST['mail_content']

                val = "_cust['"+brand_name+"']"

                server = eval("mailconfig.server"+ val)
                port=eval("mailconfig.port"+ val)
                withSSL=eval("mailconfig.withSSL"+ val)
                withTLS=eval("mailconfig.withTLS"+ val)
                user=eval("mailconfig.user"+ val)
                password=eval("mailconfig.password"+ val)

                tcc = []
                tbcc = []
                tcc.extend(cc)
                tbcc.extend(bcc)
                tcc.extend(eval("mailconfig.cc" + val))
                tbcc.extend(eval("mailconfig.bcc" + val))
                cc = tcc
                bcc = tbcc

                # Converting subject and content to unicode strings
                if not isinstance(subject, unicode):
                    subject = unicode(subject, "utf-8")
                if not isinstance(mail_content, unicode):
                    mail_content = unicode(mail_content,"utf-8")

                # Creating the mail object
                mail = smtpmailer.SMTPMail(server, port,withSSL,withTLS, 2 )

                # Authenticating the user
                mail.setSSLAuthentication(user, password)


                print "Sending mail.."
                sender = eval("mailconfig.sender" + val)

                result = mail.sendmail(sender,to1,cc,bcc,subject,mail_content)

                print "Result:", ("Failed", "Success")[result]
                if result:
                    msg = "Email sent successfully."
                    add_gcm_notes(log_id['log_id'],'Email',"Email with subject "+subject+" was sent successfully to Email Id: "+str(to1)+str(cc)+str(bcc),username,cur_time)

                else:
                    msg = "Failed to send Email. For more information check logs."

                print "Closing connection.."
                mail.closeConnection()
            else:
                mail_content = request.POST['mail_content2']
                headerImgObj = Image_Info.objects.filter(store=store_id,image_for="EMAIL",image_type="HEADER",override_flag=0)
                if headerImgObj:
                    logo_path=headerImgObj[0].image_path
                else:
                    logo_path =  Image_Info.objects.filter(store=store_id,image_for="EMAIL",image_type="LOGO",override_flag=0)[0].image_path
                generated_image_path = generate_new_path(MEDIA_ROOT_IMAGE,loan_obj.account_id,brand_name)+logo_path
                mail_status = mail_send(2, to1, subject, mail_content,files=None ,flag=1, hst=0, frm=store_obj['brand_name'],images=generated_image_path)
                if mail_status.split(" ")[0] == 'Exception':
                    log.error("Error in sending mail for loan_id "+str(loan_id)+" "+str(mail_status)+str(traceback.format_exc()))
                    msg = "Failed to send Email. For more information check logs."
                else:
                    document_type=brand_EMAILDOC[mail_type]
                    msg = document_type+" Email sent successfully."
    #                if mail_type=='DWNPMNT':
    #                    document_type = subject
    #                else:
                    try:
                        filename = mail_type+"_"+str(loan_id)+".html"
                        new_media_root = generate_new_path(MEDIA_ROOT_MAIL,accountid,brand_name)
                        output_path = output_Dir(mail_type,filename, cur_time, media_root=new_media_root)
                        file = open(output_path, "w")
                        mail_content = mail_content.encode('utf-8')
                        file.write(mail_content)
                        file.close()

                        add_gcm_email(subject, mail_type, filename, output_path, cur_time, username, case_id)
                        add_gcm_notes(log_id['log_id'],'Email',str(document_type)+" mail was sent successfully to Email Id: "+str(to1),username,cur_time)
                        flag_name = (mail_type+"_flag")
                        eval("update_or_insert_Notice_Flags(loan_id,cur_time,"+mail_type+"='SENT')")
                    except:
                        msg+="But Failed to update backend. Please check logs."
                        log.error(msg+"for loan_id "+str(loan_id)+", MAIL STATUS:"+str(mail_status)+" "+str(traceback.format_exc()))

        if notice_flag_obj:
    #        notice_flag_obj = notice_flag_obj[0]
            for type in brand_EMAILDOC:
                flag = type
                if flag in [nb.flag_name for nb in notice_flag_obj] and flag !=mail_type:
#                    result = (notice_flag_obj.filter(flag_name=flag))[0].flag_value
#                    if result == 'TO BE SENT':
                        display_dict[type] = brand_EMAILDOC[type]

    return render_to_response('custdetail/mailsend.html',{'display_dict':display_dict,
                                'msg':msg,'loan_id':loan_id,'cust_id':cust_id,
                                'store_id':store_id,'product_id':product_id,"cust_email":cust_email})

def check_SOACC_count(request):

    if request.is_ajax():
        cur_datetime = datetime.datetime.now()
        loan_id = request.POST['loan_id']
        case_id = get_case_id_by_entity_id(loan_id,'LOAN')
        count = get_SOACC_count(case_id,cur_datetime)
        if count>=3:
            return HttpResponse("1", mimetype="data")
        else:
            return HttpResponse("0", mimetype="data")
check_SOACC_count = maintenance_deco_popups(check_SOACC_count)
def refundbyother(request):

#    loan_id = request.session['loan_id']

    msg = ''
    if request.method == 'GET':
        loan_id = request.GET['loan_id']
        if 'msg' in request.GET:
           msg = request.GET['msg']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    username = request.session['username']
    refund_reason = ['Dispute','Normal']
    fund_type = ["FPS","CHAPS","BACS","DIRECT DEPOSIT","CHARGE BACK"]
    payment_method = ''
    create_date = datetime.datetime.now()
    cd_dt = datetime.datetime.now().date()
    date=str(create_date).split(" ")[0]
    refund_dt = ''
    if request.method == 'POST':

        refund_amt = request.POST['amt']
        merchant_id = request.POST['merchant_id']
        merchant_name = request.POST['merchant_name']
        refund_dt = request.POST['refund_dt']
        fund_method = request.POST['fund_method']
        if payment_method in ('Transfer Fee Waiver','Out of Pocket Payments'):
            try:
                transaction=Transactions(loan_id=loan_id,credit=float(refund_amt),debit=0.0,\
                        payment_method=fund_method,merchant_txn_id=merchant_id,\
                        tran_dt=refund_dt,merchant_name=merchant_name,create_dt=create_date,changed_by=username,payment_type=loanstatusconfig.PAYMENTTYPE["OPF"],done_on="BANK ACCOUNT",status = "VALID")
                transaction.save()
                msg = 'Refunded Successfully'
            except:
                msg = "Something went wrong and ur request wasn't saved. Kindly inform the backend team."
        elif payment_method == 'Refunds':
        # Check Waterfall is running for this loan_id.
            try:
#               loan = Loan.objects.get(pk=loan_id)
                waterfall_flag = pcfunc.waterfallcheck(loan_id)
                keytranid = getkeytranid(loan_id)
                logger.info('refund :: '+str(keytranid)+' :: loan_id,refund_amt :: '+str(loan_id)+','+str(refund_amt))
                if not waterfall_flag:
#                    print "payment_method"
#                    money = get_collected_money(loan_id)
                    money = getPaidAmt(loan_id,cd_dt)
                    if Decimal(refund_amt) > money:
                        msg = "The amount for refund is greater than amount pulled."
                    else:
                        payment_type = payment_method + ' Refund'
                        if fund_method in ["FPS","CHAPS","BACS","DIRECT DEPOSIT"]:
                            done_on = "BANK ACCOUNT"
                        elif fund_method in ["CHARGE BACK"]:
                            done_on = "DEBIT CARD"
                        else:
                            done_on = None
                        msg = pcfunc.refund(loan_id,None,refund_dt,0,refund_amt,fund_method,merchant_id,merchant_name,username,create_date,paymentType=loanstatusconfig.PAYMENTTYPE["NORMALREFUND"],done_on=done_on)
                else:
                    msg = "Waterfall is currently running for this Loan. Please try later."
            except:
                logger.info(traceback.format_exc())
    #return render_to_response('custdetail/refundbyother.html',{'refund_reason':refund_reason,'payment_method':payment_method,'loan_id':loan_id,'msg':msg,'cur_date':date,'refund_dt':refund_dt,'fund_type':fund_type})
    return msg
refundbyother = maintenance_deco_popups(refundbyother)

def validateFirstSecondPayDate(request):
    paydates_dict ={}
    if request.is_ajax():
        firstPayDate = request.POST["firstPayDate"]
        nextPayDate = request.POST["nextPayDate"]
        payFrequency = request.POST["payFrequency"]
        loanId = request.POST["loanId"]
        cust_county = request.POST["cust_county"]

        if firstPayDate and nextPayDate:
            firstPayDate = datetime.date(int(firstPayDate.split("-")[0]),int(firstPayDate.split("-")[1]),int(firstPayDate.split("-")[2]))
            nextPayDate = datetime.date(int(nextPayDate.split("-")[0]),int(nextPayDate.split("-")[1]),int(nextPayDate.split("-")[2]))
            loan_obj = loan.Loan(loanId)
            paydates_obj = paydates.OrgPayDates(loan_obj)
            paydates_dict = paydates_obj.get_all_paydates(firstPayDate, nextPayDate, payFrequency,county = cust_county)
            for key in paydates_dict:
                paydates_dict[key] = str(paydates_dict[key])

    return HttpResponse(simplejson.dumps(paydates_dict), mimetype='text/javascript')

def new_mail(request):
    """
    This view renders the Mail tab
    """
    cur_time = datetime.datetime.now()
    accountid=request.session['accountid']
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']
        if 'msg' in request.GET.keys():
            msg = request.GET['msg']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        cust_id = request.POST['cust_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    return render_to_response('custdetail/mailsend.html',{})
new_mail = maintenance_deco_popups(new_mail)
def generate_new_email(request):
    """
    This view is called on ajax call from the Mail tab.
    It generated the email content of the selected type and returns it to the page.
    accountID, storeID, productID,templateType,loan_id
    """

    mail_dict={}
    if request.is_ajax:
        accountid=request.session['accountid']
        mail_type = request.POST['mail_type']
        loan_id = request.POST['loan_id']
#        cust_id = request.POST['cust_id']
#        template_name = request.POST['template_name']
#        template_version = request.POST['version']
        loan_obj = Loan.objects.get(loan_id=loan_id)
        store_id =loan_obj.store_id
        product_id =loan_obj.product_id
        username = request.session['username']
        try:
            cust_email, subject, mailContent = emailIndividualSend(accountid, store_id, product_id,mail_type,loan_id, username, send=False)
            mail_dict['content'] = mailContent
            mail_dict['Email'] = cust_email
            mail_dict['subject'] = subject
            mail_dict['msg'] = ''
        except Exception,e:
            mail_dict['msg'] = ". Error:"+str(e)+"\nPlease refer the log for more information."
            mail_dict['content'] = ''
            mail_dict['Email'] = ''
            mail_dict['subject'] = ''
        return HttpResponse(simplejson.dumps(mail_dict), mimetype="text/javascript")

def paydate_calc(loan_id,url_main,lender,product_id,freq,first_paydate,second_paydate,
                            payoutDate,borrowed_amt,total_cycles,current_cycle,grace_period,
                            holidayFlag,decemberLogic,add_cyc,logger):
    paydate_dict = {"lender":lender,
                "product_id": product_id,
                "frequency": freq,
                "cpaydate1": first_paydate,
                "cpaydate2": second_paydate,
                "payoutdate":payoutDate,}
    product_classification = get_product_classification(loan_id)

    logger.info(str(loan_id)+":: Paydate Calc Step 1")

    if product_classification == 'LOC':
        logger.info(str(loan_id)+":: Paydate Calc Step 2")
        db = TranDB(section='TMS_DATA')
        curs = db.getcursor()
        url_sub = str(loan_id) +'/?payoutdate='+paydate_dict['payoutdate'].strftime("%d/%m/%Y")+\
        '&frequency='+paydate_dict['frequency'].replace(' ','+')+'&product_id='+paydate_dict['product_id']\
        +'&borrowed_amount='+str(borrowed_amt)+'&lender='+paydate_dict['lender']+'&cycles='+str(total_cycles)\
                +'&cpaydate1='+paydate_dict['cpaydate1']+'&cpaydate2='+paydate_dict['cpaydate2']


        #  We will consider a paydate change as similar to Funding. No need to send Stmt Date. If the newly generated Statmt Date is in past, we will skip updating that paydate.
        # if current_cycle != 1:  # Send Stmnt_Period parameter for successive cycles in LOC
        #     breather_sql = 'select statement_breather_period from Product where product_id=%s'
        #     stmt_breather = db.processquery(breather_sql, curs, 1,
        #                                     args=paydate_dict['product_id'])['statement_breather_period']
        #     url_sub += '&StmntPeriod='+str(stmt_breather)
        # logger.info(str(loan_id)+":: Paydate Calc Step 3")
    else:
        url_sub = str(loan_id) +'/?payoutdate='+paydate_dict['payoutdate'].strftime("%d/%m/%Y")+\
        '&frequency='+paydate_dict['frequency'].replace(' ','+')+'&product_id='+paydate_dict['product_id']\
        +'&borrowed_amount='+str(borrowed_amt)+'&lender='+paydate_dict['lender']+'&cycles='+str(total_cycles+5)+'&cpaydate1='+paydate_dict['cpaydate1']+'&cpaydate2='+paydate_dict['cpaydate2']
    logger.info(str(loan_id)+":: Paydate Calc Step 3.5")

    for count,elem in enumerate(url_main):
        try:
            logger.info(str(loan_id)+":: Paydate Calc Step 4")
            url = elem + url_sub
            logger.info(str(loan_id)+":: PAYDATES ::The URL to which the request is to be sent :: "+url)
            req = req_encoded(url)
            res = urllib2.urlopen(req)
            response = res.read()
            if not json.loads(response).has_key('result'):
                logger.error(str(loan_id)+":: PAYDATES :: Failure in retrieving the PayDates from the url :: "+url)
                raise Exception,'Message from the CAS - '+response
            logger.info("Successfully received from CAS from the url :: "+url)
            logger.info(str(loan_id)+":: PAYDATES :: The result from the CAS :: "+str(response))
            response = json.loads(response)
            repay_frequency = response['result'].get('frequency_map', None)
            new_paydates = []
            paydates_cas_int = {}
            paydates_cas = response['result']['paydates']
            for elem in paydates_cas.keys():
                    paydates_cas_int[int(elem)] = paydates_cas[elem]
            cycles = paydates_cas_int.keys()
            cycles.sort()
            for elem in cycles:
                new_paydates.append(datetime.datetime.strptime(paydates_cas_int[elem], "%Y-%m-%dT00:00:00").date())

            if product_classification == 'LOC':
                statement_dates_dict = response['result']['statementdates']

                for statement_date in statement_dates_dict.values():
                    new_paydates.append(datetime.datetime.strptime(statement_date, "%Y-%m-%dT00:00:00").date())

                new_paydates.sort()
            else:
                for i in new_paydates:
                    if i<=datetime.date.today():
                        new_paydates.remove(i)
                new_paydates.sort()
                new_paydates=new_paydates[:total_cycles]

            return new_paydates, repay_frequency

        except Exception,e:
            logger.error(str(loan_id)+":: PAYDATES :: Error in obtaining the response:: "+str(traceback.format_exc()))
            return None
        """ Remove manually paydate generation part
        except Exception,e:
            if count == len(url_main) - 1:
                logger.error(str(loan_id)+":: PAYDATES :: Failure in retrieving the PayDates from the url :: "+url)
                logger.error(str(loan_id)+":: PAYDATES :: Error in obtaining the response:: "+str(traceback.format_exc()))
                logger.info(str(loan_id)+":: PAYDATES :: Generating the PayDates at the TMS end")
                if first_paydate and type(first_paydate) == str:
                    first_paydate = datetime.datetime.strptime(first_paydate, "%d/%m/%Y").date()
                else:
                    first_paydate = None
                if second_paydate and type(second_paydate) == str:
                    second_paydate = datetime.datetime.strptime(second_paydate, "%d/%m/%Y").date()
                else:
                    second_paydate = None
                new_paydates = paydates.getPayCycle(freq,total_cycles - current_cycle + add_cyc, \
                                                            grace_period,first_paydate,second_paydate,\
                                                            payoutDate=payoutDate,holidayFlag=holidayFlag,\
                                                            decemberLogic=decemberLogic)
            else:
                logger.error(str(loan_id)+":: PAYDATES :: Failure in retrieving the PayDates from the url :: "+url)
                continue
        """

def update_payFreq_and_related_tables(username, loan_id, freq, first_paydate = None, second_paydate = None, freq_type = 'REPAYMENT_FREQUENCY', update_table = 1,fr_date = None,fr_flag = 0,conn_close =1,reason=None):
    """
    this api will take consider frequency change, whether it can be Repayment Frequency(Loan_Info) change or Payroll Frequency(Employement_Info) change
    and update the relevant tables, if applicable, PayDates table and PaymentCalendar table accordingly
    if the frequency change is Payroll frequency and the loan_id has valid Repayment Frequency in Loan_Info, no need to show the effect
    on related tables but if the loan doesnt have valid Repayment Frequency, then PayDates and PaymentCalendar table
    must be updated accordingto the paydates change
    if the frequency change is Repayment frequency change, then update PayDates and PaymentCalendar tables

    input arguments:
    loan_id: loan_id of the customer
    freq: valid pay_frequency from tms.tmsapi.paydateconfig.mapDict_Freq dictionary
    first_paydate: the paydate the customer proposes as his new and upcoming paydate payroll or repayment frequency
    second_paydate: the paydate the customer proposes as his new and next paydate according to payroll frequency
    freq_type: REPAYMENT_FREQUNECY change in Loan_Info table or PAYROLL_FREQUENCY change in Employment_Info
    cycle_number: current_cycle_number

    Returns:
    True: if the update is successful
    False: if the update Failed

    """
    from tms.paymentcalendar.globalvars import GlobalVars
    key_id = GlobalVars().getkeyid()

    logger = customlogger.basiclogger("update_payFreq_and_related_tables", "DEFAULT")
    logger.info(str(key_id) + ' ::In update_payFreq_and_related_tables::username:: '+username+' ::freq:: '+freq+' \
                    ::first_paydate:: '+str(first_paydate)+' :: freq_type:: '+str(freq_type)+' ::update_table:: '+str(update_table))
    from tms.paymentcalendar import pcfactory
    from utils.db.trandb import TranDB
    from tms.tmsapi.paydatesconfig import ProductParameters
    from config.paymentcalendar.pcconfig import OVERRIDE_VALUE
    cur_date = datetime.datetime.now()
    glob_logger = pcfactory.glob_logger
    product_classification = get_product_classification(loan_id)

    db = TranDB(section='TMS_DATA', logger=glob_logger)
    url = url_settings.URL_PAYDATES
    curs = db.getcursor()
    record_query = "select * from Loan_Info where loan_id = %s and override_flag = 0"
    args = (loan_id)
    record_res = db.processquery(query=record_query, curs=curs, count=1, args=args)
    logger.info(str(key_id)+ ' ::Selecting Records from Loan_Info:: '+str(record_res))
    loan_info = record_res
    repayment_freq_available = loan_info['repayment_frequency']

    # if the frequency type that needs to be updated is PAYROLL_FREQUENCY, first update the table and insert new records
    # into Emplayment_Info
    if freq_type == 'PAYROLL_FREQUENCY' and update_table:
        record_query= "select * from Employment_Info ei join Loan_Latest ll on ll.loan_id = %s\
                        and ll.cust_id = ei.cust_id where ei.override_flag = 0"
        args = (loan_id)
        emp_info = db.processquery(query=record_query, curs=curs,\
                                                  count=1, args=args)
        logger.info(str(key_id)+ ' ::Selecting Records from Employment_Info:: '+str(record_query,args))
        update_query = "update Employment_Info set override_flag = 1, last_updated = %s\
                        where employment_id = %s and override_flag = 0 "
        args = (cur_date,emp_info['employment_id'])
        logger.info(str(key_id)+ ' ::Updating Records of Employment_Info:: '+str(record_query)+str(args))
        db.processquery(query=record_query, curs=curs,args=args, fetch=False)
        insert_query = "insert into Employment_Info ('employer_name,employer_addr,employer_postcode,\
        employer_phone1,employer_phone2,employer_phone3,verified_source1,verified_source2,\
        verified_source3,start_dt,end_dt,job_title,payroll_type,pay_freq,monthly_income,\
        monthly_expense,create_date,last_updated,pay_date,next_paydate,override_flag,cust_id') values\
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # we are not capturing which user has done the change
        args = (emp_info['employer_name'],emp_info['employer_addr'],emp_info['employer_postcode'],\
                        emp_info['employer_phone1'],emp_info['employer_phone2'],emp_info['employer_phone3'],\
                        emp_info['verified_source1'],emp_info['verified_source2'],emp_info['verified_source3'],\
                        emp_info['start_dt'],emp_info['end_dt'],emp_info['job_title'],emp_info['payroll_type'],\
                        freq, emp_info['monthly_income'],emp_info['monthly_expense'],\
                        cur_date,'',first_paydate,\
                        second_paydate or emp_info['next_paydate'],0,emp_info['cust_id'])
        db.processquery(query=record_query, curs=curs,args=args, fetch=False)
        logger.info(str(key_id)+ ' ::Inserting into Employment_Info:: '+str(insert_query)+str(args))

        #if repayment frequency is available and frequency type is PAYROLL_FREQUENCY and not an LOC product, we can
        #quit as we have to just update the Employeemnt_Information.
        if repayment_freq_available and product_classification != 'LOC':  # We should also update Paydates for LOC
            if conn_close:
                db.commit()
                db.close()
            logger.info(str(key_id)+ ' ::commited and Close the connection')
            return True

    # If it is simply a payroll update, do not recompute Paydates, except for LOC. For LOC we need to recompute.
    if not (repayment_freq_available and freq_type == 'PAYROLL_FREQUENCY') or product_classification == 'LOC':
        logger.info(str(key_id)+ ' ::Computing New PayDates:: ')
        repay_freq, first_pd, next_pd = freq, first_paydate, second_paydate  # Values may change based on CAS response
        record_query= "select * from PayDates where loan_id = %s and \
                        override_flag = 0 order by cycle,payment_type desc"
        args = (loan_id)
        record_res = db.processquery(query=record_query, curs=curs,\
                                                      count=0, args=args)
        logger.info(str(key_id)+ ' ::Selecting Records from PayDates:: '+str(record_res))
        pay_dates = dict([(each['cycle'],each) for each in record_res])

        if product_classification == 'LOC':
            pay_dates = []
            statement_dates = []
            for record in record_res:
                if record['payment_type'] == 'LNCYC':
                    pay_dates.append((record['cycle'],record))
                if record['payment_type'] == 'STCYC':
                    statement_dates.append((record['cycle'],record))

            pay_dates = dict(pay_dates)
            statement_dates = dict(statement_dates)

        record_query = "select * from PaymentCalendar where loan_id = %s and override_flag = 0"
        args = (loan_id)
        record_res = db.processquery(query=record_query, curs=curs,\
                                                      count=0, args=args)
        logger.info(str(key_id)+ ' ::Selecting Records from PaymentCalendar:: '+str(record_res))
        payment_calendar = {}
        for each in record_res:
            cur_list = payment_calendar.get(each['payment_nbr'],[])
            cur_list.append(each)
            payment_calendar[each['payment_nbr']] = cur_list

        record_query = "select * from Loan l join Product p on p.product_id = l.product_id \
                                where l.loan_id = %s"
        args = (loan_id)
        record_res = db.processquery(query=record_query, curs=curs,\
                                                      count=1, args=args)
        logger.info(str(key_id)+ ' ::Selecting Records from Loan :: '+str(record_res))
        loan_product = record_res
        lender = CAS_LENDER_MAP[record_res['store_id']]
        statement_breather_period = loan_product['statement_breather_period']
        if ProductParameters.has_key(loan_product['product_id']):
            decemberLogic = ProductParameters[loan_product['product_id']]['decemberLogic']
            holidayLogic = loan_product['holiday_logic']
        else:
            if freq_type == 'REPAYMENT_FREQUENCY':
                decemberLogic=0
                holidayLogic=0
            elif freq_type == 'PAYROLL_FREQUENCY':
                decemberLogic=1
                holidayLogic=-1
        logger.info(str(key_id)+ " ::decemberLogic = '%s' and holidayLogic = '%s':: "%\
                                                            (str(decemberLogic),str(holidayLogic)))
        loc_future_date_count = 0  # Count of future Statement Dates already present in PayDates table

        if product_classification == 'LOC':
            paydt_rec = PayDates.objects.filter(loan=loan_id, override_flag=0, payment_type='STCYC',
                                                    paydate__gte=datetime.date.today()).order_by('cycle')
            loc_future_date_count = paydt_rec.count()
            current_cycle = paydt_rec[0].cycle
            max_cycle_no = paydt_rec.reverse()[0].cycle

        if payment_calendar.keys():
            isLoanActive = 1
            if product_classification != 'LOC':
                current_cycle = max(payment_calendar.keys())
        else:
            isLoanActive = 0
            current_cycle = 0

        if product_classification == 'LOC':
            total_cycles = loc_future_date_count  # Request for as many future cycles as present already
        else:
            total_cycles = loan_product['interest_only_cycles'] + loan_product['paydown_cycles']
        if not fr_flag:
            chk_date = cur_date.date()
        else:
            chk_date = fr_date
        is_cur_cycle_future = False
        if isLoanActive:
            current_cycle_paydate = pay_dates[current_cycle]['paydate']
            if chk_date < current_cycle_paydate:
                is_cur_cycle_future = True
            elif chk_date >= current_cycle_paydate:
                is_cur_cycle_future = False
        else:
            is_cur_cycle_future = True

        grace_period = {'monthly':8, 'weekly':3}[loan_product['repayment_frequency']]
        if isLoanActive:
            grace_period = loan_product['breather_time']

            if is_cur_cycle_future:
                if not fr_flag:
                    if current_cycle==1:
                        payoutDate = loan_info['fund_dt']
                    else:
                        payoutDate =  pay_dates[current_cycle-1]['paydate']
                else:
                    payoutDate = cur_date.date()

#                 if product_classification == 'LOC':
#                     payoutDate = payoutDate + datetime.timedelta(days=statement_breather_period+1)

                second_paydate = second_paydate.strftime("%d/%m/%Y") if second_paydate else ''

                first_paydate = first_paydate.strftime("%d/%m/%Y") if first_paydate else ''
                logger.info(str(key_id)+ ' :: Going to Call paydate_calc')
                new_paydates, repay_freq = paydate_calc(loan_id = loan_id,url_main = url,lender = lender,product_id = loan_product['product_id'],\
                                            freq = freq,first_paydate = first_paydate,second_paydate = second_paydate,\
                                            payoutDate = payoutDate,borrowed_amt = loan_info['borrowed_amt'],total_cycles = total_cycles,\
                                            current_cycle = current_cycle,grace_period = grace_period,\
                                            holidayFlag =  holidayLogic,decemberLogic = decemberLogic,add_cyc = 4,logger = cas_logger)
                logger.info(str(key_id)+ ' :: Returned from paydate_calc')
                if not new_paydates:
                    return False
                # for counter in range(0,len(new_paydates)):
                #     if chk_date < new_paydates[counter]:
                #         break
                # new_paydates = new_paydates[counter:]
            else:
                if fr_flag:
                    payoutDate = cur_date.date()
                else:
                    payoutDate = pay_dates[current_cycle]['paydate']

#                 if product_classification == 'LOC':
#                     payoutDate = payoutDate + datetime.timedelta(days=statement_breather_period+1)

                second_paydate = second_paydate.strftime("%d/%m/%Y") if second_paydate else ''

                first_paydate = first_paydate.strftime("%d/%m/%Y") if first_paydate else ''

                logger.info(str(key_id)+ ' :: Going to Call paydate_calc')
                new_paydates, repay_freq = paydate_calc(loan_id = loan_id,url_main = url,lender = lender,product_id = loan_product['product_id'],\
                                            freq = freq,first_paydate = first_paydate,second_paydate = second_paydate,\
                                            payoutDate = payoutDate,borrowed_amt = loan_info['borrowed_amt'],total_cycles = total_cycles,\
                                            current_cycle = current_cycle,grace_period = grace_period,\
                                            holidayFlag =  holidayLogic,decemberLogic = decemberLogic,add_cyc = 4,logger = cas_logger)
                logger.info(str(key_id)+ ' :: Returned from paydate_calc')
                if not new_paydates:
                    return False
                # for counter in range(0,len(new_paydates)):
                #     if chk_date < new_paydates[counter]:
                #         break
                # new_paydates = new_paydates[counter:]
        else:
            
            if loan_info['fund_dt'] in  (None,'NULL'):
                payoutDate=datetime.datetime.now()
                x=1
            else:
                payoutDate=loan_info['fund_dt']
                x=0
            grace_period = loan_product['breather_time']

            second_paydate = second_paydate.strftime("%d/%m/%Y") if second_paydate else ''

            first_paydate = first_paydate.strftime("%d/%m/%Y") if first_paydate else ''

            logger.info(str(key_id)+ ' :: Going to Call paydate_calc')
            total_cycles=1+x
            new_paydates, repay_freq = paydate_calc(loan_id = loan_id,url_main = url,lender = lender,product_id = loan_product['product_id'],\
                                            freq = freq,first_paydate = first_paydate,second_paydate = second_paydate,\
                                            payoutDate = payoutDate,borrowed_amt = loan_info['borrowed_amt'],total_cycles = total_cycles,\
                                            current_cycle = current_cycle,grace_period = grace_period,\
                                            holidayFlag =  holidayLogic,decemberLogic = decemberLogic,add_cyc = 2,logger = cas_logger)
            logger.info(str(key_id)+ ' :: Returned from paydate_calc')

        #updating paydates

        #which cycles has to be updates
        # if loan is not active we have to update from 1st PayDate here isLoanActive will be 0

        # if loan is active if the current PC cycle is future here isLoanActive=1 and
        # is_cur_cycle_future=True then update from current cycle (max of PaymentCalendar Cycles)

        # if loan is active if the current PC cycle paydate is crossed here isLoanActive=1 and
        # is_cur_cycle_future=False then update from current cycle+1 =(max of PaymentCalendar Cycles)+1
        logger.info(str(key_id)+ " ::New Paydates raw list = '%s':: "%(str(new_paydates)))
        if not new_paydates:
            return False
        cycle_to_consider_from = 1
        if isLoanActive:
            if product_classification == 'LOC':
                cycle_to_consider_from = current_cycle
            else:
                if is_cur_cycle_future:
                    cycle_to_consider_from = current_cycle
                else:
                    cycle_to_consider_from = current_cycle + 1
        update_paydates = {}
        update_statement_dates = {}
        var = 0
        if product_classification == 'LOC':
            update_payments_table,  update_suppress_till_date = False, False
            payments_rec = Payments.objects.filter(loan=loan_id)[0]  # Used to update Payments in case of PH/CF
            first_pd, next_pd = new_paydates[1], new_paydates[3]  # Used to update Loan_Info
            for cyc in range(cycle_to_consider_from, max_cycle_no+1):
                if (new_paydates[var] - datetime.date.today()).days <= 0 or (var >= 2 and new_paydates[var] < pay_dates[cyc-1]['paydate']):
                    #  If the newly generated statement date is in the past, skip updating this cycle. Keep old dates or
                    #  If the second statement date is before the first due date. Then also skip update
                    update_paydates[cyc] = pay_dates[cyc]['paydate']
                    update_statement_dates[cyc] = statement_dates[cyc]['paydate']
                    var += 2
                    continue
                # Check if pay-date to be changed is used as a reference in Payments table fields
                if payments_rec.arrangement_type in (1, 3):
                    if payments_rec.delin_suppress_tilldate == pay_dates[cyc]['paydate']:
                        update_payments_table = True
                        old_pay_date = pay_dates[cyc]['paydate']
                        date_to_be_updated = new_paydates[var+1]

                    if payments_rec.suppress_till_date == pay_dates[cyc]['paydate'] - datetime.timedelta(days=1):
                        update_suppress_till_date = True
                        old_suppress_date = pay_dates[cyc]['paydate']
                        new_suppress_date = new_paydates[var+1]

                if pay_dates[cyc]['paydate'] != new_paydates[var+1]:
                    update_paydates[cyc] = new_paydates[var+1]
                    update_statement_dates[cyc] = new_paydates[var]
                else:
                    if fr_flag:
                        logger.info(str(key_id)+ ' :: Going to Computegenerateby')
                        generated_by = computegeneratedby(loan_id,0,1,0,cyc)
                        logger.info(str(key_id)+ ' :: Returned from Computegenerateby')
                    else:
                        logger.info(str(key_id)+ ' :: Going to Computegenerateby')
                        generated_by = computegeneratedby(loan_id,0,0,1,cyc)
                        logger.info(str(key_id)+ ' :: Returned from Computegenerateby')
                    if generated_by:
                        logger.info(str(key_id)+ ' :: Going to update_generateby')
                        update_generatedby(loan_id,cyc,generated_by = generated_by,con_trandb=db)
                        logger.info(str(key_id)+ ' :: Returned from update_generateby')
                var += 2
            # Separate calls for waterfall_suppress and delinq_suppress since one can be independent of the other
            if update_payments_table:
                logger.info(str(key_id) + " :: Going to update_paydate_in_payments_table for new paydates")
                update_paydate_in_payments_table(loan_id, old_pay_date,
                                                 date_to_be_updated,
                                                 payments_rec, username, reason=' PAYDATE CHANGED')
                update_future_waiver_date(loan_id, old_pay_date-datetime.timedelta(days=statement_breather_period),
                                          date_to_be_updated-datetime.timedelta(days=statement_breather_period),
                                          username)
            #  if old_suppress_date == old_pay_date, waterfall & delinq suppress is for the same paydate. So we can skip
            if update_suppress_till_date and old_suppress_date != old_pay_date:
                logger.info(str(key_id) + " :: Going to update_paydate_in_payments_table for new waterfall date")
                update_paydate_in_payments_table(loan_id, old_suppress_date,
                                                 new_suppress_date,
                                                 payments_rec, username, reason=' PAYDATE CHANGED')

            import threading  # Post to RTI in a seperate thread
            cust_id_sql = "select account_cust_id from Loan_Latest where loan_id=%s"
            cust_id = db.processquery(cust_id_sql, curs, 1, loan_id)['account_cust_id']
            statement_date_list = [{'loan_id': loan_id, 'account_cust_id': cust_id,
                                    cycle_to_consider_from: new_paydates[0], cycle_to_consider_from+1: new_paydates[2]}]
            logger.info(str(key_id) + " :: RTI Theread Call :: LOC_sendStatementsToUE RTI :: %s" % statement_date_list)
            rti_thread = threading.Thread(target=LOC_sendStatementsToUE, args=(statement_date_list, ))
            rti_thread.start()
        else:
            first_pd, next_pd = new_paydates[0], new_paydates[1]
            for cyc in range(cycle_to_consider_from,total_cycles+1):

                if pay_dates[cyc]['paydate'] != new_paydates[var]:
                    update_paydates[cyc] = new_paydates[var]
                else:
                    if fr_flag:
                        logger.info(str(key_id)+ ' :: Going to Computegenerateby')
                        generated_by = computegeneratedby(loan_id,0,1,0,cyc)
                        logger.info(str(key_id)+ ' :: Returned from Computegenerateby')
                    else:
                        logger.info(str(key_id)+ ' :: Going to Computegenerateby')
                        generated_by = computegeneratedby(loan_id,0,0,1,cyc)
                        logger.info(str(key_id)+ ' :: Returned from Computegenerateby')
                    if generated_by:
                        logger.info(str(key_id)+ ' :: Going to update_generateby')
                        update_generatedby(loan_id,cyc,generated_by = generated_by,con_trandb=db)
                        logger.info(str(key_id)+ ' :: Returned from update_generateby')
                var+=1
        logger.info(str(key_id)+ " ::Paydates to be updated dictionary = '%s':: "%\
                                                            (str(update_paydates)))
        logger.info(str(key_id)+ " ::Statement dates to be updated dictionary = '%s':: "%\
                                                            (str(update_statement_dates)))

        first_pdt = datetime.datetime.strptime(first_paydate, "%d/%m/%Y") if first_paydate else None
        second_pdt = datetime.datetime.strptime(second_paydate, "%d/%m/%Y") if second_paydate else None
        logger.info(str(key_id)+ " ::Loan Info being updated with values:: repay_freq:: %s\tfirst_pd:: %s\t"
                                 "next_pd:: %s" % (repay_freq, first_pdt, second_pdt))
        update_query = "update Loan_Info set override_flag = 1, last_updated_on = %s \
                        where loan_info_id = %s"
        args = (cur_date.strftime('%Y-%m-%d %H:%M:%S' ), loan_info['loan_info_id'])
        logger.info(str(key_id)+ ' ::Updating Records of Loan_Info:: '+str(update_query)+str(args))
        db.processquery(query=update_query, curs=curs,args=args, fetch=False)
        insert_query = "insert into Loan_Info (request_amt,approved_amt,borrowed_amt,funded_amt,loc_limit,\
                    EMI_amt,request_dt,approved_dt,funding_method,booked_dt,fund_dt,commencement_dt,\
                    dp_esign_dt,fund_to,cb_fund_to,APR,relevant_dt,now_dt,wd_proposed_on,loan_esign_dt,\
                    pco_dt,downpayment_amt,creditcheck_amt,repayment_frequency,repayment_dt,next_repayment_dt,selling_price,\
                    noc_req_on,create_dt,done_by,override_flag,last_updated_on,loan_id,nosia_sent_on) values \
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args = (loan_info['request_amt'],loan_info['approved_amt'],loan_info['borrowed_amt'],\
                        loan_info['funded_amt'],loan_info['loc_limit'],loan_info['EMI_amt'],loan_info['request_dt'],\
                        loan_info['approved_dt'],loan_info['funding_method'],loan_info['booked_dt'],\
                        loan_info['fund_dt'],loan_info['commencement_dt'],loan_info['dp_esign_dt'],\
                        loan_info['fund_to'],loan_info['cb_fund_to'],loan_info['APR'],loan_info['relevant_dt'],\
                        loan_info['now_dt'],loan_info['wd_proposed_on'],loan_info['loan_esign_dt'],\
                        loan_info['pco_dt'],loan_info['downpayment_amt'],loan_info['creditcheck_amt'],\
                        repay_freq, first_pdt, second_pdt,loan_info['selling_price'],loan_info['noc_req_on'],\
                        cur_date.strftime('%Y-%m-%d %H:%M:%S' ),username,0 ,None,loan_info['loan_id'],loan_info['nosia_sent_on'])
        db.processquery(query=insert_query, curs=curs,args=args, fetch=False, returnprikey=1)
        logger.info(str(key_id)+ ' ::Inserting into Loan_Info:: '+str(insert_query)+str(args))

        if freq_type == 'REPAYMENT_FREQUENCY':
            override_reason = OVERRIDE_VALUE['rpfc']
        elif freq_type == 'PAYROLL_FREQUENCY':
            override_reason = OVERRIDE_VALUE['pfc']
        if fr_flag:
            generated_by = 2
        else:
            generated_by = 4

        for cyc in update_paydates:
            cur_rec = pay_dates[cyc]
            update_query = "update PayDates set override_flag = 1, override_reason = %s,reason=%s,\
                     modified_dt =%s, modified_by = %s       where paydates_id = %s"
            args = (override_reason,reason, cur_date,username, cur_rec['paydates_id'])
            logger.info(str(key_id)+ ' ::Updating PayDates :: '+str(update_query)+str(args))
            db.processquery(query=update_query, curs=curs,args=args, fetch=False)
            insert_query = 'insert into PayDates (paydate, cycle, override_flag, \
                        override_reason, create_dt,payment_type,\
                        modified_by, loan_id,generated_by) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            args = (update_paydates[cyc],cur_rec['cycle'],0,'',cur_date,cur_rec['payment_type'],\
                                                                            '',cur_rec['loan_id'],generated_by)
            db.processquery(query=insert_query, curs=curs,args=args, fetch=False)
            logger.info(str(key_id)+ ' ::Inserting into PayDates :: '+str(insert_query)+str(args))

        # Updating new statement days
        for cyc in update_statement_dates:
            cur_rec = statement_dates[cyc]
            update_query = "update PayDates set override_flag = 1, override_reason = %s,reason=%s,\
                     modified_dt =%s, modified_by = %s       where paydates_id = %s"
            args = (override_reason,reason, cur_date,username, cur_rec['paydates_id'])
            logger.info(str(key_id)+ ' ::Updating PayDates :: '+str(update_query)+str(args))
            db.processquery(query=update_query, curs=curs,args=args, fetch=False)
            insert_query = 'insert into PayDates (paydate, cycle, override_flag, \
                        override_reason, create_dt,payment_type,\
                        modified_by, loan_id,generated_by) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            args = (update_statement_dates[cyc],cur_rec['cycle'],0,'',cur_date,cur_rec['payment_type'],\
                                                                            '',cur_rec['loan_id'],generated_by)
            db.processquery(query=insert_query, curs=curs,args=args, fetch=False)
            logger.info(str(key_id)+ ' ::Inserting into PayDates :: '+str(insert_query)+str(args))

        if update_paydates and reason:
            case_id=get_case_id_by_entity_id(loan_id,'LOAN')
            log_id=get_logid_by_caseid(case_id)
            add_gcm_notes(log_id["log_id"],"PAYDATE CHANGE",reason,username,cur_date,db)
            logger.info(str(key_id)+ ' ::Inserted into gcm_notes')
        #updating PaymentCalendar
        #read above comments for paydates change
        #this shd happen only when isLoanActive=1 and is_cur_cycle_future=True
        if isLoanActive and is_cur_cycle_future and current_cycle in update_paydates:
            logger.info(str(key_id)+ " ::PaymentCalendar records editing for cycle=%s:: "%\
                                                            (str(current_cycle)))
            pc_obj = pcfactory.getpcobj()

            for rec in payment_calendar[current_cycle]:
                if product_classification == 'LOC':
                    pri_key = pc_obj.manualeditrecord(rec['payment_id'],loan_id,update_paydates[cycle_to_consider_from].strftime('%Y-%m-%d'),\
                                                                        current_cycle,rec['payment_amt'],rec['payment_type'],username, \
                                                                        reason = override_reason, returnprikey=1)
                else:
                    pri_key = pc_obj.manualeditrecord(rec['payment_id'],loan_id,new_paydates[0].strftime('%Y-%m-%d'),\
                                                                        current_cycle,rec['payment_amt'],rec['payment_type'],username, \
                                                                        reason = override_reason, returnprikey=1)
                logger.info(str(key_id)+ ' ::Returned from manualeditrecord')
        if not fr_flag:
            if conn_close:
                db.commit()
                db.close()
        logger.info(str(key_id)+ " ::Committed changes for the pay_frequency change ::")
        ## for daily_run phase 2: whenever there is a transaction, paydates change, status change
        #loan_id shd be flagged in DeltaMatrix table
        daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
        if update_paydates and isDailyRunStarted(date_of_run=daily_run_date):
            updateDeltaMatrix(loan_id,'paydates')
        if not fr_flag:
            return True
        else:
            return cycle_to_consider_from, False
    return
        
def payment_schedule_with_accounting(loan_id,schedule_req ='Schedule1'):
        """

        """
        max_cycle_number=0
        currDate=datetime.datetime.now()

        conn = TranDB(section="TMS_DATA")
        cur = conn.getcursor()

        from tms.tmsapi import loan
        from tms.tmsapi import paydates
        from tms.pullengine.paymentschedulegenerator import PaymentScheduleGenerator

        loan_obj = loan.Loan(loan_id)
        paydates_obj = paydates.PayDates(loan_obj)
        due_dates_dict = paydates_obj.generate_due_dates()

        psg_obj=paymentschedulegenerator.PaymentScheduleGenerator(loan_obj,due_dates_dict,conn_close = 0)
        last_id,last_cycle,last_amt,last_paid_amt = psg_obj.get_last_transaction()
        payment_schedules = paymentschedulegenerator.generate_paymentschedule(loan_id,minusAccountedFuturePrincipal=1,
                            adjustAccountedPrincipal=1,temp_flag = True, conn_close_flag = 0)


        full_schedule = payment_schedules[schedule_req]
        schedule = dict([[cycle_key,full_schedule[cycle_key]] for cycle_key in full_schedule if cycle_key <= last_cycle])
        for cycle in schedule:
            for i in range(len(schedule[cycle])):
                if schedule[cycle][i][3]==LSS_DICT["DEFLTFEE"]:
                    if schedule[cycle][0][3]== LSS_DICT["ARRFEE"]:
                        schedule[cycle].insert(1,schedule[cycle][i])
                        schedule[cycle].pop(i+1)
                    else:
                        schedule[cycle].insert(0,schedule[cycle][i])
                        schedule[cycle].pop(i+1)
                elif schedule[cycle][i][3]==LSS_DICT["ARRFEE"]:
                    schedule[cycle].insert(0,schedule[cycle][i])
                    schedule[cycle].pop(i+1)

        #     Step : Logic here for Accounting  paid amount in  FIP order money for NEW dictionary.
        totalPaid = getPaidAmt(loan_id,currDate)
        amount = Money(totalPaid,2)

        #Making paid_amt column to zero.
        if amount > 0:
            for key,items in schedule.iteritems():
                for k in range(len(items)):
                            items[k] = list(items[k])
                            items[k][4] = Decimal(0.00)
        
        for key,items in schedule.iteritems():
                    due = 0
                    remain = amount
                    for k in range(len(items)):
                        items[k] = list(items[k])
                        items[k][4] = Decimal(0.00)
                        due = due + Money(items[k][2],2)
                        payment=Money(items[k][2],2)
                        if amount>=payment:
                            items[k][4]=payment
                            amount=amount-payment
                        else:
                            items[k][4]=amount
                            amount = 0
                            break
                    if(remain>=due):
                        max_cycle_number = key
                    else:
                        break

        schedule_without_future=deepcopy(schedule)
        psg_obj.eopb =psg_obj.get_expected_opb(cycle_due_will_be_paid=1)
        status_cd=get_loan_status_by_loan_id(loan_id)
        if status_cd not in ("DEBT MANAGEMENT", "TEMPORARY ARRANGEMENT"):
            future_entries =psg_obj.generate_future_transactions(last_cycle,minus_unaccounted_principal=1,flag=1)
            for cyc in future_entries:
                schedule[cyc] = future_entries[cyc]
        for cyc in schedule:
            schedule[cyc] = sorted(schedule[cyc], key = itemgetter(1))

        conn.close()

        return {'schedule_with_future':schedule,'schedule_without_future':schedule_without_future,'max_cycle_number':max_cycle_number}


def transfer_money(request):
    """
    This Function is used for Transferring the amount from one loan id to another of the same customer.
    """
    #conn = TranDB(section="TMS_DATA")
    msg = ""
    flag=0
    cur_date=datetime.date.today()
    cur_time=datetime.datetime.now()
    username = request.session['username']

    if request.method == "GET":

        fromloan_id = request.GET['loan_id']

    if request.method=="POST":
        fromloan_id = request.POST['loan_id']
        toloan_id = request.POST['to_loan_id']
        loan_info=Loan_Info.objects.filter(loan=toloan_id,override_flag=0)
        to_cust = get_store_cust_id_from_loan_id(toloan_id)
        if to_cust:
            if get_store_cust_id_from_loan_id(fromloan_id)==to_cust:

                transfer_amount = Money(request.POST['transfer_amount'],2)
                amt_paid = getPaidAmt(fromloan_id,cur_date,0)
                if transfer_amount<=amt_paid:
                    ob_toloanid=get_amount_dtls(toloan_id)
                    conn = TranDB(section="GCMS_DATA")
                    cur = conn.getcursor()
                    sql_status="select status_cd from gcm_case where entity_id=%s and entity_type='LOAN'"%(toloan_id)
                    get_status=conn.processquery(query=sql_status, curs=cur ,fetch=True, count=1)
                    conn.close()
                    if loan_info[0].funded_amt != None:

                        if ob_toloanid!=0 and get_status['status_cd'] not in ('PRECLOSED','CLOSED','POSTCLOSED','WITHDRAWN'):

                            if transfer_amount <= ob_toloanid:
                                pcfunc.refund(loan_id=fromloan_id,reference_id=None,tran_dt=cur_time,debit=0,credit=transfer_amount,payment_method="TRANSFER CREDIT",merchant_txn_id=None,merchant_name=None,user=username,date_elem=cur_time,paymentType=loanstatusconfig.PAYMENTTYPE["NORMALREFUND"])
                                pcfunc.recvmoney(loan_id=toloan_id,reference_id=None,tran_dt=cur_time,debit=transfer_amount,credit=0,payment_method="TRANSFER DEBIT",merchant_txn_id=None,merchant_name=None,user=username,date_elem=cur_time,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"])
                                msg1 = "Successfully Transferred the amount of %s GBP to  Loan id: %s"%(transfer_amount, toloan_id)
                                flag=1
                                return render_to_response('custdetail/transfer_money.html',{'loan_id':fromloan_id, "msg1":msg1,'flag':flag})
                            else:
                                msg = "The Transfer amount seems to be greater than the required OB and you can Transfer upto %s GBP"%(ob_toloanid)

                        else:
                            msg = "The Account of the \'To Loan Id\' has been closed!!!"
                            return render_to_response('custdetail/transfer_money.html',{'loan_id':fromloan_id, "msg":msg,'flag':flag})
                    else:
                        msg="There has been no amount funded in the \'To Loan Id\'"

                else:
                    msg = "The Transfer amount is greater than the Paid amount of the \'From Loan Id\'"

                return render_to_response('custdetail/transfer_money.html',{'loan_id':fromloan_id, "msg":msg,'flag':flag})

            else:
                msg = "\'To Loan Id\' doesnt belong to the same customer"

        else:
            msg = "Invalid \'To Loan Id\'"

    return render_to_response('custdetail/transfer_money.html',{'loan_id':fromloan_id, "msg":msg,'flag':flag})

def factory(indv_flag,date = None,loan_id = None,reason=None):
    from tms.paymentcalendar.apis import unfreeze
    freeze_result = unfreeze(indv_flag,date,loan_id,reason)
    return freeze_result

def SOAC_Format_display_Schedule(schedule, last_cycle, borrowed_amt, arr_amt, loan_id):
    '''
    Used to obtain the schedule in SOAC format.
    Removes the Extra Prepayment Paid by Customer from schedule and adds the same 
    to a seperate list which is displayed as a seperate entity in Actual Schedule of TMS UI.
    @arr_amt: total arrears at any given point of time
    '''
    xpp=[]
    sumx=Decimal(0)
    tI=[]
    tP=[]
    schedule_without_epp = {}
    epp_only_schedule = []
    bal_infm = {}
    # bal_infm['OutstandingPrincipal'] = borrowed_amt
    # bal_infm['OutstandingInterest'] = Decimal(0)
    # bal_infm['OutstandingFee'] = 0
    # bal_infm['OB']=0
    # bal_infm['OA']=arr_amt
    
    for j in schedule:
        for i in schedule[j]:
            if j==last_cycle :
                if i[3]=='Extra Prepayment':
                    sumx=sumx+i[2]-i[4]
                elif i[3]=='Interest Capitalized':
                    tI.append([i[2],i[4]])
                elif i[3]=='Principal Due':
                    tP.append([i[2],i[4]])
            if i[3]=='Extra Prepayment':
                if j<=last_cycle:
                    xpp.append(i)
    if tP:
        if tP[0][1] > sumx:
            tP[0][1] -= sumx
            sumx = Decimal(0)
        else:
            sumx -= tP[0][1]
            tP[0][1] = Decimal(0.00)
    if tI:
        if tI[0][1] > sumx:
            tI[0][1] -= sumx
            sumx = Decimal(0)
        else:
            sumx -= tI[0][1]
            tI[0][1] = Decimal(0.00)
    if last_cycle in schedule:
        for i in schedule[last_cycle]:
            if  i[3]=='Interest Capitalized':
                i[4]=tI[0][1]
            elif i[3]=='Principal Due':
                i[4]=tP[0][1]
            elif i[3]=='Extra Prepayment':
                i[4]=i[2]
    
    for cycle,j in schedule.iteritems():
        for rec in j:
            if rec[3]=='Extra Prepayment':
                epp_record = [cycle, rec[5].date(), rec[2], rec[3], rec[4]]
                epp_only_schedule.append(epp_record)
            else:
                if cycle in schedule_without_epp:
                    schedule_without_epp[cycle].extend([rec])
                else:
                    schedule_without_epp[cycle] = [rec]
            # if cycle <= last_cycle:
            #     if rec[3].strip()[-4:] in ('ized','rest'):
            #         bal_infm['OutstandingInterest']+=rec[2]-rec[4]
            #     if rec[3].strip()[-4:] in ('Fees'):
            #         bal_infm['OutstandingFee']+=rec[2]-rec[4]
            #     if rec[3].strip()[-4:] in (' Due', 'ment', 'ance'):
            #         bal_infm['OutstandingPrincipal']-=rec[4]
    # OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
    # bal_infm['OB']=OB

    balance_details = get_balance_dtls(loan_id)[0]
    bal_infm['OutstandingPrincipal'] = balance_details['OutstandingPrincipal']
    bal_infm['OutstandingInterest'] = balance_details['OutstandingInterest']
    bal_infm['OutstandingFee'] = balance_details['OutstandingFee']
    bal_infm['OB']= balance_details['OutstandingPrincipal']+balance_details['OutstandingInterest']+ balance_details['OutstandingFee']
    bal_infm['OA']=arr_amt

    return schedule_without_epp, epp_only_schedule, bal_infm 

def common_schedule_converter(LoanSchedule,sort_key):
    """
    @param LoanSchedule: {cycle_no:[[payment_id, payment_dt, payment_amt, payment_type, paid_amt, create_dt],...}
    Returns schedule for display in TMS UI-Show Schedule
    Calculates the OPB, OI, OF, OB for the given loan and returns the same.
    """
    schedule = {}
    datelist1 = []
    sorted_sch = []
    new_sorted_sch = []
    list_of_records = []
    ScheduleAccounting = {}
    for cycle_key,cycle_rec in LoanSchedule.iteritems():
        for rec in cycle_rec:
            tmp_list1 = [cycle_key]
            tmp_list1.extend(rec)
            list_of_records.append(tmp_list1)            
    
    """ Sorting of schedule is done, based on date or cycle. """
    index_dict = {'cycle_sort':0,'date_sort':2}
    index = index_dict[sort_key]
    for record in list_of_records:
        if sorted_sch and sorted_sch[-1] and sorted_sch[-1][-1][index]==record[index]:
            sorted_sch[-1].append(record)
        else:
            sorted_sch.append([record])
    for sorted_group in sorted_sch:
            x = Decimal(0.00)
            y = Decimal(0.00)
            for record in sorted_group:
                x+= record[3]
                y+= record[5]
            ScheduleAccounting[record[index]] = (x,y)
    if index == 2:
        for dategroup in sorted_sch:
            datelist1.append(dategroup[0][2])
        datelist1.sort()
        for date in datelist1:
            for group in sorted_sch:
                if date == group[0][2]:
                    new_sorted_sch.append(group)
        sorted_sch = new_sorted_sch
    schedule['Schedule1'] = sorted_sch
    
    return schedule, ScheduleAccounting

def Generate_Schedule_Request(request):
    """
    This renders iframe for Payment schedule using Show Schedule button in TMS UI, where pay dates & payment information \
    can be viewed for any loan.
    """
    type_of_schedule ='Actual_Schedule'
    index = 0
    Schedule2accounting={}
    sort_key = "cycle_sort"
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
        type_of_schedule = request.POST['type_of_schedule']
        if request.method == "POST" and 'date_sort' in request.POST:
            sort_key = "date_sort"
        else:
            sort_key = 'cycle_sort'
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')
    try:
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
            
        sch_logger.info("Calling SCHEDULE MODULE for loan_id : "+str(loan_id)+"\n")
        #Creating object for the schedule loan
        sch_Obj1= schedule_for_loan.Schedule(loan_id)

        sql = "select product_classification,status_cd from Product pd join Loan_Latest ll\
             on ll.product_id=pd.product_id  JOIN GCMS_Data.gcm_case gc on \
             ll.loan_id=gc.entity_id where ll.loan_id=%s and gc.entity_type='loan'"%(loan_id)
        
        result = con.get_one_result(sql)
        if result and result['product_classification'] == 'LOC':
            prodClassification = result['product_classification']
            schedule=sch_Obj1.LOC_actualSchedule()
            scheduletemp = None
            if result['status_cd'] == 'TEMPORARY ARRANGEMENT':
                scheduletemp = sch_Obj1.TAschedule()
            Schedule, xpp, bal_infm = SOAC_Format_display_Schedule(schedule, sch_Obj1.last_cycle, sch_Obj1.borrowed_amt,
                                                               sch_Obj1.arrears, loan_id)
            schedule, Schedule1accounting = common_schedule_converter(Schedule, sort_key)
            logger.info("Inside LOC Prodcut")
            return render_to_response("custdetail/schedule_generator.html",{"loan_id":loan_id,"schedule":schedule,
                                "flag":0,"Schedule1accounting":Schedule1accounting,"scheduletemp":scheduletemp,
                                "Schedule2accounting":Schedule2accounting,"index":index,"result":bal_infm,'xpp':xpp,
                                'type_of_schedule':type_of_schedule,'productClassification':prodClassification})
            
            
        else:
            prodClassification = None    
            schedule=sch_Obj1.actualSchedule_without_temp()
            scheduletemp = sch_Obj1.TAschedule()
            Schedule, xpp, bal_infm = SOAC_Format_display_Schedule(schedule, sch_Obj1.last_cycle, sch_Obj1.borrowed_amt,
                                                                   sch_Obj1.arrears, loan_id)
            schedule, Schedule1accounting = common_schedule_converter(Schedule, sort_key)
            ueschedule = sch_Obj1.ueSchedule()
            tmsschedule = sch_Obj1.tmsSchedule()
            logger.info("Inside Daily Interest Prodcut")
            logger.info("Logging UE Schedule :: "+str(ueschedule))
            logger.info("Logging TMS Schedule :: "+str(tmsschedule))
            futureprepayment = sch_Obj1.futurePrepaymentsSchedule()
        
        #Closing the connection which we created above
        sch_Obj1.close_con()
    except Exception,e:
        sch_logger.error("Exception received while FETCHING SCHEDULE for loan_id : "+str(loan_id)+ "\n"+str(traceback.format_exc())+str(e))
        
    
    return render_to_response("custdetail/schedule_generator.html",{"loan_id":loan_id,"schedule":schedule,
                                "flag":0,"Schedule1accounting":Schedule1accounting,"scheduletemp":scheduletemp,
                                "Schedule2accounting":Schedule2accounting,"index":index,"result":bal_infm,'xpp':xpp,
                                'type_of_schedule':type_of_schedule,'ueschedule':ueschedule,'tmsschedule':tmsschedule,
                                'futureprepayment':futureprepayment,'productClassification':prodClassification})

def view_recoveries_history(request):
    """
    This renders popup to view all the Debt collection agency for the loan.
    """

    if request.method=="GET":
        loan_id=request.GET["loan_id"]

    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    coll_obj = Collection_Info.objects.filter(loan=loan_id).order_by('start_dt')
    for i in range(0,len(coll_obj)):
        coll_obj[i].dca_name=collection_config.DCA_NAMEDICT[coll_obj[i].dca_name]
    return render_to_response("custdetail/view_recoveries_history.html",{"loan_id":loan_id,"coll_obj":coll_obj})
view_recoveries_history = maintenance_deco_popups(view_recoveries_history)

def make_card_valid(request):
    result_set = {}
    reason = ''
    update_loan_id = ''
    flag = 1
    if request.method=="GET":
        loan_id=request.GET["loan_id"]
    elif request.method=="POST":
        loan_id=request.POST["loan_id"]
        reason = request.POST["selReason"]
        update_loan_id = request.POST["data"]
        flag = 0
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    make_valid_data,  list_of_reasons, alert_flag = dbtmsapi.invalid_card_data(loan_id, flag, reason, update_loan_id, card_logger)
    if make_valid_data:
        result_set['data'] = make_valid_data

    return render_to_response("custdetail/make_valid_card.html",{"loan_id":loan_id, "data" : result_set, "ReasonList" : list_of_reasons, "alert" : alert_flag})

    ''' Even the below can be used if the return function of the above has been changed'''
    #card_data = {}
    #card_data = dbtmsapi.invalid_card_data(loan_id)
@login_required
def charge_bck_csv_upload(request):

    username = request.session['username']
    menu = request.session['sessionmenu']
    exists_flag = 0
    data_value = {}
    loan_id = None
    error_flag = 0
    error_dict = {}
    cur_date = datetime.datetime.now()
    ChargeBackType = ['New ChargeBack List','Success Defended File','Not Defended File']
    validFileFormat = 'text/csv'
    header_format = queueconfig.CB_CODES['CSV_HEADER_VIEWS']
    vaidDateFormat = (cur_date.date()).strftime('%Y-%m-%d')
    
    if request.method=="GET":
        loan_id = None
    elif request.method == "POST":
        try:
            if 'datafile' in request.FILES:
                timelist = ctime().split()
    #            defence_opt = request.POST["selReason"]
                file = request.FILES['datafile']
                path = '%s/%s/%s/%s/%s' % (MEDIA_ROOT_CSV, timelist[4],timelist[1],timelist[2],file)
                f_read = os.path.isfile(path)
                if not f_read:
                    file = request.FILES['datafile']
                    externalarrange_logger.info(str(file.content_type)+ ' ::CHARGEBACK FILE FORMAT ::')
                    if not file.content_type == validFileFormat:
                        pass
                        #raise Exception, 'Invalid File!'
                    if file.size == 0:
                        raise ValueError("File is empty")

                    os.system("mkdir -p '%s/%s/%s/%s'" % (MEDIA_ROOT_CSV,timelist[4],timelist[1],timelist[2]) )
                    destination = open('%s/%s/%s/%s/%s' % (MEDIA_ROOT_CSV, timelist[4],timelist[1],timelist[2],file), 'wb')

    #                write the LOGIC to put data from uploaded CSV to in the mentioned path
                    for chunk in request.FILES['datafile'].chunks():
                        destination.write(chunk)
                        destination.close()
                    try:
                        suc_res, err_res, msg = chargeBackCSVUpload.file_receiver_from_UI(path, username, create_dt = cur_date)#Calling chargeBackRefundUpdate in zebitAPI
                    except Exception,e:
                        error_dict = {"error_flag":1,"msg":str(e)}

                    data_value = {"success":suc_res, "error":err_res}

                    if msg:
                        error_flag = 1
                    error_dict = {"error_flag":error_flag,"msg":msg}
                else:
                    exists_flag = 1

        except Exception,e:
                error_dict = {"error_flag":1,"msg":str(e)}

    return render_to_response("custdetail/charge_bck_csv.html",{"username":username, "menu":menu, "loan_id" : loan_id,
                                                                "validFileFormat" : validFileFormat, "flag" : data_value,
                                                                "exists_flag" : exists_flag, "ChargeBackType":ChargeBackType,
                                                                "vaidDateFormat":vaidDateFormat,"error_dict":error_dict,"header_format":header_format})

def cb_tran_history(request):
    tran_id= request.GET['tran_id']
    cb_tran_list = chargeBack.get_cb_tran_history(tran_id)
    return render_to_response('custdetail/cb_tran_history.html',{'tran_list':cb_tran_list})

def potential_debt_info(request):
    
    """
    This function is used to display all the screens for Potential Debt Plan.
    """

    key_id = GlobalVars().getkeyid()

    externalarrange_logger.info(str(key_id)+ ' ::Inside dca function ::')

    loan_id= request.GET['loan_id']
    cust_id= request.GET['cust_id']
    username = request.session['username']
    accountid=request.session['accountid']
    dm_dic = {'DEBT MANAGEMENT':'DM'}


    # get account_cust_id for the corresponding loan
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    quer_get_cust_id = "select account_cust_id,store_id from Loan_Latest ll where ll.loan_id = %s;"%(loan_id)
    cust_store_id_rs=con.get_all_results(query = quer_get_cust_id)
    cust_store_id = cust_store_id_rs[0]['account_cust_id']
    edit_proposal_loan={}
    edit_loan_remove = []
    selected_proposal_id = 0
    action = 'New'
    
    spl_privilege_list = ('DMP',)
    spl_priv_approved_list = gcmauthapi.get_spl_privileges_by_usr_id_list(username, spl_privilege_list)
    externalarrange_logger.info(str(key_id)+":: Special privileges for particular role are "+ str(spl_priv_approved_list))

    if spl_priv_approved_list:
        dmp=1
    else:
        dmp=0

    if request.method == "POST":

        create_date=datetime.datetime.now()
        action = request.POST.get('action_str','')
        
        if action == 'New':
            
            externalarrange_logger.info(str(key_id)+':: For store cust id::'+str(cust_store_id)+"::Inside PotentialDebtPlan add new ")

            dic1 = dict(request.POST)

            arrangement_type = request.POST.get('arrangement_type')
            ext_ref_id = request.POST.get('arrangement_id')
            dmc_name = request.POST.get('dmc_name')
            dmc_address = request.POST.get('dmc_address')
            dmc_email = request.POST.get('dmc_email')
            dmc_mobile = request.POST.get('dmc_mobile')
            dmc_home_phone = request.POST.get('dmc_home_phone')
            dmc_fax = request.POST.get('dmc_fax')
            dmc_register_no = request.POST.get('dmc_register_no')
            dmc_license_no=request.POST.get('license_no')
            company_license_expiry_dt = request.POST.get('license_expiry')


            if company_license_expiry_dt.strip() == '':
                company_license_expiry_dt = None
            loan_details_str = request.POST.get('loan_details_str')
            
            try:

                db = TranDB(section='TMS_DATA',logger=externalarrange_logger)
                curs = db.getcursor()
                payments_obj = pcfactory.getpmobj(section="TMS_DATA")

                # insert DMC details
                
                insert_PDP = "INSERT INTO PotentialDebtPlan (\
                                                            `debt_type`,\
                                                            `dmc_name`,\
                                                            `reference_no`,\
                                                            `register_no`,\
                                                            `license_no`,\
                                                            `licence_expiry_date`,\
                                                            `address`,\
                                                            `email`,\
                                                            `telephone_number`,\
                                                            `mobile_number`,\
                                                            `fax_number`,\
                                                            `create_dt`,\
                                                            `created_by`\
                                                             )\
                                                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                args = (arrangement_type,dmc_name,ext_ref_id,dmc_register_no,dmc_license_no,company_license_expiry_dt,dmc_address,dmc_email,dmc_home_phone,dmc_mobile,dmc_fax,create_date,username)

                primarykey=db.processquery(query=insert_PDP, args=args,curs=curs,fetch=False,returnprikey=1)

                loan_details = loan_details_str.split('|')
               
                if loan_details:
                    for all_rec in loan_details:
                        each_rec = all_rec.split('~')

                        externalarrange_logger.info(str(key_id)+'::Going to dbtmsapi.dcaLinkDebtPlan for loan::'+str(each_rec[0]))

                        # Mark the loan to send to dca.

                        if each_rec[3]=='RECOVERIES':
                            
                            dbtmsapi.dcaLinkDebtPlan(primarykey,each_rec[0],'PULL BACK REQUEST TRIGGERED',
                                                    username,logger=externalarrange_logger,create_dt=create_date,
                                                    key_id=key_id,conn_close=0)
                            
                        else:
                            dbtmsapi.dcaLinkDebtPlan(primarykey,each_rec[0],'READY TO SEND',
                                                    username,logger=externalarrange_logger,create_dt=create_date,
                                                    key_id=key_id,conn_close=0)
                                                
                            externalarrange_logger.info(str(key_id)+'::Going to dbtmsapi.dcaIntermediateStatus for loan ::'+str(each_rec[0]))

                            # change the loan 
                            dbtmsapi.dcaIntermediateStatus(each_rec[0],'POTENTIAL DMP',username,
                                                                logger=externalarrange_logger,create_dt=create_date,
                                                                key_id=key_id,conn_close=0)

                            externalarrange_logger.info(str(key_id)+" :: Going to pcfunc.generalsuppress for the loan :: %s to suppress waterfall and communications"%(str(each_rec[0])))

                            # suppress waterfall permanently
                            payments_obj.generalsuppress(loan_id=each_rec[0],
                                                        user=username,
                                                        prn_sup=0,
                                                        int_sup=0,
                                                        fee_sup=0,
                                                        wat_sup=1,
                                                        wat_sup_reason='POTENTIAL DMP',
                                                        date_elem=create_date,
                                                        key_id=key_id)
                                                        
                            externalarrange_logger.info(str(key_id)+" :: Returned from pcfunc.generalsuppress")

                externalarrange_logger.info(str(key_id)+'::For store cust id::'+str(cust_store_id)+"::Debt Plan made sucessfully ::")
                daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
                if isDailyRunStarted(date_of_run=daily_run_date):
                   updateDeltaMatrix(loan_id,'suppress_flag')
                db.commit()
                db.close()
                addsucess = "&add_success"

            except Exception,e:
                print e,"******************"
                externalarrange_logger.info(str(key_id)+'::For store cust id::'+str(cust_store_id)+"::Exception found ::"+str(e))
                db.rollback()
                db.close()
                addsucess = "&add_unsuccess"

            return HttpResponseRedirect('?loan_id='+loan_id+'&cust_id='+cust_id+addsucess)
        
        elif action == 'Add_Dmc':
            db = TranDB(section='TMS_DATA')
            curs = db.getcursor()
            dmc_reg = request.POST.get('dmc_reg')
            dmc_reg_name = request.POST.get('dmc_reg_name')
            dmc_reg_address = request.POST.get('dmc_reg_address')
            dmc_category = request.POST.get('dmc_category')
            dmc_reg_email = request.POST.get('dmc_reg_email')
            credit_license_no = request.POST.get('credit_license_no')
            licence_issue_date = request.POST.get('licence_issue_date')
            licence_expiry_date = request.POST.get('licence_expiry_date')
            maintenance_due_date = request.POST.get('maintenance_due_date')
            licence_status = request.POST.get('licence_status')
            tel_no = request.POST.get('tel_no')
            mob_no = request.POST.get('mob_no')
            fax_no = request.POST.get('fax_no')
            get_reg_qry = "select distinct (dmc_register_no) from DMC_Details where dmc_register_no = '%s' and override_flag = 0" %(dmc_reg)
            reg_rs=con.get_all_results(query = get_reg_qry)
            if reg_rs:#if company is already present in db
               try:
                   update_query_dmc_add ="UPDATE DMC_Details set override_flag = 1 where override_flag=0 and dmc_register_no = '%s'"%(dmc_reg)
                   db.processquery(query=update_query_dmc_add,curs=curs,fetch=False)
                   insert_update_dmc_qry = "INSERT INTO DMC_Details (`dmc_name`,\
                                                                    `category`,\
                                                                    `company_address`,\
                                                                    `company_email`,\
                                                                    `telephone_number`,\
                                                                    `mobile_number`,\
                                                                    `fax_number`,\
                                                                    `license_no`,\
                                                                    `dmc_register_no`,\
                                                                    `licence_issued_date`,\
                                                                    `licence_expiry_date`,\
                                                                    `maintenance_payment_due_date`,\
                                                                    `licence_status`,\
                                                                    `modified_date`,\
                                                                    `modified_by` \
                    ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                   arg = (dmc_reg_name,dmc_category,dmc_reg_address,dmc_reg_email,tel_no,mob_no,fax_no,credit_license_no,dmc_reg,licence_issue_date,licence_expiry_date,maintenance_due_date,licence_status,create_date,username)
                   db.processquery(query=insert_update_dmc_qry, args=arg,curs=curs,fetch=False)
                   db.commit()
                   db.close()
                   dmcsucess = "&dmc_update_success"
               except Exception,e:
                    print e
                    db.rollback()
                    db.close()
                    dmcsucess = "&dmc_update_unsuccess"
            else:

                try:
                    insert_new_dmc_qry = "INSERT INTO DMC_Details (`dmc_name`,\
                                                                    `category`,\
                                                                    `company_address`,\
                                                                    `company_email`,\
                                                                    `telephone_number`,\
                                                                    `mobile_number`,\
                                                                    `fax_number`,\
                                                                    `license_no`,\
                                                                    `dmc_register_no`,\
                                                                    `licence_issued_date`,\
                                                                    `licence_expiry_date`,\
                                                                    `maintenance_payment_due_date`,\
                                                                    `licence_status`,\
                                                                    `create_date`,\
                                                                    `created_by` \
                    ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    arg = (dmc_reg_name,dmc_category,dmc_reg_address,dmc_reg_email,tel_no,mob_no,fax_no,credit_license_no,dmc_reg,licence_issue_date,licence_expiry_date,maintenance_due_date,licence_status,create_date,username)
                    db.processquery(query=insert_new_dmc_qry, args=arg,curs=curs,fetch=False)
                    db.commit()
                    db.close()
                    dmcsucess = "&dmc_add_success"
                except Exception,e:
                    print e
                    db.rollback()
                    db.close()
                    dmcsucess = "&dmc_add_unsuccess"
            return HttpResponseRedirect('?loan_id='+loan_id+'&cust_id='+cust_id+dmcsucess)

    store_list = []
    for key, store in collection_config.GB_RELATED_STORE.items():
        store_list.extend(store)
            
    con = mysqldbwrapper.MySQLWrapper(config_file_path, 'TMS_DATA')
    new_query = """select *,if(%s,1,if(status_cd in (%s),0,1)) as dmp_chk \
                from \
                (select full.*,status_cd,gc.case_id from
                    (select py.loan_id,(pc.OutstandingInterest+pc.OutstandingFee+py.OPB) as OustandingBalance,first_name,last_name,store_id,account_cust_id,lead_id
                    from Payments py \
                    join
                    (select pc.loan_id,sum(if(pc.payment_type rlike 'LZD',pc.payment_amt-pc.paid_amt,0)) as OutstandingInterest,
                    sum(if(pc.payment_type rlike 'FEE',pc.payment_amt-pc.paid_amt,0)) as OutstandingFee,first_name,last_name,store_id,account_cust_id,lead_id
                    from PaymentCalendar as pc \
                    join \
                    (select loan_id,first_name,last_name,store_id,account_cust_id,lead_id from Loan_Latest
                    where account_cust_id='%s' and store_id in (%s) ) c \
                    on pc.loan_id=c.loan_id
                    where override_flag=0 group by pc.loan_id) pc \
                    on py.loan_id = pc.loan_id having OustandingBalance>0)
                full join \
                GCMS_Data.gcm_case gc on gc.entity_id = full.loan_id and gc.entity_type = 'LOAN' ) a
                left join \
                (select loan_id,debt_status \
                    from LinkDebtPlan where override_flag = 0 and \
                    if(debt_status='PROCESSED',0, \
                      if(debt_status in ('PULL BACK REQUEST TRIGGERED','PULL BACK REQUEST SENT') and datediff(curdate(),date(create_dt)) > 10,0,1)) = 1) b \
                using(loan_id) \
                left join \
                TMS_Data.Collection_Info cli on cli.loan_id = a.loan_id and cli.override_flag = 0 \
                where b.loan_id is null""" % (dmp, ','.join ("'" + str(status) + "'" for status in loanstatusconfig.DMP_LOAN_STATUS), cust_store_id, ','.join("'" + str(store_id) + "'" for store_id in store_list))

    new_dict_loan = con.get_all_results(query =new_query)

    return render_to_response('custdetail/potential_debt_info.html',{'loan_id':loan_id,'cust_id':cust_id,'loan_dic':new_dict_loan,
                              'selected_proposal_id':selected_proposal_id,
                              'action':str(action).lower()})
@maintenance_deco_popups
def external_arrangement(request):
    """
    This function is used to display all the screens for External Arrangement PopUp.
    """

    loan_id= request.GET['loan_id']
    cust_id= request.GET['cust_id']
    username = request.session['username']
    accountid=request.session['accountid']
    dm_dic = {'DEBT MANAGEMENT':'DM','IVA':'IVA',"TRUST DEED":"TRUST DEED"}
    timelist = ctime().split()
    
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    quer_get_cust_id = "select account_cust_id,store_id from Loan_Latest ll where ll.loan_id = %s;"%(loan_id)
    cust_store_id_rs=con.get_all_results(query = quer_get_cust_id)
    cust_store_id = cust_store_id_rs[0]['account_cust_id']
    brand_name = get_Store_Info_frm_storeid(cust_store_id_rs[0]['store_id'])['brand_name']
    quer_get_all_purposal = "select distinct proposal_arrangement_id from ProposalArrangement where store_cust_id = %s and override_flag=0 and status='OPEN';"%(cust_store_id)
    purposal_id_dic=con.get_all_results(query = quer_get_all_purposal)
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    edit_proposal_loan={}
    edit_loan_remove = []
    selected_proposal_id = 0
    action = 'New'

    if request.method == "POST":

        create_date=datetime.datetime.now()
        action = request.POST.get('action_str','')
        if action == 'New':
            externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Inside external_arrangement add new ")
            arrangement_type = request.POST.get('arrangement_type')
            ext_ref_id = request.POST.get('arrangement_id') 
            dmc_name = request.POST.get('dmc_name')
            dmc_address = request.POST.get('dmc_address')
            dmc_email = request.POST.get('dmc_email')
            dmc_mobile = request.POST.get('dmc_mobile')
            dmc_home_phone = request.POST.get('dmc_home_phone')
            dmc_fax = request.POST.get('dmc_fax')
            dmc_register_no = request.POST.get('dmc_register_no')
            company_license_expiry_dt = request.POST.get('license_expiry')
            if company_license_expiry_dt.strip() == '':
                company_license_expiry_dt = None
            loan_details_str = request.POST.get('loan_details_str')
            upload_file_flag = 0

            try:
                
                db = TranDB(section='TMS_DATA',logger=externalarrange_logger)
                curs = db.getcursor()
              
                insert_PA = "INSERT INTO ProposalArrangement (\
                                                            `proposal_arrangement_id`, \
                                                            `external_ref_id`, \
                                                            `arrange_type`,\
                                                            `company_name`,\
                                                            `dmc_register_no`,\
                                                            `company_license_expiry_dt`,\
                                                            `company_address`,\
                                                            `company_email`,\
                                                            `company_phone`,\
                                                            `company_mobile`,\
                                                            `company_fax`,\
                                                            `create_date`,\
                                                            `created_by`,\
                                                            `store_cust_id`,\
                                                            `status`\
                                                             )\
                                                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                args = ('0',ext_ref_id,arrangement_type,dmc_name,dmc_register_no,company_license_expiry_dt,dmc_address,dmc_email,dmc_home_phone,dmc_mobile,dmc_fax,create_date,username,cust_store_id,'OPEN')

                primarykey=db.processquery(query=insert_PA, args=args,curs=curs,fetch=False,returnprikey=1)

                update_sql = "update ProposalArrangement set proposal_arrangement_id = %s where arrangement_auto_id = %s"                
                db.processquery(query=update_sql, args=('PROARG'+str(primarykey),primarykey),curs=curs,fetch=False,returnprikey=1)
                externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Updated  ProposalArrangement.proposal_arrangement_id for arrangement_auto_id::"+str(primarykey)+' to::PROARG'+str(primarykey))

                if 'proposal_file_add' in request.FILES:
                    proposal_file = request.FILES['proposal_file_add']
                    if proposal_file.size>0:
                        proposal_file = cust_store_id + "_" + 'PROARG'+str(primarykey) + "_" + str(proposal_file)
                        invalid_char = re.compile(r'%%[a-f0-9A-F]{2}')
                        proposal_file = re.sub(invalid_char,"",proposal_file)
                        new_media_root = generate_new_path(MEDIA_ROOT,accountid,brand_name)
                        os.system("mkdir -p '%s/%s/%s/%s'" % (new_media_root,timelist[4],timelist[1],timelist[2]) )
                        destination = open('%s/%s/%s/%s/%s' % (new_media_root, timelist[4],timelist[1],timelist[2],proposal_file), 'wb')
                        path = "RECEIVED_DOCS" + "/" + '%s/%s/%s/%s' % (timelist[4],timelist[1],timelist[2],proposal_file)
                        size1 = (request.FILES['proposal_file_add'].size)
                        for chunk in request.FILES['proposal_file_add'].chunks():
                            destination.write(chunk)
                        destination.close()
                        upload_file_flag = 1
                        externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::uploaded file>> "+proposal_file)

                loan_details = loan_details_str.split('|')

                if loan_details:
                    for all_rec in loan_details:
                        each_rec = all_rec.split('~')
                        
                        if each_rec[2].strip() =='':
                                each_rec[2] = 0
                        if each_rec[1].strip() =='':
                                each_rec[1] = 0
                        quer_insert_freq = "INSERT INTO LinkProposal(\
                        `proposal_arrangement_id`,\
                        `loan_id`,\
                        `proposal_frenquency`,\
                        `every_in_frenquency`,\
                        `frenquency_payable`,\
                        `total_proposed_amt`,\
                        `create_date`,\
                        `created_by`\
                        )\
                        values(%s,%s,%s,%s,%s,%s,%s,%s);"
                        args=('PROARG'+str(primarykey),each_rec[0],each_rec[3],each_rec[4],each_rec[2],each_rec[1],create_date,request.session['username'])
                        externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Inserting loan ::"+str(each_rec[0]))
                        db.processquery(query=quer_insert_freq, args=args,curs=curs,fetch=False)
                        
                        msg = pcfunc.general_status_change(dm_dic[arrangement_type],int(each_rec[5]),username,date_elem=create_date,conn_close=0)
                        trandbupdateGCMCase(each_rec[5],status_cd=arrangement_type,done_by=username,date_elem=create_date)
                        
                        if upload_file_flag:
                                logid= get_log_id_by_loan_id(each_rec[0])
                                if logid is not None:
                                    date_today = fetch_curr_date()
                                    if check_file_name_exists(proposal_file,each_rec[5],date_today) == 0:
                                        traninsert_gcm_document(proposal_file,path,'RECEIVED',size1,'External Proposal Arrangement', request.session['username'],each_rec[5],'',create_date)
                                        trandbadd_gcm_notes(logid,"Document","External Proposal Arrangement Document",username,create_date)
                                        
                                        exists_flag = 0
                                    else:
                                        exists_flag = 1
        
                
                #changed message type in the general_status_change() api so changing here.
                if msg.find("couldn't") == -1:
                    externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::status changed sucessfully with message ::"+str(msg))
                    db.commit()
                    db.close()
                    addsucess = "&add_success"
                else:
                    externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Unsucess status changed with message ::"+str(msg))
                    db.rollback()
                    db.close()
                    addsucess = "&add_unsuccess"
            #external_arrangement/?loan_id=113&cust_id=85'
            except Exception,e:
                print e,"******************"
                externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Exception found ::"+str(e))
                db.rollback()
                db.close()
                addsucess = "&add_unsuccess"

            return HttpResponseRedirect('?loan_id='+loan_id+'&cust_id='+cust_id+addsucess)
        elif action == 'Edit' and not request.POST.has_key('arrangement_id_edit_post'):#if being posted to save changes from edit, not to see the deatails of an arrangement id
            externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Inside external_arrangement edit ")
            msg=''
            arrangement_id_edit = request.POST.get('arrangement_id','')#Ref id created by us and saved in db
            ext_ref_id_edit = request.POST.get('arrange_id_edit_post')#External Reference Id
            arrange_type_edit = request.POST.get('arrange_type_edit')
            dmc_register_no_edit = request.POST.get('dmc_register_no_edit')
            license_expiry_dt_edit = request.POST.get('license_expiry_edit')
            print '*************************************',license_expiry_dt_edit,'*************************'
            try:

                
                db = TranDB(section='TMS_DATA',logger=externalarrange_logger)
                curs = db.getcursor()


                if request.POST.has_key('ref_changed') and request.POST.get('ref_changed') == '1':#If changes are made in the DMC details
                    dmc_name_edit = request.POST.get('dmc_name_edit_post')
                    dmc_address_edit = request.POST.get('dmc_address_edit')
                    dmc_email_edit = request.POST.get('dmc_email_edit')
                    dmc_mobile_edit = request.POST.get('dmc_mobile_edit')
                    dmc_home_phone_edit = request.POST.get('dmc_home_phone_edit')
                    dmc_fax_edit = request.POST.get('dmc_fax_edit')
                    
                    
                    update_PA = "update ProposalArrangement set override_flag =1, modified_date=%s,modified_by=%s \
                                        where proposal_arrangement_id =%s and override_flag =0"
                    args = (create_date,username,arrangement_id_edit)
                    db.processquery(query=update_PA, args=args,curs=curs,fetch=False)
                    externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::updating override_flag,modified_date,modified_by for proposal_arrangement_id"+str(arrangement_id_edit))

                    insert_PA = "INSERT INTO ProposalArrangement (\
                                                            `proposal_arrangement_id`, \
                                                            `external_ref_id`, \
                                                            `arrange_type`,\
                                                            `company_name`,\
                                                            `dmc_register_no`,\
                                                            `company_license_expiry_dt`,\
                                                            `company_address`,\
                                                            `company_email`,\
                                                            `company_phone`,\
                                                            `company_mobile`,\
                                                            `company_fax`,\
                                                            `create_date`,\
                                                            `created_by`,\
                                                            `store_cust_id`,\
                                                            `status`\
                                                             )\
                                                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    args = (arrangement_id_edit,ext_ref_id_edit,arrange_type_edit,dmc_name_edit,dmc_register_no_edit,
                            license_expiry_dt_edit,dmc_address_edit,dmc_email_edit,dmc_home_phone_edit,dmc_mobile_edit,
                            dmc_fax_edit,create_date,username,cust_store_id,'OPEN')
                    db.processquery(query=insert_PA, args=args,curs=curs,fetch=False)
                    externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Inserted value for arrangement_id_edit::"+str(arrangement_id_edit))
                    msg = "Inserted INTO ProposalArrangement"
                    

                loan_details_str_edit = request.POST.get('loan_details_str_edit','')
                upload_file_flag = 0
                if 'proposal_file_edit' in request.FILES :#and loan_details_str_edit.strip() !="":
                    proposal_file = request.FILES['proposal_file_edit']
                    if proposal_file.size>0:
                        proposal_file = cust_store_id + "_" + arrangement_id_edit + "_" + str(proposal_file)
                        invalid_char = re.compile(r'%%[a-f0-9A-F]{2}')
                        proposal_file = re.sub(invalid_char,"",proposal_file)
                        new_media_root = generate_new_path(MEDIA_ROOT,accountid,brand_name)
                        os.system("mkdir -p '%s/%s/%s/%s'" % (new_media_root,timelist[4],timelist[1],timelist[2]) )
                        destination = open('%s/%s/%s/%s/%s' % (new_media_root, timelist[4],timelist[1],timelist[2],proposal_file), 'wb')
                        path = "RECEIVED_DOCS" + "/" + '%s/%s/%s/%s' % (timelist[4],timelist[1],timelist[2],proposal_file)
                        size1 = (request.FILES['proposal_file_edit'].size)
                        for chunk in request.FILES['proposal_file_edit'].chunks():
                            destination.write(chunk)
                        destination.close()
                        upload_file_flag = 1
                        externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::uploaded file>> "+proposal_file)
                        


                if upload_file_flag:
                    select_sql="select distinct loan_id from ProposalArrangement PA \
                                join LinkProposal LP using(proposal_arrangement_id) \
                                where PA.override_flag =0 and LP.override_flag = 0 and status = 'OPEN' and \
                                PA.proposal_arrangement_id = %s"
                    args = (arrangement_id_edit)
                    result = db.processquery(query=select_sql, args=args,curs=curs,fetch=True)
                    
                    for row in result:
                        #logid= get_log_id_by_loan_id(row['loan_id'])
                        #case_id=get_case_id_by_entity_id(row['loan_id'],'LOAN')
                        case_id=get_case_id_by_entity_id(row['loan_id'],'LOAN')
                        logid = get_logid_by_caseid(case_id)['log_id']
                        
                        if logid is not None:
                            date_today = fetch_curr_date()
                            if check_file_name_exists(proposal_file,case_id,date_today) == 0:
                                traninsert_gcm_document(proposal_file,path,'RECEIVED',size1,'External Proposal Arrangement', request.session['username'],case_id,'',create_date)
                                trandbadd_gcm_notes(logid,"Document","External Proposal Arrangement Document",request.session['username'],create_date)

                                exists_flag = 0
                            else:
                                exists_flag = 1
                if (loan_details_str_edit.strip() !=""):#If some loans are being attached with the arrangement id
                    loan_details_edit = loan_details_str_edit.split('|')
                    if loan_details_edit:
                        for all_rec in loan_details_edit:
                            each_rec = all_rec.split('~')
                            if each_rec[2].strip() =='':
                                each_rec[2] = 0
                            if each_rec[1].strip() =='':
                                each_rec[1] = 0
                            if each_rec[6] == 'Add':
                                quer_insert_freq = "INSERT INTO LinkProposal(\
                                `proposal_arrangement_id`,\
                                `loan_id`,\
                                `proposal_frenquency`,\
                                `every_in_frenquency`,\
                                `frenquency_payable`,\
                                `total_proposed_amt`,\
                                `create_date`,\
                                `created_by`\
                                )\
                                values(%s,%s,%s,%s,%s,%s,%s,%s);"
                                args=(arrangement_id_edit,each_rec[0],each_rec[3],each_rec[4],each_rec[2],each_rec[1],create_date,username)

                                db.processquery(query=quer_insert_freq, args=args,curs=curs,fetch=False)
                                
                                msg = pcfunc.general_status_change(dm_dic[arrange_type_edit],int(each_rec[5]), request.session['username'],date_elem=create_date,conn_close=0)
                                trandbupdateGCMCase(each_rec[5],status_cd=arrange_type_edit,done_by=request.session['username'],date_elem=str(datetime.datetime.now()))
                                externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Under edit loan added>> "+str(each_rec[0]))
                                if upload_file_flag:
                             
                                    logid= get_log_id_by_loan_id(each_rec[0])
                                    if logid is not None:
                                        date_today = fetch_curr_date()
                                        if check_file_name_exists(proposal_file,each_rec[5],date_today) == 0:
                                            traninsert_gcm_document(proposal_file,path,'RECEIVED',size1,'External Proposal Arrangement', request.session['username'],each_rec[5],'',create_date)
                                            trandbadd_gcm_notes(logid,"Document","External Proposal Arrangement Document",request.session['username'],create_date)

                                            exists_flag = 0
                                        else:
                                            exists_flag = 1

                                
                            elif each_rec[6] == 'Update':

                                update_LP = "update LinkProposal set override_flag =1, modified_date=%s,modified_by=%s \
                                            where loan_id =%s and override_flag =0 and proposal_arrangement_id = %s"
                                args = (create_date,username,each_rec[0],arrangement_id_edit)
                                db.processquery(query=update_LP, args=args,curs=curs,fetch=False)

                                insert_LP = "INSERT INTO LinkProposal(\
                                `proposal_arrangement_id`,\
                                `loan_id`,\
                                `proposal_frenquency`,\
                                `every_in_frenquency`,\
                                `frenquency_payable`,\
                                `total_proposed_amt`,\
                                `create_date`,\
                                `created_by`\
                                )\
                                values(%s,%s,%s,%s,%s,%s,%s,%s);"
                                args=(arrangement_id_edit,each_rec[0],each_rec[3],each_rec[4],each_rec[2],each_rec[1],create_date,username)
                                db.processquery(query=insert_LP, args=args,curs=curs,fetch=False)
                                externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Under edit loan updated>> "+str(each_rec[0]))
                                
                #changing message type as changes made in the general_status_change() api
                if msg.find("couldn't") == -1:
                    externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::sucess status update under edit with messgae:: "+str(msg))
                    db.commit()
                    db.close()
                    editsucess = "&edit_success"
                else:
                    externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Unsucess status update under edit with messgae:: "+str(msg))
                    db.rollback()
                    db.close()
                    editsucess = "&edit_unsuccess"
            except Exception,e:
                externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::under edit found exception:: "+str(e))
                print e,'***************'
                db.rollback()
                db.close()
                editsucess = "&edit_unsuccess"
            return HttpResponseRedirect('?loan_id='+loan_id+'&cust_id='+cust_id+editsucess)
        elif action == 'Return':
            
            externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Inside return back")
            post_reference_return = request.POST.get('post_reference_return','')
            if (post_reference_return.strip() !=""):#If some loans are being attached with the arrangement id
                    return_list = post_reference_return.split('~')
                    if return_list:
                        try:
                            db = TranDB(section='TMS_DATA',logger=externalarrange_logger)
                            curs = db.getcursor()
                            return_reason = request.POST.get('reason')
                            for case_loan_str in return_list:
                                case_loan = case_loan_str.split('|')
                                update_GB = "update ProposalArrangement set status ='CLOSED',override_flag=1 where proposal_arrangement_id =%s and override_flag = 0"
                                args=(case_loan[0],)
                                db.processquery(query=update_GB, args=args,curs=curs,fetch=False)
                                update_LP = "update LinkProposal set override_flag = 1 where proposal_arrangement_id = %s and override_flag=0"
                                args=(case_loan[0],)
                                db.processquery(query=update_LP, args=args,curs=curs,fetch=False)
                                cases = case_loan[1].split(',')
                                for case in cases:
                                    sql2 = "select status_cd from GCMS_Data.gcm_case where case_id=%s"
                                    get_cur_status = db.processquery(query=sql2,args=case,curs=curs,fetch=True)
                                    if get_cur_status[0]['status_cd'] in dm_dic.keys():
                                        trandbupdateGCMCase(case_id=case,status_cd='RETURNED',done_by=request.session['username'],reason_cd=return_reason,date_elem=create_date)
                            db.commit()
                            db.close()
                            returnsucess = "&return_success"
                            externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::for return back, loans for the case "+str(case)+" are returned.")
                        except Exception,e:
                            externalarrange_logger.info('For store cust id::'+str(cust_store_id)+"::Under return found exception"+str(e))
                            db.rollback()
                            db.close()
                            print e
                            returnsucess = "&return_unsuccess"
                    return HttpResponseRedirect('?loan_id='+loan_id+'&cust_id='+cust_id+returnsucess)
        elif action == 'Add_Dmc':
            db = TranDB(section='TMS_DATA')
            curs = db.getcursor()
            dmc_reg = request.POST.get('dmc_reg')
            dmc_reg_name = request.POST.get('dmc_reg_name')
            dmc_reg_address = request.POST.get('dmc_reg_address')
            dmc_category = request.POST.get('dmc_category')
            dmc_reg_email = request.POST.get('dmc_reg_email')
            credit_license_no = request.POST.get('credit_license_no')
            licence_issue_date = request.POST.get('licence_issue_date')
            licence_expiry_date = request.POST.get('licence_expiry_date')
            maintenance_due_date = request.POST.get('maintenance_due_date')
            licence_status = request.POST.get('licence_status')
            tel_no = request.POST.get('tel_no')
            mob_no = request.POST.get('mob_no')
            fax_no = request.POST.get('fax_no')
            get_reg_qry = "select distinct (dmc_register_no) from DMC_Details where dmc_register_no = '%s' and override_flag = 0" %(dmc_reg)
            reg_rs=con.get_all_results(query = get_reg_qry)
            if reg_rs:#if company is already present in db
               try:
                   update_query_dmc_add ="UPDATE DMC_Details set override_flag = 1 where override_flag=0 and dmc_register_no = '%s'"%(dmc_reg)
                   db.processquery(query=update_query_dmc_add,curs=curs,fetch=False)
                   insert_update_dmc_qry = "INSERT INTO DMC_Details (`dmc_name`,\
                                                                    `category`,\
                                                                    `company_address`,\
                                                                    `company_email`,\
                                                                    `telephone_number`,\
                                                                    `mobile_number`,\
                                                                    `fax_number`,\
                                                                    `license_no`,\
                                                                    `dmc_register_no`,\
                                                                    `licence_issued_date`,\
                                                                    `licence_expiry_date`,\
                                                                    `maintenance_payment_due_date`,\
                                                                    `licence_status`,\
                                                                    `modified_date`,\
                                                                    `modified_by` \
                    ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                   arg = (dmc_reg_name,dmc_category,dmc_reg_address,dmc_reg_email,tel_no,mob_no,fax_no,credit_license_no,dmc_reg,licence_issue_date,licence_expiry_date,maintenance_due_date,licence_status,create_date,username)
                   db.processquery(query=insert_update_dmc_qry, args=arg,curs=curs,fetch=False)
                   db.commit()
                   db.close()
                   dmcsucess = "&dmc_update_success"
               except Exception,e:
                    print e
                    db.rollback()
                    db.close()
                    dmcsucess = "&dmc_update_unsuccess"
            else:
                
                try:
                    insert_new_dmc_qry = "INSERT INTO DMC_Details (`dmc_name`,\
                                                                    `category`,\
                                                                    `company_address`,\
                                                                    `company_email`,\
                                                                    `telephone_number`,\
                                                                    `mobile_number`,\
                                                                    `fax_number`,\
                                                                    `license_no`,\
                                                                    `dmc_register_no`,\
                                                                    `licence_issued_date`,\
                                                                    `licence_expiry_date`,\
                                                                    `maintenance_payment_due_date`,\
                                                                    `licence_status`,\
                                                                    `create_date`,\
                                                                    `created_by` \
                    ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    arg = (dmc_reg_name,dmc_category,dmc_reg_address,dmc_reg_email,tel_no,mob_no,fax_no,credit_license_no,dmc_reg,licence_issue_date,licence_expiry_date,maintenance_due_date,licence_status,create_date,username)
                    db.processquery(query=insert_new_dmc_qry, args=arg,curs=curs,fetch=False)
                    db.commit()
                    db.close()
                    dmcsucess = "&dmc_add_success"
                except Exception,e:
                    print e
                    db.rollback()
                    db.close()
                    dmcsucess = "&dmc_add_unsuccess"
            return HttpResponseRedirect('?loan_id='+loan_id+'&cust_id='+cust_id+dmcsucess)
 
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    new_query= """select *,b.proposal_arrangement_id as alreadyproposed from
                (select full.*,status_cd,gc.case_id from  (select py.loan_id,(pc.OutstandingInterest+pc.OutstandingFee+py.OPB) as OustandingBalance,first_name,last_name
                from Payments py
                join
                 (select pc.loan_id,sum(if(pc.payment_type rlike 'LZD',pc.payment_amt-pc.paid_amt,0)) as OutstandingInterest,
                 sum(if(pc.payment_type rlike 'FEE',pc.payment_amt-pc.paid_amt,0)) as OutstandingFee,first_name,last_name
                 from PaymentCalendar as pc
                 join (select loan_id,first_name,last_name from Loan_Latest  where account_cust_id='%s' ) c
                 on pc.loan_id=c.loan_id where override_flag=0 group by pc.loan_id) pc
                 on py.loan_id = pc.loan_id having OustandingBalance>0) full
                 join GCMS_Data.gcm_case gc on gc.entity_id = full.loan_id and gc.entity_type = 'LOAN'
                 where gc.status_cd in (%s)) a
                 left join
                 (select loan_id,proposal_arrangement_id from ProposalArrangement pa join LinkProposal lp
                 using (proposal_arrangement_id)
                 where pa.override_flag =0 and lp.override_flag =0 and status = 'OPEN'
                 and store_cust_id = '%s') b using(loan_id)
                 where b.proposal_arrangement_id is null;"""%(cust_store_id,','.join ("'"+str(status)+"'" for status in loanstatusconfig.EXTERNAL_ARRANGE_LOAN_STATUS),cust_store_id)
    
    new_proposal_loan = con.get_all_results(query =new_query)


    if purposal_id_dic:

        
        if request.method == "POST" and request.POST.get('action_str','') =='Edit' and request.POST.has_key('arrangement_id_edit_post'):
            selected_proposal_id = request.POST.get('arrangement_id_edit_post')
        else:
            selected_proposal_id = purposal_id_dic[0]['proposal_arrangement_id']
        edit_query = """select a.*,b.*,if(proposal_arrangement_id is not null,'checked disabled','') as checked
                        from (select full.*,status_cd,gc.case_id from
                        (select py.loan_id,(pc.OutstandingInterest+pc.OutstandingFee+py.OPB) as OustandingBalance,first_name,last_name
                        from Payments py
                        join  (select pc.loan_id,sum(if(pc.payment_type rlike 'LZD',pc.payment_amt-pc.paid_amt,0)) as OutstandingInterest,
                        sum(if(pc.payment_type rlike 'FEE',pc.payment_amt-pc.paid_amt,0)) as OutstandingFee,first_name,last_name
                        from PaymentCalendar as pc
                        join (select loan_id,first_name,last_name from Loan_Latest  where account_cust_id='%s' ) c
                        on pc.loan_id=c.loan_id where override_flag=0 group by pc.loan_id) pc
                        on py.loan_id = pc.loan_id having OustandingBalance>0) full
                        join GCMS_Data.gcm_case gc on gc.entity_id = full.loan_id and gc.entity_type = 'LOAN'
                        where gc.status_cd in (%s)) a
                        left join
                        ( select PA.proposal_arrangement_id,PA.external_ref_id as arrange_ref_id,PA.arrange_type,PA.dmc_register_no,
                        PA.company_license_expiry_dt AS licence_expiry_date,PA.company_name,PA.company_address,
                        PA.company_email,PA.company_phone,PA.company_mobile,
                        PA.company_fax,LP.loan_id,LP.proposal_frenquency,LP.every_in_frenquency,
                        LP.frenquency_payable,LP.total_proposed_amt
                        from ProposalArrangement PA join LinkProposal LP using (proposal_arrangement_id)
                        where PA.override_flag =0 and LP.override_flag =0 and
                        status = 'OPEN' and store_cust_id = '%s' ) b using(loan_id)
                        where b.proposal_arrangement_id='%s' or b.proposal_arrangement_id is null order by checked desc,a.loan_id;"""%(cust_store_id,','.join ("'"+str(status)+"'" for status in loanstatusconfig.EXTERNAL_ARRANGE_LOAN_STATUS),cust_store_id,selected_proposal_id)
        
        edit_proposal_loan = con.get_all_results(query = edit_query)

    getback_query = "select a.proposal_arrangement_id,a.external_ref_id as arrange_ref_id,a.arrange_type,a.company_name,\
                        group_concat(loan_id ORDER BY loan_id  SEPARATOR ', ') as loans,group_concat(case_id SEPARATOR ', ') as cases \
                        from ProposalArrangement a join \
                        LinkProposal b using(proposal_arrangement_id) \
                        join GCMS_Data.gcm_case gc on b.loan_id = gc.entity_id and gc.entity_type = 'LOAN' \
                        where a.override_flag=0 and b.override_flag=0 and store_cust_id = %s and a.status='OPEN' group by 1"
    rs_getback = con.get_all_results(query = getback_query,args=(cust_store_id,))
 
    retuned_reason = loanstatusconfig.RETURNED_STATUS_REASON
    days_month = [x for x in range(1,32)]
    days_week =  ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
    return render_to_response('custdetail/external_arrangement_template.html',{'loan_id':loan_id,'cust_id':cust_id,'loan_dic':new_proposal_loan,
                              'days_month':days_month,'days_week':days_week,'purposal_id_dic':purposal_id_dic,'rs_edit':edit_proposal_loan,
                              'selected_proposal_id':selected_proposal_id, 'action':str(action).lower(),'rs_getback':rs_getback,
                              'retuned_reason':retuned_reason
                              })

def getDMCDetailsAjax(request):    
    req_reg_no = request.POST.get('dmc_reg','')
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    query1 = "select * from DMC_Details where dmc_register_no = '%s' and override_flag = 0" %(req_reg_no)
    dmc_db_details=con.get_all_results(query = query1)
    if dmc_db_details:
        dmp_name = dmc_db_details[0]['dmc_name']
        category = dmc_db_details[0]['category']
        address = dmc_db_details[0]['company_address']
        print address,'####################################'
        email_address = dmc_db_details[0]['company_email']
        licence_issued_date = str(dmc_db_details[0]['licence_issued_date'])
        expiry_date = str(dmc_db_details[0]['licence_expiry_date'])
        maintenance_payment_due_date = str(dmc_db_details[0]['maintenance_payment_due_date'])
        licence_status = dmc_db_details[0]['licence_status']
        telephone_number = dmc_db_details[0]['telephone_number']
        mobile_number = dmc_db_details[0]['mobile_number']
        fax_number = dmc_db_details[0]['fax_number']
        company_address = dmc_db_details[0]['company_address']
        fax_number = dmc_db_details[0]['fax_number']
        license_no = dmc_db_details[0]['license_no']
        rs_dic = {'dmp_name':dmp_name,'category':category,
                'email_address':email_address,'licence_issued_date':licence_issued_date,
                'expiry_date':expiry_date,'maintenance_payment_due_date':maintenance_payment_due_date,
                'licence_status':licence_status,'telephone_number':telephone_number,'mobile_number':mobile_number,
                'address':address,'fax_number':fax_number,'company_address':company_address,'mobile_number':mobile_number,
                'fax_number':fax_number,'license_no':license_no}
        return HttpResponse(simplejson.dumps(rs_dic))
    else:
        return HttpResponse("")
def regSearchSuggest(request):
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        if request.POST.has_key('search_str'):
            req_reg_no = request.POST.get('search_str')
            
            query1 = "select distinct (dmc_register_no) from DMC_Details where dmc_register_no like \'%%%s%%' and override_flag = 0 limit 10" %(req_reg_no)
            dmc_suggest=con.get_all_results(query = query1)
            print dmc_suggest
            if dmc_suggest:
                suggest_lst = [str(x['dmc_register_no']) for x in dmc_suggest]
                suggest_str_ret = '~'.join(suggest_lst)
            else:
                suggest_str_ret = ''
            return HttpResponse(suggest_str_ret)
        else:
            return HttpResponse('')

def getAjaxDatesforFreq(request):
    '''1. This api is used to generate the Start From: month based on the current date and selected date for Auto TA
       2. This api is also used to calculate the start date as per the selected options'''
    #finding last working day of month.
    config_dict = {'LAST MONDAY OF EACH MONTH':0,'LAST TUESDAY OF EACH MONTH':1,'LAST WEDNESDAY OF EACH MONTH':2,'LAST THURSDAY OF EACH MONTH':3,'LAST FRIDAY OF EACH MONTH':4}
    month_str = ""
    first_date = ""
    evry = request.GET.get('evry','')
    spec_dt = request.GET.get('spec_dt','0')
    tmp_mnt_year = request.GET.get('sel_month','')
    if tmp_mnt_year:
        tmp_mnt_year = tmp_mnt_year.split('-')
    try:
        sel_month = int(tmp_mnt_year[0])
    except:
        sel_month = 0
    #all_momths_dict = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
    all_momths_dict = {0:'January', 1:'February', 2:'March', 3:'April', 4:'May', 5:'June', 6:'July', 7:'August', 8:'September', 9:'October', 10:'November', 11:'December'}
    week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
    current_dt = datetime.datetime.now().replace(second=0, microsecond=0, minute=0,hour=0)
    current_year = current_dt.year
    current_month = current_dt.month
    current_day = current_dt.day
    last_day_cur_month = calendar.monthrange(current_year,current_month)[1]
    cur_mnt_last_date = datetime.datetime(current_year,current_month,last_day_cur_month)
    #sel_year = current_year
    if tmp_mnt_year:
        sel_year = int(tmp_mnt_year[1])
    else:
        sel_year = 0
    
    if sel_month:
        #if current_month > sel_month:
        #    sel_year = current_year+1
        try:
            selected_month_dt = datetime.datetime.now().replace(year=sel_year,month=sel_month,second=0, microsecond=0, minute=0,hour=0)
        except:
            selected_month_dt = datetime.datetime.now().replace(year=sel_year,month=sel_month,day=calendar.monthrange(sel_year,sel_month)[1],second=0, microsecond=0, minute=0,hour=0)
        #else:
        #    selected_month_dt = datetime.datetime.now().replace(month=int(sel_month),second=0, microsecond=0, minute=0,hour=0)
        last_day_sel_month = calendar.monthrange(sel_year,sel_month)[1]
        sel_mnt_last_date = datetime.datetime(sel_year,sel_month,last_day_sel_month)
        sel_mnt_last_working_day = prevWorkingDay(sel_mnt_last_date)
    else:
        selected_month_dt = ''
    cur_mnt_last_working_day = prevWorkingDay(cur_mnt_last_date)
    #first_day_next_mnth = cur_mnt_last_date+datetime.timedelta(days=1)
    ##building from month list for last working day of the month
    if evry == 'LAST WORKING DAY OF A MONTH':
        if selected_month_dt:
            first_date = sel_mnt_last_working_day.strftime('%Y-%m-%d')
        diff_delta = int((cur_mnt_last_working_day - current_dt).total_seconds()/float(60*60*24))
        if diff_delta > 0:#Today's date is less than the last working day of current month    
            for i in range(current_month-1,current_month+11):#show start months including current month
                #l = deepcopy(i)
                year_str = current_year
                if i > 11:
                    #i = i%12
                    #l = l%12
                    year_str = current_year+1
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                #month_dict[i] = all_momths_dict[i]
            #print month_str
        else:
            for i in range(current_month,current_month+12):#show start months excluding current month
                year_str = current_year
                if i > 11:
                #    i = i%12
                    year_str = current_year+1
                #month_dict[i] = all_momths_dict[i]
                if i == 24:##in the last day of december
                    year_str = current_year+2
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
    elif evry == 'LAST DAY OF MONTH' or evry == 'A SPECIFIC DATE OF THE MONTH':
        if selected_month_dt:
            if evry == 'LAST DAY OF MONTH':
                    first_date = sel_mnt_last_date.strftime('%Y-%m-%d')
            elif evry == 'A SPECIFIC DATE OF THE MONTH':
                    first_date = selected_month_dt.strftime('%Y-%m')##send only year and month so that javascript will add specified date
        diff_delta1 = int((cur_mnt_last_date - current_dt).total_seconds()/float(60*60*24))
        #print 'current_day',current_day,'int(spec_dt)',int(spec_dt)
        if spec_dt !='0' and current_day >= int(spec_dt) and evry == 'A SPECIFIC DATE OF THE MONTH':
            sp_date_more = 1
        else:
            sp_date_more = 0
        if diff_delta1 < 1 or sp_date_more:#today is the last day of the month
            for i in range(current_month,current_month+12):#show start months excluding current month
                year_str = current_year
                if i > 11:
                #    i = i%12
                    year_str = current_year+1
                #month_dict[i] = all_momths_dict[i]
                if i == 24:##in the last day of december
                    year_str = current_year+2
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
        else:
            for i in range(current_month-1,current_month+11):#show start months including current month
                year_str = current_year
                if i > 11:
                    year_str = current_year+1
                #    i = i%12
                #month_dict[i] = all_momths_dict[i]
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
    elif evry in config_dict.keys():
        if selected_month_dt:
            first_date = prevWeekday(sel_mnt_last_date,config_dict[evry]).strftime('%Y-%m-%d')
            #print getLastDayOfNextMonth(selected_month_dt),'**********************','getLastDayOfNextMonth(',selected_month_dt,')'
            #print prevWeekday(sel_mnt_last_date,config_dict[evry]),'prevWeekday(',sel_mnt_last_date,config_dict[evry],')'
        #lastDayOfNextMonth=getLastDayOfNextMonth(firstDate)
        diff_delta2 = int((prevWeekday(cur_mnt_last_date,config_dict[evry]) - current_dt).total_seconds()/float(60*60*24))    
        if diff_delta2 <= 0:
            for i in range(current_month,current_month+12):#show start months excluding current month
                year_str = current_year
                if i > 11:
                #    i = i%12
                    year_str = current_year+1
                if i == 24:
                    year_str = current_year+2
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
        else:
            for i in range(current_month-1,current_month+11):#show start months including current month
                year_str = current_year
                if i > 11:
                #    i = i%12
                   year_str = current_year+1
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
    elif evry in week_list:
        if selected_month_dt:
            #if selected_month_dt > current_dt:##future date
            if current_month != selected_month_dt.month:
                date_for_calculation = selected_month_dt.replace(day=1)
            else:
                date_for_calculation = deepcopy(selected_month_dt)
            if week_list.index(evry)-date_for_calculation.weekday() > 0:
                count_sel_date = week_list.index(evry)-date_for_calculation.weekday()
            else:
                count_sel_date = 7-abs(week_list.index(evry)-date_for_calculation.weekday())
            first_date = (date_for_calculation+datetime.timedelta(days=count_sel_date)).strftime('%Y-%m-%d')
            #print 'first_date--',first_date,'  selected_month_dt--',selected_month_dt,'count_sel_date',count_sel_date,'date_for_calculation',date_for_calculation
        if week_list.index(evry)-current_dt.weekday() > 0:
            next_day_count = week_list.index(evry)-current_dt.weekday()
        else:
            next_day_count = 7 - abs(week_list.index(evry)-current_dt.weekday())
        date_of_req = current_dt+datetime.timedelta(days=next_day_count)
        #print 'date_of_req@@@@@@@@@@@@@@',date_of_req,'int((date_of_req - current_dt).total_seconds()/float(60*60*24))',int((date_of_req - current_dt).total_seconds()/float(60*60*24))
        #if int((date_of_req - current_dt).total_seconds()/float(60*60*24)) < 0:
        if current_dt.month != date_of_req.month:##week day is not falling in the current month
            for i in range(current_month,current_month+12):#show start months excluding current month
                year_str = current_year
                if i > 11:
                #    i = i%12
                    year_str = current_year+1
                if i == 24:
                    year_str = current_year+2
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
             
        else:
            for i in range(current_month-1,current_month+11):#show start months including current month
                year_str = current_year
                if i > 11:
#                    i = i%12
                    year_str = current_year+1
                if month_str == "":
                    month_str += str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
                else:
                    month_str += '|'+str((i%12)+1)+'-'+str(year_str)+'~'+all_momths_dict[i%12]+' ['+str(year_str)+']'
        #diff_delta4 =
    
    if request.GET.has_key('forfirstdate') and request.GET['forfirstdate'] == 'forfirstdate':
        return HttpResponse(first_date)
    else:
        month_str = '0~Select Month|'+month_str
        return HttpResponse(month_str)
def generateAutoSchedules(request):
    strt_dt = request.GET.get('strt_from','')
    strt_from = datetime.datetime.strptime(strt_dt,'%Y-%m-%d')
    #print '*(&^(*&*))))))))))))))))))',strt_from
    frequency = request.GET.get('evry','')
    if frequency in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']:
        frequency = 'WEEKLY'
    cycle = int(request.GET.get('cycle'))
    payoutDate = strt_from-datetime.timedelta(days=2)
    response_text = ''
    #print "dt_lst = getPayCycle(frequency='A SPECIFIC DATE OF THE MONTH',cycles=",cycle,"gracePeriod=1,firstUserDate=",strt_from,"holidayFlag=0,decemberLogic=0)"
    dt_lst = paydates.getPayCycle(frequency=frequency,cycles=cycle,gracePeriod=1,firstUserDate=strt_from,payoutDate=payoutDate,holidayFlag=0,decemberLogic=0)
    if dt_lst:
        for dt in dt_lst:
            if response_text == "":
                response_text += datetime.datetime.strftime(dt,'%Y-%m-%d')
            else:
                response_text += '~'+datetime.datetime.strftime(dt,'%Y-%m-%d')
    return HttpResponse(response_text)
def tempArrangementDateValidation(request):
    '''
    Validations for TA:
    1=>Duplicate dates.
    2=> Having two or more dates with a diffrerance less than or equals to the min day.
    3=> No Change in the input temp paydates received from TMS application.
    4=> Received TA Date is <= todays date.
    5=> Received TA Amount is <=0.00.
    6=> TA Reason Code not Provided
    '''
    min_day_diff = pcconfig.TA_MIN_DAYS_DIFF
    post_str = request.POST.get('post_str','')
    loan_id = request.POST.get('loan_id')
    ta_reason = request.POST.get('ta_res')
    from_page = request.POST.get('from_page')
    temp_key_val = []
    sorted_lst = []
    return_str = ''
    ta_dict = {}
    err_code = 0
    if post_str:
        lst1 = post_str.split('|')
        for x in lst1:
            temp_key_val.append((x.split('~')[0],x.split('~')[1]))
        post_dict = {datetime.datetime.strptime(k,'%Y-%m-%d'):v for k,v in temp_key_val}
        rec_dict = {datetime.datetime.strptime(k,'%Y-%m-%d').date():Decimal(v) for k,v in temp_key_val}
        if len(post_dict.keys()) < len(temp_key_val):##having same dates
            err_code = 1
        if not err_code:
            con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
            query = "select payment_dt dt, sum(payment_amt) amt from temparrangement where loan_id = %s and active=1 \
                    and override_flag=0 group by temppayment_nbr"
            ta = con.get_all_results(query, args=(loan_id))
            for temp in ta:
                ta_dict[temp['dt']] = temp['amt']
#            ta_dict = {temp['dt']:temp['amt'] for temp in ta} #Dict comprehension
            count = 0
            today_dt = datetime.date.today()
            for date in rec_dict.keys():
                if date <= today_dt:
                    err_code = 4
                    break
                if rec_dict[date] <=0:
                    err_code = 5
                    break
                if ta_dict and date in ta_dict.keys() and rec_dict[date] == ta_dict[date]:
                    count+=1
            if count == len(rec_dict) and len(ta_dict) == count:
                err_code = 3
        if not err_code:
            sorted_lst = sorted(post_dict.keys())
            revese_sorted_lst = sorted_lst[::-1]
            for i in range(len(revese_sorted_lst)-1):
                for j in range(i+1,len(revese_sorted_lst)):    
                    if abs((revese_sorted_lst[i] - revese_sorted_lst[j]).days) <= min_day_diff:
                        err_code = 2
#                        return HttpResponse(err_code)

        if not err_code and not ta_reason:
            err_code = 6
            
        if err_code not in (1,3,4,5,6):
            if from_page == 'refund':
                sorted_lst = sorted(post_dict.keys())
                dt = str(sorted_lst[0]-datetime.datetime.now())
                if 'day' in dt:
                    pay_dt =int(dt.split(' ')[0])
                else:
                    pay_dt = 0 
                if  pay_dt < url_settings.REFUND_TA_BREATHER :
                    err_code=7
            for dte in sorted_lst:
                print dte
                if return_str == "":
                    return_str += datetime.datetime.strftime(dte,'%Y-%m-%d')+'~'+post_dict[dte]
                else:
                    return_str += '|'+datetime.datetime.strftime(dte,'%Y-%m-%d')+'~'+post_dict[dte]    
    return HttpResponse(simplejson.dumps({'return_str':return_str,'err_code':err_code,'min_day_diff':min_day_diff}))

def cheque_direct_deposit(request):
#    import pdb; pdb.set_trace()
    return render_to_response("custdetail/cheque_popup.html")

def random_number_gen(trandt,loan_id):
    date_time_now = datetime.datetime.utcnow()
    random_head=random.randint(101,999)
    order_id = trandt+str(date_time_now.microsecond)+'_'+str(random_head)+'_'+str(loan_id)
    return order_id


def trivial_refunds(request):
    from tms.refund import views as refund_views
    return refund_views.trivial_refunds(request)

trivial_refunds = maintenance_deco_popups(trivial_refunds)


def alreadyRefunded(request):
    """
    Refund the amount to customer back.
    Gets Trasaction date range and refund amount through post.
    calls the api 'refund' for refunding
    """

    msg= ''    
    if request.method=='GET':
        loan_id = request.GET['loan_id']
        if 'msg' in request.GET:
           msg = request.GET['msg']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    #adding status variable initialisation##for dailyrun temp table
    status = None

    sanity_check_done = 0

    refund_reason = ['Dispute','Normal']
    #logger.info('refund :: loan_id :: '+str(loan_id))
    if request.session.has_key('refnd_msg'):
        msg = request.session['refnd_msg']
        del request.session['refnd_msg']


    if request.method == 'POST':
        payment_method = 'Normal' #request.POST['refund_reason']
        create_date = datetime.datetime.now()
        try:
            loan = Loan.objects.get(pk=loan_id)
            waterfall_flag = pcfunc.waterfallcheck(loan.loan_id)
            keytranid = getkeytranid(loan_id)
            if not waterfall_flag:
                from_date = request.POST['refund_dt']
                to_date = request.POST.get('to_dt')
                refund_amt = request.POST['amt']
                logger.info('refund :: '+str(keytranid)+' :: loan_id,refund_amt,from_date,to_date :: '+str(loan_id)+','+str(refund_amt)+','+str(from_date)+','+str(to_date))
                if from_date:
                    if not to_date:
                        transactions = Transactions.objects.filter(tran_dt__gte=from_date, loan=loan.loan_id, debit__gt=0, payment_type__in=[loanstatusconfig.PAYMENTTYPE["PULL"]],payment_method__in=['WATERFALL','IMMEDIATE PULL','SSP']).order_by('-debit')
                    else:
                        to_date = to_date + datetime.timedelta(days=1)
                        transactions = Transactions.objects.filter(tran_dt__range=[from_date, to_date], loan=loan.loan_id, debit__gt=0, payment_type__in=loanstatusconfig.PAYMENTTYPE["PULL"],payment_method__in=['WATERFALL','IMMEDIATE PULL','SSP']).order_by('-debit')
                    excess = 0
                    if transactions:
                        tran_list=[]
                        rem_amt = float(refund_amt)
                        transactions = list(transactions)
                        #Getting already refunded list
                        refunded_list = get_refunded_transactions(loan_id, from_date, to_date)
                        logger.info('refund :: '+str(keytranid)+' :: list of transactions having already refunded :: '+str(refunded_list))
                        # Making neccessary correction in transactions.
                        if refunded_list:
                            #tranid_list = [tran_id[0] for tran_id in refunded_list]
                            for tran in transactions:
                                for tranid in refunded_list:
                                    if tran.merchant_txn_id == tranid[0]:
                                        transactions[transactions.index(tran)].debit -= tranid[1]
                            transactions = sorted(transactions, key=lambda x: x.debit, reverse=True)                            
                        for tran in transactions:
                            if float(tran.debit) == rem_amt:
                                tran_list.append((tran, tran.debit))
                                rem_amt = 0
                                excess = 0
                                break
                            elif float(tran.debit) > rem_amt:
                                excess = tran
                            elif tran.debit >0:
                                if excess:
                                    tran_list.append((excess, rem_amt))
                                    rem_amt = 0
                                    excess =0
                                    break
                                tran_list.append((tran, tran.debit))
                                rem_amt -= float(tran.debit)
                                if not rem_amt:
                                    break
                        if excess:
                            tran_list.append((excess, rem_amt))
                            rem_amt = 0

                        if not rem_amt:
                            logger.info('refund :: '+str(keytranid)+' :: transactions for refund :: '+str([(vars(i), j) for (i,j) in tran_list]))
                            logger.info('refund :: '+str(keytranid)+' :: Got all required transactions ')
                            returned = 0
                            loan_dict = {"tranid" :keytranid}
                            for record in tran_list:
                                loan_dict.update(merchant_service=str(record[0].merchant_name),
                                                  merchant_tid=str(record[0].merchant_txn_id),
                                                  return_amt=record[1],
                                                  trantype=payment_method + ' Refund',
                                                  loan_id=str(loan_id))
                                req_dict = {}
                                try:
                                    if  record[0].merchant_name not in ('Barclays', 'VoicePay'):
                                        msg = "Please select any Merchant service provider"
                                    req_dict.update({"KeyTranID" : loan_dict['tranid'],
                                                     "TranType" : loan_dict['trantype'],
                                                     "ReturnAmount" : loan_dict['return_amt'],
                                                     "OrigId" : loan_dict['merchant_tid'],
                                                     'MerchantService': record[0].merchant_name,
                                                     'LoanID': 'loan_id'})
                                    sanityParser.check_sanity(req_dict, 0)
                                    sanity_check_done = 1
                                    logger.info('refund :: '+str(keytranid)+' :: sanity check done :: merchant_txn_id ::'+str(record[0].merchant_txn_id))

                                except FieldNotFound, e:
                                    msg = '<ERROR>Missing Field or Empty Field:: '+str(e.args[1])
                                except LoggedExceptions, e:
                                    msg = str(e.args[1])
                                tran_time = create_date
                                logger.info("refund :: REQUEST :: "+str(keytranid)+ " :: "+str(req_dict))
                                if sanity_check_done:
                                    logger.info('refund :: '+str(keytranid)+' :: refunding the transaction:: '+str(vars(record[0])))
                                    logger.info('refund :: '+str(keytranid)+ ':: refunding amount of '+str(record[1]))
                                    if str(record[0].merchant_name) == 'VoicePay':
                                        voicepay_obj = VoicePay(logger)
                                        status, txn_id, exitmsg, failure_note = voicepay_obj.connectService(req_dict)
                                    elif str(record[0].merchant_name) == 'Barclays':
                                        barclays_obj = Barclays(logger)
                                        status, txn_id, exitmsg, failure_note = barclays_obj.connectService(req_dict)
                                    logger.info("refund :: "+str(keytranid)+" ::  amount, status, reason,payment_type, tran_time,merchant_name, loan_id :: " + str(loan_dict['return_amt'])+","+ status+","+exitmsg+","+"Refund"+","+ str(tran_time)+","+ str(req_dict['MerchantService'])+","+ str(loan_dict['loan_id']))
                                    Merchant_service_log_id = dbtmsapi.update_merchant_service_log(str(loan_dict['return_amt']), status, exitmsg, "Refund", str(tran_time), str(req_dict['MerchantService']), str(loan_dict['loan_id']), failure_note)
                                    logger.info("refund :: "+str(keytranid)+" :: updated merchant service log :: "+str(Merchant_service_log_id))
                                    if status == 'success':
                                        logger.info('refund :: '+str(keytranid)+' return successful :: merchant_txn_id ::'+str(record[0].merchant_txn_id))
                                        logger.info('refund :: '+str(keytranid)+' return successful ')

                                        print traceback.format_exc()
                                        if payment_method == 'Normal':
                                            msg = pcfunc.refund(loan_id,None, tran_time, 0, loan_dict['return_amt'], "MERCHANT PROVIDER",loan_dict['merchant_tid'], str(req_dict['MerchantService']), request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["NORMALREFUND"],done_on="DEBIT CARD")
                                        elif payment_method == 'Dispute':
                                           transaction=Transactions(loan_id=loan_id,credit=loan_dict['return_amt'],debit=0.0,tran_dt=tran_time,\
                                                                    payment_method="MERCHANT PROVIDER",merchant_txn_id=loan_dict['merchant_tid'],\
                                                                    merchant_name=str(req_dict['MerchantService']),create_dt=create_date,changed_by=request.session['username'],payment_type=loanstatusconfig.PAYMENTTYPE["OPF"],done_on="DEBIT CARD")
                                           transaction.save()
                                        returned = returned + loan_dict['return_amt']
                                        logger.info('refund :: '+str(keytranid)+' returned_amt ::'+str(returned))
                                        request.session["update_flag"]=1
                                    else:
                                        logger.warn('refund :: '+str(keytranid)+' failure pull :: '+failure_note)
                                        msg = "[Refund Failed] ", exitmsg or status


                            if returned > 0:
                                msg= 'money returned = '+str(returned)
                            else:
                                msg = 'Failure to refund money from merchant service. money returned = '+str(returned)
                        else:
                            msg = "The amount for refund is greater than amount pulled."
                    else:
                        msg = "No transaction found!!"
            else:
                msg = "Waterfall is currently running for this Loan. Please try later."
            if status == 'success':
                ## for daily_run phase 2: whenever there is a transaction, paydates change, status change
                #loan_id shd be flagged in DeltaMatrix table
                daily_run_date = datetime.datetime.now() + datetime.timedelta(days=1)
                if isDailyRunStarted(date_of_run=daily_run_date):
                    updateDeltaMatrix(loan_id,'transaction')
            logger.info('refund :: '+str(keytranid)+' '+str(msg)+'\n\n')
            return HttpResponse(str(msg))
        except Loan.DoesNotExist:
            msg = 'Invalid Loan'
            logger.debug('refund :: '+str(keytranid)+' '+str(msg)+'\n\n')
            return HttpResponseRedirect('/info/amt_due/refund/?loan_id='+str(loan_id)+"&msg="+str(msg))
        except Exception, e:
            t = traceback.format_exc()
            print t
            msg = 'Failed to refund!'
            logger.warn('refund :: '+str(keytranid)+' '+str(msg))
            logger.error('refund :: '+str(keytranid)+' '+str(e))
            logger.debug('refund :: '+str(keytranid)+' '+str(t)+'\n\n')
            return HttpResponseRedirect('/info/amt_due/refund/?loan_id='+str(loan_id)+"&msg="+str(msg))
#    related_tbl=Loan_Info.objects.filter(loan=loan_id,override_flag=0)[0]
#    fund_date=""
#    if related_tbl.fund_dt:
#        fund_date=datetime.date.strftime(related_tbl.fund_dt, "%Y-%m-%d")
#    else:
#        return HttpResponse('Loan is not yet ACTIVE!')

    cxt = Context({'loan_id':loan_id, 'msg':msg, 'refund_reason':refund_reason})
    return render_to_response('custdetail/refund.html', cxt)
alreadyRefunded = maintenance_deco_popups(alreadyRefunded)




#@transaction.commit_manually
def cheque_popup(request):
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')

    msg = ''
    update_flag=0
    transaction_commit_flag=0
    if request.session.has_key("update_flag"):
        update_flag=request.session["update_flag"]
        del request.session["update_flag"]

    if request.session.has_key('cheque_msg'):
        msg = request.session['cheque_msg']
        del request.session['cheque_msg']
        
    cheques, direct_deps = [], []
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        fund_flag =Loan_Info.objects.filter(loan=loan.loan_id, override_flag=0)
        loan_status= get_loan_status_by_loan_id(loan_id)
        if not fund_flag[0].booked_dt or loan_status=='BOOKED':
            if transaction_commit_flag:
                transaction.commit()
            else:
                transaction.rollback()
            return HttpResponse('Not Applicable')
        direct_deps = list(Direct_Deposit.objects.filter(loan=loan.loan_id))
        cheques = list(Cheque.objects.filter(loan=loan.loan_id, override_flag=0))
    except Loan.DoesNotExist:
        msg = "Invalid Loan!"
    except Exception, e:
        print e
    isOB = isOutStandingBalance(loan_id)
    chqDD = get_Cheque_DD_Details(loan_id)
    if request.method=='POST':
#        import pdb;pdb.set_trace()
        logger.info('cheque :: loan_id :: '+str(loan_id))
        create_date=datetime.datetime.now()
        try:
            waterfall_flag = pcfunc.waterfallcheck(loan.loan_id)
            if waterfall_flag:
                msg = "Waterfall is currently running. Please try later."
                raise Exception
#            record_list = []
#            new_record_list = []
#            data = request.POST.copy()
#            for k, v in data.iteritems():
#                if v == 'on':
#                    record_list.append(k)
#            for rec in record_list:
#                if rec.__contains__('record_nbr'):
#                    idx = rec[10:]
#                    if idx == u'0' and data['payment_method'+idx] == 'direct_dep':
#                        new_record_list.append({'reference_id': data['reference_id'+idx],'payment_method':data['payment_method'+idx],'amount': data['amount'+idx],'receive_dt': data['receiving_dt'+idx]})
#                    else:
#                        new_record_list.append({'reference_id': data['reference_id'+idx],'payment_method':data['payment_method'+idx],'amount': data['amount'+idx],'receive_dt': data['receiving_dt'+idx],'status': data['status'+idx],'status_dt': data['status_dt'+idx]})
#                else:
#                    idx = rec[0]
#                    if data['['+idx+',2]'] == 'direct_dep':
#                        new_record_list.append({'reference_id': data['['+idx+',1]'],'payment_method':data['['+idx+',2]'],'amount':data['['+idx+',3]'],'receive_dt': data['['+idx+',4]']})
#                    else:
#                        new_record_list.append({'reference_id': data['['+idx+',1]'],'payment_method':data['['+idx+',2]'],'amount':data['['+idx+',3]'],'receive_dt': data['['+idx+',4]'],'status': data['['+idx+',5]'],'status_dt': data['['+idx+',6]']})
#
#            for record in new_record_list:
            ref_id = request.POST['reference_id']
            amt = request.POST['amount']
            rec_dt = request.POST['receiving_dt']
            pay_method = request.POST['payment_method']
            clear_dt = request.POST['clear_dt']
            record = {'reference_id':ref_id, 'amount':amt, 'receive_dt':rec_dt, 'payment_method':pay_method,'status_dt':clear_dt, 'status':'cleared'}
            logger.info('cheque :: loan_id :: '+str(loan_id)+' :: record :: '+str(record))  
            reference_id = record['reference_id']
            amount = record['amount']
            receive_dt = record['receive_dt']
            logid= get_log_id_by_loan_id(loan_id)
            if record['payment_method'] == 'cheque':
                if reference_id and amount and receive_dt:
                    state_change_dt=record['status_dt'] or receive_dt
                    if record['status'] == "bounced":
                        bounced=1
                    elif record['status'] == 'cleared':
                        bounced=0
                    try:
                        refund_flag = 0
                        payment_flag = 0
                        cheque = Cheque.objects.get(cheque_nbr=reference_id, loan=loan, override_flag=0)
                        logger.info('cheque :: loan_id :: '+str(loan_id)+' :: Updating existing cheque ')
                        if cheque.bounce_flag != bounced or str(cheque.clear_dt) != state_change_dt:
                            if cheque.bounce_flag == 0 and bounced == 1:
                                refund_flag = 1
                                logger.info('cheque :: loan_id :: '+str(loan_id)+' :: Cheque bounced!! ')
                            elif cheque.bounce_flag == 1 and bounced == 0:
                                payment_flag = 1
                                logger.info('cheque :: loan_id :: '+str(loan_id)+' :: cheque cleared!! ')
                            cheque.override_flag=1
                            cheque.save()
                            new_cheque = Cheque(cheque_nbr=reference_id, cheque_amt=amount, \
                                                receive_dt=receive_dt, clear_dt=state_change_dt, \
                                                bounce_flag=bounced, override_flag=0, create_dt=create_date, \
                                                loan=loan)
                            new_cheque.save()
                            if refund_flag:
                                msg = pcfunc.refund(loan_id, new_cheque.cheque_nbr, state_change_dt, 0,
                                                    float(amount), 'CHEQUE', "", "",
                                                    request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["NORMALREFUND"],
                                                    done_on="BANK ACCOUNT")
                                logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: response from refund :: '+str(msg))
                                if msg.__contains__('FAILURE::'):
                                    raise CustomException, msg
                                add_gcm_notes(logid,"Cheque","Cheque with "+str(amount)+" has bounced on "+str(state_change_dt),
                                              request.session['username'],create_date)
#                                request.session['cheque_msg'] = msg
                                request.session["update_flag"]=1
                            if payment_flag:
                                msg = pcfunc.recvmoney(loan_id,cheque.cheque_nbr, receive_dt, float(amount), 0,
                                                'CHEQUE','', '', request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"],done_on="BANK ACCOUNT")
                                if msg.__contains__('FAILURE::'):
                                    raise CustomException, msg
                                add_gcm_notes(logid,"Cheque","A cheque was received with amount "+str(amount)+" on "+str(receive_dt),
                                              request.session['username'],create_date)
                                request.session['cheque_msg'] = msg
                                request.session["update_flag"]=1
                        else:
                            logger.info('cheque :: loan_id :: '+str(loan_id)+' :: No changes made!  ')

                    except Cheque.DoesNotExist:
                        try:
                            logger.info('cheque :: loan_id :: '+str(loan_id)+' :: Adding new cheque ')
                            cheque = Cheque(cheque_nbr=reference_id, cheque_amt=amount, \
                                            receive_dt=receive_dt, clear_dt=state_change_dt, \
                                            bounce_flag=0, override_flag=0, create_dt=create_date, \
                                            loan=loan)
                            cheque.save()
                            msg = pcfunc.recvmoney(loan_id,cheque.cheque_nbr, receive_dt, float(amount), 0,
                                            'CHEQUE','', '', request.session['username'],create_date,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"],done_on="BANK ACCOUNT")
                            logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: response from recvmoney :: '+str(msg))
                            if msg.__contains__('FAILURE::'):
                                raise CustomException, msg
                            add_gcm_notes(logid,"Cheque",str(amount)+" has recieved as a cheque on "+str(receive_dt),
                                          request.session['username'],create_date)
                            request.session['cheque_msg'] = msg
                            request.session["update_flag"]=1

                        except CustomException, e:
                            request.session['cheque_msg'] = e
                            delete_transaction(loan_id, cheque.cheque_nbr, float(amount),0, 'cheque')
                            transaction.rollback()
#                                return HttpResponseRedirect('/info/cheque/')
                        except Exception, e:
                            request.session['cheque_msg'] = "Failed, Please try again later."
                            transaction.rollback()
                            logger.info('cheque :: loan_id :: '+str(loan_id)+' :: '+str(traceback.format_exc()))
#                                return HttpResponseRedirect('/info/cheque/')
                        else:
                            transaction.commit()
                            transaction_commit_flag=1
                            chk_cc_paid_not=Downpayments.objects.filter(loan=loan_id,override_flag=0,downpayment_type='CC')
                            if chk_cc_paid_not:
                                if chk_cc_paid_not[0].paid_amt>0:
                                    flag=1
                                else:
                                    flag=0
                                updateCreditCheckStatus(loan_id,flag)

#                                return HttpResponseRedirect('/info/cheque/')

                    except CustomException, e:
                        request.session['cheque_msg'] = e
                        delete_transaction(loan_id, cheque.cheque_nbr, 0, float(amount),'cheque')
                        transaction.rollback()
#                            return HttpResponseRedirect('/info/cheque/')
                    except Exception, e:
                        transaction.rollback()
                        request.session['cheque_msg'] = "Failed!! Please try again!!"
                        logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: '+str(traceback.format_exc()))
#                            return HttpResponseRedirect('/info/cheque/')
                    else:
                        transaction.commit()
                        transaction_commit_flag=1
#                            return HttpResponseRedirect('/info/cheque/')
                else:
                    logger.info('cheque :: loan_id :: '+str(loan_id)+' :: there is no valid data')
            elif record['payment_method'] == 'direct_dep':
                if reference_id and amount and receive_dt:
                    try:
                        direct_dep = Direct_Deposit(dd_nbr=reference_id, deposit_amt=amount, deposit_date=receive_dt, create_dt=create_date, loan=loan)
                        direct_dep.save()
                        msg = pcfunc.recvmoney(loan_id, direct_dep.dd_nbr, receive_dt, float(amount), 0,
                                        'DIRECT DEPOSIT', '', '', request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"],done_on="BANK ACCOUNT")
                        logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: direct deposit :: response from recvmoney :: '+str(msg))
                        if msg.__contains__('FAILURE::'):
                            raise CustomException, msg
                        #direct_deps.append(direct_dep)
                        add_gcm_notes(logid,"Direct Deposit",str(amount)+" has recieved as a Direct Deposit on "+str(receive_dt),request.session['username'],create_date)
                        request.session['cheque_msg'] = msg
                        request.session["update_flag"]=1
                    except CustomException, e:
                        request.session['cheque_msg'] = e
                        delete_transaction(loan_id, direct_dep.dd_nbr, float(amount),0, 'direct deposit')
                        transaction.rollback()
#                            return HttpResponseRedirect('/info/cheque/')
                    except Exception, e:
                        request.session['cheque_msg'] = 'Falied!! Please try later.'
                        transaction.rollback()
                        logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: direct deposit :: '+str(traceback.format_exc()))
#                            return HttpResponseRedirect('/info/cheque/')
                    else:
                        transaction.commit()
                        transaction_commit_flag=1
                        chk_cc_paid_not=Downpayments.objects.filter(loan=loan_id,override_flag=0,downpayment_type='CC')
                        if chk_cc_paid_not:
                                if chk_cc_paid_not[0].paid_amt>0:
                                    flag=1
                                else:
                                    flag=0
                                updateCreditCheckStatus(loan_id,flag)
#                            return HttpResponseRedirect('/info/cheque/')
                else:
                    request.session['cheque_msg'] = "Please give all values."
                    logger.info('cheque :: loan_id :: '+str(loan_id)+' ::direct deposit :: there is no valid data')
            else:

                if reference_id and amount and receive_dt:
                    try:
                        msg = pcfunc.recvmoney(loan_id,reference_id , receive_dt, float(amount), 0,
                                        record['payment_method'].upper(), '', '', request.session['username'], create_date,paymentType=loanstatusconfig.PAYMENTTYPE["PULL"],done_on="BANK ACCOUNT")
                        logger.debug('cheque :: loan_id :: '+str(loan_id)+' ::'+ record['payment_method'].upper()+ ':: response from recvmoney :: '+str(msg))
                        if msg.__contains__('FAILURE::'):
                            raise CustomException, msg
                        add_gcm_notes(logid,record['payment_method'].upper(),str(amount)+" has recieved as a "+record['payment_method'].upper()+" on "+str(receive_dt),request.session['username'],create_date)
                        request.session['cheque_msg'] = msg
                        request.session["update_flag"]=1
                    except CustomException, e:
                        request.session['cheque_msg'] = e
                        delete_transaction(loan_id, reference_id, float(amount),0, record['payment_method'].upper())
                        transaction.rollback()
                    except Exception, e:
                        request.session['cheque_msg'] = 'Falied!! Please try later.'
                        transaction.rollback()
                        logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: ' + record['payment_method'].upper() +' :: '+str(traceback.format_exc()))
                    else:
                        transaction.commit()
                        transaction_commit_flag=1
                        chk_cc_paid_not=Downpayments.objects.filter(loan=loan_id,override_flag=0,downpayment_type='CC')
                        if chk_cc_paid_not:
                                if chk_cc_paid_not[0].paid_amt>0:
                                    flag=1
                                else:
                                    flag=0
                                updateCreditCheckStatus(loan_id,flag)
                else:
                    request.session['cheque_msg'] = "Please give all values."
                    logger.info('cheque :: loan_id :: '+str(loan_id)+' ::'+record['payment_method'].upper()+' :: there is no valid data')
            
        except Exception, e:
            logger.debug('cheque :: loan_id :: '+str(loan_id)+' :: '+str(traceback.format_exc()))
    fund_date=fund_flag[0].booked_dt
    if transaction_commit_flag:
        transaction.commit()
        return  HttpResponseRedirect('/info/amt_due/chequeDirectDeposit/?loan_id=%s'%(loan_id))
    else:
        transaction.rollback()
        
    bal_infm=get_balance_dtls(loan_id)[0]
    Max_OB=bal_infm['OutstandingPrincipal']+bal_infm['OutstandingInterest']+ bal_infm['OutstandingFee']
    return render_to_response("custdetail/cheque_popup.html", {'cheques':cheques,
                                                                 'direct_deps':direct_deps,'msg': msg,"isOB":isOB,
                                                                 "update_flag":update_flag,'fund_date':fund_date,'loan_id':loan_id,"Max_OB":Max_OB,"chqDD":chqDD})
cheque_popup = transaction.commit_manually(cheque_popup)
cheque_popup=maintenance_deco_popups(cheque_popup)

def get_Cheque_DD_Details(loan_id):
    try:        
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        tranQuery = "select payment_method as type,reference_id as refid,debit as amt,date(tran_dt) as dt from Transactions where loan_id=%s and payment_method in ('CHEQUE','DIRECT DEPOSIT','EPDQ','STANDING ORDER') and debit > 0"
        result = con.get_all_results(tranQuery, args=(loan_id))       
        
        if len(result)>0:
            return result
        else:
            return ('None')
    except Exception, e:
        logger.debug('Error :: loan_id :: '+str(loan_id)+' :: '+str(traceback.format_exc()) + str(e))
        
#Two way sms views
def upload_sms(request):
    '''
        TWO WAY SMS : This function will redirect to SMS upload UI page and once file has uploaded.
        The uploaded file will be validated for file format and moves to further process.
    '''
    try:
        tway_sms_log = customlogger.basiclogger("SMS_Upload", "TWO_WAY_SMS")
        username = request.session['username']
        menu = request.session['sessionmenu']
        keytranid = getKeyTranID()
        exists_flag = 0
        error_flag = 0
        success_flag = 0
        error_dict = {}
        cur_date = datetime.datetime.now()
        validFileFormat = 'text/csv'
        header_format = queueconfig.TWO_WAY_SMS_CONF['CSV_HEADER']
        if request.method=="GET":
            pass
            
        elif request.method == "POST":
            
            if 'datafile' in request.FILES:
                
                timelist = ctime().split()
                file_name = request.FILES['datafile']
                
                if (str(file_name).lower()[:-11]+'.csv' != 'two_way_sms_'+ datetime.date.today().strftime("%Y%m%d")+'.csv' or 
                    str(file_name).lower()[21:-4] > datetime.datetime.now().strftime('%H%M%S')):
                    
                    tway_sms_log.info("File Name received is invalid : " +str(file_name))
                    raise Exception, 'File Name Invalid'
                
                file_path = '%s/%s/%s/%s/%s' % (MEDIA_ROOT_CSV, timelist[4],timelist[1],timelist[2],file_name)
                f_read = os.path.isfile(file_path)
                
                if not f_read:
                    
                    file_name = request.FILES['datafile']
                    
                    if not file_name.content_type == validFileFormat:
                        
                        tway_sms_log.info("File received not in valid format" +str(file_name))
                        raise Exception, 'File not in prescribed format'
                    
                    if file_name.size == 0:
                        
                        tway_sms_log.info("File received is empty" +str(file_name))
                        raise ValueError("Empty file uploaded.")

                    os.system("mkdir -p '%s/%s/%s/%s'" % (MEDIA_ROOT_CSV,timelist[4],timelist[1],timelist[2]))
                    destination = open('%s/%s/%s/%s/%s' % (MEDIA_ROOT_CSV, timelist[4],timelist[1],timelist[2],file_name), 'wb')

                    for chunk in request.FILES['datafile'].chunks():
                        
                        destination.write(chunk)
                        destination.close()
                else:
                    
                    exists_flag=1
            
            if not exists_flag:
                error_flag, msg = SMSUploaded.read_uploadedSMS_file(file_path, username, 'DD-1', 
                                                                    current_dt = cur_date, logger = tway_sms_log, keytranid=keytranid)
                
                if not error_flag:
                    success_flag = 1
                error_dict = {"error_flag":error_flag,"msg":str(msg)}
            else:
                error_dict = {'error_flag':1,'msg':'File Already Exist'}
                                
    except Exception,e:
        
        t = traceback.format_exc()
        tway_sms_log.error('Two way sms :: Exception caught '+str(keytranid)+'\n'+str(t))
        
        if e:
            error_dict = {"error_flag":1,"msg":str(e)}
        else:
            error_dict = {"error_flag":1,"msg":"Exception Raised While Uploading File. Contact BackEND team"}
        
    return render_to_response("custdetail/upload_sms.html",{"username":username, "menu":menu,"header_format":header_format,
                                                            "validFileFormat":validFileFormat,"error_dict":error_dict,"success_flag":success_flag})
    
def cpareinstate(request):
    '''
        This function differentiates the eligible loans and not eligibe loans of
         a customer and gets the due amount and OB of all the loans of the customer.  
    '''
    if request.method=='GET':
        loan_id = request.GET['loan_id']
    elif request.method=='POST':
        loan_id = request.POST['loan_id']
    else:
        return HttpResponse('Loan ID is Missing check with Back End Team!')    
    if request.session.has_key("username"):
        username=request.session['username']
    else:
        HttpResponse("Session Expired")
        
    card_special_prev = get_spl_privileges_by_usr_id(username,8)

    if str(card_special_prev).upper() == 'GRANT':
        store_id=Loan.objects.filter(loan_id=loan_id)[0].store_id
        try:
            con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
            sql = "select status_cd,entity_id,account_cust_id,due_amt from GCMS_Data.gcm_case \
                join (select loan_id,account_cust_id,fund_dt,store_id from Loan_Latest \
                l join Product p on l.product_id = p.product_id  and product_classification != 'LOC' \
                where account_cust_id = (select account_cust_id from Loan_Latest where loan_id=%s )) acc \
                on loan_id=entity_id and entity_type='loan' and acc.store_id='%s' \
                and status_cd not in %s and fund_dt is not null join Payments ps on ps.loan_id=acc.loan_id"%(loan_id,store_id,str(END_STATUS_CPA))

            loanStatus = con.get_all_results(sql)
            if len(loanStatus):
                cpaEgblList = []
                cpaNtEgblList = []
                loanStatusDict = {}
                custId = loanStatus[0]['account_cust_id']
                
                #chkCPAFlag,cpaSupFlag,cpaSupRsn,cpaReinstFlag,cpaImmPullFlag,cpaUpdateFlag = dbtmsapi.update_cpa_status(custId,store_id,username,logger)
                #getTotalHitsFrmDriver(loanStatus,custId,store_id,username)
                for i in range(len(loanStatus)):
                    tempDict = {}
                    cpaCnclSql = "select loan_id from CPA_cancellations where loan_id=%s and override_flag=0"%(loanStatus[i]['entity_id'])
                    cpaCnclLn = con.get_one_result(cpaCnclSql)
                    if cpaCnclLn:
                        cpaNtEgblList.append(int(loanStatus[i]['entity_id']))
                        tempDict['status'] = loanStatus[i]['status_cd']
                        tempDict['due_amt'] = loanStatus[i]['due_amt']
                    else:                    
                        if (loanStatus[i]['status_cd'] in LOAN_LEVEL_EXCLUSION_LIST) or (loanStatus[i]['status_cd'] in CUSTOMER_LEVEL_EXCLUSION_LIST):
                            cpaNtEgblList.append(int(loanStatus[i]['entity_id']))
                            tempDict['status'] = loanStatus[i]['status_cd']
                            tempDict['due_amt'] = loanStatus[i]['due_amt']
                        else:
                            cpaEgblList.append(int(loanStatus[i]['entity_id']))
                            tempDict['status'] = loanStatus[i]['status_cd']
                            tempDict['due_amt'] = loanStatus[i]['due_amt']
                    loanStatusDict[loanStatus[i]['entity_id']] = tempDict
                    
                loanIfo = {}
                cpaInfoDict = getTotalHitsFrmDriver(loanStatus,custId,store_id,username)
                if len(cpaEgblList):
                    loanIfo['cpaEblLoanList'] = getPastFuturePaydateForCPA(cpaEgblList,loanStatusDict)
                    for loan_id in loanIfo['cpaEblLoanList'].keys():
                        OB      = get_balance_dtls(loan_id)
                        loanIfo['cpaEblLoanList'][loan_id]['due_amt']   = loanStatusDict[loan_id]['due_amt']
                        loanIfo['cpaEblLoanList'][loan_id]['OB']        = OB[0]['OutstandingFee']+OB[0]['OutstandingPrincipal']+OB[0]['OutstandingInterest']                    
                        loanIfo['cpaEblLoanList'][loan_id]['status']    = loanStatusDict[loan_id]['status']
                else:
                    loanIfo['cpaEblLoanList'] = ''
                if len(cpaNtEgblList):
                    loanIfo['cpaNotEblLoanList'] = getPastFuturePaydateForCPA(cpaNtEgblList,loanStatusDict)
                    for loan_id in loanIfo['cpaNotEblLoanList'].keys():
                        OB      = get_balance_dtls(loan_id)
                        loanIfo['cpaNotEblLoanList'][loan_id]['due_amt'] = loanStatusDict[loan_id]['due_amt']
                        loanIfo['cpaNotEblLoanList'][loan_id]['OB'] = OB[0]['OutstandingFee']+OB[0]['OutstandingPrincipal']+OB[0]['OutstandingInterest']
                        loanIfo['cpaNotEblLoanList'][loan_id]['status']    = loanStatusDict[loan_id]['status']               
                else:
                    loanIfo['cpaNotEblLoanList'] = ''
                
                content = {'cpaEblLoans':tuple(cpaEgblList),'cpaEblList':loanIfo['cpaEblLoanList'],\
                           'cpaNotElList':loanIfo['cpaNotEblLoanList'],'cpaInfo':cpaInfoDict}
                return render_to_response("custdetail/cpareinstate.html",content)
        except Exception,e:
            logger.debug('CPA :: Process for reinstate CPA :: '+str(traceback.format_exc()) + str(e))
            content = {'techError':'Technical Error. Please try again.'}
            return render_to_response("custdetail/cpareinstate.html",content)            
    else:
        logger.debug("You do not have permission to Reinstate CPA.")
        content = {'techError':'You do not have permission to Reinstate CPA.'}
        return render_to_response("custdetail/cpareinstate.html",content)          

def getPastFuturePaydateForCPA(loanDict,loanStatusDict):
    '''
        This function returns a dictionary which contains previous pay date and 
        future pay date of customer's associated loans. 
    '''
    loanWiseCycleDict = {}
    for loanId in loanDict:
        schObj   = schedule_for_loan.Schedule(loanId)
        if loanStatusDict[loanId]['status'] == 'TEMPORARY ARRANGEMENT':
            schedule = schObj.TAschedule()
        else:
            schedule = schObj.actualSchedule()        
        schObj.close_con()
        dateList = {'pastdate':'','upComingDate':''}
        for key in schedule.keys():            
            if schedule[key][0][1] > datetime.date.today():
                dateList['upComingDate'] = schedule[key][0][1]
                break
            dateList['pastdate'] = schedule[key][0][1]
        loanWiseCycleDict[loanId] = dateList
     
    return loanWiseCycleDict


def processReinstateCPA(request):
    '''
        This function checks whether any one of the customer loan have due amount.
        If yes, then it return the error message else it will make changes in the appropiate
        table and return a success message.
    '''
    if request.method=='POST':
        loan_id = eval(request.POST['loanList'])
        custId = request.POST['custId'].strip()
        cpaSupReason = request.POST['cpaReason'].strip()
        cpaSupValue = int(request.POST['cpaSupValue'].strip())
        cpaReInstValue = int(request.POST['cpaReInstValue'].strip())
        cpaUpdateFlag = int(request.POST['cpaUpdateFlag'].strip())
        
        store_id=Loan.objects.filter(loan_id=loan_id[0])[0].store_id

        if request.session.has_key("username"):
            username=request.session['username']
        else:
            return HttpResponse("Technical Error: Session Expired.", mimetype="data")
            
        con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
        try:            
            card_special_prev    = get_spl_privileges_by_usr_id(username,8)
            if str(card_special_prev).upper() == 'GRANT':
                loan_id = str(tuple(loan_id)).replace(',)',')')
                sql = "select ps.loan_id from Payments ps join Loan_Latest ll on \
                ps.loan_id=ll.loan_id where ps.loan_id in %s and due_amt>0 \
                and account_cust_id='%s'"%(loan_id,custId)
                resultSet = con.get_all_results(sql)
            
                if resultSet:
                    loanLst = []
                    result = "You need to either clear his/her Payment dues or make any arrangements for the following loans:<br/> "
                    for i in resultSet:
                        loanLst.append(str(i['loan_id']))
                    result = result+','.join(loanLst)
                    return HttpResponse(result, mimetype="data")
                else:
                    query = "select * from CPA_Info where store_cust_id='%s' and store_id='%s'"%(custId,store_id)
                    cpaInfo = con.get_one_result(query)
                    
                    query = "insert into CPA_history(store_cust_id,cpa_suppress,suppress_reason,\
                                cpa_reinstate,reinstate_time,did_customer_contact,store_id,create_time,modified_time,\
                                created_by,changed_by)\
                                select store_cust_id,cpa_suppress,suppress_reason,cpa_reinstate,reinstate_time,\
                                did_customer_contact,store_id,create_time,modified_time,created_by,changed_by from CPA_Info \
                                where store_cust_id='%s' and store_id='%s'"%(custId,store_id)
                    exeQry = con.execute(query)
                    
                    if cpaUpdateFlag:
                        query = "insert into CPA_history(store_cust_id,cpa_suppress,suppress_reason,\
                                cpa_reinstate,reinstate_time,did_customer_contact,store_id,create_time,modified_time,\
                                created_by,changed_by) values (%s,%s,%s,%s,%s,%s,%s,%s,now(),%s,%s)"                               
                        args = (custId,cpaSupValue,'Hits Exhausted',cpaReInstValue,cpaInfo['reinstate_time'],cpaInfo['did_customer_contact'],store_id,cpaInfo['create_time'],cpaInfo['created_by'],username)
                        exeQry = con.execute(query, args=args)
                        
                    query = "update CPA_Info set cpa_suppress=0,suppress_reason='%s',cpa_reinstate=1,\
                    reinstate_time=now(),did_customer_contact=0,modified_time=now(),changed_by='%s'where store_cust_id='%s' and store_id='%s'\
                    "%(cpaSupReason,username,custId,store_id)
                    exeQry = con.execute(query)
                    
                    dvrQry = "update Driver set CPA_hits=0,total_CPA_hits=0 where loan_id in %s"%(str(loan_id))
                    exeQry = con.execute(dvrQry)
                    
                    #taResetQry = "update TA_Mailers_Flag set flag_value='CPA_RESET' where \
                    #loan_id in %s and flag_value='To BE SENT' and flag_name='SSP_NOT'"%(str(loan_id))
                    #exeQry = con.execute(taResetQry)

                    return HttpResponse('CPA has been successfully reinstated.', mimetype="data")
            else:
                return HttpResponse("Technical Error: You do not have permission to Reinstate CPA.", mimetype="data")
        except Exception,e:
            logger.debug('CPA :: Process for reinstate CPA :: '+str(traceback.format_exc()) + str(e))
            return HttpResponse("Technical Error: Please Try again.", mimetype="data")
            

def getTotalHitsFrmDriver(loanStatus,cust_id,store_id,username):
    cpaInfoDetails = {}
    cpaInfoDetails['update_flag']       = 0
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    query   = "select * from CPA_Info where \
                store_cust_id='%s' and store_id='%s'"%(cust_id,store_id)
    cpaInfo = con.get_one_result(query)
    if not cpaInfo:
        ins_query = "insert into CPA_Info (store_cust_id,store_id,\
                        create_time,created_by) values ('%s','%s',now(),'%s')"%(cust_id,store_id,username)
        con.execute(ins_query)
        cpaInfo = con.get_one_result(query)
    
    if cpaInfo:
        if cpaInfo['cpa_suppress']:
            cpaInfoDetails.update(cpaInfo)
        else:
            egblLoans = []
            for loanDtls in loanStatus:
                query = "select count(*) as cnt from CPA_cancellations where override_flag=0 and loan_id=%s"%(loanDtls['entity_id'])
                getCanclLn = con.get_one_result(query)
                if (loanDtls['status_cd']  not in CUSTOMER_LEVEL_EXCLUSION_LIST) and \
                (loanDtls['status_cd']  not in LOAN_LEVEL_EXCLUSION_LIST) and not getCanclLn['cnt']:
                    egblLoans.append(int(loanDtls['entity_id']))
            
            if egblLoans:
                eglLoans = str(tuple(egblLoans)).replace(',)',')')
                query = "select max(total_CPA_hits) as maxHits from Driver where loan_id in %s"%(eglLoans)
                getHitCnt = con.get_one_result(query)
                if getHitCnt['maxHits']>=2:
                    cpaInfoDetails['store_cust_id']     = cust_id
                    cpaInfoDetails['cpa_suppress']      = 1
                    cpaInfoDetails['cpa_reinstate']     = 0
                    cpaInfoDetails['update_flag']       = 1
                    cpaInfoDetails['reinstate_time']    = cpaInfo['reinstate_time']
                else:             
                    cpaInfoDetails.update(cpaInfo)
            else:
                cpaInfoDetails.update(cpaInfo)
    return cpaInfoDetails

def updateImmPullinCPAInfo(cust_id,store_id,username,maxHit=None):
    
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    try:
        if maxHit==None:
            query = "select max(total_CPA_hits) as maxHit from Driver dr join (select ll.loan_id from GCMS_Data.gcm_case gc \
                                        join Loan_Latest ll on loan_id=entity_id and entity_type='loan' and account_cust_id='%s' \
                                        and store_id='%s' and status_cd not in %s and fund_dt is not null left join CPA_cancellations cc \
                                        on cc.loan_id=ll.loan_id where cc.loan_id is null) acc on acc.loan_id=dr.loan_id"%(cust_id,store_id,\
                                        str(tuple(set(END_STATUS_CPA+LOAN_LEVEL_EXCLUSION_LIST+CUSTOMER_LEVEL_EXCLUSION_LIST))))
            maxHit = con.get_one_result(query)['maxHit']
            
        query1 ="select did_customer_contact, cpa_suppress from CPA_Info where store_cust_id =%s and store_id='%s' "%(cust_id,store_id)       
        result = con.get_one_result(query1)
        
        if (maxHit>=2 or (result and result['cpa_suppress'] ==1)):
            
            if (result['did_customer_contact']!=1):
                query = "insert into CPA_history(store_cust_id,cpa_suppress,suppress_reason,\
                        cpa_reinstate,reinstate_time,did_customer_contact,store_id,create_time,modified_time,\
                        created_by,changed_by)\
                        select store_cust_id,cpa_suppress,suppress_reason,cpa_reinstate,reinstate_time,\
                        did_customer_contact,store_id,create_time,modified_time,created_by,changed_by from CPA_Info \
                        where store_cust_id='%s' and store_id='%s'"%(cust_id,store_id)
                exeQry = con.execute(query) 
                              
                cpaInfQry = "update CPA_Info set did_customer_contact=1,\
                modified_time=now(),changed_by='%s'where store_cust_id='%s' and store_id='%s'\
                "%(username,cust_id,store_id)
                exeQry = con.execute(cpaInfQry)
  
    except Exception,e:
        imm_pull_logger.error("Error in Update Immediate PULL flag in CPA Info :: Explaination::"+str(e)+str(traceback.format_exc()))
        
def update_CPA_Info(request):
#     import pdb;pdb.set_trace()
    if request.method=='POST':
        cust_id = request.POST['cust_id']
        store_id =request.POST['store_id']
    if request.session.has_key("username"):
        username=request.session['username']
    else:
        return HttpResponse("Technical Error: Session Expired.", mimetype="data")
    
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    try:
        query1 ="select did_customer_contact, cpa_suppress from CPA_Info where store_cust_id =%s and store_id='%s' "%(cust_id,store_id)       
        result = con.get_one_result(query1)
        if result and result['cpa_suppress'] == 1:
            if (result['did_customer_contact']!=1):
                query = "insert into CPA_history(store_cust_id,cpa_suppress,suppress_reason,\
                        cpa_reinstate,reinstate_time,did_customer_contact,store_id,create_time,modified_time,\
                        created_by,changed_by)\
                        select store_cust_id,cpa_suppress,suppress_reason,cpa_reinstate,reinstate_time,\
                        did_customer_contact,store_id,create_time,modified_time,created_by,changed_by from CPA_Info \
                        where store_cust_id='%s' and store_id='%s'"%(cust_id,store_id)
                exeQry = con.execute(query)
                
                query2 = "update CPA_Info set did_customer_contact=1,modified_time=now(),changed_by='%s'where store_cust_id='%s' and store_id='%s'"%(username,cust_id,store_id)
                exeQry = con.execute(query2)
        
            return HttpResponse('Customer contacted Agent and gave concern about CPA.', mimetype="data")
    except Exception,e:
        logger.debug('CPA_Info ::set did_customer_contact :: '+str(traceback.format_exc()) + str(e))
        return HttpResponse("Technical Error: Please Try again.", mimetype="data")  


def payment_holiday(loan_id,from_page='',trivial_refund_id=0):
    """
        This function will set all the payment holiday related flags.
    """
   
    conn = TranDB(section="TMS_DATA")
    curs = conn.getcursor()  
    currentdate = datetime.datetime.now().date()
    int_freeze_period_ph = pcconfig.int_freeze_period_ph
    result_dict= {}
    result_dict1= {}
    refund_int_fee=0
    try:
        q1="select * from Refund_Request where triv_rfnds_id=%s"%(trivial_refund_id)
        re=conn.processquery(query=q1, curs=curs,count=1)
        #OPB and Payment Holiday Count
        query4 = "select OPB,payment_holiday_count from Payments where loan_id =%s"%(loan_id)
        result4 = conn.processquery(query=query4, curs=curs,count=1)
        
        OPB=result4['OPB']
        if(from_page=='refund'):
            OPB=re['OPB']
            difference=OPB-result4['OPB']
            if difference>0:
                refund_int_fee=re['refund_amount']-difference
           
        ph="select max(payment_holiday_flag) as phf from PayDates where loan_id =%s and paydate>curdate() and override_flag=0"%(loan_id)
        ph_result = conn.processquery(query=ph, curs=curs,count=1) 
        #loan_interest_rate
        query1 = "select loan_interest_rate,pct_principal_paydown,min_due_amount from Product p join Loan l on p.product_id=l.product_id where loan_id =%s"%(loan_id)
        result1 = conn.processquery(query=query1, curs=curs,count=1)
        
        query6 = "Select paydate,cycle from PayDates where override_flag = 0 and  loan_id = %s and paydate >curdate() and payment_type = 'LNCYC' order by  paydate limit 2"%(loan_id)
        result6 = conn.processquery(query=query6, curs=curs)
        
        query2 = "Select paydate,cycle from PayDates where override_flag = 0 and  loan_id = %s and cycle in (%s,%s) and payment_type = 'STCYC' order by  paydate limit 2 "%(loan_id,result6[0]['cycle'],result6[1]['cycle'])
        result2 = conn.processquery(query=query2, curs=curs)
        
        #Fees_part  
        query7 = "select ifnull(sum(payment_amt - paid_amt),0) as fees from PaymentCalendar \
        where payment_type in ('ARRFEE') and override_flag = 0 and loan_id =%s"%(loan_id)
        result7 = conn.processquery(query=query7, curs=curs,count=1) 
        
        #OB
        query5 =" select sum(close_amt) as OB from (select (OPB + sum(if(pc.payment_type rlike 'LZD',pc.payment_amt-pc.paid_amt,0)) + sum(if(pc.payment_type rlike 'FEE',pc.payment_amt-pc.paid_amt,0))) \
                             as close_amt from PaymentCalendar as pc  join Payments using(loan_id) where loan_id in (%s) and override_flag=0 group by loan_id)a"%(loan_id)
        result5 = conn.processquery(query = query5 , curs=curs,count=1)
        
        principle = Money((Money((result1['pct_principal_paydown']/100),2)) * Money(OPB,2), 2, ROUND_DOWN)
        result_dict={}
        paydates=()
#         import pdb;pdb.set_trace()
        if result6:
            for i in range(len(result6)):
                j=0
                tempDict={}
                #interest_already_accrued    
                query3 = "select ifnull(sum(payment_amt - paid_amt),0) as interest_already_accrued from PaymentCalendar \
                where payment_type in ('INTCAPLZD') and override_flag = 0 and loan_id =%s and payment_nbr <=%s "%(loan_id,result2[i]['cycle'])
                result3 = conn.processquery(query=query3, curs=curs,count=1)
                
                #With Interest Suppression
                no_of_days_no_interest = min (int_freeze_period_ph, ((result2[i]['paydate'] - currentdate).days) )
                interest_till_date = currentdate + datetime.timedelta(days=no_of_days_no_interest)
                one_day_interest = Money(Money(result1['loan_interest_rate']/100, 4, ROUND_DOWN)*OPB, 2, ROUND_DOWN)
                interest = Money(one_day_interest * (result2[i]['paydate'] - interest_till_date).days, 2, ROUND_DOWN)
                nextdue = Money((principle + interest + result3['interest_already_accrued'] + result7['fees']+refund_int_fee),2)    
                next_due_amt=min (max (nextdue, result1['min_due_amount']), result5['OB'])
                tempDict['paydate']=result6[i]['paydate']
                tempDict['WithIntSupp'] = next_due_amt
                result_dict[result6[i]['paydate']] = interest_till_date
                
                #Without Interest Suppression
                one_day_interest = Money(Money(result1['loan_interest_rate']/100, 4, ROUND_DOWN)*OPB, 2, ROUND_DOWN)
                interest = Money(((result2[i]['paydate'] - currentdate).days * one_day_interest), 2, ROUND_DOWN)
                nextdue = Money(principle + interest + result3['interest_already_accrued'] + result7['fees']+refund_int_fee, 2)
                next_due_amt=min (max(nextdue, result1['min_due_amount']), result5['OB'])
                tempDict['WithoutIntSupp'] = next_due_amt
                paydates=paydates+(tempDict,)
                
#         render_to_response('custdetail/payment_holiday.html',{'result_dict':result_dict,'result_dict1':result_dict1})         
#     paydates = ({'paydate':'2015-01-10','withInt':50,'withOutInt':100},{'paydate':'2015-02-10','withInt':150,'withOutInt':200})
#     result_dict = {'2015-01-10IntTillDate':2015-01-29,'2015-02-10IntTillDate':2015-02-20}
    #render_to_response('custdetail/payment_holiday.html',{'result_dict':result_dict,'result_dict1':result_dict1,'paydates':paydates})
            final_dict = {'paydates':paydates,'result_dict':result_dict,'PH_Count':result4['payment_holiday_count'],'PH_Check':ph_result['phf']}    
            return final_dict
    except TMSCustomException,e:
        logger.debug(" :: Exception for Loan=%s while sending Payment Holiday / Communication Freeze details." % (loan['loan_id'],) + traceback.format_exc()) 

def payment_holiday_post(request):
    
    logger.info("Inside Payment Holiday Post Method")
    curtime= datetime.datetime.today()
    conn = TranDB(section="TMS_DATA")
    curs = conn.getcursor()
    from_page = None
    ta_status = ''
    if request.method=='POST':
        loan_id = request.POST['loan_id']
        payDate = request.POST['payDate']
        flag = int(request.POST['flag'])                                      
        payDate = (datetime.datetime.strptime(payDate,'%Y-%m-%d')).date()
        intSupFlag = int(request.POST['intSupFlag'])
        payDateCycle = int(request.POST['payDateCycle'])
        resultSet = eval(request.POST['resultSet'])
        interest_till_date=resultSet[payDate]
        arrg_till_date = payDate-datetime.timedelta(days=1)
        from_page = request.POST.get('from_page', '')  # In case of refund, this value will be 'refund'
#         nextDueAmtToPay = request.POST['nextDueAmtToPay']                                   
        int_supp =0
    if request.session.has_key("username"):
        username=request.session['username']
    try:      
        if(payDateCycle==1 and intSupFlag ==0):
            value=1
        elif(payDateCycle==1 and intSupFlag ==1):
            value=2
        elif(payDateCycle==2 and intSupFlag ==0):
            value=3
        elif(payDateCycle==2 and intSupFlag ==1):
            value=4
        if(value==4 or  value==3):
            reason = 'PH'
            ta_status = 'Arrangement - PH was set'
        else:
            reason = 'CF'
            ta_status = 'Arrangement - CF was set'
            
        reason_code = pcconfig.ARR_REASON[reason] 
        
        #Increase Payment Holiday Count.
        payments_obj = pcfactory.getpmobj(section="TMS_DATA", log=logger)
        payments_obj.getstate(loan_id,temp=0)
        acc_sup_reason = payments_obj.accrual_sup_reason 
        if(payDateCycle == 2):
            payments_obj.payment_holiday_count=payments_obj.payment_holiday_count + 1
        payments_obj.modified_date = curtime
        payments_obj.suspend_flag =1 
        payments_obj.modified_by = username
        payments_obj.updatetable(vars(payments_obj))
        #import pdb;pdb.set_trace()
        #Update Previous PaymentHoliday Records payment_holiday_flag to 1.
        q1="select ifnull(min(cycle),0) as cycle from PayDates where paydate>curdate() and override_flag=0 and payment_holiday_flag=1 and loan_id =%s"%(loan_id)
        cy_num = conn.processquery(query=q1, curs=curs,count=1)
        if(cy_num['cycle'])!=0:
            up_paydates=" update PayDates set payment_holiday_flag =0 where loan_id =%s and override_flag =0 and cycle =%s"%(loan_id,cy_num['cycle'])
            conn.processqueryandcommit(query=up_paydates, curs=curs)
            up_pay_cal="update PaymentCalendar set payment_holiday_flag =0 where loan_id =%s and override_flag =0 and  payment_nbr=%s"%(loan_id,cy_num['cycle'])
            conn.processqueryandcommit(query=up_pay_cal, curs=curs)
        
        #Update paymentholiday flag in paydates table and paymentcalendar table.
        if(payDateCycle == 2):
            
            cycle_fetch = "select  cycle-1 as cycle from PayDates where  loan_id =%s and override_flag=0 and  paydate='%s'"%(loan_id,payDate)
            cycle_result = conn.processquery(query=cycle_fetch, curs=curs,count=1)
            
            query1 = "update PayDates set payment_holiday_flag = 1 ,modified_dt='%s',modified_by='%s' where loan_id =%s and override_flag=0 and cycle = '%s'"%(curtime,username,loan_id,cycle_result['cycle'])
            conn.processqueryandcommit(query=query1, curs=curs)
            
            query2 = "update PaymentCalendar set payment_holiday_flag = 1,modified_date='%s',modified_by='%s' where loan_id =%s and override_flag=0 and payment_nbr = '%s'"%(curtime,username,loan_id,cycle_result['cycle'])
            conn.processqueryandcommit(query=query2, curs=curs)
        
        if(value==1):
            if(flag==1 and acc_sup_reason==pcconfig.ACC_SUP_REASON['LS']):
                int_supp =-1
            payments_obj.generalsuppress(loan_id,username,int_sup=int_supp,fee_sup=1,accrual_sup_reason=reason_code,\
                       status_sup =1,delin_sup=1,mpc_sup=1,arr_sup=1,mpc_suppress_tilldate=payDate,delin_suppress_tilldate=payDate,\
                       status_suppress_tilldate=payDate,arrangement_till_date=arrg_till_date,interest_suppress_tilldate=None,fees_suppress_tilldate=payDate,\
                       status_sup_reason=reason_code,delin_sup_reason=reason_code,mpc_sup_reason=reason_code,arrangement_sup_reason=reason_code,\
                       wat_sup=1,wat_sup_tilldate=arrg_till_date,wat_sup_reason=reason_code,\
                       date_elem=None,key_id=None,to_update=1,temp=0)
        
        elif(value==2):
            payments_obj.generalsuppress(loan_id,username,int_sup=1,fee_sup=1,accrual_sup_reason=reason_code,\
                       status_sup =1,delin_sup=1,mpc_sup=1,arr_sup=1,mpc_suppress_tilldate=payDate,delin_suppress_tilldate=payDate,\
                       status_suppress_tilldate=payDate,arrangement_till_date=arrg_till_date,interest_suppress_tilldate=interest_till_date,fees_suppress_tilldate=payDate,\
                       status_sup_reason=reason_code,delin_sup_reason=reason_code,mpc_sup_reason=reason_code,arrangement_sup_reason=reason_code,\
                       wat_sup=1,wat_sup_tilldate=arrg_till_date,wat_sup_reason=reason_code,\
                       date_elem=None,key_id=None,to_update=1,temp=0)
            
        if(value==3):
            if(flag==1 and acc_sup_reason==pcconfig.ACC_SUP_REASON['LS']):
                int_supp =-1
            payments_obj.generalsuppress(loan_id,username,int_sup=int_supp,fee_sup=1,accrual_sup_reason=reason_code,\
                       status_sup =1,delin_sup=1,mpc_sup=1,arr_sup=3,mpc_suppress_tilldate=payDate,delin_suppress_tilldate=payDate,\
                       status_suppress_tilldate=payDate,arrangement_till_date=arrg_till_date,interest_suppress_tilldate=None,fees_suppress_tilldate=payDate,\
                       status_sup_reason=reason_code,delin_sup_reason=reason_code,mpc_sup_reason=reason_code,arrangement_sup_reason=reason_code,\
                       wat_sup=1,wat_sup_tilldate=arrg_till_date,wat_sup_reason=reason_code,\
                       date_elem=None,key_id=None,to_update=1,temp=0)
        
        elif(value==4):
            payments_obj.generalsuppress(loan_id,username,int_sup=1,fee_sup=1,accrual_sup_reason=reason_code,\
                       status_sup =1,delin_sup=1,mpc_sup=1,arr_sup=3,mpc_suppress_tilldate=payDate,delin_suppress_tilldate=payDate,\
                       status_suppress_tilldate=payDate,arrangement_till_date=arrg_till_date,interest_suppress_tilldate=interest_till_date,fees_suppress_tilldate=payDate,\
                       status_sup_reason=reason_code,delin_sup_reason=reason_code,mpc_sup_reason=reason_code,arrangement_sup_reason=reason_code,\
                       wat_sup=1,wat_sup_tilldate=arrg_till_date,wat_sup_reason=reason_code,\
                       date_elem=None,key_id=None,to_update=1,temp=0)

        if from_page == 'refund':  # Updating Refund Reqeust if the from_page is refund
            triv_refund_id = request.POST['triv_id']
            refund_req_upd = 'update Refund_Request set ta_status=%s where triv_rfnds_id=%s'
            conn.processquery(refund_req_upd, curs=curs, args=(ta_status, triv_refund_id), fetch=False)
        logger.info("Informing UE about Payment Holiday")
        conn.commit()
        conn.close()
        LOC_paymentHoliday(loan_id)
        logger.info("Informed to UE about Payment Holiday")
        return HttpResponse('Success')
    except TMSCustomException,e:
        logger.debug(" :: Exception for Loan=%s while setting Payment Holiday / Communication Freeze." % (loan['loan_id'],) + traceback.format_exc())
        return HttpResponse('Failure') 

def auto_interest_fee_waiver(request):

    '''
    Procceses the front end requests ans returns the appropriate
    response using AutoWaiverAPI    
    '''
    waive_logger=customlogger.rotatinglogger("Auto_Fee_Waiver_Offline",'AUTO_FEE_WAIVER_LOGGER_ROTATING')
    if request.session.get("username",None):
        if request.method == "GET":
            try:
                get_waiveobj=None
                fromcust_id=request.GET['cust_id']
                fromstore_id=request.GET['store_id']
                user_name=request.session.get("username",None)
                print 'Get Request - Auto_Interest_Fee_Waiver'
                get_waiveobj=AutoWaiverAPI(int(fromcust_id),fromstore_id,user_name)
                cpa_loans=get_waiveobj.get_cpa_applicable_loans_list()
                llel_loans=get_waiveobj.get_llel_loans_list()
                clel_loans=get_waiveobj.get_clel_loans_list()
                cust_name,cust_soundex_name = get_waiveobj.get_customer_name()
                messages_aifw={'success':request.session.get('success_aifw',None),
                               'error': request.session.get('error_aifw',None),
                               'exceptions':get_waiveobj.get_exceptions(),
                               'warnings':request.session.get('warning_aifw',None)}
                request.session['exceptions_aifw']=[]
                request.session['warning_aifw']=None
                request.session['error_aifw']=None
                request.session['success_aifw']=None
                return render_to_response('custdetail/auto_waiver.html',
                                     {'cpa_loans':cpa_loans,'clel_loans':clel_loans,
                                     'llel_loans':llel_loans,'cust_id':fromcust_id,
                                     'cust_name':cust_name,'messages_aifw':messages_aifw,
                                     'cust_soundex_name':cust_soundex_name,'store_id':fromstore_id})
            except Exception,e:
                waive_logger.info('CPA_Waiver :: Exception is :: '+str(traceback.format_exc()) + str(e))
                request.session['exceptions_aifw'].append(e)
                
        if request.is_ajax():
            post_waiveobj=None
            fromcust_id=request.POST['cust_id']
            fromstore_id=request.POST['store_id']
            user_name=request.session.get("username",None)
            try:
                post_waiveobj=AutoWaiverAPI(int(fromcust_id),fromstore_id,user_name)
                #Update Request
                if request.POST.has_key('update'):
                    print 'Update Request - Auto_Fee_Waiver'
                    data=post_waiveobj.get_row(request.POST.get('loan_id'))
                    return HttpResponse(data, mimetype='application/json')
                
                #Waiver Request
                elif request.POST.has_key('waiver_dict'):
                    print 'Post Request - Auto_Fee_Waiver'
                    posted_dict = json.loads(request.POST['waiver_dict'])
                    response=post_waiveobj.process_waiver(posted_dict)
                    if not response.get('errors',None):
                        request.session['warning_aifw']=post_waiveobj.get_warnings()
                    if response.get('success',False):
                        request.session['success_aifw']=response['success']
                        return HttpResponse('success')
                    elif response.get('errors',False):
                        request.session['error_aifw']=response['errors']
                    
                    return HttpResponse(response)
                                                    
            except Exception,e:
                waive_logger.info('CPA_Waiver :: Exception is :: '+str(traceback.format_exc()) + str(e))
                request.session['exceptions_aifw'].append(e)
                pass
    else:
        return HttpResponse('<h3>Please Login to open this utility.</h3>')
        
def manualchange(request):
    """
    @summary: This API provides functionality to Receive Information from ManualChange Interface r
    and used to insert/update the manualchange table with appropriate entries 
    @param request: HTML Request
    @return type_change:
    @rtype: dictionary
     
    """
    
    username = request.session['username']
    type_post=''
    msg=''
    ref=''
    type_change=["Select","Payment Calendar Fix","Transaction fix","Paydates Fix","Status Change","Other"]

    currDate=datetime.datetime.now()
    conn = TranDB(section="CRAReporting_Data")
    cur = conn.getcursor()

    if request.method == "POST":
        try:
            loan_id = request.POST['loan_id']
            cust_id = request.POST['cust_id']
            type_post = request.POST['type_of_change']
            reason = type_post            
            ref = request.POST['ref']
            select_quer ="select * from CRAReporting_Data.Manual_Changes where loan_id ='%s' and override_flag=0"%(loan_id)
            select_res = conn.processquery(query = select_quer, curs = cur, count=0,fetch = True)
    
            if select_res:
                upd_query = "update CRAReporting_Data.Manual_Changes set \
                                 override_flag = 1,override_reason ='%s',modified_datetime = '%s',modified_by='%s' where \
                                 Manual_Changes_id = %s"%(reason,currDate,username,select_res[0]['Manual_Changes_id'])
                conn.processquery(query = upd_query, curs = cur)
                ins_quer = "insert into CRAReporting_Data.Manual_Changes (loan_id,cust_id,reason,\
                        create_datetime,created_by,override_flag,reference) \
                        values('%s','%s','%s','%s','%s','%s','%s')"%(loan_id,cust_id,reason,currDate,username,0,ref)
                conn.processquery(query = ins_quer, curs = cur)
            else:
                ins_quer = "insert into CRAReporting_Data.Manual_Changes (loan_id,cust_id,reason,\
                        create_datetime,created_by,override_flag,reference) \
                        values('%s','%s','%s','%s','%s','%s','%s')"%(loan_id,cust_id,reason,currDate,username,0,ref)
                conn.processquery(query = ins_quer, curs = cur)
            conn.commit()
            msg= 'success'
            conn.close()  
        except Exception,e:
            conn.rollback()
            conn.close()
            msg ='Error'
                    
    else:
        loan_id = request.GET['loan_id']
        cust_id = request.GET['cust_id']

    return render_to_response('custdetail/manual_changes.html',{"type_change":type_change,
                                                             'type_post':type_post,'msg':msg,
                                                             "loan_id": loan_id,"cust_id":cust_id})

def validateBankWizard(request):
    if 1:
        return True
    else:
        return False
    
    
def statement_view_Loc(request):
    loan_id = request.GET.get('loan_id')        
    con = mysqldbwrapper.MySQLWrapper(config_file_path,'TMS_DATA')
    sql = "select loan_id,statement_date,due_date,min_due_amount,interest_part,\
    fees_part,principal_part, outstanding_balance as loc_amt, \
    file_path from Statements where loan_id=%s order by statement_date desc" % (loan_id)
    result = con.get_all_results(sql)
    if result:
        paginator = Paginator(result, 10)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            statements = paginator.page(page)
        except (EmptyPage, InvalidPage):
            statements = paginator.page(paginator.num_pages)

        account_id = request.session['accountid']
        brand_name = Store_Info.objects.filter(store = Loan.objects.filter(loan_id = loan_id)[0].store_id)[0].brand_name
       
        folder = MEDIA_ROOT_INPUT.split("/")[-1]
        folder+='/'+account_id+'/'+brand_name
        return render_to_response('custdetail/statement_loc.html', {"statements": statements,'domaimPath':folder,'loan_id':loan_id})
    else:
        return render_to_response('custdetail/statement_loc.html', {"msg": "Statemets are not available for the Loan Id : "+str(loan_id)})
    
    return

