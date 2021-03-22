from app import app, labcorp_results_processing, match_labtest, match_employer, labcorp_requisitions
from apscheduler.schedulers.background import BackgroundScheduler

def process_results():
    # Get HL7 result fils that have not been processed
    #insert_file_names = labcorp_results_processing.files_to_process()
    # Clean files and separate messages 
    #labcorp_results_processing.format_hl7_files(insert_file_names)
    # run match logic#    
    #match_labtest.match_labtests()
    #match_employer.match_employer()
    #labcorp_requisitions.register_labtests()
    print("Processed all HL7")


sched = BackgroundScheduler(daemon=True)
sched.add_job(process_results,'interval',seconds=3)
sched.start()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=49002, debug=False)#, ssl_context=('cert.pem','key.pem'))
