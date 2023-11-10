import json
import os
import re
from lxml import etree
import jmespath



# def parse_leboncoin_event(var):
#     with open(var, "r") as opened:
#         dico = json.load(opened)
#         return dico


def parse_leboncoin_event(var):
    dico = json.loads(var)

    ## channel : 
    from_email = jmespath.search("from", dico)

    ## On cherche ce qui est entre les chevrons
    match = re.search(r'<([^>]+)>', from_email)
    if match:
        ##On prend le sous groupe et on divise à "@" pour obtenir le domaine
        email = match.group(1)
        domain = email.split('@')[1]
        ## si le domaine a plusieurs parties, on affiche la premiere, sinon on affiche tout
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            dico["channel"] = domain_parts[0]
        else:
            dico["channel"] = domain
    
    ##FROM email : 

    from_email = jmespath.search("from", dico)

    match_email = re.search(r'<([^>]+)>', from_email)

    dico["from_email"] = match_email.group(1)
    
    #To email

    from_to_email = jmespath.search("to", dico)

    ##On découpe le paragraphe en retours à la ligne, et on s'arrete au 3eme.
    #On part du principe que l'email sera toujours à ce retour à la ligne.

    split_from_to_email = from_to_email.split("\r\n\t")[3]

    ## on enleve les guillemets

    without_quote = split_from_to_email.replace('\"', "")

    ## Je mets souvens cette ligne inutile, mais je trouve ça plus lisible !

    result_from_to_email = without_quote

    dico["to_email"] = result_from_to_email

    #Workspace name : 

    ##On se place dans la clé "to"
    from_workspace_name = jmespath.search('to', dico)

    # on se place au bon retour de ligne
    split_workspace_name = from_workspace_name.split("\r\n\t")[4]

    #On capture ce qui a entre le "<" et le "."
    result_workspace_name = split_workspace_name.split('<')[1].split(".")[0]

    dico["workspace_name"] = result_workspace_name

    #Workspace id

    from_workspace = jmespath.search("to", dico)

    split_workspace = from_workspace.split('@')

    desired_field = split_workspace[4]

    ##On part du principe que l'id sera toujours de 36 chiffres...
    number = 36

    length = len(desired_field)

    ## Et on le récupère.
    result_workspace = desired_field[length - number:]

    dico["workspace_id"] = result_workspace

    ## brand

    from_brand = jmespath.search('subject', dico)
    
    afterQuote = from_brand.split("\"")[1]

    firstWord = afterQuote.split(" ")[0]

    dico["brand"] = firstWord

    ##Model : 

    from_model = jmespath.search('text', dico)

    ## On se place au bon endroit
    split_from_model = from_model.split('\r\n\r\n')[9].split('\r\n')[0]

    #On enlève le premier mot, que ce soit mazda, ferrari ou un autre

    result_model = split_from_model.split(' ', 1)[1]

    dico["model"] = result_model

    ##Message

    from_message = jmespath.search('text', dico)

    ##On se place entre les guillemets

    split_from_message = from_message.split('\u00ab')[1].split('\u00bb')[0]

    #on enlève les retours à la ligne

    without_new_line = split_from_message.replace('\r\n', "")


    result_message = f'«{without_new_line}»'

    dico["message"] = result_message

    ##Firstname

    from_firstname = jmespath.search('from', dico)

    beforeQuote = from_firstname.split('<')[0]

    firstWord = beforeQuote.split(' ')[0]

    lowercase = firstWord[0].lower() + firstWord[1:]

    dico["firstname"] = lowercase

    #Lastname

    from_last_name = jmespath.search("text", dico)

    split_from_last_name = from_last_name.split('Nom : ')[1].split('\r\n')[0]

    ## On enlève les espaces.
    result_from_last_name = split_from_last_name.replace(' ', '')

    dico["lastname"] = result_from_last_name

    #Phone number : 

    from_phone_number = jmespath.search('text', dico)

    #On se mettre entre "téléphone" et le retour à la ligne

    split_from_phone_number = from_phone_number.split('T\u00e9l\u00e9phone : ')[1].split('\r\n')[0]

    ## Pas d'espace dans un numéro de téléphone : 

    result_phone_number = split_from_phone_number.replace(' ', '')

    dico['customer_phone_number'] = result_phone_number

    ##customer Email : 
    
    from_customer_email = jmespath.search('text', dico)

    ## On se place entre "Email :" et la fin de la ligne
    split_from_customer_email = from_customer_email.split('E-mail : ')[1].split('\r\n')[0]

    result_without_space = split_from_customer_email.replace(' ', '')

    dico["customer_email"] = result_without_space
    ## Subject : 

    from_subject = jmespath.search("subject", dico)

    result = from_subject.replace('\r\n', "")
    dico["subject"] = result

    print(from_subject)

    ##Link

    from_link = jmespath.search('text', dico)

    split_from_link = from_link.split('Lien : ')[1].split('\r\n')[0]

    link_without_space = split_from_link.replace(' ', '')

    ## On utilise les variables pré-existantes.
    dico['links'] = {
        "lead": link_without_space
    }

    ## Contact info
    dico["contact_info"] = [
        {
            "type": "email",
            "value": dico['customer_email']
        },
        {
            "type": "phone_number",
            "value": dico['customer_phone_number']
        }
    ]

    return dico