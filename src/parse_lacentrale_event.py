import json
import re
import os
from lxml import etree
import jmespath

def parse_lacentrale_event(var):
    dico = json.loads(var)

    ## channel : 
    from_channel = jmespath.search("from", dico)

    match = re.search(r'<([^>]+)>', from_channel)
    if match:
        email = match.group(1)
        domain = email.split('@')[1]

        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            dico["channel"] = domain_parts[0]
        else:
            dico["channel"] = domain

    
    ##From Email : 

    from_email = jmespath.search("from", dico)

    match_email = re.search(r'<([^>]+)>', from_email)

    if match_email:
        email = match_email.group(1)
        dico["from_email"] = email

    ## To email : 

    from_toemail = jmespath.search("to", dico)

    from_toemail_split = from_toemail.split(",")

    goodsplit = from_toemail_split[2]

    withoutSpecialChar = goodsplit.replace('\r\n\t\"', "").replace('\r\n\t', "").replace('\"', "")

    
    arretAuChevron = withoutSpecialChar.split('<')[0]

    result_toemail = arretAuChevron

    dico["to_email"] = result_toemail

    ##Workspacename

    from_workspace = jmespath.search('to', dico)
    
    new_line_split = from_workspace.split('\r\n\t')

    start_of_line = new_line_split[3]

    first_word_of_new_line = start_of_line.split('.')[0]

    delete_quote_from_first_word = first_word_of_new_line.replace('\"', "")

    dico["workspace_name"] = delete_quote_from_first_word

    ##Workspace id : 

    from_workspace = jmespath.search("to", dico)

    split_workspaceid = from_workspace.split('@')

    desired_field = split_workspaceid[3]

    number = 36

    length = len(desired_field)

    result_workspace = desired_field[length - number:]

    dico["workspace_id"] = result_workspace

    #Brand :

    from_brand = jmespath.search('subject', dico)

    afterDash = from_brand.split("-")[1]

    firstword = afterDash.split(" ")[1]

    dico["brand"] = firstword

    next_words = afterDash.split(" ")[2:4]  # Prend les deux prochains mots
    combined_words = " ".join(next_words)
    dico["model"] = combined_words

     ##Model : 

    from_model = jmespath.search('subject', dico)

    after_dash = from_model.split("-")[1]

    ## message : 
    from_text = jmespath.search("text", dico)
    
    result_message = from_text.replace('\r\n', " ")

    dico["message"] = result_message

    print(from_text)

    ##Lastname et Firstname s: 

    from_lastname = jmespath.search('html', dico)

    result_lastname_firstname = from_lastname.split('Message de ')[1].split(' <img')[0]

    result_lastname = result_lastname_firstname.split(' ')[0]

    dico["lastname"] = result_lastname

    dico["firstname"] = result_lastname_firstname.split(' ')[1]

    ##Customer email

    from_customer_email = jmespath.search('html', dico)

    search_mail = from_customer_email.split('Mail : ')[1].split('</')[0]

    ## La ligne ci-dessous n'est pas nécessaire, mais je trouve ça plus lisible!
    result_customer_email = search_mail

    dico["customer_email"] = result_customer_email
   

    ## Subject

    from_subject = jmespath.search("subject", dico)

    result_subject = from_subject.replace('\r\n', "")
    dico["subject"] = result_subject

    ## Contact info

    dico['contact_info'] = [
        {
            "type": "email",
            "value": dico['customer_email']
        }
    ]

    return dico